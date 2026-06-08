# -*- coding: utf-8 -*-
"""Đăng ký Web UI với PupyWebServer. Đường dẫn cố định /webui."""

from pupy.pupylib.web_ui.api_handlers import (
    ApiSessionsHandler,
    ApiListenersHandler,
    ApiModulesHandler,
    ApiRunHandler,
    ApiJobsHandler,
    ApiConfigHandler,
    ApiPingHandler,
    ApiServerInfoHandler,
    ApiSessionKillHandler,
    ApiSessionDropHandler,
    ApiJobKillHandler,
    ApiConfigListHandler,
    ApiCommandsHandler,
    ApiLootKindsHandler,
    ApiLootHandler,
    ApiPlaybookListHandler,
    ApiPlaybookRunHandler,
)
from pupy.pupylib.web_ui.web_ui_index import WebUIIndexHandler

WEBUI_BASE = '/webui'


def register_web_ui(pupweb):
    """Đăng ký routes Web UI tại /webui (cố định). Gọi sau khi start_webserver()."""
    if not pupweb or not getattr(pupweb, 'app', None):
        return None
    kwargs = {'config': pupweb.config}
    routes = [
        (r'/webui/api/ping', ApiPingHandler),
        (r'/webui/api/sessions', ApiSessionsHandler),
        (r'/webui/api/sessions/kill', ApiSessionKillHandler),
        (r'/webui/api/sessions/drop', ApiSessionDropHandler),
        (r'/webui/api/listeners', ApiListenersHandler),
        (r'/webui/api/modules', ApiModulesHandler),
        (r'/webui/api/run', ApiRunHandler),
        (r'/webui/api/jobs', ApiJobsHandler),
        (r'/webui/api/jobs/kill', ApiJobKillHandler),
        (r'/webui/api/config', ApiConfigHandler),
        (r'/webui/api/config/list', ApiConfigListHandler),
        (r'/webui/api/commands', ApiCommandsHandler),
        (r'/webui/api/serverinfo', ApiServerInfoHandler),
        (r'/webui/api/loot/kinds', ApiLootKindsHandler),
        (r'/webui/api/loot', ApiLootHandler),
        (r'/webui/api/playbooks', ApiPlaybookListHandler),
        (r'/webui/api/playbook/run', ApiPlaybookRunHandler),
        (r'/webui/?', WebUIIndexHandler),
    ]
    for path, handler in routes:
        pupweb.app.add_handlers(r'.*', [(path, handler, kwargs)])
    setattr(pupweb.app, 'web_ui_base', WEBUI_BASE)
    pupweb._registered = getattr(pupweb, '_registered', {})
    pupweb._registered['webui'] = (WEBUI_BASE, [h for _, h in routes], None)
    return pupweb.port, WEBUI_BASE
