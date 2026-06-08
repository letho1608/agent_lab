# -*- encoding: utf-8 -*-
"""Xóa màn hình console."""

from pupy.pupylib.PupyModule import PupyArgumentParser

usage = 'Clear the screen'
parser = PupyArgumentParser(prog='clear', description=usage)


def do(server, handler, config, args):
    try:
        out = getattr(handler, 'stdout', None)
        if out is not None and hasattr(out, 'write'):
            out.write(b'\033[2J\033[H')
            if hasattr(out, 'flush'):
                out.flush()
            return
    except Exception:
        pass
    handler.display('\n' * 60)
