# -*- coding: utf-8 -*-


from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser

__class_name__ = 'CheckVM'


@config(category="gather", compatibilities=['windows'])
class CheckVM(PupyModule):
    """ check if running on Virtual Machine """

    dependencies = ['checkvm']

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(
            prog='CheckVM', description=cls.__doc__
        )

    def run(self, args):
        check_vm = self.client.remote('checkvm')
        vms = check_vm.Check_VM().run()
        if vms:
            for vm in vms:
                self.success(vm)
        else:
            self.error('No Virtual Machine found')
