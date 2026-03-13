# tools/vector_multipart_tool.py
# -*- coding: utf-8 -*-

import os
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsVectorLayer, QgsWkbTypes, QgsFeedback

from ..utils.vector.VectorLayerGeometry import VectorLayerGeometry
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ToolKeys import ToolKey
from .BasePlugin import BasePluginMTL

class VectorMultipartPlugin(BasePluginMTL):

    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        # Inicializar plugin sem UI
        self.init(
            tool_key=ToolKey.CONVERTER_MULTIPART,
            class_name="VectorMultipartPlugin",
            build_ui=False
        )

    def initGui(self):
        self.create_action(
            "../resources/icons/vector_multpart.ico",
            "Converter para Multipart",
            self.run_multpart
        )


    def unload(self):
        for a in self.actions:
            self.iface.removePluginMenu("Cadmus", a)

    # --------------------------------------------------
    # CONTROLLER
    # --------------------------------------------------
    def run_multpart(self):
        self.logger.info("Iniciando conversão de multipart para singlepart")
        
        layer = self.iface.activeLayer()

        if not layer or not isinstance(layer, QgsVectorLayer):
            self.logger.debug("Camada ativa inválida ou não é vetorial")
            QgisMessageUtil.bar_critical(
                self.iface,
                "Selecione uma camada vetorial"
            )
            return

        from ..utils.ProjectUtils import ProjectUtils
        from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
        layer = ProjectUtils.get_active_vector_layer(self.iface.activeLayer(), self.logger)
        if not layer:
            QgisMessageUtil.bar_critical(self.iface, "Selecione uma camada vetorial")
            self.logger.warning("Validação falhou: camada inválida")
            return
        if not VectorLayerAttributes.ensure_has_features(layer, self.logger):
            QgisMessageUtil.bar_warning(self.iface, "A camada não possui feições")
            self.logger.warning("Validação falhou: camada sem feições")
            return

        self.logger.debug(f"Camada validada: {layer.name()}, Total de feições: {layer.featureCount()}")
        already_editing = layer.isEditable()

        # 🔔 Confirmação
        if layer.selectedFeatureCount() > 0:
            msg = "Converter apenas as feições SELECIONADAS para multipart?"
            self.logger.debug(f"Feições selecionadas: {layer.selectedFeatureCount()}")
        else:
            msg = "Converter TODAS as feições para multipart?"
            self.logger.debug("Nenhuma feição selecionada - será convertida toda a camada")

        if not QgisMessageUtil.confirm(self.iface, msg):
            self.logger.debug("Usuário cancelou a operação")
            return

        # 🔓 Inicia edição se não estiver em edição
        if not already_editing:
            self.logger.debug("Camada não estava em edição - iniciando edição")
            layer.startEditing()

        feedback = QgsFeedback()
        
        only_selected = layer.selectedFeatureCount() > 0
        self.logger.info(f"Executando conversão para multipart - Apenas selecionadas: {only_selected}")
        
        ok = VectorLayerGeometry.singleparts_to_multparts(
            layer,
            feedback,
            only_selected=only_selected
        )

        if not ok:
            self.logger.warning("Operação cancelada ou falhou durante conversão")
            layer.rollBack()
            QgisMessageUtil.bar_warning(
                self.iface,
                "Operação cancelada pelo usuário"
            )
            return

        # 🔒 Se já estava em edição → NÃO salva
        if already_editing:
            self.logger.info("Geometrias convertidas para multipart (não salvas - camada já estava em edição)")
            QgisMessageUtil.bar_success(
                self.iface,
                "Geometrias convertidas para multipart (não salvas)"
            )
            return
