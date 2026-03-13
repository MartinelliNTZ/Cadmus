# -*- coding: utf-8 -*-
from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.MrkParseTask import MrkParseTask
from ..config.LogUtils import LogUtils
from ...utils.vector.VectorLayerGeometry import VectorLayerGeometry
from qgis.core import QgsProject


class MrkParseStep(BaseStep):
    """Step responsável por ler MRKs e criar camada de pontos inicial."""

    def name(self) -> str:
        return "MrkParseStep"

    def create_task(self, context: ExecutionContext):
        context.require(["paths", "recursive", "tool_key"])

        return MrkParseTask(
            paths=context.get("paths"),
            recursive=context.get("recursive", True),
            merge=context.get("merge", True),
            extra_fields=context.get("extra_fields"),
            tool_key=context.get("tool_key"),
        )

    def on_success(self, context: ExecutionContext, result):
        points = result.get("points", []) if isinstance(result, dict) else []
        if not points:
            LogUtils(
                tool=context.get("tool_key"),
                class_name=self.__class__.__name__,
            ).warning("Nenhum ponto encontrado após leitura de MRKs")
            return

        layer_name = context.get("points_layer_name", "MRK_Pontos")
        layer = VectorLayerGeometry.create_point_layer_from_dicts(
            points=points,
            name=layer_name,
            extra_fields=context.get("extra_fields"),
        )

        if layer and layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            context.set("layer", layer)
            context.set("points", points)
            context.set("base_folder", result.get("base_folder"))
        else:
            LogUtils(
                tool=context.get("tool_key"),
                class_name=self.__class__.__name__,
            ).error("Falha ao criar camada de pontos a partir dos MRKs")
