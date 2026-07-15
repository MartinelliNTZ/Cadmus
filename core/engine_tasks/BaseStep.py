# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Optional

from .ExecutionContext import ExecutionContext
from ..config.LogUtils import LogUtils


class BaseStep(ABC):
    """
    Contrato padrão para qualquer etapa da pipeline.
    """

    def __init__(self):
        self.logger: Optional[LogUtils] = None

    # -----------------------------
    # Logger
    # -----------------------------

    def _init_logger(self, context: ExecutionContext) -> LogUtils:
        """
        Inicializa self.logger a partir do tool_key do context (se ainda não foi criado).
        """
        if self.logger is None:
            tool_key = context.tool_key
            if not tool_key:
                raise KeyError("ExecutionContext.tool_key não definido")
            self.logger = LogUtils(tool=tool_key, class_name=self.__class__.__name__)
        return self.logger

    # -----------------------------
    # Identificação
    # -----------------------------

    @abstractmethod
    def name(self) -> str:
        """Nome do step (para logs/debug)."""
        pass

    # -----------------------------
    # Controle de execução
    # -----------------------------

    def should_run(self, context: ExecutionContext) -> bool:
        """Permite pular etapa dinamicamente."""
        return True

    # -----------------------------
    # Task creation
    # -----------------------------

    @abstractmethod
    def create_task(self, context: ExecutionContext):
        """
        Deve retornar uma instância de BaseTask.
        """
        pass

    # -----------------------------
    # Callbacks
    # -----------------------------

    @abstractmethod
    def on_success(self, context: ExecutionContext, result: Any) -> None:
        """
        Atualiza o contexto após sucesso da task.
        """
        pass

    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        """
        Tratamento opcional de erro específico do step.
        """
        pass

    # -----------------------------
    # Futuro (opcional)
    # -----------------------------

    def rollback(self, context: ExecutionContext) -> None:
        """
        Permite desfazer alterações (opcional).
        """
        pass
