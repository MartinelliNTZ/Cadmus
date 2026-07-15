# -*- coding: utf-8 -*-

from qgis.core import QgsVectorLayer, QgsMapLayerProxyModel
from ..utils.ToolKeys import ToolKey
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..core.ui.WidgetFactory import WidgetFactory
from ..utils.Preferences import Preferences
from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
from .BasePlugin import BasePluginMTL
from ..i18n.TranslationManager import STR


class CopyAttributes(BasePluginMTL):
    TOOL_KEY = ToolKey.COPY_ATTRIBUTES

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(ToolKey.COPY_ATTRIBUTES, "CopyAttributes")

    # =========================
    # UI
    # =========================
    def _build_ui(self, **kwargs):
        super()._build_ui(
            title=STR.COPY_ATTRIBUTES_TITLE,
            icon_path="copy_attributes.ico",
            enable_scroll=True,
        )
        self.logger.info("Construindo interface da ferramenta")

        # CAMADA DESTINO
        tgt_layout, self.target_layer_input = WidgetFactory.create_layer_input(
            label_text=STR.TARGET_LAYER,
            filters=[QgsMapLayerProxyModel.Filter.VectorLayer],
            parent=self,
        )
        self.logger.debug("Componente de camada de target adicionado")

        # CAMADA ORIGEM
        src_layout, self.source_layer_input = WidgetFactory.create_layer_input(
            label_text=STR.SOURCE_LAYER,
            filters=[QgsMapLayerProxyModel.Filter.VectorLayer],
            parent=self,
        )
        self.source_layer_input.layerChanged.connect(self._populate_fields)
        self.logger.debug("Componente de camada de origem adicionado")

        # ATRIBUTOS
        attr_layout, self.attr_widget = WidgetFactory.create_attribute_selector(
            parent=self, title=STR.SOURCE_LAYER_ATTRIBUTES
        )

        # BOTÕES
        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
            )
        )

        self.layout.add_items([tgt_layout, src_layout, attr_layout, buttons_layout])

        self._populate_fields()

    def _populate_fields(self):
        layer = self.source_layer_input.current_layer()
        if not isinstance(layer, QgsVectorLayer):
            self.attr_widget.set_fields([])
            return

        self.attr_widget.set_fields([f.name() for f in layer.fields()])

    def _load_prefs(self):
        self.attr_widget.set_checked_all(
            self.preferences.get("chk_all", False)
        )

    def _save_prefs(self):
        self.preferences["chk_all"] = bool(self.attr_widget.use_all_fields())
        self.preferences["window_width"] = self.width()
        self.preferences["window_height"] = self.height()
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)

    # =========================
    # CONTROLLER
    # =========================
    def execute_tool(self):
        self.logger.info("Execução iniciada")

        source = self.source_layer_input.current_layer()
        target = self.target_layer_input.current_layer()

        if not isinstance(source, QgsVectorLayer):
            QgisMessageUtil.bar_warning(self.iface, STR.INVALID_SOURCE_LAYER)
            self.logger.warning("Camada de origem inválida")
            return

        if not isinstance(target, QgsVectorLayer):
            QgisMessageUtil.bar_warning(self.iface, STR.INVALID_TARGET_LAYER)
            self.logger.warning("Camada de destino inválida")
            return

        from ..utils.ProjectUtils import ProjectUtils

        if not ProjectUtils.ensure_editable(target, self.logger):
            QgisMessageUtil.bar_critical(self.iface, STR.LAYER_MUST_BE_EDITABLE)
            self.logger.warning("Camada de destino não editável")
            return

        fields = None
        if not self.attr_widget.use_all_fields():
            fields = self.attr_widget.get_selected_fields()

            if not fields:
                QgisMessageUtil.bar_warning(self.iface, STR.NO_ATTRIBUTE_SELECTED)
                self.logger.warning("Execução abortada: nenhum atributo selecionado")
                return

        def conflict_resolver(field_name):
            return QgisMessageUtil.ask_field_conflict(self.iface, field_name)

        ok = VectorLayerAttributes.copy_attributes(
            target_layer=target,
            source_layer=source,
            field_names=fields,
            conflict_resolver=conflict_resolver,
        )

        if ok:
            QgisMessageUtil.bar_success(self.iface, STR.ATTRIBUTES_COPIED_SUCCESS)
            self.logger.info("Cópia de atributos finalizada com sucesso")
        else:
            self.logger.error("Falha na cópia de atributos")


def run(iface):
    dlg = CopyAttributes(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
