# -*- coding: utf-8 -*-
"""
Widget para exibição de logo com altura fixa e centralização.
- Expande horizontalmente (Expanding)
- Altura fixa configurável
- Imagem redimensionada proporcionalmente para caber na altura
- Opcionalmente clicável (emite sinal clicked)
"""

import os
from qgis.PyQt.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtCore import Qt, pyqtSignal


class ImageWidget(QWidget):
    """
    Widget que exibe uma imagem redimensionada e centralizada.
    """

    clicked = pyqtSignal()

    def __init__(self, image_path: str, parent=None, fixed_height: int = 60):
        """
        Inicializa o widget.

        :param image_path: Caminho absoluto para o arquivo de imagem.
        :param parent: Widget pai.
        :param fixed_height: Altura fixa do widget (a imagem será redimensionada para essa altura).
        """
        super().__init__(parent)

        self.image_path = image_path
        self.fixed_height = fixed_height

        # Layout horizontal para centralizar a imagem
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Política de tamanho: expande horizontalmente, altura fixa
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(fixed_height)

        self._load_image()

    def _load_image(self):
        """Carrega a imagem e a redimensiona proporcionalmente para a altura fixa."""
        if not os.path.exists(self.image_path):
            self.label.setText("Imagem não encontrada")
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self.label.setText("Erro ao carregar imagem")
            return

        # Redimensiona mantendo a proporção para caber na altura definida
        scaled_pixmap = pixmap.scaledToHeight(self.fixed_height, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        """Torna o widget clicável (opcional)."""
        self.clicked.emit()
        super().mousePressEvent(event)

    def set_image(self, image_path: str):
        """Permite trocar a imagem em tempo de execução."""
        self.image_path = image_path
        self._load_image()
