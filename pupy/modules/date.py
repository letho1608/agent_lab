# -*- coding: utf-8 -*-

import sys
from pupy.pupylib.PupyModule import config, PupyArgumentParser, PupyModule

__class_name__ = 'date'


@config(cat="admin")
class date(PupyModule):
    """ Get current date """
    is_module=False

    dependencies = ['pupyutils.basic_cmds']

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog="date", description=cls.__doc__)

    def run(self, args):
        try:
            date = self.client.remote('pupyutils.basic_cmds', 'now', False)
            self.success(date())

        except Exception as e:
            self.error(
                ' '.join(x for x in e.args if isinstance(x, str))
            )
