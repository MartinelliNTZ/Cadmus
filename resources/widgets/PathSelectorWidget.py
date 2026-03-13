# -*- coding: utf-8 -*-
"""
Widget universal para seleção de pastas e arquivos.

Arquitetura ENCAPSULADA:
- Suporta múltiplos modos: folder, file, files, save
- SEMPRE retorna lista via get_paths()
- Validação automática de input
- Plugin apenas chama: get_paths() ou is_enabled()

Modos:
    - folder: selecionar 1 pasta
    - folders: selecionar múltiplas pastas
    - file: selecionar 1 arquivo (read mode)
    - files: selecionar múltiplos arquivos (read mode)
    - save: selecionar 1 arquivo para salvar (save mode)
    - checkbox: adiciona checkbox para ativar/desativar seleção

Uso:
    widget = PathSelectorWidget(mode="save", checkbox=True)
    if widget.is_enabled():
        paths = widget.get_paths()  # ["C:/arquivo.txt"]
"""

import os
from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox
)
from qgis.PyQt.QtCore import pyqtSignal


class PathSelectorWidget(QWidget):
    """Widget universal para seleção de pastas/arquivos com checkbox opcional.

    Características:
    - Modos: folder, folders, file, files, save
    - Checkbox opcional para ativar/desativar seleção
    - Sempre retorna lista via get_paths()
    - Validação automática de input
    - Filtros customizáveis para arquivos

    Sinais:
        pathsChanged: emitido quando a lista de paths muda
        enabledChanged: emitido quando checkbox muda (se habilitado)
    """

    MODE_FOLDER = "folder"      # 1 pasta
    MODE_FOLDERS = "folders"    # múltiplas pastas
    MODE_FILE = "file"          # 1 arquivo (read)
    MODE_FILES = "files"        # múltiplos arquivos (read)
    MODE_SAVE = "save"          # 1 arquivo (save)

    pathsChanged = pyqtSignal(list)
    enabledChanged = pyqtSignal(bool)

    def __init__(
        self,
        *,
        title: str = "Selecionar",
        file_filter: str = "Todos (*.*)",
        mode: str = MODE_FOLDER,
        checkbox: bool = False,
        checkbox_text: str = "Ativar",
        parent=None
    ):
        """Inicializa widget universal.

        Parameters:
            title: Rótulo do campo input
            file_filter: Filtro de arquivos (ex: "Imagens (*.png *.jpg)")
            mode: "folder" | "folders" | "file" | "files" | "save"
            checkbox: Se True, adiciona checkbox para ativar/desativar
            checkbox_text: Texto do checkbox
            parent: Widget pai
        """
        super().__init__(parent)

        self._title = title
        self._file_filter = file_filter
        self._mode = mode
        self._last_path = None
        self._paths = []
        self._checkbox_enabled = not checkbox  # Se sem checkbox, sempre habilitado

        self._build_ui(checkbox, checkbox_text)
    
    def _build_ui(self, checkbox: bool, checkbox_text: str):
        """Constrói UI: checkbox (opcional) + label + input + botão."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # ========== CHECKBOX (OPCIONAL) ==========
        if checkbox:
            self._checkbox = QCheckBox(checkbox_text)
            self._checkbox.setChecked(False)
            self._checkbox.toggled.connect(self._on_checkbox_toggled)
            main_layout.addWidget(self._checkbox)
        else:
            self._checkbox = None

        # ========== INPUT + BOTÃO ==========
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(4)
        
        label = QLabel(self._title)
        label_width = label.fontMetrics().horizontalAdvance(self._title) + 4
        label.setFixedWidth(label_width)
        input_layout.addWidget(label)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Nenhum caminho selecionado")
        self._input.setMaximumHeight(24)
        self._input.setMinimumWidth(50)
        self._input.textChanged.connect(self._on_input_changed)
        
        # Desabilitar se houver checkbox desativado
        if checkbox:
            self._input.setEnabled(False)
        
        input_layout.addWidget(self._input)

        btn = QPushButton("...")
        btn.setFixedWidth(24)
        btn.setFixedHeight(24)
        btn.clicked.connect(self._browse)
        
        # Desabilitar se houver checkbox desativado
        if checkbox:
            btn.setEnabled(False)
        
        self._browse_btn = btn
        input_layout.addWidget(btn)
        main_layout.addLayout(input_layout)
    
    def _on_checkbox_toggled(self, checked: bool):
        """Checkbox foi alternado."""
        self._checkbox_enabled = checked
        self._input.setEnabled(checked)
        self._browse_btn.setEnabled(checked)
        
        if not checked:
            self._paths = []
        
        self.enabledChanged.emit(checked)
        self.pathsChanged.emit(self._paths)
    
    def _on_input_changed(self, text: str):
        """User digitou/colou algo - validar e processar."""
        text = text.strip()

        if not text:
            self._paths = []
            self.pathsChanged.emit([])
            return

        # Processar conforme o modo
        if self._mode == self.MODE_FOLDER:
            if os.path.isdir(text):
                self._paths = [text]
                self._last_path = text
                self.pathsChanged.emit([text])
        
        elif self._mode == self.MODE_FOLDERS:
            # Multi-pasta via input não faz muito sentido, mas aceitar como pasta singular
            if os.path.isdir(text):
                self._paths = [text]
                self._last_path = text
                self.pathsChanged.emit([text])
        
        elif self._mode == self.MODE_FILE:
            if os.path.isfile(text):
                self._paths = [text]
                self._last_path = os.path.dirname(text)
                self.pathsChanged.emit([text])
        
        elif self._mode == self.MODE_FILES:
            if os.path.isfile(text):
                self._paths = [text]
                self._last_path = os.path.dirname(text)
                self.pathsChanged.emit([text])
        
        elif self._mode == self.MODE_SAVE:
            # Modo save: qualquer caminho é válido (será criado)
            self._paths = [text]
            self._last_path = os.path.dirname(text)
            self.pathsChanged.emit([text])
    
    def _browse(self):
        """Abre dialog apropriado conforme o modo."""
        initial_dir = self._get_initial_directory()
        
        try:
            if self._mode == self.MODE_FOLDER:
                self._browse_folder(initial_dir)
            elif self._mode == self.MODE_FOLDERS:
                self._browse_multiple_folders(initial_dir)
            elif self._mode == self.MODE_FILE:
                self._browse_single_file(initial_dir)
            elif self._mode == self.MODE_FILES:
                self._browse_multiple_files(initial_dir)
            elif self._mode == self.MODE_SAVE:
                self._browse_save_file(initial_dir)
        except Exception:
            pass
    
    def _get_initial_directory(self) -> str:
        """Retorna diretório inicial para dialog."""
        current_path = self._input.text().strip()
        
        if current_path:
            if os.path.isdir(current_path):
                return current_path
            elif os.path.isfile(current_path):
                return os.path.dirname(current_path)
        
        if self._last_path and os.path.isdir(self._last_path):
            return self._last_path
        
        return str(Path.home())
    
    def _browse_folder(self, initial_dir: str):
        """Dialog: selecionar 1 pasta."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self._title,
            initial_dir
        )
        
        if folder:
            self._paths = [folder]
            self._last_path = folder
            self._input.setText(folder)
            self.pathsChanged.emit([folder])
    
    def _browse_multiple_folders(self, initial_dir: str):
        """Dialog: selecionar múltiplas pastas (implementado como pasta única por limitação do Qt)."""
        # Qt não tem dialog nativo para múltiplas pastas, então usar getExistingDirectory
        folder = QFileDialog.getExistingDirectory(
            self,
            self._title,
            initial_dir
        )
        
        if folder:
            self._paths = [folder]
            self._last_path = folder
            self._input.setText(folder)
            self.pathsChanged.emit([folder])
    
    def _browse_single_file(self, initial_dir: str):
        """Dialog: selecionar 1 arquivo (read mode)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._title,
            initial_dir,
            self._file_filter
        )
        
        if file_path:
            self._paths = [file_path]
            self._last_path = os.path.dirname(file_path)
            self._input.setText(file_path)
            self.pathsChanged.emit([file_path])
    
    def _browse_multiple_files(self, initial_dir: str):
        """Dialog: selecionar múltiplos arquivos (read mode)."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self._title,
            initial_dir,
            self._file_filter
        )
        
        if files:
            self._paths = files
            self._last_path = os.path.dirname(files[0])
            
            if len(files) == 1:
                self._input.setText(files[0])
            else:
                self._input.setText(f"{len(files)} arquivo(s) selecionado(s)")
            
            self.pathsChanged.emit(files)
    
    def _browse_save_file(self, initial_dir: str):
        """Dialog: selecionar 1 arquivo para salvar (save mode)."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._title,
            initial_dir,
            self._file_filter
        )
        
        if file_path:
            self._paths = [file_path]
            self._last_path = os.path.dirname(file_path)
            self._input.setText(file_path)
            self.pathsChanged.emit([file_path])
    
    def get_paths(self) -> list:
        """
        Retorna lista de paths selecionados.
        
        Sempre retorna lista:
        - [] se vazio ou checkbox desabilitado
        - ["C:/pasta"] se 1 pasta/arquivo
        - ["C:/a.txt", "C:/b.txt"] se múltiplos
        
        Returns:
            list: Lista de paths
        """
        if not self._checkbox_enabled:
            return []
        return self._paths.copy()
    
    def is_enabled(self) -> bool:
        """Retorna se widget está habilitado (relevante se houver checkbox)."""
        return self._checkbox_enabled
    
    def set_enabled(self, enabled: bool):
        """Define se widget está habilitado (só funciona se checkbox existir)."""
        if self._checkbox:
            self._checkbox.setChecked(enabled)
    
    def set_path(self, path: str):
        """Define um caminho único."""
        if path:
            self._input.setText(path)
    
    def set_paths(self, paths: list):
        """Define múltiplos caminhos."""
        if paths:
            if len(paths) == 1:
                self._input.setText(paths[0])
            else:
                self._input.setText(f"{len(paths)} item(s)")
            self._paths = paths.copy()
            self.pathsChanged.emit(paths)
    
    def get_file_path(self) -> str:
        """Retorna primeiro caminho como string (compatibilidade com widget anterior)."""
        if self._checkbox_enabled and self._paths:
            return self._paths[0]
        return ""
    
    def set_file_path(self, path: str):
        """Define primeiro caminho (compatibilidade com widget anterior)."""
        self.set_path(path)
    
    def clear(self):
        """Limpa tudo."""
        self._input.setText("")
        self._paths = []
        if self._checkbox:
            self._checkbox.setChecked(False)
        self.pathsChanged.emit([])
    
    def is_empty(self) -> bool:
        """Verifica se está vazio."""
        return len(self._paths) == 0

