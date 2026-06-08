# -*- coding: utf-8 -*-
# Stub termios/tty/pty/fcntl/readline tren Windows de PupyCmd (server) load duoc.

import sys


def install():
    if sys.platform != 'win32':
        return
    # termios stub
    class _Termios:
        TCSANOW = 0
        TCSADRAIN = 1
        TIOCGWINSZ = 0x5413
        FIONREAD = 0x541B

        @staticmethod
        def tcgetattr(fd):
            return [0] * 6

        @staticmethod
        def tcsetattr(fd, when, mode):
            pass

    sys.modules['termios'] = _Termios()

    # tty stub
    class _Tty:
        @staticmethod
        def setraw(fd, when=0):
            pass

    sys.modules['tty'] = _Tty()

    # pty stub
    class _Pty:
        STDOUT_FILENO = 1

    sys.modules['pty'] = _Pty()

    # fcntl stub
    class _Fcntl:
        @staticmethod
        def ioctl(fd, op, arg, *args):
            return 0

    sys.modules['fcntl'] = _Fcntl()

    # readline stub (Windows thieu readline) — cmd.Cmd.cmdloop goi get_completer/set_completer
    if 'readline' not in sys.modules or sys.modules['readline'] is None:
        class _Readline:
            _line_buffer = ''
            _completer = None

            @staticmethod
            def set_history_length(n):
                pass

            @staticmethod
            def read_history_file(path):
                pass

            @staticmethod
            def write_history_file(path):
                pass

            @staticmethod
            def set_pre_input_hook(fn):
                pass

            @staticmethod
            def set_completer_delims(s):
                pass

            @classmethod
            def get_completer(cls):
                return cls._completer

            @classmethod
            def set_completer(cls, fn):
                cls._completer = fn

            @staticmethod
            def parse_and_bind(s):
                pass

            @classmethod
            def get_line_buffer(cls):
                return getattr(cls, '_line_buffer', '')

            @staticmethod
            def redisplay():
                pass

        sys.modules['readline'] = _Readline()
