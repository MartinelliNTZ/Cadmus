# -*- coding: utf-8 -*-
from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.reverse_geocoding_task import ReverseGeocodeTask
from ..config.LogUtils import LogUtils


class ReverseGeocodeStep(BaseStep):
    def name(self) -> str:
        return "reverse_geocode"

    def create_task(self, context: ExecutionContext):
        lat = context.get("lat")
        lon = context.get("lon")
        if lat is None or lon is None:
            return None

        task = ReverseGeocodeTask(lat, lon, callback=None)
        return task

    def on_success(self, context: ExecutionContext, result):
        logger = LogUtils(tool=context.get("tool_key"), class_name=self.__class__.__name__)
        try:
            dialog = context.get("dialog")
            if dialog:
                dialog.set_address(result)
            logger.debug(f"ReverseGeocodeStep.on_success: {result}")
        except Exception as e:
            logger.error(f"ReverseGeocodeStep.on_success error: {e}")

    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        logger = LogUtils(tool=context.get("tool_key"), class_name=self.__class__.__name__)
        try:
            dialog = context.get("dialog")
            if dialog:
                dialog.set_address(None)
            logger.warning(f"ReverseGeocodeStep.on_error: {exception}")
        except Exception:
            pass
