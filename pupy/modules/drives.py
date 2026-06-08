# -*- coding: utf-8 -*-


from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupy.pupylib.PupyOutput import Table, MultiPart
from pupy.modules.lib import size_human_readable

__class_name__="Drives"

@config(category='admin', compatibilities=['windows'])
class Drives(PupyModule):
    """ List valid drives in the system """

    dependencies={
        'all': ['psutil'],
        'windows': [
            'pupyps', 'netresources',
        ],
    }

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(
            prog="drives",
            description=cls.__doc__
        )

    def run(self, args):
        list_drives = self.client.remote('pupyps', 'drives')
        EnumNetResources = self.client.remote('netresources', 'EnumNetResources')
        drives = list_drives()

        formatted_drives = []
        parts = []

        for drive in drives:
            formatted_drives.append({
                'MP': drive['mountpoint'],
                'FS': drive['fstype'],
                'OPTS': drive['opts'],
                'USED': (
                    '{}% ({}/{})'.format(
                        drive['percent'],
                        size_human_readable(drive['used']),
                        size_human_readable(drive['total'])
                    ) if ('used' in drive and 'total' in drive) else '?'
                )
            })

        parts.append(Table(formatted_drives, ['MP', 'FS', 'OPTS', 'USED']))

        providers = {}

        net_resources = EnumNetResources()
        for resource in net_resources:
            if resource['provider'] not in providers:
                providers[resource['provider']] = []

            if 'used' in resource:
                resource['used'] = '{}% ({}/{})'.format(
                    resource['percent'],
                    size_human_readable(resource['used']),
                    size_human_readable(resource['total'])
                )
            else:
                resource['used'] = '?'

            providers[resource['provider']].append(dict(
                (k, v) for k, v in resource.items() if k not in (
                    'usage', 'provider', 'scope'
                )
            ))

        for provider, records in providers.items():
            parts.append(
                Table(records, [
                    'remote', 'local', 'type', 'used'
                ], caption=provider))

        self.log(MultiPart(parts))
