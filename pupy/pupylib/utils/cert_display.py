# -*- coding: utf-8 -*-
"""Format X.509 certificate as text (cryptography library)."""



def cert_to_text(cert):
    """
    Format a cryptography.x509.Certificate as human-readable text.
    """
    lines = [
        'Certificate:',
        '    Data:',
        '        Version: {} (0x{:x})'.format(
            getattr(cert.version, 'value', 2) + 1, getattr(cert.version, 'value', 2)
        ),
        '        Serial Number:',
        '            {}'.format(_serial_hex(cert.serial_number)),
        '        Signature Algorithm: {}'.format(
            getattr(cert.signature_algorithm_oid, '_name', None) or str(cert.signature_algorithm_oid)
        ),
        '        Issuer: {}'.format(cert.issuer.rfc4514_string()),
        '        Validity',
        '            Not Before: {}'.format(_format_date(getattr(cert, 'not_valid_before_utc', None) or getattr(cert, 'not_valid_before', None))),
        '            Not After : {}'.format(_format_date(getattr(cert, 'not_valid_after_utc', None) or getattr(cert, 'not_valid_after', None))),
        '        Subject: {}'.format(cert.subject.rfc4514_string()),
        '        Subject Public Key Info:',
        '            Public Key Algorithm: {}'.format(cert.public_key().__class__.__name__),
    ]
    return '\n'.join(lines)


def _format_date(d):
    if d is None:
        return 'N/A'
    return d.strftime('%b %d %H:%M:%S %Y GMT')


def _serial_hex(n):
    if n == 0:
        return '00'
    h = hex(n)[2:].upper()
    if len(h) % 2:
        h = '0' + h
    return ':'.join(h[i:i+2] for i in range(0, len(h), 2))
