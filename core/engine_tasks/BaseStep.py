# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any

from .ExecutionContext import ExecutionContext


class BaseStep(ABC):
    """
    Contrato padrão para qualquer etapa da pipeline.
    """

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