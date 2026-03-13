"""
Diálogo para visualização detalhada de uma entrada de log.

Mostra todos os detalhes, permite copiar.
"""
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from ..core.model.log_entry import LogEntry


class LogDetailDialog(QDialog):
    """
    Diálogo modal para exibir detalhes completos de uma entrada de log.
    """
    
    def __init__(self, entry: LogEntry, parent=None):
        """
        Inicializa o diálogo.
        
        Args:
            entry: LogEntry a exibir
            parent: Widget pai
        """
        super().__init__(parent)
        self.entry = entry
        self.setWindowTitle(f"Log Details - {entry.level}")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        self._build_ui()
    
    def _build_ui(self):
        """Constrói a interface."""
        layout = QVBoxLayout()
        
        # Cabeçalho com informações resumidas
        header = QLabel(
            f"<b>{self.entry.level}</b> | "
            f"{self.entry.ts} | "
            f"<b>{self.entry.tool}</b> | "
            f"{self.entry.class_name}"
        )
        layout.addWidget(header)
        
        layout.addSpacing(10)
        
        # Área de texto com detalhes completos
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier", 9))
        text_edit.setText(self.entry.get_full_details())
        layout.addWidget(text_edit)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_copy = QPushButton("Copy All")
        btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(btn_copy)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _copy_to_clipboard(self):
        """Copia detalhes completos para clipboard."""
        from qgis.PyQt.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.entry.get_full_details())
