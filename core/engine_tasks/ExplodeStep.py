# -*- coding: utf-8 -*-
import os
import tempfile

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.ExplodeHugeLayerTask import ExplodeHugeLayerTask
from ..config.LogUtils import LogUtils
from ...utils.vector.VectorLayerSource import VectorLayerSource


class ExplodeStep(BaseStep):

    def name(self) -> str:
        return "explode"

    def create_task(self, context: ExecutionContext):

        context.require(["layer", "tool_key"])

        layer = context.get("layer")
        tool_key = context.get("tool_key")
        logger = LogUtils(tool=tool_key, class_name=self.__class__.__name__)

        tmp_dir = context.get("tmp_dir")
        if not tmp_dir:
            tmp_dir = tempfile.mkdtemp(prefix="pipeline_")
            context.set("tmp_dir", tmp_dir)

        input_path = os.path.join(tmp_dir, "input.gpkg")
        exploded_path = os.path.join(tmp_dir, "exploded.gpkg")

        input_path = VectorLayerSource.save_vector_layer(
            layer=layer,
            output_path=input_path,
            decision="overwrite",
            external_tool_key=tool_key,
        )

        if not input_path:
            logger.error(
                f"Falha ao exportar camada para explode. "
                f"Layer valid: {layer.isValid()}, "
                f"Provider: {layer.providerType()}"
            )
            raise RuntimeError(
                f"Falha ao exportar camada para explode.\n"
                f"Layer valid: {layer.isValid()}\n"
                f"Provider: {layer.providerType()}\n"
                f"Path: {input_path}"
            )
        logger.debug(f"ExplodeStep: criando task para {input_path}")
        return ExplodeHugeLayerTask(
            input_path=input_path, output_path=exploded_path, tool_key=tool_key
        )

    def on_success(self, context: ExecutionContext, result):
        logger = LogUtils(
            tool=context.get("tool_key"), class_name=self.__class__.__name__
        )
        logger.info(f"ExplodeStep.on_success: camada explodida salva em {result}")
        context.set("current_path", result)
