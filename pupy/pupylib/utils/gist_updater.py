# -*- coding: utf-8 -*-
"""
Gist updater: server tự kiểm tra IPv6, so sánh với last_published, PATCH Gist khi thay đổi.
GIST_RAW_URL, GIST_TOKEN lấy từ .env (hoặc os.environ).
"""

import json
import os
import re
import threading
import time

from pupy.pupylib.utils.dotenv import load_dotenv

load_dotenv()

try:
    import requests
except ImportError:
    requests = None

from pupy.pupylib import getLogger
logger = getLogger('gist_updater')

# Parse gist_id và filename từ GIST_RAW_URL
# https://gist.githubusercontent.com/USER/GIST_ID/raw/REV/filename
GIST_RAW_URL_PATTERN = re.compile(
    r'https?://gist\.githubusercontent\.com/[^/]+/([a-f0-9]+)/raw/[^/]+/([^/?]+)'
)


def get_current_ipv6():
    """Lấy IPv6 outbound hiện tại (api64.ipify.org hoặc fallback)."""
    if requests:
        try:
            r = requests.get('https://api64.ipify.org', timeout=10)
            if r.status_code == 200 and r.text.strip():
                return r.text.strip()
        except Exception as e:
            logger.debug('api64.ipify.org failed: %s', e)
    try:
        from pupy.network.lib.online import external_ip
        ip = external_ip(force_ipv4=False)
        if ip and getattr(ip, 'version', 4) == 6:
            return str(ip)
    except Exception as e:
        logger.debug('external_ip(ipv6) failed: %s', e)
    return None


def parse_gist_id_from_raw_url(raw_url):
    """Từ GIST_RAW_URL trả về (gist_id, filename)."""
    if not raw_url:
        return None, None
    m = GIST_RAW_URL_PATTERN.match(raw_url.strip())
    if m:
        return m.group(1), m.group(2)
    return None, None


def publish_to_gist(gist_id, filename, content, token):
    """PATCH nội dung file trong Gist. content = str ([IPv6]:port hoặc JSON)."""
    if not requests or not gist_id or not filename or not token:
        return False
    url = 'https://api.github.com/gists/{}'.format(gist_id)
    headers = {
        'Authorization': 'token {}'.format(token.strip()),
        'Accept': 'application/vnd.github.v3+json',
    }
    payload = {
        'files': {
            filename: {'content': content}
        }
    }
    try:
        r = requests.patch(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            logger.info('Gist updated: %s', content.strip())
            return True
        logger.warning('Gist PATCH failed: %s %s', r.status_code, r.text[:200])
    except Exception as e:
        logger.exception('Gist PATCH error: %s', e)
    return False


def format_c2_content(ipv6, port):
    """Định dạng nội dung Gist: [IPv6]:port."""
    if ':' in ipv6 and not ipv6.startswith('['):
        ipv6 = '[{}]'.format(ipv6)
    return '{}:{}\n'.format(ipv6, port)


def _gist_check_loop(pupsrv, interval_sec, raw_url, token):
    """Thread: định kỳ lấy IPv6+port, so sánh với last; nếu khác thì PATCH Gist."""
    gist_id, filename = parse_gist_id_from_raw_url(raw_url)
    if not gist_id or not filename or not token:
        logger.warning('Gist updater: missing gist_id/filename/token, skip thread')
        return
    last_published = None
    last_port = None
    while getattr(pupsrv, '_gist_updater_running', True):
        try:
            ipv6 = get_current_ipv6()
            listeners = pupsrv.get_listeners()
            port = None
            for lst in (listeners or {}).values():
                if lst and getattr(lst, 'external_port', None):
                    port = lst.external_port
                    break
                if lst and getattr(lst, 'port', None):
                    port = lst.port
                    break
            if not port and listeners:
                lst = next(iter(listeners.values()), None)
                if lst:
                    port = getattr(lst, 'external_port', None) or getattr(lst, 'port', 443)
            if not port:
                port = 443
            if ipv6 and port is not None:
                current = (ipv6, port)
                if last_published != current:
                    content = format_c2_content(ipv6, port)
                    if publish_to_gist(gist_id, filename, content, token):
                        last_published = current
                        last_port = port
        except Exception as e:
            logger.debug('Gist check loop: %s', e)
        time.sleep(interval_sec)


def start_gist_updater(pupsrv, interval_sec=300, raw_url=None, token=None):
    """
    Khởi chạy thread cập nhật Gist khi IPv6/port thay đổi.
    raw_url, token lấy từ os.environ (GIST_RAW_URL, GIST_TOKEN) nếu không truyền.
    """
    raw_url = raw_url or os.environ.get('GIST_RAW_URL', '').strip()
    token = token or os.environ.get('GIST_TOKEN', '').strip()
    if not raw_url or not token:
        logger.debug('Gist updater: GIST_RAW_URL or GIST_TOKEN empty, skip')
        return None
    if not requests:
        logger.warning('Gist updater: requests not available')
        return None
    pupsrv._gist_updater_running = True
    t = threading.Thread(
        target=_gist_check_loop,
        args=(pupsrv, max(60, int(interval_sec)), raw_url, token),
        name='GistUpdater'
    )
    t.daemon = True
    t.start()
    logger.info('Gist updater started (interval=%ss)', interval_sec)
    return t
