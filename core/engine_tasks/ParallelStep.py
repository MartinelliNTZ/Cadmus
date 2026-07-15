# -*- coding: utf-8 -*-
from typing import List, Any, Dict, Optional
import threading
import time

from qgis.core import QgsTask, QgsApplication

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..config.LogUtils import LogUtils


class ParallelStep(BaseStep):
    """
    Composite Step que executa vários `BaseStep` em paralelo.

    - Recebe uma lista de steps independentes
    - Cria as tasks desses sub-steps
    - Agenda todas as tasks com `QgsApplication.taskManager().addTask()`
    - Aguarda todas finalizarem, agrupa resultados e retorna um dict

    Nota: Todo o paralelismo fica encapsulado aqui; o `AsyncPipelineEngine`
    continua tratando `ParallelStep` como um `BaseStep` normal.
    """

    def __init__(self, steps: List[BaseStep], description: Optional[str] = None):
        if not isinstance(steps, list):
            raise TypeError("ParallelStep expects a list of BaseStep instances")
        self._steps = steps
        self._description = description
        self.logger = LogUtils(tool="ParallelStep", class_name="ParallelStep")

    def name(self) -> str:
        if self._description:
            return f"Parallel[{self._description}]"
        names = ",".join([s.name() for s in self._steps])
        return f"Parallel[{names}]"

    def should_run(self, context: ExecutionContext) -> bool:
        # Executa se pelo menos um sub-step desejar rodar
        return any(s.should_run(context) for s in self._steps)

    def create_task(self, context: ExecutionContext):
        return _ParallelGroupTask(self._steps, context, self.name())

    def on_success(self, context: ExecutionContext, result: Any) -> None:
        # Por design, os on_success dos sub-steps já foram executados
        # pelo _ParallelGroupTask; aqui podemos adicionar agregações
        try:
            context.set("parallel_result", result)
        except Exception as e:
            self.logger.error(f"ParallelStep.on_success error: {e}")

    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        # Já foi coletado pelo grupo; apenas registre
        try:
            context.add_error(exception)
        except Exception as e:
            self.logger.error(f"ParallelStep.on_error error: {e}")


class _ParallelGroupTask(QgsTask):
    """
    Task composta que agenda e monitora um grupo de tasks.

    Comportamento:
    - Cria as tasks dos sub-steps
    - Anexa callbacks locais para coletar resultados/erros
    - Agenda as tasks em paralelo
    - Monitora até todas terminarem ou até cancelamento
    - Em caso de erro, cancela tasks restantes e chama `self.on_error`
    - Em caso de sucesso, chama `self.on_success` com dict {step_name: result}
    """

    def __init__(
        self,
        steps: List[BaseStep],
        context: ExecutionContext,
        description: str = "ParallelGroup",
    ):
        super().__init__(description, QgsTask.CanCancel)
        self._steps = steps
        self._context = context

        self._lock = threading.Lock()
        self._pending = 0
        self._results: Dict[str, Any] = {}
        self._error: Optional[Exception] = None
        self._done_event = threading.Event()
        self._subtasks: List[QgsTask] = []
        self.logger = LogUtils(
            tool="ParallelGroupTask", class_name="_ParallelGroupTask"
        )

        # callbacks that will be set by engine
        self.on_success = None
        self.on_error = None

    def run(self) -> bool:
        # Cria e agenda subtasks
        with self._lock:
            for step in self._steps:
                try:
                    task = step.create_task(self._context)
                except Exception as e:
                    # falha ao criar task -> aborta
                    self._error = e
                    self._done_event.set()
                    break

                if task is None:
                    # step optou por não criar task
                    continue

                # Guarda referência
                self._subtasks.append(task)

                # Envolva callbacks para coletar resultados
                def make_success_handler(s, t):
                    def _on_success(result):
                        try:
                            # permite que o próprio sub-step aplique sua lógica
                            try:
                                s.on_success(self._context, result)
                            except Exception as e:
                                self.logger.error(f"substep on_success error: {e}")

                            with self._lock:
                                self._results[s.name()] = result
                                self._pending -= 1
                                if self._pending <= 0:
                                    self._done_event.set()
                        except Exception as e:
                            # registro local
                            self.logger.error(f"subtask success handler error: {e}")

                    return _on_success

                def make_error_handler(s, t):
                    def _on_error(exc):
                        try:
                            try:
                                s.on_error(self._context, exc)
                            except Exception as e:
                                self.logger.error(f"substep on_error error: {e}")

                            with self._lock:
                                # registra primeira exceção
                                if self._error is None:
                                    self._error = exc
                                # força cancelamento das demais
                                for st in self._subtasks:
                                    try:
                                        st.cancel()
                                    except Exception as e:
                                        self.logger.error(
                                            f"Error cancelling subtask: {e}"
                                        )

                                self._done_event.set()
                        except Exception as e:
                            self.logger.error(f"subtask error handler error: {e}")

                    return _on_error

                # Attach handlers
                task.on_success = make_success_handler(step, task)
                task.on_error = make_error_handler(step, task)

                # Forward subtask progress to group progress
                try:
                    task.progressChanged.connect(self._on_subtask_progress)
                except Exception as e:
                    self.logger.error(f"Failed connecting progressChanged: {e}")
                self._pending += 1

        # Se erro na criação das tasks
        if self._error:
            return False

        # Agenda subtasks
        for st in list(self._subtasks):

            try:
                QgsApplication.taskManager().addTask(st)
            except Exception as e:
                # falha ao agendar
                with self._lock:
                    if self._error is None:
                        self._error = e
                    # cancela os já agendados
                    for s in self._subtasks:
                        try:
                            s.cancel()
                        except Exception as e:
                            self.logger.error(
                                f"Error cancelling scheduled subtask: {e}"
                            )

                    self._done_event.set()
                break

        # Aguarda conclusão ou cancelamento
        while not self._done_event.is_set():
            if self.isCanceled():
                # Propaga cancelamento para subtasks
                for st in list(self._subtasks):
                    try:
                        st.cancel()
                    except Exception as e:
                        self.logger.error(
                            f"Error cancelling subtask during shutdown: {e}"
                        )
                self._done_event.set()
                break
            QgsApplication.processEvents()
            time.sleep(0.01)

        # Retorna sucesso se não houve erro
        return self._error is None

    def _on_subtask_progress(self, value: float) -> None:
        # Calcula média simples de progresso entre subtasks
        try:
            # tenta ler progress individuais (não disponível), então apenas
            # estima com base no último valor recebido e número de tasks
            # para manter o feed de progresso ao engine.
            # Aqui adotamos: group_progress = value / max(1, len(self._subtasks))
            total = max(1, len(self._subtasks))
            group_progress = min(100.0, float(value) / total)
            try:
                self.setProgress(int(group_progress))
            except Exception as e:
                self.logger.error(f"_on_subtask_progress setProgress error: {e}")
        except Exception as e:
            self.logger.error(f"_on_subtask_progress error: {e}")

    def finished(self, success: bool):
        # Se sucesso, chama on_success com dicionário de resultados
        if success and self._error is None:
            if callable(self.on_success):
                try:
                    self.on_success(self._results)
                except Exception as e:
                    self.logger.error(f"Parallel group on_success error: {e}")
            return

        # Em caso de erro, prioriza a primeira exceção coletada
        exc = (
            self._error
            if self._error is not None
            else Exception("ParallelGroup failed")
        )
        if callable(self.on_error):
            try:
                self.on_error(exc)
            except Exception as e:
                self.logger.error(f"Parallel group on_error error: {e}")
