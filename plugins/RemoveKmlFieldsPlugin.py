# -*- coding: utf-8 -*-
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.StringManager import StringManager
from ..utils.ToolKeys import ToolKey
from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
from ..utils.vector.VectorLayerSource import VectorLayerSource
from .BasePlugin import BasePluginMTL


class RemoveKmlFieldsPlugin(BasePluginMTL):

    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.init(
            tool_key=ToolKey.REMOVE_KML_FIELDS,
            class_name="RemoveKmlFieldsPlugin",
            build_ui=False,
        )

    def initGui(self):
        self.create_action(
            im.icon_path(im.REMOVE_KML_FIELDS),
            STR.REMOVE_KML_FIELDS_TITLE,
            self.run_remove_kml_fields,
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu("Cadmus", action)

    def run_remove_kml_fields(self):
        self.logger.info("Iniciando remoção dos campos KML")

        layer = ProjectUtils.get_active_vector_layer(self.iface.activeLayer(), self.logger)
        if not layer:
            self.logger.warning("Nenhuma camada vetorial ativa válida")
            QgisMessageUtil.bar_critical(self.iface, STR.SELECT_VECTOR_LAYER)
            return

        source_path = (layer.source() or "").split("|", 1)[0]
        extension = VectorLayerSource.get_extension(
            source_path, tool_key=self.TOOL_KEY
        )

        if extension in (".kml", ".kmz"):
            self.logger.warning("Camada KML/KMZ não pode ser editada")
            QgisMessageUtil.bar_critical(
                self.iface,
                f"{STR.KML_FILES_ARE_NOT_EDITABLE}\n\n"
                f"{STR.CONVERT_LAYER_TO_GPKG_OR_SHP_BEFORE_USING}",
            )
            return

        if not ProjectUtils.ensure_editable(layer, self.logger):
            self.logger.warning("Camada não está em edição")
            QgisMessageUtil.bar_critical(self.iface, STR.SELECT_EDITABLE_VECTOR_LAYER)
            return

        try:
            removed_count = VectorLayerAttributes.delete_fields_by_names(
                layer, StringManager.KML_FIELDS, self.logger
            )
        except Exception as e:
            self.logger.error(f"Erro ao remover campos KML: {e}")
            QgisMessageUtil.bar_critical(
                self.iface, f"{STR.ERROR_REMOVING_KML_FIELDS} {str(e)}"
            )
            return

        if removed_count > 0:
            self.logger.info(f"Campos KML removidos com sucesso: {removed_count}")
            QgisMessageUtil.bar_success(
                self.iface, f"{STR.KML_FIELDS_REMOVED_SUCCESS} ({removed_count})"
            )
            return

        self.logger.info("Nenhum campo KML encontrado para remover")
        QgisMessageUtil.bar_warning(self.iface, STR.NO_KML_FIELDS_FOUND)


def run(iface):
    plugin = RemoveKmlFieldsPlugin(iface)
    plugin.run_remove_kml_fields()
