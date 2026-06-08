# -*- encoding: utf-8 -*-
"""Hiển thị phiên bản và thông tin server."""

from pupy.pupylib.PupyModule import PupyArgumentParser
from pupy.pupylib.PupyOutput import Line, Color, Success

usage = 'Show Pupy version and server info'
parser = PupyArgumentParser(prog='version', description=usage)


def do(server, handler, config, args):
    from pupy.pupylib.PupyVersion import BANNER, UPSTREAM
    handler.display(Line(Color(BANNER.strip(), 'green')))
    handler.display(Line(Color(UPSTREAM, 'cyan')))
    handler.display(Line(Success('Server: {} listeners, {} sessions'.format(
        len(server.listeners or {}),
        len(server.clients)))))
