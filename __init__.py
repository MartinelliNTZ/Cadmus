# -*- coding: utf-8 -*-
def classFactory(iface):
    from .cadmus_plugin import CadmusPlugin

    return CadmusPlugin(iface)
