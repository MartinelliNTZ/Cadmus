# -*- coding: utf-8 -*-

from .BaseStep import BaseStep
from ..config.LogUtils import LogUtils
from ..task.SaveVectorLayerTask import SaveVectorLayerTask
from qgis.core import QgsVectorLayer


class SaveVectorStep(BaseStep):

    def name(self) -> str:
        return "SaveVectorStep"

    def create_task(self, context):

        context.require(["current_path", "tool_key"])

        current_path = context.get("current_path")
        save_to_folder = context.get("save_to_folder", False)
        output_path = context.get("output_path")
        output_name = context.get("output_name")
        tool_key = context.get("tool_key")
        logger = LogUtils(tool=tool_key, class_name=self.__class__.__name__)

        layer = QgsVectorLayer(current_path, output_name, "ogr")

        if not layer.isValid():
            logger.error(
                f"SaveVectorStep: falha ao carregar camada de {current_path}. "
                f"Provider: {layer.providerType()}"
            )
            raise RuntimeError(
                "SaveVectorStep: falha ao carregar camada do current_path."
            )

        logger.debug(f"SaveVectorStep: salvando {output_name} para {output_path}")

        return SaveVectorLayerTask(
            layer=layer,
            output_path=output_path,
            save_to_folder=save_to_folder,
            output_name=output_name or layer.name(),
            decision="rename",
            tool_key=tool_key,
        )

    def on_success(self, context, result):
        logger = LogUtils(
            tool=context.get("tool_key"), class_name=self.__class__.__name__
        )

        if not result:
            logger.error("SaveVectorStep: falha ao salvar camada")

        logger.info("SaveVectorStep.on_success: camada salva com sucesso")
        context.set("layer", result)
