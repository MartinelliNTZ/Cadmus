from qgis.core import QgsProcessingFeedback

class TaskFeedback(QgsProcessingFeedback):

    def __init__(self, task):
        super().__init__()
        self.task = task

    def isCanceled(self):
        return self.task.isCanceled()

    # Forwarding helpers so VectorField tasks can use a standard
    # QgsProcessingFeedback interface without worrying about the underlying QgsTask.
    # These are safe and allow callers to treat this as a standard processing feedback.
    def setProgress(self, pct):
        try:
            self.task.setProgress(int(pct))
        except Exception:
            pass

    def pushInfo(self, msg):
        try:
            self.task.pushInfo(str(msg))
        except Exception:
            pass

    def pushWarning(self, msg):
        try:
            self.task.pushWarning(str(msg))
        except Exception:
            pass

    def pushCritical(self, msg):
        try:
            self.task.pushCritical(str(msg))
        except Exception:
            pass