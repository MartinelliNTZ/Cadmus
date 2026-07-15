import time
from qgis.PyQt.QtWidgets import QDialog, QLabel, QHBoxLayout, QGraphicsBlurEffect
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtCore import QCoreApplication


class TemporaryDialog(QDialog):
    def __init__(
        self,
        iface,
        message="Mensagem",
        time=5,
        icon=None,
        alpha=80,
        background_color="#333333",
        font_color="#ffffff",
        border=None,
        blur=1,
    ):

        # Verifica se iface.mainWindow() existe
        main_window = iface.mainWindow()

        if main_window is None:
            pass

        super().__init__(main_window)

        self.iface = iface
        self.time = time * 1000

        # Flags
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window

        self.setWindowFlags(flags)
        self.setModal(False)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(8)

        # Ícone
        if icon:
            icon_label = QLabel()
            if isinstance(icon, QIcon):
                pix = icon.pixmap(20, 20)
            else:
                pix = QPixmap(icon).scaled(
                    20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            icon_label.setPixmap(pix)
            layout.addWidget(icon_label)

        # Texto
        text_label = QLabel(message)
        text_label.setStyleSheet(f"color: {font_color}; font-size: 12px;")
        layout.addWidget(text_label)

        self.setLayout(layout)
        self.setMinimumSize(200, 80)

        # Estilo
        border_style = "none" if border is None else border
        stylesheet = f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 {background_color},
                                            stop:1 #000000);
                border-radius: 14px;
                border: {border_style};
            }}
        """
        self.setStyleSheet(stylesheet)

        # Transparência
        self.setWindowOpacity(alpha / 100.0)
        # Fade timing
        self.duration_ms = int(time * 1000)
        self.fade_start_ms = int(self.duration_ms * 0.8)
        self.fade_steps = 20
        self.fade_interval_ms = max(
            1, int((self.duration_ms - self.fade_start_ms) / self.fade_steps)
        )
        self.base_opacity = alpha / 100.0

        # Blur
        if blur > 0:
            effect = QGraphicsBlurEffect()
            effect.setBlurRadius(blur)
            self.setGraphicsEffect(effect)
        else:
            pass

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)

    def show(self):

        super().show()

        self.raise_()

        self.activateWindow()

        self.adjustSize()

        parent_geom = self.iface.mainWindow().geometry()
        x = parent_geom.right() - self.width() - 20
        y = parent_geom.bottom() - self.height() - 40

        parent_geom = self.iface.mainWindow().geometry()
        x = parent_geom.center().x() - self.width() // 2
        y = parent_geom.center().y() - self.height() // 2
        self.move(x, y)

        self.timer.start(self.time)
        self.setMinimumSize(200, 200)  # largura mínima 200, altura mínima 80
        QCoreApplication.processEvents()

        fade_wait = self.fade_start_ms / 1000.0
        if fade_wait > 0:
            time.sleep(fade_wait)

        step_wait = self.fade_interval_ms / 1000.0
        for step in range(1, self.fade_steps + 1):
            alpha = self.base_opacity * (1.0 - step / self.fade_steps)
            self.setWindowOpacity(max(0.0, alpha))
            QCoreApplication.processEvents()
            time.sleep(step_wait)

    def stop(self):
        print(">>> [DEBUG] stop() chamado")
        self.fade_start_timer.stop()
        self.fade_timer.stop()
        self.close()
