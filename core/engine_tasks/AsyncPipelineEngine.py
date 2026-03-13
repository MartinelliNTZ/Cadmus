# -*- coding: utf-8 -*-
from typing import List, Optional

from qgis.core import QgsApplication

from .ExecutionContext import ExecutionContext
from .BaseStep import BaseStep
from ..config.LogUtils import LogUtils
from ..task.BaseTask import BaseTask
from qgis.core import QgsTask


class AsyncPipelineEngine:
    """
    Orquestrador genérico de Steps e QgsTasks.
    """
    logger = LogUtils(tool="AsyncPipelineEngine", class_name="AsyncPipelineEngine", level=LogUtils.DEBUG)

    def __init__(
        self,
        steps: List[BaseStep],
        context: ExecutionContext,
        *,
        on_finished=None,
        on_error=None,
        on_cancelled=None,
    ):
        self._pipeline_task = None
        self._steps = steps
        self._context = context

        self._on_finished = on_finished
        self._on_error = on_error
        self._on_cancelled = on_cancelled

        self._current_index = 0
        self._current_task = None
        self._is_running = False
        self._is_cancelled = False
    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def start(self) -> None:
        if self._is_running:
            raise RuntimeError("Pipeline already running.")

        self._is_running = True
        self._is_cancelled = False
        self._current_index = 0


        self._pipeline_task = PipelineTask("Processando trilha")
        QgsApplication.taskManager().addTask(self._pipeline_task)
        self._run_next_step()

    def _set_global_progress(self, step_progress: float):
        total_steps = len(self._steps)
        step_index = self._current_index

        step_progress = max(0.0, min(100.0, float(step_progress)))

        global_progress = ((step_index + step_progress / 100.0) / total_steps) * 100.0

        if self._pipeline_task:
            self._pipeline_task.setProgress(global_progress)

    def cancel(self) -> None:
        self._is_cancelled = True
        self._context.cancel()

        if self._current_task:
            try:
                self._current_task.cancel()
            except RuntimeError:
                pass

        if self._pipeline_task:
            self._pipeline_task.cancel()

        self._finish_cancelled()

    def is_running(self) -> bool:
        return self._is_running


    def _run_next_step(self) -> None:

        if self._is_cancelled or self._context.is_cancelled():
            self._finish_cancelled()
            return

        if self._current_index >= len(self._steps):
            self._finish_success()
            return

        step = self._steps[self._current_index]

        if not step.should_run(self._context):
            self._current_index += 1
            self._run_next_step()
            return

        task = step.create_task(self._context)

        if task is None:
            raise RuntimeError(f"Step '{step.name()}' returned no task.")

        self._current_task = task

        task.on_success = self._handle_task_success
        task.on_error = self._handle_task_error
        task.progressChanged.connect(self._set_global_progress)

        QgsApplication.taskManager().addTask(task)

    def _handle_task_success(self, result):

        step = self._steps[self._current_index]

        try:
            step.on_success(self._context, result)
        except Exception as exc:
            self._handle_task_error(exc)
            return

        self._current_index += 1
        self._run_next_step()

    def _handle_task_error(self, exception: Exception):

        step = self._steps[self._current_index]

        try:
            step.on_error(self._context, exception)
        except Exception:
            pass

        self._context.add_error(exception)
        self._finish_error()

    # -------------------------------------------------
    # Finalization
    # -------------------------------------------------

    def _finish_success(self):
        self._is_running = False
        self._current_task = None

        if self._pipeline_task:
            self._pipeline_task.setProgress(100)
            self._pipeline_task.mark_done()

        if self._on_finished:
            try:
                self._on_finished(self._context)
            except Exception as e:
                self.logger.error(f"Error:{e}")

    def _finish_error(self):
        self._is_running = False
        self._current_task = None

        if self._pipeline_task:
            self._pipeline_task.mark_done()

        if self._on_error:
            try:
                self._on_error(self._context.get_errors())
            except Exception as e:
                self.logger.error(f"Error:{e}")

    def _finish_cancelled(self):
        self._is_running = False
        self._current_task = None

        if self._pipeline_task:
            self._pipeline_task.mark_done()

        if self._on_cancelled:
            try:
                self._on_cancelled(self._context)
            except Exception as e:
                self.logger.error(f"Error:{e}")

class PipelineTask(QgsTask):

    def __init__(self, description="Pipeline"):
        super().__init__(description, QgsTask.CanCancel)
        self._done = False

    def run(self):
        # mantém task viva até engine marcar done
        while not self._done:
            if self.isCanceled():
                return False
            QgsApplication.processEvents()
        return True

    def mark_done(self):
        self._done = True

    def finished(self, result):
        pass