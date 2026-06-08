# -*- coding: utf-8 -*-

from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser

try:
    from cryptography import x509
    from pupy.pupylib.utils.cert_display import cert_to_text
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    x509 = None
    cert_to_text = None
    _CRYPTOGRAPHY_AVAILABLE = False

__class_name__ = 'x509'


@config(cat='admin')
class x509(PupyModule):
    ''' Fetch certificate from server '''

    dependencies = ['pupyutils.basic_cmds']

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog='x509', description=cls.__doc__)
        cls.arg_parser.add_argument('host', help='Address or path')
        cls.arg_parser.add_argument('port', type=int, default=443, nargs='?', help='Port')
        cls.arg_parser.add_argument('-F', '--file', action='store_true', default=False,
                                     help='Force treat host as file path')
        cls.arg_parser.add_argument('-R', '--raw', action='store_true', default=False,
                                     help='Do not convert to text')

    def run(self, args):
        if args.file or '/' in args.host or '\\' in args.host:
            cat = self.client.remote('pupyutils.basic_cmds', 'cat', False)
            cert = cat(args.host, None, None, None)
        else:
            get_server_certificate = self.client.remote('ssl', 'get_server_certificate')
            cert = get_server_certificate((args.host, args.port))

        if not args.raw:
            parsed = None
            if not _CRYPTOGRAPHY_AVAILABLE or x509 is None or cert_to_text is None:
                self.error(
                    'cryptography is required to parse certificates. '
                    'Install with: pip install cryptography'
                )
                return
            cert_bytes = cert if isinstance(cert, bytes) else cert.encode('utf-8')
            try:
                if b'-----BEGIN' in cert_bytes or b'BEGIN CERTIFICATE' in cert_bytes:
                    c = x509.load_pem_x509_certificate(cert_bytes)
                else:
                    c = x509.load_der_x509_certificate(cert_bytes)
                parsed = cert_to_text(c)
            except Exception:
                try:
                    c = x509.load_der_x509_certificate(cert_bytes)
                    parsed = cert_to_text(c)
                except Exception:
                    pass

            cert = parsed

        if cert:
            self.log(cert)
        else:
            self.error('Invalid certificate format')
