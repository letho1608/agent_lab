# -*- coding: utf-8 -*-


from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser

import subprocess

__class_name__="PupyMod"

@config(compat=["windows"], cat="manage", tags=["lock", "screen", "session"])
class PupyMod(PupyModule):
    """ Lock the session """

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog="lock_screen", description=cls.__doc__)

    def run(self, args):
        ok = self.client.conn.modules['ctypes'].windll.user32.LockWorkStation()
        if ok:
            self.success("windows locked")
        else:
            self.error("couldn't lock the screen")
