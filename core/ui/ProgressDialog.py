# -*- coding: utf-8 -*-
"""
ProgressDialog - Wrapper para QProgressDialog com interface padronizada

Fornece uma classe simples e direta para barra de progresso modal com logging.
"""

from qgis.PyQt.QtWidgets import QProgressDialog
from qgis.PyQt.QtCore import Qt
from ..config.LogUtils import LogUtils


class ProgressDialog:
    """
    Wrapper padronizado para QProgressDialog com logging integrado.

    Uso:
        progress = ProgressDialog("Processando...", "Cancelar", 0, total, parent_widget)
        for i in range(total):
            progress.set_value(i)
            QCoreApplication.processEvents()
            if progress.is_canceled():
                break
        progress.set_value(total)
        progress.close()
    """

    def __init__(
        self,
        title: str,
        cancel_button_text: str,
        minimum: int,
        maximum: int,
        parent=None,
    ):
        """
        Inicializa barra de progresso modal com logging.

        Parameters
        ----------
        title : str
            Texto principal da caixa de diálogo
        cancel_button_text : str
            Texto do botão cancelar
        minimum : int
            Valor inicial (típico: 0)
        maximum : int
            Valor máximo/final (típico: total de itens)
        parent : QWidget, optional
            Widget pai (típico: self em dialogs)
        """

        self.logger = LogUtils(
            tool="ui_progress", class_name="ProgressDialog", level=LogUtils.DEBUG
        )

        # Criar QProgressDialog
        self.dialog = QProgressDialog(
            title, cancel_button_text, minimum, maximum, parent
        )
        self.dialog.setWindowModality(Qt.WindowModal)

        self.title = title
        self.current_value = minimum

        self.logger.info(
            f"ProgressDialog CRIADO: '{title}' (min={minimum}, max={maximum})"
        )

    def set_value(self, value: int):
        """Define o valor atual da barra de progresso."""
        self.dialog.setValue(value)
        self.current_value = value

        max_val = self.dialog.maximum()
        if max_val > 0:
            percent = (value / max_val) * 100
            self.logger.debug(f"Progresso: {value}/{max_val} ({percent:.0f}%)")

    def set_maximum(self, value: int):
        """Define o valor máximo da barra de progresso."""
        self.dialog.setMaximum(value)
        self.logger.info(f"Máximo definido para: {value}")

    def is_canceled(self) -> bool:
        """Verifica se o usuário clicou em Cancelar."""
        canceled = self.dialog.wasCanceled()
        if canceled:
            self.logger.warning(
                f"ProgressDialog CANCELADO em {self.current_value}/{self.dialog.maximum()}"
            )
        return canceled

    def cancel(self):
        """Cancela a operação programaticamente."""
        self.logger.info("ProgressDialog cancelado programaticamente")
        self.dialog.cancel()

    def close(self):
        """Fecha a caixa de progresso."""
        self.dialog.close()
        self.logger.info(
            f"ProgressDialog FECHADO: '{self.title}' (final: {self.current_value}/{self.dialog.maximum()})"
        )

    def show(self):
        """Exibe a caixa de progresso."""
        self.dialog.show()
        self.logger.info(f"ProgressDialog EXIBIDO: '{self.title}'")
