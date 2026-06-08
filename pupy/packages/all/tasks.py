# -*- coding: utf-8 -*-

# Wrapper around tasks module

import pupy.agent

def list():
    return pupy.agent.manager.status()
