# -*- coding: utf-8 -*-
"""
Botão simples que ocupa o espaço disponível.

Características:
- Widget QPushButton com SizePolicy Expanding
- Ocupa espaço disponível horizontalmente e verticalmente
- Padronizado via WidgetFactory
- Estilizado pelo Styles.simple_button_widget()

Uso:
    widget = SimpleButtonWidget("Clique em mim")
    widget.clicked.connect(callback)
"""

from qgis.PyQt.QtWidgets import QPushButton, QSizePolicy
from ...i18n.TranslationManager import STR


class SimpleButtonWidget(QPushButton):
    """
    Botão simples que ocupa a largura disponível com altura fixa.

    Características:
    - Expande para preencher espaço horizontal (largura)
    - Altura fixa em 12px (padrão Styles.BUTTON_HEIGHT)
    - Simplificado e reutilizável
    - Aplicar estilo via: widget.setStyleSheet(Styles.simple_button_widget())
    """

    def __init__(self, text: str = STR.BUTTON, parent=None):
        """
        Inicializa botão simples.

        Parameters:
            text: Texto exibido no botão
            parent: Widget pai
        """
        super().__init__(text, parent)

        # Configurar política de tamanho: largura expande, altura fixa
        from ...resources.styles.Styles import Styles
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(Styles.BUTTON_HEIGHT)
