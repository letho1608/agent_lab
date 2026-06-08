# -*- coding: utf-8-*-
import sys

if __name__ == '__main__':
    sys.path.append('..')

from .PupyConfig import PupyConfig

from io import open
from os import path, urandom, chmod, makedirs

import string
import errno
import time
import json
import hashlib

from datetime import datetime

from pupy.network.lib.transports.cryptoutils import ECPV
from getpass import getpass

from . import getLogger
logger = getLogger('credentials')

try:
    from cryptography import x509 as crypto_x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa as rsa_module
    from cryptography.x509.oid import NameOID
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError as e:
    logger.warning(e)
    _CRYPTOGRAPHY_AVAILABLE = False
    crypto_x509 = serialization = rsa_module = NameOID = None

from hashlib import md5
try:
    from Crypto.Cipher import AES
    from Crypto import Random
except Exception as e:
    logger.warning(e)
    AES=None
    Random=None

from io import BytesIO

try:
    import secretstorage
except ImportError:
    secretstorage = None


def bord(x):
    return x

long = int  # alias for Py3

# AES encryption compatible with OpenSSL (pycryptodome)


DEFAULT_ROLE = 'CLIENT'


class EncryptionError(Exception):
    pass


class GnomeKeyring(object):
    def __init__(self):
        if secretstorage:
            try:
                self.bus = secretstorage.dbus_init()
            except Exception as e:
                logger.exception(
                    'secretstorage dbus intialization failed: %s', e
                )

                self.bus = None

        self.collection = {
            'application': 'pupy'
        }

    def get_pass(self):
        if not self.bus:
            return

        try:
            collection = secretstorage.get_default_collection(self.bus)
            if collection.is_locked():
                collection.unlock()  # will open a gnome-keyring popup

            x = next(collection.search_items(self.collection))
            return x.get_secret()

        except StopIteration:
            pass

        except Exception as e:
            logger.warning("Error with GnomeKeyring get_pass: %s", e)

    def store_pass(self, password):
        if not self.bus:
            return

        try:
            collection = secretstorage.get_default_collection(self.bus)
            if collection.is_locked():
                collection.unlock()

            collection.create_item(
                'pupy_credentials', self.collection, password
            )

        except Exception as e:
            logger.warning("Error with GnomeKeyring store_pass: %s", e)

    def del_pass(self):
        if not self.bus:
            return

        collection = secretstorage.get_default_collection(self.bus)
        if collection.is_locked():
            collection.unlock()

        x = next(collection.search_items(self.collection))
        x.delete()


class Encryptor(object):
    _instance = None
    _getpass = getpass

    def __init__(self, password):
        self.password = password

    @staticmethod
    def initialized():
        return not (Encryptor._instance is None)

    @staticmethod
    def instance(password=None, getpass_hook=None, config=None):
        if secretstorage and not Encryptor._instance:
            if not password:
                config = config or PupyConfig()
                use_gnome_keyring = config.getboolean(
                    'pupyd', 'use_gnome_keyring'
                )

                if use_gnome_keyring:
                    gkr = GnomeKeyring()
                    password = gkr.get_pass()

            if not password:
                getpass_hook = getpass_hook or getpass
                if use_gnome_keyring:
                    logger.warning(
                        'use_gnome_keyring is true, the password '
                        'will be stored in the Gnome-Keyring'
                    )

                password = getpass_hook('[I] Credentials password: ')
                if use_gnome_keyring:
                    gkr.store_pass(password)

            Encryptor._instance = Encryptor(password)

        return Encryptor._instance

    def derive_key_and_iv(self, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = md5(d_i + self.password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length+iv_length]

    def encrypt(self, in_file, out_file, key_length=32):
        bs = AES.block_size
        salt = Random.new().read(bs - len('Salted__'))
        key, iv = self.derive_key_and_iv(salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        out_file.write('Salted__' + salt)
        finished = False

        while not finished:
            chunk = in_file.read(1024 * bs)
            if len(chunk) == 0 or len(chunk) % bs != 0:
                padding_length = bs - (len(chunk) % bs)
                chunk += padding_length * chr(padding_length)
                finished = True

            out_file.write(cipher.encrypt(chunk))

    def decrypt(self, in_file, out_file, key_length=32):
        bs = AES.block_size
        salt = in_file.read(bs)[len('Salted__'):]
        key, iv = self.derive_key_and_iv(salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        next_chunk = ''
        finished = False

        while not finished:
            chunk, next_chunk = next_chunk, cipher.decrypt(
                in_file.read(1024 * bs))

            if len(next_chunk) == 0:
                padding_length = bord(chunk[-1])

                if padding_length < 1 or padding_length > bs:
                    try:
                        # to avoid keep using a bad credential
                        GnomeKeyring().del_pass()
                    except Exception as e:
                        logger.exception('GnomeKeyring del_pass failed: %s', e)

                    raise ValueError("bad decrypt pad (%d)" % padding_length)

                # all the pad-bytes must be the same
                expected_padding = (padding_length * chr(padding_length))
                if chunk[-padding_length:] != expected_padding:
                    # this is similar to the bad decrypt:evp_enc.c
                    # from openssl program
                    raise ValueError("bad decrypt")

                chunk = chunk[:-padding_length]
                finished = True

            out_file.write(chunk)


ENCRYPTOR = Encryptor.instance

HELP_RESET_MSG = 'FYI you can reset your credentials by removing ' \
    'crypto/credentials.py but you will have to re-generate your payloads.'


def _generate_password(length):
    alphabet = string.punctuation + string.ascii_letters + string.digits
    return ''.join(
        alphabet[bord(c) % len(alphabet)] for c in urandom(length)
    )


def _generate_id(length):
    alphabet = string.ascii_letters
    return ''.join(
        alphabet[bord(c) % len(alphabet)] for c in urandom(length)
    )


def _generate_ecpv_keypair(curve='brainpoolP160r1'):
    return ECPV(curve=curve).generate_key()


def _generate_rsa_keypair(bits=2048):
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise EncryptionError(
            'cryptography is required to generate RSA credentials. '
            'Install with: pip install cryptography'
        )
    key = rsa_module.generate_private_key(public_exponent=65537, key_size=bits)
    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    if isinstance(private_key, bytes):
        private_key = private_key.decode('utf-8')
    public_key = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.PKCS1,
    )
    if isinstance(public_key, bytes):
        public_key = public_key.decode('utf-8')
    return private_key, public_key, key


def _gen_identifier_from_public_key(public_key, dig='sha1'):
    """SubjectKeyIdentifier-style digest from public key (cryptography)."""
    data = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    h = hashlib.new(dig)
    h.update(data)
    digest = h.hexdigest().upper()
    return ':'.join(digest[pos:pos + 2] for pos in range(0, min(40, len(digest)), 2))


def _generate_ssl_ca():
    _, _, ca_key = _generate_rsa_keypair()
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise EncryptionError('cryptography required for SSL CA')
    t = int(time.time())
    subject = issuer = crypto_x509.Name([
        crypto_x509.NameAttribute(NameOID.ORGANIZATION_NAME, _generate_id(10)),
    ])
    ski = crypto_x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key())
    cert_builder = (
        crypto_x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(1)
        .not_valid_before(datetime.utcfromtimestamp(t))
        .not_valid_after(datetime.utcfromtimestamp(t + 365 * 24 * 60 * 60))
        .add_extension(
            crypto_x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(ski, critical=False)
    )
    ca_cert = cert_builder.sign(ca_key, hashes.SHA256())
    ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM)
    if isinstance(ca_cert_pem, bytes):
        ca_cert_pem = ca_cert_pem.decode('utf-8')
    ca_key_pem = ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    if isinstance(ca_key_pem, bytes):
        ca_key_pem = ca_key_pem.decode('utf-8')
    return ca_key_pem, ca_cert_pem, ca_key, ca_cert


def _generate_ssl_keypair(
    rsa_key, ca_key, ca_cert, role='CONTROL',
        client=False, serial=2):
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise EncryptionError('cryptography required for SSL keypair')
    t = int(time.time())
    subject = crypto_x509.Name([
        crypto_x509.NameAttribute(NameOID.ORGANIZATION_NAME, _generate_id(10)),
        crypto_x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, role),
    ])
    cert_builder = (
        crypto_x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(rsa_key.public_key())
        .serial_number(serial)
        .not_valid_before(datetime.utcfromtimestamp(t))
        .not_valid_after(datetime.utcfromtimestamp(t + 365 * 24 * 60 * 60 * 3))
        .add_extension(
            crypto_x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            crypto_x509.SubjectKeyIdentifier.from_public_key(rsa_key.public_key()),
            critical=False,
        )
    )
    if client:
        cert_builder = cert_builder.add_extension(
            crypto_x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    else:
        cert_builder = cert_builder.add_extension(
            crypto_x509.KeyUsage(
                digital_signature=False,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    cert = cert_builder.sign(ca_key, hashes.SHA256())
    key_pem = rsa_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    if isinstance(key_pem, bytes):
        key_pem = key_pem.decode('utf-8')
    if isinstance(cert_pem, bytes):
        cert_pem = cert_pem.decode('utf-8')
    return key_pem, cert_pem


def _generate_ecpv_keypair_bp384():
    return _generate_ecpv_keypair(curve='brainpoolP384r1')


def _generate_rsa_keypair_4096():
    priv, pub, _ = _generate_rsa_keypair(bits=4096)
    return priv, pub


def _generate_path_secret():
    return {
        'PATH_GEN_SECRET': _generate_password(20)
    }

def _generate_bind_payloads_password():
    return {
        'BIND_PAYLOADS_PASSWORD': _generate_password(20)
    }


def _generate_ecpv_rc4():
    CONTROL_ECPV_RC4_PRIVATE_KEY, CONTROL_ECPV_RC4_PUBLIC_KEY = \
        _generate_ecpv_keypair_bp384()

    CLIENT_ECPV_RC4_PRIVATE_KEY, CLIENT_ECPV_RC4_PUBLIC_KEY = \
        _generate_ecpv_keypair_bp384()

    return {
        'CONTROL_ECPV_RC4_PRIVATE_KEY': CONTROL_ECPV_RC4_PRIVATE_KEY,
        'CONTROL_ECPV_RC4_PUBLIC_KEY': CONTROL_ECPV_RC4_PUBLIC_KEY,
        'CLIENT_ECPV_RC4_PRIVATE_KEY': CLIENT_ECPV_RC4_PRIVATE_KEY,
        'CLIENT_ECPV_RC4_PUBLIC_KEY': CLIENT_ECPV_RC4_PUBLIC_KEY,
    }


def _generate_rsa_keys():
    CONTROL_RSA_PRIVATE_KEY, CONTROL_RSA_PUBLIC_KEY, _ = \
        _generate_rsa_keypair()
    CLIENT_RSA_PRIVATE_KEY, CLIENT_RSA_PUBLIC_KEY, _ = \
        _generate_rsa_keypair()

    return {
        'CONTROL_RSA_PUB_KEY': CONTROL_RSA_PUBLIC_KEY,
        'CLIENT_RSA_PUB_KEY': CLIENT_RSA_PUBLIC_KEY,
        'CONTROL_RSA_PRIV_KEY': CONTROL_RSA_PRIVATE_KEY,
        'CLIENT_RSA_PRIV_KEY': CLIENT_RSA_PRIVATE_KEY,
    }


def _generate_dnscnc_v1_keys():
    ECPV_PRIVATE_KEY, ECPV_PUBLIC_KEY = _generate_ecpv_keypair()

    return {
        'CONTROL_DNSCNC_PRIV_KEY': ECPV_PRIVATE_KEY,
        'CLIENT_DNSCNC_PUB_KEY': ECPV_PUBLIC_KEY,
    }


def _generate_dnscnc_v2_keys():
    ECPV_PRIVATE_KEY_V2, ECPV_PUBLIC_KEY_V2 = _generate_ecpv_keypair(
        curve='brainpoolP224r1')

    return {
        'CONTROL_DNSCNC_PRIV_KEY_V2': ECPV_PRIVATE_KEY_V2,
        'CLIENT_DNSCNC_PUB_KEY_V2': ECPV_PUBLIC_KEY_V2,
    }


def _generate_simple_rsa_keys():
    RSA_PRIVATE_KEY_1, RSA_PUBLIC_KEY_1 = _generate_rsa_keypair_4096()
    RSA_PRIVATE_KEY_2, RSA_PUBLIC_KEY_2 = _generate_rsa_keypair_4096()

    return {
        'CONTROL_SIMPLE_RSA_PRIV_KEY': RSA_PRIVATE_KEY_1,
        'CLIENT_SIMPLE_RSA_PUB_KEY': RSA_PUBLIC_KEY_1,
        'CLIENT_SIMPLE_RSA_PRIV_KEY': RSA_PRIVATE_KEY_2,
        'CONTROL_SIMPLE_RSA_PUB_KEY': RSA_PUBLIC_KEY_2,
    }

def gen_identifier(cert, dig='sha1'):
    """SubjectKeyIdentifier-style string from cert (cryptography x509.Certificate)."""
    return _gen_identifier_from_public_key(cert.public_key(), dig=dig)


def _generate_apk_keypair():
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise EncryptionError('cryptography required for APK keypair')
    priv, pub, key = _generate_rsa_keypair(2048)
    t = int(time.time())
    subject = issuer = crypto_x509.Name([
        crypto_x509.NameAttribute(NameOID.ORGANIZATION_NAME, _generate_id(10)),
    ])
    cert_builder = (
        crypto_x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1337)
        .not_valid_before(datetime.utcfromtimestamp(t))
        .not_valid_after(datetime.utcfromtimestamp(t + 365 * 24 * 60 * 60 * 5))
        .add_extension(
            crypto_x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
            critical=False,
        )
    )
    cert = cert_builder.sign(key, hashes.SHA256())
    priv_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    if isinstance(priv_pem, bytes):
        priv_pem = priv_pem.decode('utf-8')
    if isinstance(cert_pem, bytes):
        cert_pem = cert_pem.decode('utf-8')
    return {
        'CONTROL_APK_PRIV_KEY': priv_pem,
        'CONTROL_APK_PUB_KEY': cert_pem,
    }

def _generate_pki_ssl_keys():
    SSL_CA_PRIVATE_KEY, SSL_CA_CERTIFICATE, CAKEY, CACERT = \
        _generate_ssl_ca()

    _, _, KEY1 = _generate_rsa_keypair()
    _, _, KEY2 = _generate_rsa_keypair()
    _, _, KEY3 = _generate_rsa_keypair()
    _, _, KEY4 = _generate_rsa_keypair()

    CONTROL_SSL_BIND_KEY, CONTROL_SSL_BIND_CERTIFICATE = \
        _generate_ssl_keypair(KEY1, CAKEY, CACERT)
    CLIENT_SSL_BIND_KEY, CLIENT_SSL_BIND_CERTIFICATE = \
        _generate_ssl_keypair(
            KEY2, CAKEY, CACERT, role='CLIENT', serial=3
        )

    CONTROL_SSL_CLIENT_KEY, CONTROL_SSL_CLIENT_CERTIFICATE = \
        _generate_ssl_keypair(
            KEY3, CAKEY, CACERT, client=True, serial=4
        )
    CLIENT_SSL_CLIENT_KEY, CLIENT_SSL_CLIENT_CERTIFICATE = \
        _generate_ssl_keypair(
            KEY4, CAKEY, CACERT, role='CLIENT', client=True, serial=5
        )

    return {
        'SSL_CA_CERT': SSL_CA_CERTIFICATE,
        'SSL_CA_KEY': SSL_CA_PRIVATE_KEY,
        'CONTROL_SSL_BIND_KEY': CONTROL_SSL_BIND_KEY,
        'CLIENT_SSL_BIND_KEY': CLIENT_SSL_BIND_KEY,
        'CONTROL_SSL_BIND_CERT': CONTROL_SSL_BIND_CERTIFICATE,
        'CLIENT_SSL_BIND_CERT': CLIENT_SSL_BIND_CERTIFICATE,
        'CONTROL_SSL_CLIENT_CERT': CONTROL_SSL_CLIENT_CERTIFICATE,
        'CLIENT_SSL_CLIENT_CERT': CLIENT_SSL_CLIENT_CERTIFICATE,
        'CONTROL_SSL_CLIENT_KEY': CONTROL_SSL_CLIENT_KEY,
        'CLIENT_SSL_CLIENT_KEY': CLIENT_SSL_CLIENT_KEY,
    }


class Credentials(object):
    GENERATORS = {
        # path secret used to generate random path that do not change between each pupysh run
        'PATH_GEN_SECRET': _generate_path_secret,
        'BIND_PAYLOADS_PASSWORD': _generate_bind_payloads_password,
        'CONTROL_ECPV_RC4_PRIVATE_KEY': _generate_ecpv_rc4,
        'CONTROL_ECPV_RC4_PUBLIC_KEY': _generate_ecpv_rc4,
        'CLIENT_ECPV_RC4_PRIVATE_KEY': _generate_ecpv_rc4,
        'CLIENT_ECPV_RC4_PUBLIC_KEY': _generate_ecpv_rc4,
        'CONTROL_RSA_PUB_KEY': _generate_rsa_keys,
        'CLIENT_RSA_PUB_KEY': _generate_rsa_keys,
        'CONTROL_RSA_PRIV_KEY': _generate_rsa_keys,
        'CLIENT_RSA_PRIV_KEY': _generate_rsa_keys,
        'CONTROL_DNSCNC_PRIV_KEY': _generate_dnscnc_v1_keys,
        'CLIENT_DNSCNC_PUB_KEY': _generate_dnscnc_v1_keys,
        'CONTROL_DNSCNC_PRIV_KEY_V2': _generate_dnscnc_v2_keys,
        'CLIENT_DNSCNC_PUB_KEY_V2': _generate_dnscnc_v2_keys,
        'CONTROL_SIMPLE_RSA_PRIV_KEY': _generate_simple_rsa_keys,
        'CLIENT_SIMPLE_RSA_PUB_KEY': _generate_simple_rsa_keys,
        'CLIENT_SIMPLE_RSA_PRIV_KEY': _generate_simple_rsa_keys,
        'CONTROL_SIMPLE_RSA_PUB_KEY': _generate_simple_rsa_keys,
        #'CONTROL_APK_PRIV_KEY': _generate_apk_keypair,
        #'CONTROL_APK_PUB_KEY': _generate_apk_keypair,
        'SSL_CA_CERT': _generate_pki_ssl_keys,
        'SSL_CA_KEY': _generate_pki_ssl_keys,
        'CONTROL_SSL_BIND_KEY': _generate_pki_ssl_keys,
        'CLIENT_SSL_BIND_KEY': _generate_pki_ssl_keys,
        'CONTROL_SSL_BIND_CERT': _generate_pki_ssl_keys,
        'CLIENT_SSL_BIND_CERT': _generate_pki_ssl_keys,
        'CONTROL_SSL_CLIENT_CERT': _generate_pki_ssl_keys,
        'CLIENT_SSL_CLIENT_CERT': _generate_pki_ssl_keys,
        'CONTROL_SSL_CLIENT_KEY': _generate_pki_ssl_keys,
        'CLIENT_SSL_CLIENT_KEY': _generate_pki_ssl_keys,
    }

    def __init__(self, role=None, password=None, config=None, validate=False):
        config = config or PupyConfig()

        self._configfile = path.join(
            config.get_folder('crypto'), 'credentials.py'
        )
        self._credentials = {}
        self._config = config
        self._encrypted = True

        role = role or DEFAULT_ROLE
        self.role = role.upper() if role else 'ANY'

        if self.role not in ('CONTROL', 'CLIENT'):
            raise ValueError('Unsupported role: {}'.format(self.role))

        self._load(password)
        if validate:
            self._generate(password)

    def _get_cert_expiration(self, cert_pem):
        """Lay ngay het han cert (cryptography hoac pyOpenSSL). Tra None neu khong parse duoc."""
        try:
            if _CRYPTOGRAPHY_AVAILABLE and crypto_x509 is not None:
                data = cert_pem if isinstance(cert_pem, bytes) else cert_pem.encode('utf-8')
                cert = crypto_x509.load_pem_x509_certificate(data)
                not_after = getattr(cert, 'not_valid_after_utc', None) or getattr(cert, 'not_valid_after', None)
                if not_after:
                    return datetime(
                        not_after.year, not_after.month, not_after.day,
                        not_after.hour, not_after.minute, not_after.second
                    )
        except Exception:
            pass
        try:
            from OpenSSL import crypto
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
            not_after = cert.get_not_after()
            return datetime(
                not_after.year, not_after.month, not_after.day,
                not_after.hour, not_after.minute, not_after.second
            )
        except Exception:
            return None

    def _generate(self, password):
        required_generators = set()

        for cred in Credentials.GENERATORS:
            generator = Credentials.GENERATORS[cred]
            if cred not in self._credentials:
                required_generators.add(generator)
                logger.warning(
                    'Credential "%s" is missing and will be generated', cred
                )
            elif b'BEGIN CERTIFICATE' in self._credentials[cred]:
                expiration = self._get_cert_expiration(self._credentials[cred])
                if expiration is not None:
                    now = datetime.utcnow()
                    diff = (expiration - now).days

                    if expiration <= now:
                        logger.error(
                            'Credential "%s" is expired! '
                            'All related credentials will be regenerated',
                            cred
                        )
                        required_generators.add(generator)
                    elif diff < 7:
                        logger.error('%s will expire in %d days', cred, diff)
                    elif diff < 90:
                        logger.warning('%s will expire in %d days', cred, diff)
                    else:
                        logger.debug(
                            'Credential "%s" will expire in %d days', cred, diff
                        )
            else:
                logger.debug('Credential "%s" exists', cred)

        if required_generators and not _CRYPTOGRAPHY_AVAILABLE:
            raise EncryptionError(
                'cryptography is required to generate SSL credentials. '
                'Install with: pip install cryptography'
            )
        for generator in required_generators:
            new_creds = generator()
            self._credentials.update(new_creds)

        updated = bool(required_generators)

        if updated:
            self.save(password)

        return updated

    def save(self, password=None):
        logger.warning('Saving credentials to %s', self._configfile)

        try:
            creds_dir = path.dirname(self._configfile)
            if not path.isdir(creds_dir):
                makedirs(creds_dir)
        except OSError as e:
            if not e.errno == errno.EEXIST:
                raise

        backup = None

        if path.isfile(self._configfile):
            with open(self._configfile) as user_config:
                backup = user_config.read()

        try:
            with open(self._configfile, 'wb') as user_config:
                chmod(self._configfile, 0o600)

                content = json.dumps(
                    {
                        key: value.decode('latin1') if isinstance(
                            value, bytes
                        ) else value
                        for key, value in self._credentials.items()
                    },
                    sort_keys=True, indent=2
                ).encode('latin1')

                if self._encrypted and ENCRYPTOR and password:
                    encryptor = ENCRYPTOR(password=password)
                    encryptor.encrypt(BytesIO(content), user_config)
                else:
                    user_config.write(content)

        except Exception:
            if backup:
                with open(self._configfile, 'wb') as user_config:
                    user_config.write(backup)

            raise

    def _load(self, password):
        if path.exists(self._configfile):
            with open(self._configfile, 'rb') as creds:
                logger.info('Reading credentials from %s', self._configfile)

                content = creds.read()
                if not content:
                    logger.error(
                        'Credentials storage (%s) is empty', self._configfile
                    )
                    return

                if content.startswith(b'Salted__'):
                    if not ENCRYPTOR:
                        raise EncryptionError(
                            'Encrpyted credential storage: {}'.format(
                                self._configfile
                            )
                        )

                    fcontent = BytesIO()
                    encryptor = ENCRYPTOR(
                        password=password,
                        config=self._config
                    )

                    try:
                        encryptor.decrypt(BytesIO(content), fcontent)
                    except Exception as e:
                        raise EncryptionError(
                            'Invalid password or corrupted data '
                            '({}).\n{}'.format(e, HELP_RESET_MSG)
                        )

                    content = fcontent.getvalue()
                else:
                    self._encrypted = False

                if content.startswith(b'{'):
                    credentials_dict = json.loads(content)
                    self._credentials = {
                        k: credentials_dict[k].encode('latin1')
                        for k in credentials_dict
                    }
                else:
                    exec(content, self._credentials)
                    for key in tuple(self._credentials):
                        if key.startswith('_'):
                            del self._credentials[key]

                    self.save(password)

    def __getitem__(self, key):
        env = globals()

        if key in self._credentials:
            return self._credentials[key]
        elif '{}_{}'.format(self.role, key) in self._credentials:
            return self._credentials['{}_{}'.format(self.role, key)]
        elif key in env:
            return env[key]
        elif 'DEFAULT_{}'.format(key) in env:
            logger.warning("Using default credentials for %s", key)
            return env['DEFAULT_{}'.format(key)]
        else:
            return None

    def __setitem__(self, key, value):
        self._credentials[key] = value

    def __iter__(self):
        return iter(self._credentials)


if __name__ == '__main__':
    credentials = Credentials()
    credentials._generate(force=True)
