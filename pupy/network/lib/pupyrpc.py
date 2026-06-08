# -*- coding: utf-8 -*-
# Glue for backward compatibility


__all__ = ('nowait', 'brine')

import sys

if 'rpyc' in sys.modules:
    import rpyc

    nowait = getattr(rpyc, 'async')
    brine = rpyc.core.brine
    netref = rpyc.core.netref

else:
    from pupy.network.lib.rpc import nowait
    from pupy.network.lib.rpc.core import brine
