# -*- coding: utf-8 -*-
"""
Widget de scroll customizado integrado ao tema do software.

Arquitetura:
- QScrollArea com estilo padronizado
- Scrollbars com cores do tema
- Comportamento suave e responsivo
- Propaga eventos de mouse para detecção de resize nas bordas
"""

from qgis.PyQt.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout
)
from qgis.PyQt.QtCore import Qt
from ...resources.styles.Styles import Styles


class ScrollWidget(QScrollArea):
    """
    QScrollArea customizada com estilo integrado ao tema.
    
    Propaga eventos de mouse para permitir detecção de bordas e resize.
    
    Uso:
        scroll = ScrollWidget(parent=self)
        scroll.setWidget(my_content_widget)
        layout.addWidget(scroll)
    """
    
    def __init__(self, parent=None):
        """
        Inicializa o widget de scroll.
        
        Parameters
        ----------
        parent : QWidget, optional
            Widget pai (geralmente o dialog)
        """
        super().__init__(parent)
        
        # Configurações de comportamento
        self.setWidgetResizable(True)
        self.setStyleSheet(Styles.scroll_area())
        
        # Ativa suavização de scroll
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Remove borda padrão
        self.setFrameShape(QScrollArea.NoFrame)
        self.setFrameShadow(QScrollArea.Plain)
        
        # Ativa rastreamento de mouse para propagar eventos de resize
        self.setMouseTracking(True)

    def set_content_widget(self, widget: QWidget):
        """
        Define o widget de conteúdo.
        
        Parameters
        ----------
        widget : QWidget
            Widget que será exibido no scroll
        """
        if widget:
            self.setWidget(widget)

    def add_layout_as_content(self, layout):
        """
        Cria um widget container e adiciona um layout a ele.
        
        Parameters
        ----------
        layout : QLayout
            Layout a ser adicionado como conteúdo
        """
        container = QWidget()
        container.setLayout(layout)
        self.set_content_widget(container)
    
    def mouseMoveEvent(self, event):
        """Propaga eventos de mouse para o parent para permitir detecção de resize."""
        super().mouseMoveEvent(event)
        # Propagar para o parent se for perto das bordas
        if self.parent():
            self.parent().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Propaga eventos de mouse para o parent para permitir detecção de resize."""
        super().mousePressEvent(event)
        if self.parent():
            self.parent().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Propaga eventos de mouse para o parent para permitir detecção de resize."""
        super().mouseReleaseEvent(event)
        if self.parent():
            self.parent().mouseReleaseEvent(event)
