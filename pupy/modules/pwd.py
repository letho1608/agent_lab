# -*- coding: utf-8 -*-

import sys

from pupy.pupylib.PupyModule import config, PupyArgumentParser, PupyModule

getcwd = 'getcwd'

__class_name__ = 'pwd'


@config(cat="admin")
class pwd(PupyModule):
    """ Get current working dir """
    is_module=False

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog="pwd", description=cls.__doc__)

    def run(self, args):
        try:
            rgetcwd = self.client.remote('os', getcwd, False)
            self.success(rgetcwd())
        except Exception as e:
            self.error(
                ' '.join(x for x in e.args if isinstance(x, str))
            )
