# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QObject, pyqtSignal
from ...utils.ToolKeys import ToolKey
from .LogUtils import LogUtils


class _PluginSignalHub(QObject):
    """Barramento global de sinais PyQt usados pelo plugin."""

    plugin_instantiated = pyqtSignal(dict)
    plugin_finished = pyqtSignal(dict)
    toolbar_category_visibility_changed = pyqtSignal(dict)


_plugin_signal_hub = None


def get_plugin_signal_hub():
    """Retorna singleton do barramento global de sinais."""
    global _plugin_signal_hub
    if _plugin_signal_hub is None:
        _plugin_signal_hub = _PluginSignalHub()
    return _plugin_signal_hub


class PyQtSignalManager(QObject):
    """Escuta sinais globais do plugin e registra eventos relevantes no log."""

    def create_menu_manager(self, iface, tools, logger):
        """Cria e retorna uma instância de MenuManager, menus e toolbar."""
        from .MenuManager import MenuManager

        menu_manager = MenuManager(iface, tools, logger)
        menu_manager.create_menu()
        logger.debug("Criando toolbar para o plugin via PyQtSignalManager")
        menu_manager.create_toolbar()
        menu_manager.populate_menus()
        logger.info(
            f"MenuManager criado e menus/toolbars populados via PyQtSignalManager: {menu_manager}."
        )
        return menu_manager

    def __init__(self, tool_key=ToolKey.UNTRACEABLE, parent=None):
        super().__init__(parent)
        self.tool_key = tool_key or ToolKey.UNTRACEABLE
        self.logger = LogUtils(
            tool=self.tool_key,
            class_name="PyQtSignalManager",
            level=LogUtils.DEBUG,
        )
        self._signal_hub = get_plugin_signal_hub()
        self._is_connected = False

    def start(self):
        """Conecta handlers aos sinais globais."""
        if self._is_connected:
            self.logger.debug("[start] PyQtSignalManager jÃ¡ conectado")
            return

        self._signal_hub.plugin_instantiated.connect(self._on_plugin_instantiated)
        self._signal_hub.plugin_finished.connect(self._on_plugin_finished)
        self._signal_hub.toolbar_category_visibility_changed.connect(
            self._on_toolbar_category_visibility_changed
        )
        self._is_connected = True
        self.logger.info("[start] PyQtSignalManager conectado ao hub de sinais")

    def stop(self):
        """Desconecta handlers dos sinais globais."""
        if not self._is_connected:
            return

        try:
            self._signal_hub.plugin_instantiated.disconnect(
                self._on_plugin_instantiated
            )
            self._signal_hub.plugin_finished.disconnect(self._on_plugin_finished)
            self._signal_hub.toolbar_category_visibility_changed.disconnect(
                self._on_toolbar_category_visibility_changed
            )
            self.logger.info("[stop] PyQtSignalManager desconectado do hub de sinais")
        except Exception as e:
            self.logger.error(
                f"[stop] Erro ao desconectar PyQtSignalManager do hub: {e}"
            )
        finally:
            self._is_connected = False

    def _on_plugin_instantiated(self, payload):
        """
        Executado quando um plugin é instanciado (aberto).
        Coordena atualização de main_action e reconstrução de toolbar.
        """
        try:
            event_tool_key = payload.get("tool_key", ToolKey.UNTRACEABLE)

            # Delegar para ToolRegistry (gerencia ToolList + Preferences)
            from .ToolRegistry import ToolRegistry

            tool_registry = ToolRegistry.get_instance()
            if tool_registry is None:
                self.logger.error(
                    "[_on_plugin_instantiated] ToolRegistry não inicializado!"
                )
                return

            category = tool_registry.update_tool_main_action(event_tool_key)
            if category is None:
                return

            # Disparar sinal de alteração de visibilidade da toolbar se houver um plugin ativo
            self._signal_hub.toolbar_category_visibility_changed.emit({})
            self.logger.info(
                f"[_on_plugin_instantiated] Plugin iniciado: {event_tool_key}"
            )

        except Exception as e:
            self.logger.error(f"[_on_plugin_instantiated] Erro: {e}", exc_info=True)

    def _on_toolbar_category_visibility_changed(self, payload):
        """Manipula alterações na visibilidade das categorias da toolbar."""
        try:
            from .MenuManager import MenuManager

            menu_manager = MenuManager.get_instance()
            if menu_manager is not None:
                menu_manager.reconstruct_toolbar()
                self.logger.info(
                    "[_on_toolbar_category_visibility_changed] Toolbar reconstruída"
                )
            else:
                self.logger.warning(
                    "[_on_toolbar_category_visibility_changed] MenuManager não disponível"
                )
        except Exception as e:
            self.logger.error(
                f"[_on_toolbar_category_visibility_changed] Erro ao reconstruir toolbar: {e}",
                exc_info=True,
            )

    def _on_plugin_finished(self, payload):
        """
        Executado quando um plugin é finalizado (fechado).
        Atualiza main_action apenas (sem reconstruir toolbar).
        """
        try:
            tool_key = payload.get("tool_key", ToolKey.UNTRACEABLE)

            # Delegar para ToolRegistry
            from .ToolRegistry import ToolRegistry

            tool_registry = ToolRegistry.get_instance()
            if tool_registry is None:
                self.logger.error(
                    "[_on_plugin_finished] ToolRegistry não inicializado!"
                )
                return

            category = tool_registry.update_tool_main_action(tool_key)
            if category is not None:
                self.logger.debug(f"[_on_plugin_finished] Plugin '{tool_key}' fechado")

        except Exception as e:
            self.logger.error(f"[_on_plugin_finished] Erro: {e}", exc_info=True)
