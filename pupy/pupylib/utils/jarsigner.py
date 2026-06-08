# -*- coding: utf-8 -*-


from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha1
from base64 import b64encode

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs7
    from cryptography.hazmat.primitives.serialization.pkcs7 import (
        PKCS7SignatureBuilder,
        PKCS7Options,
    )
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    _CRYPTOGRAPHY_AVAILABLE = False
    x509 = hashes = serialization = pkcs7 = PKCS7SignatureBuilder = PKCS7Options = None


def _jarsigner_impl(pem_priv, pem_cert, apk_path, dest_fileobj):
    if not isinstance(pem_priv, bytes):
        pem_priv = pem_priv.encode('utf-8')
    if not isinstance(pem_cert, bytes):
        pem_cert = pem_cert.encode('utf-8')

    cert = x509.load_pem_x509_certificate(pem_cert)
    key = serialization.load_pem_private_key(pem_priv, password=None)

    MANIFEST_MF = (
        'Manifest-Version: 1.0\r\n'
        'Created-By: 9.0.4 (Oracle Corporation)\r\n'
        '\r\n'
    )
    SHA1_MAIN_ATTRIBUTES = b64encode(sha1(MANIFEST_MF.encode()).digest())
    SIGNER_SF = ''

    with ZipFile(apk_path) as infile:
        with ZipFile(dest_fileobj, "w", ZIP_DEFLATED) as outfile:
            for name in infile.namelist():
                if name.startswith('META-INF'):
                    continue

                content = infile.read(name)
                digest = sha1(content)
                outfile.writestr(name, content)

                manifest_record = 'Name: {}\r\nSHA1-Digest: {}\r\n\r\n'.format(
                    name, b64encode(digest.digest())
                )
                MANIFEST_MF += manifest_record

                sf_record = 'Name: {}\r\nSHA1-Digest: {}\r\n\r\n'.format(
                    name, b64encode(sha1(manifest_record.encode()).digest())
                )
                SIGNER_SF += sf_record

            SIGNER_SF = (
                'Signature-Version: 1.0\r\n'
                'Created-By: 9.0.4 (Oracle Corporation)\r\n'
                'SHA1-Digest-Manifest: {}\r\n'
                'SHA1-Digest-Manifest-Main-Attributes: {}\r\n'
                '\r\n'.format(
                    b64encode(sha1(MANIFEST_MF.encode()).digest()),
                    SHA1_MAIN_ATTRIBUTES,
                )
                + SIGNER_SF
            )

            outfile.writestr('META-INF/MANIFEST.MF', MANIFEST_MF)
            outfile.writestr('META-INF/SIGNER.SF', SIGNER_SF)

            # PKCS#7 detached signature (SHA1 for APK v1 signing)
            signer_sf_bytes = SIGNER_SF.encode('utf-8')
            pkcs7_sig = (
                PKCS7SignatureBuilder()
                .set_data(signer_sf_bytes)
                .add_signer(cert, key, hashes.SHA1())
                .sign(serialization.Encoding.DER, [PKCS7Options.DetachedSignature])
            )
            outfile.writestr('META-INF/SIGNER.RSA', pkcs7_sig)


def jarsigner(pem_priv, pem_cert, apk_path, dest_fileobj):
    """Sign an APK. Uses cryptography (no M2Crypto)."""
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError(
            'cryptography is required to sign APK. '
            'Install with: pip install cryptography>=42.0.0'
        )
    _jarsigner_impl(pem_priv, pem_cert, apk_path, dest_fileobj)


JARSIGNER_AVAILABLE = _CRYPTOGRAPHY_AVAILABLE
