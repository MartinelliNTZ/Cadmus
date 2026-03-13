from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont


class HudProgressBar(QWidget):

    def __init__(self, title="PROCESSING DATA"):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        #self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()

        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignCenter)

        self.percent = QLabel("0 %")
        self.percent.setAlignment(Qt.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setTextVisible(False)

        layout.addWidget(self.label)
        layout.addWidget(self.bar)
        layout.addWidget(self.percent)

        self.setLayout(layout)

        self.setStyleSheet(self._style())

    def setValue(self, value):

        self.bar.setValue(value)
        self.percent.setText(f"{value} %")

    def _style(self):

        return """
        QWidget{
            background-color:#0b0f14;
        }

        QLabel{
            color:#00eaff;
            font-size:12px;
            font-family:Consolas;
            letter-spacing:2px;
        }

        QProgressBar{
            border:2px solid #00eaff;
            border-radius:4px;
            background:#02060a;
            height:18px;
        }

        QProgressBar::chunk{
            background-color:qlineargradient(
                x1:0,y1:0,
                x2:1,y2:0,
                stop:0 #00f7ff,
                stop:1 #0051ff
            );
            margin:1px;
        }
        """