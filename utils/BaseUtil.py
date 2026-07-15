# -*- coding: utf-8 -*-
"""
BaseUtil — Classe base para todos os utilitários do sistema
=============================================================
Centraliza logging consistente para todas as classes em `utils/`.

Toda classe em utils/ DEVE herdar de BaseUtil.

Duas formas de uso:

1. **Instantiable** (classe com estado):
    class MinhaUtil(BaseUtil):
        def __init__(self, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE):
            super().__init__(tool_key)

        def meu_metodo(self):
            self.logger.info("Executando", code="EXEC")

2. **Static** (apenas métodos estáticos, sem estado):
    class MinhaUtil(BaseUtil):
        @staticmethod
        def meu_metodo(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE):
            logger = MinhaUtil._get_logger(tool_key)
            logger.info("Executando", code="EXEC")
"""

from typing import Optional

from ..core.config.LogUtils import LogUtils
from .ToolKeys import ToolKey


class BaseUtil:
    """
    Classe base para utilitários do sistema.

    Toda classe em utils/ DEVE herdar de BaseUtil.

    Constantes:
        TOOL_KEY_UNTRACEABLE: str — valor padrão para tool_key quando não há
            ferramenta específica. Evita importar ToolKey em cada classe filha.

    Para uso instantiate (com self.logger):
        super().__init__(tool_key)  # tool_key opcional

    Para uso estático:
        BaseUtil._get_logger(tool_key, class_name)
    """

    TOOL_KEY_UNTRACEABLE: str = ToolKey.UNTRACEABLE

    def __init__(self, tool_key: str = TOOL_KEY_UNTRACEABLE):
        """
        Inicializa a instância com logger próprio.

        Args:
            tool_key: Chave da ferramenta para rastreamento de logs.
        """
        self.tool_key = tool_key
        self.logger = self._get_logger(tool_key)

    @classmethod
    def _get_logger(cls, tool_key: str = TOOL_KEY_UNTRACEABLE, class_name: Optional[str] = None) -> LogUtils:
        """
        Retorna uma instância de LogUtils para a classe e tool especificadas.

        Args:
            tool_key: Chave da ferramenta (ex: ToolKey.CONSOLE).
            class_name: Nome da classe (opcional; usa cls.__name__ se omitido).

        Returns:
            Instância de LogUtils configurada.
        """
        if class_name is None:
            class_name = cls.__name__
        return LogUtils(tool=tool_key, class_name=class_name)
