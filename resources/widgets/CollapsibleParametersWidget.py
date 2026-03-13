# -*- coding: utf-8 -*-
"""
Widget genérico para parâmetros avançados com suporte a expansão/recolhimento.

Arquitetura:
- Reutilizável em qualquer plugin (padrão de composição)
- Aceita qualquer widget/layout como conteúdo
- Suporta animação suave na expansão/recolhimento
- Header com ícone dinâmico (→ expandido | ↓ recolhido)
- Totalmente independente de lógica de negócio

Uso:
    widget = CollapsibleParametersWidget(title="Configurações Avançadas")
    widget.add_content_widget(my_qml_selector)
    widget.add_content_layout(my_other_layout)
    widget.set_expanded(True)
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame
)
from qgis.PyQt.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from ..styles.Styles import Styles


class CollapsibleParametersWidget(QWidget):
    """
    Widget expansível para parâmetros avançados.
    
    Sinais:
        expandedChanged: emitido quando o estado de expansão muda (bool)
    """
    
    expandedChanged = pyqtSignal(bool)
    
    def __init__(self, title: str = "Parâmetros Avançados", parent=None):
        """
        Inicializa o widget.
        
        Parameters
        ----------
        title : str
            Título exibido no header
        parent : QWidget, optional
            Widget pai
        """
        super().__init__(parent)
        
        self._title = title
        self._is_expanded = False
        self._animation = None
        
        # Container para o conteúdo (será animado)
        self._content_container = None
        self._content_layout = None
        
        # Componentes do header
        self._header_button = None
        self._title_label = None
        self._icon_label = None
        
        self._build_ui()
        self._bind_events()
    
    def _build_ui(self):
        """Constrói a interface com header + content container"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ============================================================
        # HEADER (sempre visível)
        # ============================================================
        header = QFrame()
        header.setObjectName("collapsible_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, Styles.CONTENT_PADDING, 8, Styles.CONTENT_PADDING)
        header_layout.setSpacing(Styles.LAYOUT_H_SPACING)
        
        # Ícone expansível (→ ou ↓)
        self._icon_label = QLabel("→")
        self._icon_label.setObjectName("collapsible_icon")
        self._icon_label.setFixedWidth(14)
        header_layout.addWidget(self._icon_label)
        
        # Título
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("collapsible_title")
        header_layout.addWidget(self._title_label)
        
        # Espaço flexível
        header_layout.addStretch()
        
        # Botão invisível para capturar cliques (melhor UX)
        self._header_button = QPushButton()
        self._header_button.setObjectName("collapsible_header_btn")
        self._header_button.setFlat(True)
        self._header_button.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self._header_button)
        
        main_layout.addWidget(header)
        
        # ============================================================
        # CONTENT CONTAINER (animado)
        # ============================================================
        self._content_container = QFrame()
        self._content_container.setObjectName("collapsible_content")
        
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(
            Styles.CONTENT_PADDING, 
            Styles.CONTENT_PADDING, 
            Styles.CONTENT_PADDING, 
            Styles.CONTENT_PADDING
        )
        self._content_layout.setSpacing(Styles.LAYOUT_V_SPACING)
        
        # Inicialmente recolhido (altura = 0)
        self._content_container.setMaximumHeight(0)
        
        main_layout.addWidget(self._content_container)
        main_layout.addStretch()
    
    def _bind_events(self):
        """Conecta eventos do header com toggle"""
        self._header_button.clicked.connect(self.toggle_expanded)
        
        # Permitir clicar no título também
        self._title_label.mousePressEvent = lambda e: self.toggle_expanded()
        self._icon_label.mousePressEvent = lambda e: self.toggle_expanded()
    
    def add_content_widget(self, widget: QWidget):
        """
        Adiciona um widget ao conteúdo.
        
        Parameters
        ----------
        widget : QWidget
            Widget a ser adicionado
        """
        if widget:
            self._content_layout.addWidget(widget)
    
    def add_content_layout(self, layout):
        """
        Adiciona um layout ao conteúdo.
        
        Parameters
        ----------
        layout : QLayout
            Layout a ser adicionado
        """
        if layout:
            self._content_layout.addLayout(layout)
    
    def add_content_item(self, item):
        """
        Versão genérica que aceita widget ou layout.
        
        Parameters
        ----------
        item : QWidget or QLayout
            Widget ou layout a ser adicionado
        """
        if isinstance(item, QWidget):
            self.add_content_widget(item)
        else:
            self.add_content_layout(item)
    
    def toggle_expanded(self):
        """Alterna entre expandido e recolhido"""
        self.set_expanded(not self._is_expanded)
    
    def set_expanded(self, expanded: bool):
        """
        Define o estado de expansão com animação.
        
        Parameters
        ----------
        expanded : bool
            True para expandir, False para recolher
        """
        if self._is_expanded == expanded:
            return  # Já está nesse estado
        
        self._is_expanded = expanded
        self._update_icon()
        self._animate_content(expanded)
        self.expandedChanged.emit(expanded)
    
    def _update_icon(self):
        """Atualiza o ícone baseado no estado"""
        self._icon_label.setText("↓" if self._is_expanded else "→")
    
    def _animate_content(self, expanded: bool):
        """Anima a expansão/recolhimento do conteúdo"""
        if self._animation:
            self._animation.stop()
        
        # Calcular altura do conteúdo
        content_height = self._content_layout.sizeHint().height()
        target_height = content_height if expanded else 0
        
        # Criar animação
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(200)  # 200ms
        self._animation.setStartValue(self._content_container.maximumHeight())
        self._animation.setEndValue(target_height)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._animation.start()
    
    def is_expanded(self) -> bool:
        """Retorna se está expandido"""
        return self._is_expanded
    
    def clear_content(self):
        """Remove todo o conteúdo adicionado"""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _clear_layout(self, layout):
        """Remove todos os itens de um layout recursivamente"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
