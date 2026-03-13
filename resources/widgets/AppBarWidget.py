# resources/widgets/AppBarWidget.py
from ...core.config.LogUtils import LogUtils
from qgis.PyQt.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout
from qgis.PyQt.QtCore import Qt, pyqtSignal, QPoint
from qgis.PyQt.QtGui import QPixmap
import os


class AppBarWidget(QFrame):
    def set_title(self, title: str):
            """Atualiza o título exibido na AppBar."""
            self.lbl_title.setText(title)
    runClicked = pyqtSignal()
    infoClicked = pyqtSignal()
    closeClicked = pyqtSignal()

    def __init__(
        self,
        *,
        title: str,
        icon_path: str = None,
        show_run: bool = False,
        show_info: bool = False,
        show_close: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("app_bar")
        self.logger = LogUtils(tool="Untraceable", class_name=self.__class__.__name__, level=LogUtils.DEBUG)
        self.logger.debug(f"Inicializando AppBarWidget com arquivo: {icon_path}")
        if icon_path:
            # Resolve icon relative to resources/ (AppBarWidget is in resources/widgets)
            icon_path = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "..", "icons", icon_path)
            )

        self._drag_pos: QPoint = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # optional icon label
        self.lbl_icon = None
        if icon_path:
            try:
                if os.path.exists(icon_path):
                    pix = QPixmap(icon_path)
                    if not pix.isNull():
                        self.lbl_icon = QLabel()
                        self.lbl_icon.setPixmap(pix.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        self.lbl_icon.setObjectName("app_bar_icon")
                        layout.addWidget(self.lbl_icon)
                        self.logger.debug(f"Ícone carregado com sucesso para AppBar: {icon_path}")
                    else:
                        self.logger.warning(f"Ícone encontrado mas inválido para AppBar: {icon_path}")
                else:                    self.logger.warning(f"Ícone não encontrado para AppBar: {icon_path}")
            except Exception as e:
                self.logger.error(f"Erro ao carregar ícone para AppBar: {icon_path}. Detalhes: {e}")                
        else:
            self.logger.debug("Nenhum ícone fornecido para AppBar.")
            
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("app_bar_title")
        self.lbl_title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(self.lbl_title)
        layout.addStretch()

        if show_run:
            self.btn_run = QPushButton("Executar")
            self.btn_run.setObjectName("app_bar_btn_run")
            self.btn_run.clicked.connect(self.runClicked.emit)
            layout.addWidget(self.btn_run)

        if show_info:
            self.btn_info = QPushButton("Info")
            self.btn_info.setObjectName("app_bar_btn_info")
            self.btn_info.clicked.connect(self.infoClicked.emit)
            layout.addWidget(self.btn_info)

        if show_close:
            self.btn_close = QPushButton("✕")
            self.btn_close.setObjectName("app_bar_btn_close")

            # 🔑 comportamento padrão
            self.btn_close.clicked.connect(self._on_close_clicked)

            layout.addWidget(self.btn_close)

    # =====================================================
    # FECHAR JANELA
    # =====================================================

    def _on_close_clicked(self):
        self.closeClicked.emit()
        self.window().close()

    # =====================================================
    # DRAG DA JANELA (QT 5)
    # =====================================================

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)
