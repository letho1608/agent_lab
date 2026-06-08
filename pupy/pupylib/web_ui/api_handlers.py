# -*- coding: utf-8 -*-
"""API handlers cho Web UI: sessions, listeners, run module, jobs."""

import json
import os
import time
import traceback
from argparse import Namespace

from pupy.pupylib.PupyWeb import RequestHandler
from pupy.pupylib.PupyCmd import ObjectStream, IOGroup
from pupy.pupylib.utils.term import as_term_bytes
from pupy.pupylib.web_ui.module_docs_vi import MODULE_DOCS_VI
from pupy.pupylib.web_ui.command_docs_vi import COMMAND_DESCS_VI


def _serialize_client(c):
    """Chuyển PupyClient thành dict JSON-safe (bỏ conn, bytes -> str)."""
    d = getattr(c, 'desc', c)
    if not hasattr(d, 'items'):
        return {'id': getattr(c, 'id', str(c)), 'user': '', 'hostname': str(c)}
    out = {}
    for k, v in d.items():
        if k == 'conn' or callable(v):
            continue
        if isinstance(v, bytes):
            v = v.decode('utf-8', errors='replace')
        out[k] = v
    return out


class WebUIHandler(RequestHandler):
    """Base: lấy pupsrv từ application."""
    def get_pupsrv(self):
        return getattr(self.application, 'pupsrv', None)


def _safe_json(self, data):
    self.set_header('Content-Type', 'application/json; charset=utf-8')
    self.finish(json.dumps(data, ensure_ascii=False))


class ApiSessionsHandler(WebUIHandler):
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            lock = pupsrv.clients_lock
            if not lock.acquire(timeout=2):
                self.set_status(503)
                _safe_json(self, {'error': 'Server busy', 'sessions': []})
                return
            try:
                clients = []
                for c in pupsrv.clients:
                    d = _serialize_client(c)
                    try:
                        d['tags'] = ', '.join(pupsrv.config.tags(c.node()).get()) if hasattr(c, 'node') else ''
                    except Exception:
                        d['tags'] = ''
                    clients.append(d)
            finally:
                lock.release()
            _safe_json(self, {'sessions': clients})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'sessions': []})


class ApiListenersHandler(WebUIHandler):
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available', 'listeners': []})
            return
        try:
            listeners = []
            for name, lst in (pupsrv.listeners or {}).items():
                if lst and hasattr(lst, 'port'):
                    listeners.append({
                        'name': name,
                        'port': getattr(lst, 'port', None),
                        'address': getattr(lst, 'address', ''),
                    })
            _safe_json(self, {'listeners': listeners})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'listeners': []})


class ApiModulesHandler(WebUIHandler):
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available', 'modules': []})
            return
        try:
            modules = []
            for mod in pupsrv.iter_modules():
                name = mod.get_name()
                doc_key = name.split('.')[-1] if '.' in name else name
                doc = MODULE_DOCS_VI.get(doc_key) or (mod.__doc__ or '').strip()[:200]
                modules.append({
                    'name': name,
                    'doc': doc,
                    'category': getattr(mod, 'category', 'general'),
                })
            if not modules and getattr(pupsrv, 'modules', None):
                from inspect import isclass
                from pupy.pupylib.PupyModule import PupyModule
                for _name, modobj in pupsrv.modules.items():
                    for item_name in dir(modobj):
                        item = getattr(modobj, item_name)
                        if isclass(item) and issubclass(item, PupyModule) and item != PupyModule:
                            name = item.get_name()
                            doc_key = name.split('.')[-1] if '.' in name else name
                            doc = MODULE_DOCS_VI.get(doc_key) or (item.__doc__ or '').strip()[:200]
                            modules.append({
                                'name': name,
                                'doc': doc,
                                'category': getattr(item, 'category', 'general'),
                            })
                            break
            _safe_json(self, {'modules': modules})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'modules': []})


class ApiRunHandler(WebUIHandler):
    def post(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            self.finish(json.dumps({'error': 'Server not available'}))
            return
        try:
            body = json.loads(self.request.body or b'{}')
        except Exception as e:
            self.set_status(400)
            self.finish(json.dumps({'error': str(e)}))
            return
        session_id = body.get('session_id')
        module_name = body.get('module', '').strip()
        args_list = body.get('args', [])
        if isinstance(args_list, str):
            args_list = args_list.split() if args_list else []
        if not module_name:
            self.set_status(400)
            self.finish(json.dumps({'error': 'module required'}))
            return
        clients_filter = str(session_id) if session_id is not None else None
        if not clients_filter and not pupsrv.clients:
            self.set_status(400)
            self.finish(json.dumps({'error': 'No clients connected'}))
            return

        out_buffer = []
        display_buffer = []
        import threading
        lock = threading.Lock()

        def web_display(text, nocrlf=False, to_bytes=False):
            try:
                raw = as_term_bytes(text)
                if isinstance(raw, bytes):
                    raw = raw.decode('utf-8', errors='replace')
                with lock:
                    display_buffer.append(raw + ('' if nocrlf else '\n'))
            except Exception:
                with lock:
                    display_buffer.append(str(text) + '\n')

        def web_acquire_io(requirements, amount, background=False, pipe=None):
            return [IOGroup(None, ObjectStream(stream=True)) for _ in range(amount)]

        def web_process(job, background=False, daemon=False, unique=False):
            if background or daemon:
                return
            try:
                job.worker_pool.join(timeout=300)
            except Exception:
                pass
            for inst in getattr(job, 'pupymodules', []):
                stdout = getattr(inst, 'stdout', None)
                if stdout and hasattr(stdout, 'getvalue'):
                    for block in stdout.getvalue():
                        if isinstance(block, bytes):
                            out_buffer.append(block.decode('utf-8', errors='replace'))
                        else:
                            out_buffer.append(str(block))

        class WebHandler:
            default_filter = clients_filter
            display_lock = lock

            def display(self, text, nocrlf=False, to_bytes=False):
                web_display(text, nocrlf)

            def acquire_io(self, req, amount, bg=False, pipe=None):
                return web_acquire_io(req, amount, bg, pipe)

            def process(self, job, background=False, daemon=False, unique=False):
                web_process(job, background, daemon, unique)

        web_handler = WebHandler()
        background = bool(body.get('background', False))
        modargs = Namespace(
            module=module_name,
            arguments=args_list,
            filter=clients_filter,
            background=background,
            output=None,
            pipe=None,
            once=False,
        )
        try:
            from pupy.commands.run import do as run_do
            run_do(pupsrv, web_handler, pupsrv.config, modargs)
        except Exception as e:
            display_buffer.append(traceback.format_exc())
            self.set_header('Content-Type', 'application/json; charset=utf-8')
            self.finish(json.dumps({
                'ok': False,
                'error': str(e),
                'display': ''.join(display_buffer),
                'output': ''.join(out_buffer),
            }, ensure_ascii=False))
            return
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.finish(json.dumps({
            'ok': True,
            'display': ''.join(display_buffer),
            'output': ''.join(out_buffer),
        }, ensure_ascii=False))


class ApiJobsHandler(WebUIHandler):
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available', 'jobs': []})
            return
        try:
            jobs = []
            for jid, job in getattr(pupsrv, 'jobs', {}).items():
                jobs.append({
                    'id': jid,
                    'name': getattr(job, 'name', ''),
                    'clients': [getattr(c, 'id', str(c)) for c in getattr(job, 'clients', [])],
                    'status': 'finished' if job.is_finished() else 'running',
                })
            _safe_json(self, {'jobs': jobs})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'jobs': []})


class ApiConfigHandler(WebUIHandler):
    def get(self):
        try:
            base = getattr(self.application, 'web_ui_base', '')
            _safe_json(self, {'base': base})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'base': '', 'error': str(e)})


class ApiPingHandler(WebUIHandler):
    """Trả về ngay, không dùng lock — để kiểm tra kết nối."""
    def get(self):
        _safe_json(self, {'ok': True})


class ApiServerInfoHandler(WebUIHandler):
    """Thông tin server: version, số sessions, listeners."""
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            import sys
            from pupy.pupylib.PupyVersion import BANNER, UPSTREAM

            _safe_json(self, {
                'version': UPSTREAM or 'Pupy',
                'python_version': getattr(sys, 'version', '')[:60],
                'sessions': len(getattr(pupsrv, 'clients', [])),
                'listeners': len(getattr(pupsrv, 'listeners', {}) or {}),
                'jobs': len(getattr(pupsrv, 'jobs', {}) or {}),
                'ts': int(time.time() * 1000),
            })
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e)})


class ApiSessionKillHandler(WebUIHandler):
    """Kill session: gửi exit tới client."""
    def post(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            body = json.loads(self.request.body or b'{}')
            sid = body.get('session_id')
            if sid is None:
                self.set_status(400)
                _safe_json(self, {'error': 'session_id required'})
                return
            clients = pupsrv.get_clients(int(sid))
            if not clients:
                self.set_status(404)
                _safe_json(self, {'error': 'Session not found'})
                return
            try:
                clients[0].conn.exit()
                _safe_json(self, {'ok': True})
            except Exception as e:
                _safe_json(self, {'ok': False, 'error': str(e)})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e)})


class ApiSessionDropHandler(WebUIHandler):
    """Drop session: đóng socket ngay."""
    def post(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            body = json.loads(self.request.body or b'{}')
            sid = body.get('session_id')
            if sid is None:
                self.set_status(400)
                _safe_json(self, {'error': 'session_id required'})
                return
            clients = pupsrv.get_clients(int(sid))
            if not clients:
                self.set_status(404)
                _safe_json(self, {'error': 'Session not found'})
                return
            try:
                clients[0].conn._conn.close()
                _safe_json(self, {'ok': True})
            except Exception as e:
                _safe_json(self, {'ok': False, 'error': str(e)})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e)})


class ApiJobKillHandler(WebUIHandler):
    """Kill/dừng job."""
    def post(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            body = json.loads(self.request.body or b'{}')
            jid = body.get('job_id')
            if jid is None:
                self.set_status(400)
                _safe_json(self, {'error': 'job_id required'})
                return
            jid = int(jid)
            job = pupsrv.get_job(jid)
            if job.is_finished():
                pupsrv.del_job(jid)
                _safe_json(self, {'ok': True, 'message': 'Job closed'})
            else:
                job.interrupt()
                job.stop()
                pupsrv.del_job(jid)
                _safe_json(self, {'ok': True, 'message': 'Job killed'})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e)})


class ApiConfigListHandler(WebUIHandler):
    """Trả về config dạng { section: { key: value } } (chỉ đọc)."""
    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available'})
            return
        try:
            config = pupsrv.config
            out = {}
            for section in config.sections():
                if section == 'randoms':
                    out[section] = dict(getattr(config, 'randoms', {}))
                else:
                    try:
                        out[section] = dict(config.items(section))
                    except Exception:
                        out[section] = {}
            _safe_json(self, {'config': out})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e)})


class ApiCommandsHandler(WebUIHandler):
    """Danh sách lệnh server (commands) + mô tả tiếng Việt."""
    def get(self):
        try:
            from pupy.commands import Commands
            c = Commands()
            out = []
            for name, desc in c.list():
                description = COMMAND_DESCS_VI.get(name) or (desc or '')[:200]
                out.append({'name': name, 'description': description})
            _safe_json(self, {'commands': out})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'commands': []})


class ApiLootKindsHandler(WebUIHandler):
    """Liệt kê các loại loot (file *.jsonl trong thư mục loot)."""

    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available', 'kinds': []})
            return

        try:
            config = pupsrv.config
            try:
                loot_dir = config.get_folder('loot', create=False)
            except Exception:
                _safe_json(self, {'error': 'Loot folder not available', 'kinds': []})
                return

            if not loot_dir or not os.path.isdir(loot_dir):
                _safe_json(self, {'error': 'Loot folder not available', 'kinds': []})
                return

            kinds = []
            for name in os.listdir(loot_dir):
                if not name.endswith('.jsonl'):
                    continue
                kind = name[:-6]
                if kind and kind not in kinds:
                    kinds.append(kind)

            kinds.sort()
            _safe_json(self, {'kinds': kinds})
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'kinds': []})


class ApiLootHandler(WebUIHandler):
    """Truy vấn loot dạng JSON (dùng cùng logic với lệnh loot)."""

    def get(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            _safe_json(self, {'error': 'Server not available', 'records': []})
            return

        kind = (self.get_argument('kind', 'get_info') or 'get_info').strip()
        campaign = (self.get_argument('campaign', '') or '').strip()
        text_filter = (self.get_argument('filter', '') or '').strip()
        try:
            limit = int(self.get_argument('limit', '50') or '50')
        except Exception:
            limit = 50

        limit = max(1, min(limit, 1000))

        try:
            config = pupsrv.config
            try:
                loot_dir = config.get_folder('loot', create=False)
            except Exception:
                _safe_json(self, {
                    'error': 'Loot folder not available',
                    'records': [],
                })
                return

            path = os.path.join(loot_dir, '{}.jsonl'.format(kind))
            if not os.path.isfile(path):
                _safe_json(self, {
                    'error': 'No loot file for kind: {}'.format(kind),
                    'records': [],
                })
                return

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                _safe_json(self, {
                    'error': 'Failed to read loot file: {}'.format(e),
                    'records': [],
                })
                return

            lines = lines[-limit:]
            records = []
            needle = (text_filter or '').lower()

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue

                if campaign:
                    camp = (row.get('campaign') or '') or ''
                    if campaign not in str(camp):
                        continue

                if needle:
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

                record = {
                    'kind': kind,
                    'ts': ts,
                    'ts_str': ts_str,
                    'campaign': row.get('campaign') or '',
                    'host': row.get('host') or '',
                    'user': row.get('user') or '',
                    'platform': row.get('platform') or '',
                    'data': row.get('data', None),
                }
                records.append(record)

            _safe_json(self, {
                'error': None,
                'records': records,
            })
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'records': []})


class ApiPlaybookListHandler(WebUIHandler):
    """Liệt kê các playbook có sẵn."""

    def get(self):
        try:
            from pupy.commands.playbook import PLAYBOOKS
        except Exception as e:
            self.set_status(500)
            _safe_json(self, {'error': str(e), 'playbooks': []})
            return

        items = []
        for name, steps in sorted(PLAYBOOKS.items()):
            items.append({
                'name': name,
                'modules': [m for (m, _) in steps],
            })

        _safe_json(self, {'playbooks': items})


class ApiPlaybookRunHandler(WebUIHandler):
    """Chạy playbook (giống lệnh playbook)."""

    def post(self):
        pupsrv = self.get_pupsrv()
        if not pupsrv:
            self.set_status(500)
            self.finish(json.dumps({'ok': False, 'error': 'Server not available'}))
            return

        try:
            body = json.loads(self.request.body or b'{}')
        except Exception as e:
            self.set_status(400)
            self.finish(json.dumps({'ok': False, 'error': str(e)}))
            return

        playbook_name = (body.get('playbook') or '').strip()
        clients_filter = (body.get('filter') or '').strip() or None
        background = bool(body.get('background', False))
        extra_args = body.get('arguments') or []
        if isinstance(extra_args, str):
            extra_args = extra_args.split() if extra_args else []

        if not playbook_name:
            self.set_status(400)
            self.finish(json.dumps({'ok': False, 'error': 'playbook required'}))
            return

        # Nếu chưa chọn filter mà đã có session chọn sẵn ở UI, frontend sẽ gửi filter=tên mã phiên
        if clients_filter and clients_filter.isdigit():
            clients_filter = str(int(clients_filter))

        out_buffer = []
        display_buffer = []
        import threading
        lock = threading.Lock()

        def web_display(text, nocrlf=False, to_bytes=False):
            try:
                raw = as_term_bytes(text)
                if isinstance(raw, bytes):
                    raw = raw.decode('utf-8', errors='replace')
                with lock:
                    display_buffer.append(raw + ('' if nocrlf else '\n'))
            except Exception:
                with lock:
                    display_buffer.append(str(text) + '\n')

        def web_acquire_io(requirements, amount, background=False, pipe=None):
            return [IOGroup(None, ObjectStream(stream=True)) for _ in range(amount)]

        def web_process(job, background=False, daemon=False, unique=False):
            if background or daemon:
                return
            try:
                job.worker_pool.join(timeout=300)
            except Exception:
                pass

        class WebHandler:
            default_filter = clients_filter
            display_lock = lock

            def display(self, text, nocrlf=False, to_bytes=False):
                web_display(text, nocrlf)

            def acquire_io(self, req, amount, bg=False, pipe=None):
                return web_acquire_io(req, amount, bg, pipe)

            def process(self, job, background=False, daemon=False, unique=False):
                web_process(job, background, daemon, unique)

        web_handler = WebHandler()

        modargs = Namespace(
            playbook=playbook_name,
            filter=clients_filter,
            background=background,
            list=False,
            arguments=extra_args,
        )

        try:
            from pupy.commands.playbook import do as playbook_do
            playbook_do(pupsrv, web_handler, pupsrv.config, modargs)
            self.set_header('Content-Type', 'application/json; charset=utf-8')
            self.finish(json.dumps({
                'ok': True,
                'display': ''.join(display_buffer),
            }, ensure_ascii=False))
        except Exception as e:
            display_buffer.append(traceback.format_exc())
            self.set_header('Content-Type', 'application/json; charset=utf-8')
            self.finish(json.dumps({
                'ok': False,
                'error': str(e),
                'display': ''.join(display_buffer),
            }, ensure_ascii=False))
