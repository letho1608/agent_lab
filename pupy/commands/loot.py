# -*- encoding: utf-8 -*-


"""
loot: xem nhanh loot đã lưu (JSONL) từ các module như get_info.
"""

import os
import json
import time

from pupy.pupylib.PupyModule import PupyArgumentParser
from pupy.pupylib.PupyOutput import Error, Success, Table


usage = 'Query loot stored on the server (JSONL under loot/ folder)'
parser = PupyArgumentParser(prog='loot', description=usage)

parser.add_argument(
    '-k', '--kind', default='get_info',
    help='Loại loot (tên file .jsonl), mặc định: get_info'
)
parser.add_argument(
    '-c', '--campaign', metavar='<campaign>',
    help='Lọc theo campaign (substring)'
)
parser.add_argument(
    '-f', '--filter', metavar='<text>',
    help='Lọc theo chuỗi xuất hiện trong host/user/platform/data'
)
parser.add_argument(
    '-n', '--limit', type=int, default=50,
    help='Số bản ghi mới nhất cần hiển thị (mặc định 50)'
)


def do(server, handler, config, modargs):
    try:
        loot_dir = config.get_folder('loot', create=False)
    except Exception:
        handler.display(Error('Loot folder not available'))
        return

    path = os.path.join(loot_dir, '{}.jsonl'.format(modargs.kind))
    if not os.path.isfile(path):
        handler.display(Error('No loot file for kind: {}'.format(modargs.kind)))
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        handler.display(Error('Failed to read loot file: {}'.format(e)))
        return

    lines = lines[-max(1, modargs.limit):]

    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue

        if modargs.campaign:
            camp = (row.get('campaign') or '') or ''
            if modargs.campaign not in str(camp):
                continue

        if modargs.filter:
            needle = modargs.filter.lower()
            haystack = ' '.join([
                str(row.get('host') or ''),
                str(row.get('user') or ''),
                str(row.get('platform') or ''),
                json.dumps(row.get('data', ''), ensure_ascii=False),
            ]).lower()
            if needle not in haystack:
                continue

        ts = row.get('ts') or 0
        try:
            ts_str = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(float(ts))
            )
        except Exception:
            ts_str = str(ts)

        records.append({
            'TIME': ts_str,
            'CAMPAIGN': row.get('campaign') or '',
            'HOST': row.get('host') or '',
            'USER': row.get('user') or '',
            'PLATFORM': row.get('platform') or '',
            'SUMMARY': json.dumps(row.get('data', ''), ensure_ascii=False)[:200],
        })

    if not records:
        handler.display(Success('No loot records match criteria'))
        return

    handler.display(Table(records, ['TIME', 'CAMPAIGN', 'HOST', 'USER', 'PLATFORM', 'SUMMARY']))
