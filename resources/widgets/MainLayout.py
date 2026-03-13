from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QCheckBox, QTextEdit, QComboBox, QListWidget, QDoubleSpinBox, QGridLayout, QFrame, QApplication
)
from qgis.PyQt.QtWidgets import QLayout, QWidget
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QCursor
from typing import Optional
from ..styles.Styles import Styles
from .ScrollWidget import ScrollWidget
from ...core.config.LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey

logger = LogUtils(tool=ToolKey.CADMUS_PLUGIN, class_name="MainLayout", level=LogUtils.DEBUG)

class EdgeFrame(QFrame):
    """QFrame que notifica o MainLayout quando for redimensionado."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._owner_layout = None

    def set_owner_layout(self, layout):
        self._owner_layout = layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        try:
            if self._owner_layout:
                self._owner_layout._update_border_geometries()
        except Exception:
            pass


class BorderHitWidget(QWidget):
    """Widget invisível que representa uma borda "hit-only" para captura de mouse.

    Ele não pinta conteúdo; captura enter/leave/mouse events e delega para MainLayout.
    """
    def __init__(self, parent, edge: str, main_layout):
        super().__init__(parent)
        self._edge = edge
        self._layout = main_layout
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(0,0,0,0); border: none;")

    def enterEvent(self, event):
        try:
         #   logger.debug(f"BorderHitWidget.enterEvent: edge={self._edge}")
            self._layout._update_cursor(self._edge)
        except Exception:
            pass

    def leaveEvent(self, event):
        try:
            #logger.debug(f"BorderHitWidget.leaveEvent: edge={self._edge}")
            self._layout._update_cursor(None)
            QApplication.restoreOverrideCursor()
        except Exception:
            pass

    def mousePressEvent(self, event):
        try:
            #logger.debug(f"BorderHitWidget.mousePressEvent: edge={self._edge}")
            self._layout._start_resize_from_edge(event, self._edge)
            event.accept()
        except Exception:
            pass

    def mouseMoveEvent(self, event):
        try:
            if self._layout._resize_active:
                self._layout._perform_resize_move(event)
            else:
                self._layout._update_cursor(self._edge)
        except Exception:
            pass

    def mouseReleaseEvent(self, event):
        try:
            #logger.debug(f"BorderHitWidget.mouseReleaseEvent: edge={self._edge}")
            self._layout._end_resize()
            event.accept()
        except Exception:
            pass

class MainLayout(QVBoxLayout):
    def set_appbar_title(self, title: str):
        """Atualiza o título da AppBar se presente."""
        appbar = self.get_appbar()
        if appbar:
            appbar.set_title(title)

    def get_appbar(self):
        """Retorna referência para o AppBarWidget se presente."""
        for i in range(self._inner_layout.count()):
            widget = self._inner_layout.itemAt(i).widget()
            if widget and hasattr(widget, "set_title"):
                return widget
        return None
    """Container layout customizado para plugins Cadmus com suporte a resize.
    
    ARQUITETURA:
    ============
    1. RESIZE (Separação de Responsabilidades):
       - BasePlugin recebe eventos de mouse do Qt
       - MainLayout executa lógica de resize (_get_resize_edge, _update_cursor)
       - Limpo e reutilizável em qualquer plugin
    
    2. SCROLL (Encapsulamento Automático):
       - MainLayout cria ScrollWidget INTERNAMENTE se enable_scroll=True
       - Plugin NÃO importa ScrollWidget (encapsulado)
       - Plugin NÃO toca em self.scroll_container (não existe)
       - add_items() decide automaticamente para onde vai cada item:
         * Se scroll habilitado: encaminha para scroll
         * Se scroll desabilitado: encaminha para inner_layout
       - Responsabilidade única: MainLayout gerencia scroll, plugin só adiciona itens
    
    Benefícios:
    - Separação de responsabilidades: BasePlugin recebe, MainLayout executa
    - Encapsulamento: scroll é detalhe interno
    - Reutilizável: MainLayout funciona com ou sem scroll
    - Testável: lógica concentrada em uma classe
    - Simples: BasePlugin tem apenas 3 métodos de delegação
    """
    def __init__(self, parent=None, enable_scroll=False):
        super().__init__(parent)

        # margens externas do dialog (recorte do radius)
        self.setContentsMargins(3, 3, 3, 3)
        self.setSpacing(0)

        # container visual (frame customizado para atualizar bordas)
        self._frame = EdgeFrame(parent)
        self._frame.setObjectName("main_container")
        self._frame.setStyleSheet(Styles.main_application())
        self._frame.setMouseTracking(True)  # Ativa rastreamento no frame
        try:
            self._frame.set_owner_layout(self)
        except Exception:
            pass
        # layout interno real (sempre criado, com ou sem scroll)
        self._inner_layout = QVBoxLayout(self._frame)
        self._inner_layout.setContentsMargins(5, 5, 5, 5)
        self._inner_layout.setSpacing(Styles.LAYOUT_V_SPACING)  # Consistente com ou sem scroll

        # scroll widget (criado apenas se enable_scroll=True)
        self._scroll = None
        if enable_scroll:
            self._scroll = ScrollWidget(parent)
            self._inner_layout.addWidget(self._scroll)

        # adiciona o frame ao layout principal
        super().addWidget(self._frame)
        
        # Resize handler attributes
        self._resize_border = 10  # pixels
        self._resize_active = False
        self._resize_edge = None
        self._last_pos = None
        self._parent_dialog = parent
        
        # border hit widgets
        self._borders = {}
        try:
            self._create_border_widgets()
            self._update_border_geometries()
        except Exception:
            pass
        # Ativa rastreamento de mouse para atualizar cursor continuamente
        if parent:
            parent.setMouseTracking(True)
        try:
            pname = type(parent).__name__ if parent is not None else None
            logger.debug(f"MainLayout.__init__: parent={pname}, enable_scroll={enable_scroll}")
        except Exception:
            pass

    def addWidget(self, widget, *args, **kwargs):
        """
        Adiciona widget ao layout.
        
        Se scroll está habilitado, adiciona ao scroll.
        Caso contrário, adiciona ao inner_layout.
        """
        if self._scroll is not None:
            # Cria container para o widget se necessário
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(widget)
            self._scroll.add_layout_as_content(layout)
        else:
            self._inner_layout.addWidget(widget, *args, **kwargs)

    def addLayout(self, layout, *args, **kwargs):
        """
        Adiciona layout ao layout.
        
        Se scroll está habilitado, adiciona ao scroll.
        Caso contrário, adiciona ao inner_layout.
        """
        if self._scroll is not None:
            self._scroll.add_layout_as_content(layout)
        else:
            self._inner_layout.addLayout(layout, *args, **kwargs)

    def addStretch(self, *args, **kwargs):
        self._inner_layout.addStretch(*args, **kwargs)

    def addSpacing(self, *args, **kwargs):
        self._inner_layout.addSpacing(*args, **kwargs)
        
    def add_items(self, items):
        """
        Adiciona widgets e/ou layouts ao layout.

        Se scroll está habilitado, coleta todos os itens e os adiciona
        ao scroll como um único layout.
        
        Se scroll está desabilitado, adiciona ao inner_layout diretamente.

        Parameters
        ----------
        items : iterable
            Lista ou tupla contendo QLayout e/ou QWidget
        """
        if not items:
            return

        if self._scroll is not None:
            # Scroll habilitado: coleta itens em um layout e adiciona ao scroll
            container_layout = QVBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(Styles.LAYOUT_V_SPACING)
            
            for item in items:
                if isinstance(item, QLayout):
                    container_layout.addLayout(item)
                elif isinstance(item, QWidget):
                    container_layout.addWidget(item)
                else:
                    raise TypeError(
                        f"Tipo inválido em MainLayout.add_items: {type(item)}"
                    )
            
            # Adiciona ao scroll
            self._scroll.add_layout_as_content(container_layout)
            
            # Adiciona stretch ao final para preenchimento consistente
            #self._inner_layout.addStretch()
        else:
            # Scroll desabilitado: adiciona diretamente ao inner_layout
            for item in items:
                if isinstance(item, QLayout):
                    self._inner_layout.addLayout(item)
                elif isinstance(item, QWidget):
                    self._inner_layout.addWidget(item)
                else:
                    raise TypeError(
                        f"Tipo inválido em MainLayout.add_items: {type(item)}"
                    )
            
            # Adiciona stretch ao final para evitar gaps quando sem scroll
            # Isso mantém itens compactos no topo, preenchendo espaço restante com stretch
            self._inner_layout.addStretch()

    def get_size(self) -> tuple:
        """
        Retorna a dimensão atual do layout container (width, height).
        
        Returns
        -------
        tuple
            (width, height) em pixels
        """
        if self._frame:
            return (self._frame.width(), self._frame.height())
        return (0, 0)

    def set_size(self, width: int, height: int):
        """
        Define a dimensão do layout container.
        
        Parameters
        ----------
        width : int
            Largura em pixels
        height : int
            Altura em pixels
        """
        if self._frame:
            self._frame.setMinimumSize(width, height)
            self._frame.resize(width, height)
    
    def _get_resize_edge(self, pos: QPoint) -> Optional[str]:
        """Detecta qual borda está sendo apontada."""
        if not self._parent_dialog:
            return None
        try:
            logger.debug(f"_get_resize_edge: pos=({pos.x()},{pos.y()})")
        except Exception:
            logger.debug("_get_resize_edge: unable to read pos")
        
        rect = self._parent_dialog.rect()
        if pos.x() < self._resize_border and pos.y() < self._resize_border:
            return "top-left"
        elif pos.x() > rect.width() - self._resize_border and pos.y() < self._resize_border:
            return "top-right"
        elif pos.x() < self._resize_border and pos.y() > rect.height() - self._resize_border:
            return "bottom-left"
        elif pos.x() > rect.width() - self._resize_border and pos.y() > rect.height() - self._resize_border:
            return "bottom-right"
        elif pos.x() < self._resize_border:
            return "left"
        elif pos.x() > rect.width() - self._resize_border:
            return "right"
        elif pos.y() < self._resize_border:
            return "top"
        elif pos.y() > rect.height() - self._resize_border:
            return "bottom"
        return None

    def _create_border_widgets(self):
        edges = ["left", "right", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]
        for e in edges:
            try:
                w = BorderHitWidget(self._frame, e, self)
                w.setObjectName(f"border_hit_{e}")
                w.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                w.setMouseTracking(True)
                w.raise_()
                self._borders[e] = w
            except Exception:
                logger.debug(f"_create_border_widgets: failed for {e}")

    def _update_border_geometries(self):
        try:
            if not self._frame:
                return
            fw = self._frame.width()
            fh = self._frame.height()
            b = self._resize_border
            if "left" in self._borders:
                self._borders["left"].setGeometry(0, 0, b, fh)
            if "right" in self._borders:
                self._borders["right"].setGeometry(max(0, fw - b), 0, b, fh)
            if "top" in self._borders:
                self._borders["top"].setGeometry(0, 0, fw, b)
            if "bottom" in self._borders:
                self._borders["bottom"].setGeometry(0, max(0, fh - b), fw, b)
            if "top-left" in self._borders:
                self._borders["top-left"].setGeometry(0, 0, b, b)
            if "top-right" in self._borders:
                self._borders["top-right"].setGeometry(max(0, fw - b), 0, b, b)
            if "bottom-left" in self._borders:
                self._borders["bottom-left"].setGeometry(0, max(0, fh - b), b, b)
            if "bottom-right" in self._borders:
                self._borders["bottom-right"].setGeometry(max(0, fw - b), max(0, fh - b), b, b)
            for w in self._borders.values():
                w.raise_()
        except Exception:
            logger.debug("_update_border_geometries: failed")

    def _start_resize_from_edge(self, event, edge):
        try:
            self._resize_active = True
            self._resize_edge = edge
            self._last_pos = event.globalPos()
            logger.debug(f"_start_resize_from_edge: edge={edge}, last_pos=({self._last_pos.x()},{self._last_pos.y()})")
        except Exception:
            logger.debug("_start_resize_from_edge: failed")

    def _perform_resize_move(self, event):
        try:
            if not (self._resize_active and self._resize_edge and self._last_pos and self._parent_dialog):
                return
            delta = event.globalPos() - self._last_pos
            new_rect = self._parent_dialog.geometry()
            if "top" in self._resize_edge:
                new_rect.setTop(new_rect.top() + delta.y())
            if "bottom" in self._resize_edge:
                new_rect.setBottom(new_rect.bottom() + delta.y())
            if "left" in self._resize_edge:
                new_rect.setLeft(new_rect.left() + delta.x())
            if "right" in self._resize_edge:
                new_rect.setRight(new_rect.right() + delta.x())
            if new_rect.width() >= self._parent_dialog.minimumWidth() and new_rect.height() >= self._parent_dialog.minimumHeight():
                self._parent_dialog.setGeometry(new_rect)
                self._last_pos = event.globalPos()
        except Exception:
            logger.debug("_perform_resize_move: failed")

    def _end_resize(self):
        try:
            self._resize_active = False
            self._resize_edge = None
            self._last_pos = None
            self._update_cursor(None)
            QApplication.restoreOverrideCursor()
            logger.debug("_end_resize: resize finished, cursor reset")
        except Exception:
            logger.debug("_end_resize: failed")

    def _update_cursor(self, edge: Optional[str]):
        """Atualiza cursor baseado na borda detectada."""
        cursors = {
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top-left": Qt.SizeFDiagCursor,
            "top-right": Qt.SizeBDiagCursor,
            "bottom-left": Qt.SizeBDiagCursor,
            "bottom-right": Qt.SizeFDiagCursor,
        }
        if self._parent_dialog:
            cur = cursors.get(edge, Qt.ArrowCursor)
            try:
                logger.debug(f"_update_cursor: edge={edge} cursor={cur}")
            except Exception:
                logger.debug("_update_cursor: unable to log edge")
            self._parent_dialog.setCursor(QCursor(cur))

    def handle_mouse_press(self, event):
        """Inicia resize ao clicar nas bordas."""
        if event.button() == Qt.LeftButton:
            try:
                p = event.pos(); g = event.globalPos(); b = event.button()
                logger.debug(f"handle_mouse_press: pos=({p.x()},{p.y()}), global=({g.x()},{g.y()}), button={b}")
            except Exception:
                logger.debug("handle_mouse_press: unable to read event data")

            # Map event global position to parent dialog coordinates to ensure
            # correct edge detection when events come from child widgets.
            mapped_pos = None
            if self._parent_dialog:
                try:
                    mapped = self._parent_dialog.mapFromGlobal(event.globalPos())
                    mapped_pos = QPoint(mapped.x(), mapped.y())
                except Exception:
                    mapped_pos = event.pos()
            else:
                mapped_pos = event.pos()

            edge = self._get_resize_edge(mapped_pos)
            if edge:
                self._resize_active = True
                self._resize_edge = edge
                self._last_pos = event.globalPos()
                event.accept()
                return True
        return False

    def handle_mouse_move(self, event):
        """Redimensiona a janela ao arrastar."""
        try:
            p = event.pos(); g = event.globalPos()
            logger.debug(f"handle_mouse_move: pos=({p.x()},{p.y()}), global=({g.x()},{g.y()})")
        except Exception:
            logger.debug("handle_mouse_move: unable to read event positions")

        # Map event to parent dialog coordinates for edge detection
        mapped_pos = None
        if self._parent_dialog:
            try:
                mapped = self._parent_dialog.mapFromGlobal(event.globalPos())
                mapped_pos = QPoint(mapped.x(), mapped.y())
            except Exception:
                mapped_pos = event.pos()
        else:
            mapped_pos = event.pos()

        edge = self._get_resize_edge(mapped_pos)

        # Log: mouse position relative to parent dialog (mapped from global)
        if self._parent_dialog:
            try:
                w, h = self.get_size()
                inside = 0 <= mapped_pos.x() <= w and 0 <= mapped_pos.y() <= h
                logger.debug(f"handle_mouse_move: mapped=({mapped_pos.x()},{mapped_pos.y()}), inside_window={inside}, window_size=({w},{h})")
            except Exception:
                logger.debug("handle_mouse_move: unable to compute mapped pos")

        # SEMPRE atualiza o cursor baseado na posição atual
        # Mesmo quando não está em resize, isso garante que o cursor resete corretamente
        self._update_cursor(edge)
        try:
            geom = self._parent_dialog.geometry()
            logger.debug(f"handle_mouse_move: geometry=({geom.x()},{geom.y()},{geom.width()},{geom.height()})")
        except Exception:
            logger.debug("handle_mouse_move: unable to read geometry")
        
        if self._resize_active and self._resize_edge and self._last_pos and self._parent_dialog:
            delta = event.globalPos() - self._last_pos
            new_rect = self._parent_dialog.geometry()
            
            if "top" in self._resize_edge:
                new_rect.setTop(new_rect.top() + delta.y())
            if "bottom" in self._resize_edge:
                new_rect.setBottom(new_rect.bottom() + delta.y())
            if "left" in self._resize_edge:
                new_rect.setLeft(new_rect.left() + delta.x())
            if "right" in self._resize_edge:
                new_rect.setRight(new_rect.right() + delta.x())
            
            # Respeita tamanho mínimo
            if new_rect.width() >= self._parent_dialog.minimumWidth() and new_rect.height() >= self._parent_dialog.minimumHeight():
                self._parent_dialog.setGeometry(new_rect)
                self._last_pos = event.globalPos()

    def handle_mouse_release(self, event):
        """Finaliza resize ao soltar o mouse."""
        if event.button() == Qt.LeftButton and self._resize_active:
            self._resize_active = False
            self._resize_edge = None
            self._last_pos = None
            self._update_cursor(None)
            logger.debug("handle_mouse_release: resize finished, cursor reset")
            event.accept()
            return True
        return False
