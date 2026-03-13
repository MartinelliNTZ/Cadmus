"""
Diálogo para visualização de múltiplas entradas de log.

Permite copiar/exportar várias entradas de uma só vez.
"""
from typing import List
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QTabWidget
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from ..core.model.log_entry import LogEntry


class LogMultipleDetailDialog(QDialog):
    """
    Diálogo modal para exibir e exportar múltiplas entradas de log.
    """
    
    def __init__(self, entries: List[LogEntry], parent=None):
        """
        Inicializa o diálogo.
        
        Args:
            entries: Lista de LogEntry a exibir
            parent: Widget pai
        """
        super().__init__(parent)
        self.entries = entries
        self.setWindowTitle(f"Log Details - {len(entries)} entries")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        self._build_ui()
    
    def _build_ui(self):
        """Constrói a interface."""
        layout = QVBoxLayout()
        
        # Cabeçalho
        header = QLabel(f"Showing {len(self.entries)} log entries")
        layout.addWidget(header)
        
        layout.addSpacing(10)
        
        # Tabs: uma aba por entry ou unified view
        tab_widget = QTabWidget()
        
        # Aba "Combined" - tudo junto
        combined_text = QTextEdit()
        combined_text.setReadOnly(True)
        combined_text.setFont(QFont("Courier", 9))
        combined_text.setText(self._get_combined_text())
        tab_widget.addTab(combined_text, "Combined")
        
        # Aba "Individual" - por entrada
        for idx, entry in enumerate(self.entries, 1):
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Courier", 9))
            text_edit.setText(entry.get_full_details())
            tab_widget.addTab(text_edit, f"Entry {idx}")
        
        layout.addWidget(tab_widget)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_copy_combined = QPushButton("Copy Combined")
        btn_copy_combined.clicked.connect(self._copy_combined)
        btn_layout.addWidget(btn_copy_combined)
        
        btn_copy_all = QPushButton("Copy All Individual")
        btn_copy_all.clicked.connect(self._copy_all_individual)
        btn_layout.addWidget(btn_copy_all)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _get_combined_text(self) -> str:
        """Retorna todas as entradas formatadas juntas."""
        lines = []
        for idx, entry in enumerate(self.entries, 1):
            lines.append(f"{'='*60}")
            lines.append(f"Entry {idx}/{len(self.entries)}")
            lines.append(f"{'='*60}")
            lines.append(entry.get_full_details())
            lines.append("")
        return "\n".join(lines)
    
    def _copy_combined(self):
        """Copia tudo junto para clipboard."""
        from qgis.PyQt.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self._get_combined_text())
    
    def _copy_all_individual(self):
        """Copia com separação clara de cada entry."""
        from qgis.PyQt.QtWidgets import QApplication
        separator = "\n\n" + ("="*80) + "\n\n"
        all_text = separator.join([e.get_full_details() for e in self.entries])
        clipboard = QApplication.clipboard()
        clipboard.setText(all_text)
