def classFactory(iface):
    from .cadmus_plugin  import CadmusPlugin
    return CadmusPlugin(iface)
