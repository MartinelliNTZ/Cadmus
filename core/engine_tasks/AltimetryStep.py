# -*- coding: utf-8 -*-
from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.altimetry_task import AltimetriaTask
from ..config.LogUtils import LogUtils


class AltimetryStep(BaseStep):
    def name(self) -> str:
        return "altimetry"

    def create_task(self, context: ExecutionContext):
        lat = context.get("lat")
        lon = context.get("lon")
        tool_key = context.get("tool_key", "coord_click")

        if lat is None or lon is None:
            return None

        task = AltimetriaTask(lat, lon, callback=None)
        return task

    def on_success(self, context: ExecutionContext, result):
        logger = LogUtils(tool=context.get("tool_key"), class_name=self.__class__.__name__)
        try:
            dialog = context.get("dialog")
            if dialog:
                dialog.set_altitude(result)
            logger.debug(f"AltimetryStep.on_success: {result}")
        except Exception as e:
            logger.error(f"AltimetryStep.on_success error: {e}")

    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        logger = LogUtils(tool=context.get("tool_key"), class_name=self.__class__.__name__)
        try:
            dialog = context.get("dialog")
            if dialog:
                dialog.set_altitude(None)
            logger.warning(f"AltimetryStep.on_error: {exception}")
        except Exception:
            pass
