# -*- coding: utf-8 -*-
"""
Plugin wrapper para integração do Logcat ao Cadmus.

Este arquivo serve como ponto de entrada para a ferramenta Logcat,
permitindo que ela seja invocada a partir do menu do plugin.
"""

from .ui.logcat_dialog import LogcatDialog


def run(iface):
    """
    Abre o diálogo Logcat de forma não-modal.

    Args:
        iface: Interface do QGIS

    Returns:
        LogcatDialog: A janela do Logcat (mantém referência viva)
    """
    dlg = LogcatDialog(iface.mainWindow())
    dlg.setModal(False)
    dlg.show()
    return dlg  # ESSENCIAL: manter referência viva
