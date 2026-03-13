# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtCore import QUrl


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Sobre o Cadmus")
        self.setMinimumWidth(420)

        main_layout = QVBoxLayout(self)

        # =====================================================
        # LOGO
        # =====================================================
        logo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "resources","icons", "mtl_agro.png"
        )

        if os.path.exists(logo_path):
            lbl_logo = QLabel()
            pixmap = QPixmap(logo_path)
            lbl_logo.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
            lbl_logo.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(lbl_logo)

        # =====================================================
        # INFORMAÇÕES
        # =====================================================
        lbl_title = QLabel("<h2>Cadmus</h2>")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_info = QLabel(
            """
            <b>Versão:</b> 1.2.6<br>
            <b>Atualizada em:</b> 12 de Janeiro de 2026<br>
            <b>Criado em:</b> 9 de Dezembro de 2025<br>
            <b>Criador:</b> MTL Agricultura e Tecnologia<br>
            <b>Local:</b> Palmas - Tocantins - Brasil<br>
            <b>Email:</b> <a href="mailto:martinelli.matheus11@gmail.com">martinelli.matheus11@gmail.com</a><br>
            <b>Site:</b> <a href="https://github.com/MartinelliNTZ/mtl-tools-repo">https://github.com/MartinelliNTZ/mtl-tools-repo</a><br>
            <b>GitHub:</b>
            <a href="https://github.com/MartinelliNTZ/mtl-tools-repo">
            https://github.com/MartinelliNTZ/mtl-tools-repo</a>
            """
        )

        lbl_info.setTextFormat(Qt.RichText)
        lbl_info.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl_info.setOpenExternalLinks(True)
        lbl_info.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(lbl_title)
        main_layout.addWidget(lbl_info)

        # =====================================================
        # BOTÃO FECHAR
        # =====================================================
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)

        h_btn = QHBoxLayout()
        h_btn.addStretch()
        h_btn.addWidget(btn_close)
        h_btn.addStretch()

        main_layout.addLayout(h_btn)


# =====================================================
# FUNÇÃO PÚBLICA (PADRÃO DO SEU PLUGIN)
# =====================================================
def run_about_dialog(iface):
    dlg = AboutDialog(iface.mainWindow())
    dlg.exec()
