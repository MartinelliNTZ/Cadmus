# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QToolBar
from ....utils.ToolKeys import ToolKey
from ....core.config.LogUtils import LogUtils


class CadmusToolBar(QToolBar):
    """
    Toolbar exclusiva do plugin Cadmus.

    Herda de QToolBar e fornece métodos para adicionar botões dropdown
    de forma organizada, com separadores automáticos.
    """

    def __init__(self, title, parent=None):
        """
        Inicializa a toolbar.

        :param title: Título da toolbar
        :param parent: Widget pai
        """
        self.logger = LogUtils(
            tool=ToolKey.SYSTEM, class_name="CadmusToolBar", level=LogUtils.DEBUG
        )
        super().__init__(title, parent)
        self.setObjectName(f"{title}_Toolbar")
        self.setVisible(True)  # Garantir que a toolbar seja visível
        self.logger.debug(f"Toolbar '{title}' inicializada com sucesso")

    def add_dropdown_buttons(self, buttons):
        """
        Adiciona múltiplos botões dropdown à toolbar.

        :param buttons: Lista de DropdownToolButton a adicionar
        """
        for button in buttons:
            self.addAction(button.action)
            self.logger.debug(f"Botão '{button.action.text()}' adicionado à toolbar")

            # Adicionar separador após cada botão, exceto o último
            if button != buttons[-1]:
                self.addSeparator()

        # Garantir que a toolbar seja visível após adicionar botões
        self.show()
