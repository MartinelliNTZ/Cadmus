from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QPainter, QColor, QPen, QFont
import math


class HudCircularLoader(QWidget):

    def __init__(self):

        super().__init__()

        self.progress = 0
        self.angle = 0

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

       # self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(220,220)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def setProgress(self,val):

        self.progress = val
        self.update()

    def animate(self):

        self.angle += 4
        if self.angle > 360:
            self.angle = 0

        self.update()

    def paintEvent(self,event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()
        radius = 80

        # fundo
        pen = QPen(QColor(30,40,60),3)
        painter.setPen(pen)
        painter.drawEllipse(center,radius,radius)

        # progresso
        pen = QPen(QColor(0,230,255),6)
        painter.setPen(pen)

        span = int(-self.progress * 360 * 16 / 100)

        painter.drawArc(
            center.x()-radius,
            center.y()-radius,
            radius*2,
            radius*2,
            90*16,
            span
        )

        # bola girando
        angle_rad = math.radians(self.angle)

        bx = center.x() + radius * math.cos(angle_rad)
        by = center.y() + radius * math.sin(angle_rad)

        painter.setBrush(QColor(0,255,255))
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(int(bx)-6,int(by)-6,12,12)

        # percentual
        painter.setPen(QColor(0,255,255))

        font = QFont("Consolas",22,QFont.Bold)
        painter.setFont(font)

        text = f"{self.progress}%"

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            text
        )