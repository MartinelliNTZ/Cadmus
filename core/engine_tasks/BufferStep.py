# -*- coding: utf-8 -*-
import os

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.BufferLayerTask import BufferLayerTask
from ..config.LogUtils import LogUtils


class BufferStep(BaseStep):

    def name(self) -> str:
        return "buffer"

    def create_task(self, context: ExecutionContext):

        context.require(["current_path", "buffer_distance", "tool_key"])

        input_path = context.get("current_path")
        tool_key = context.get("tool_key")
        distance = context.get("buffer_distance")
        logger = LogUtils(tool=tool_key, class_name=self.__class__.__name__)

        tmp_dir = context.get("tmp_dir")
        if not tmp_dir:
            logger.error("tmp_dir não definido no contexto")
            raise RuntimeError("tmp_dir não definido no contexto.")

        output_path = os.path.join(tmp_dir, "buffer.gpkg")

        logger.debug(
            f"BufferStep: criando buffer com distância={distance}, "
            f"entrada={input_path}, saída={output_path}"
        )

        return BufferLayerTask(
            input_path=input_path,
            output_path=output_path,
            distance=distance,
            segments=context.get("buffer_segments", 5),
            end_cap_style=context.get("buffer_end_cap", 1),
            join_style=context.get("buffer_join_style", 1),
            miter_limit=context.get("buffer_miter_limit", 2.0),
            dissolve=context.get("buffer_dissolve", False),
            tool_key=tool_key,
        )

    def on_success(self, context: ExecutionContext, result):
        logger = LogUtils(
            tool=context.get("tool_key"), class_name=self.__class__.__name__
        )
        logger.info(f"BufferStep.on_success: buffer criado e salvo em {result}")
        context.set("current_path", result)
