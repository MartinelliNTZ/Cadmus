# -*- coding: utf-8 -*-
from qgis.core import QgsProcessingFeedback
from ..config.LogUtils import LogUtils


class TaskFeedback(QgsProcessingFeedback):

    def __init__(self, task, tool_key="untraceable"):
        super().__init__()
        self.task = task
        self.logger = LogUtils(tool=tool_key, class_name="TaskFeedback")

    def isCanceled(self):
        return self.task.isCanceled()

    # Forwarding helpers so VectorField tasks can use a standard
    # QgsProcessingFeedback interface without worrying about the underlying QgsTask.
    # These are safe and allow callers to treat this as a standard processing feedback.
    def setProgress(self, pct):
        try:
            self.task.setProgress(int(pct))
        except Exception as e:
            self.logger.error(f"Error {e}")

    def pushInfo(self, msg):
        try:
            self.task.pushInfo(str(msg))
        except Exception as e:
            self.logger.error(f"Error {e}")

    def pushWarning(self, msg):
        try:
            self.task.pushWarning(str(msg))
        except Exception as e:
            self.logger.error(f"Error {e}")

    def pushCritical(self, msg):
        try:
            self.task.pushCritical(str(msg))
        except Exception as e:
            self.logger.error(f"Error {e}")
