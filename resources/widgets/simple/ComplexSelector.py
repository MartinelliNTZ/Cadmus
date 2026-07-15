# -*- coding: utf-8 -*-
"""
ComplexSelector — Seletor avançado com suporte a QgsMapLayerComboBox e file/folder.
============================================================================
NÃO usa GridRadio. O comportamento é definido pelos parâmetros:
  - allow_file / allow_folder: quais botões aparecem (🔍 / 📁)
  - multiple: se pode selecionar múltiplos itens
  - selection_mode: modo padrão ("file" ou "folder")
  - mode_type: "input" ou "output"

Lógica central (MODO INPUT):
  - Padrão: QLineEdit exibindo path(s)
  - 📄 clicado → troca line edit por QgsMapLayerComboBox (sem diálogo)
  - 🔍 clicado → seleciona arquivo(s) via ExplorerUtils, volta ao line edit
  - 📁 clicado → seleciona pasta(s) via ExplorerUtils, volta ao line edit
  - ➡️ → abre o Windows Explorer no diretório do path atual ou da layer escolhida

Lógica central (MODO OUTPUT):
  - 🔍 clicado → sempre line edit, diálogo de salvar arquivo
  - 📁 clicado → sempre line edit, diálogo de selecionar pasta
  - 📥 → gera path usando parent + suffix + extension + subfolder
  - 🛠️ → gera path usando ProjectUtils + subfolder + fixed_name
  - ➡️ → abre o Windows Explorer no diretório do path atual

Uso:
    sel = ComplexSelector(label_text="Entrada:", allow_file=True, allow_folder=True, multiple=False, selection_mode="file")

    sel.get_root_path()      # diretório base
    sel.get_selected_list()  # itens selecionados
    sel.path()               # primeiro item
    sel.path_type()          # "file" | "folder" | "files" | "folders"
"""

from __future__ import annotations

import os
from typing import Callable
from typing import Optional

from qgis.PyQt.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QStackedWidget, QSizePolicy,
)
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel, QgsProject

from ....core.config.LogUtils import LogUtils
from ....resources.widgets.SimpleButtonWidget import SimpleButtonWidget
from ....resources.styles.Styles import Styles
from ....utils.ExplorerUtils import ExplorerUtils
from ....utils.ProjectUtils import ProjectUtils


class ComplexSelector(QWidget):
    """
    Seletor avançado com suporte a file/folder/files/folders e QgsMapLayerComboBox.

    O widget sempre armazena:
      - root_path: diretório base da seleção
      - selected_list: lista de itens selecionados (paths completos)

    Em modo input, o 📄 alterna entre QLineEdit e QgsMapLayerComboBox.
    """

    pathChanged = pyqtSignal(list)  # paths: list[str]

    def __init__(
        self,
        label_text: str = "",
        default_path: str = "",
        placeholder: str = "Caminho...",
        tooltip: str = "",
        file_filter: str = "Todos (*.*)",
        label_width: int = 130,
        # ── Controle de modo ──
        allow_file: bool = True,
        allow_folder: bool = False,
        multiple: bool = False,
        selection_mode: str = "file",   # "file" | "folder"
        # ── Controle de botões ──
        show_suggest_button: bool = False,
        show_project_button: bool = False,
        show_explorer_button: bool = True,
        show_origin_button: bool = False,
        suggested_path: str = "",
        # ── CRS embutido ──
        crs_enable: bool = False,
        # ── Output config ──
        mode_type: str = "input",  # "input" | "output"
        fixed_name: str = "",
        subfolder: str = "",
        # ── Origin config (📥) ──
        suffix: str = "",
        extension: str = "",
        parent_selector=None,  # Referência a outro ComplexSelector (parent)
        # ── Filtro de camada ──
        layer_filters=QgsMapLayerProxyModel.All,
        parent=None,
    ):
        super().__init__(parent)

        # Validação
        if not allow_file and not allow_folder:
            allow_file = True

        # Sanitiza selection_mode
        if selection_mode not in ("file", "folder"):
            selection_mode = "file"
        if selection_mode == "folder" and not allow_folder:
            selection_mode = "file"
        if selection_mode == "file" and not allow_file:
            selection_mode = "folder"

        self._file_filter = file_filter
        self._allow_file = allow_file
        self._allow_folder = allow_folder
        self._multiple = multiple
        self._selection_mode = selection_mode
        self._show_suggest_button = show_suggest_button
        self._show_project_button = show_project_button
        self._show_explorer_button = show_explorer_button
        self._show_origin_button = show_origin_button
        self._suggested_rel_path: str = suggested_path
        self._mode_type = mode_type
        self._fixed_name = fixed_name
        self._subfolder = subfolder
        self._suffix = suffix
        self._extension = extension
        self._parent_selector = parent_selector
        self._layer_filters = layer_filters

        # Estado interno
        self._root_path: str = ""
        self._selected_list: list[str] = []
        self._updating_display: bool = False  # guard para loop textChanged
        self._using_layer_combo: bool = False  # True = QgsMapLayerComboBox ativo

        # Logger
        self._logger = LogUtils(tool="ComplexSelector",
                                class_name="ComplexSelector")

        # CRS embutido
        self._crs_enable = crs_enable
        self._crs_widget = None  # CrsSelectorWidget | None

        # Callbacks públicos
        self.on_path_change = None    # callback(paths: list[str])
        self.on_browse_click = None   # callback()
        self.on_suggest_click = None  # callback()
        self.on_origin_click = None   # callback() — botão 📥, grid configura

        # Constrói UI
        self._build_ui(label_text, placeholder, tooltip, label_width)

        # Se default_path foi passado, inicializa
        if default_path:
            self.set_path(default_path)

    # ══════════════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════════════

    def _build_ui(self, label_text, placeholder, tooltip, label_width):
        """Constrói o layout com QStackedWidget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Trava a altura do widget inteiro para não esticar dentro de grids/forms externos
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Label
        self._label = QLabel(label_text)
        self._label.setFixedWidth(label_width)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if tooltip:
            self._label.setToolTip(tooltip)
        layout.addWidget(self._label, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── QStackedWidget: página 0 = QLineEdit, página 1 = QgsMapLayerComboBox ──
        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1, Qt.AlignmentFlag.AlignVCenter)

        # Página 0: QLineEdit
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setStyleSheet(Styles.input())
        if tooltip:
            self._edit.setToolTip(tooltip)
        self._edit.textChanged.connect(self._on_edit_text_changed)
        self._stack.addWidget(self._edit)

        # Página 1: QgsMapLayerComboBox (apenas input)
        self._combo = QgsMapLayerComboBox()
        self._combo.setAllowEmptyLayer(True)
        self._combo.setFilters(self._layer_filters)
        self._combo.setStyleSheet(Styles.map_layer_combobox())
        self._combo.setVisible(False)  # começa invisível
        self._combo.currentIndexChanged.connect(self._on_combo_layer_changed)
        self._stack.addWidget(self._combo)

        # Se modo input e show_project_button=True, começa com combo visível?
        # Não, começa sempre com line edit. 📄 alterna.

        # Botões
        self._add_buttons(layout)

        # Atualiza display
        self._update_display()

    def _add_buttons(self, layout):
        """Adiciona botões conforme configuração."""
        # ── 🔍 (file) ──
        if self._allow_file:
            self._btn_file = SimpleButtonWidget("🔍")
            self._btn_file.setFixedWidth(30)
            self._btn_file.setFixedHeight(32)
            self._btn_file.setToolTip(
                "Selecionar arquivos" if self._multiple else "Selecionar arquivo"
            )
            self._btn_file.clicked.connect(self._browse_file)
            layout.addWidget(self._btn_file, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── 📁 (folder) ──
        if self._allow_folder:
            self._btn_folder = SimpleButtonWidget("📁")
            self._btn_folder.setFixedWidth(30)
            self._btn_folder.setFixedHeight(32)
            self._btn_folder.setToolTip(
                "Selecionar pastas" if self._multiple else "Selecionar pasta"
            )
            self._btn_folder.clicked.connect(self._browse_folder)
            layout.addWidget(self._btn_folder, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── 📄 (project — só input, alterna entre line edit e combo) ──
        if self._mode_type == "input" and self._show_project_button:
            self._btn_project = SimpleButtonWidget("📄")
            self._btn_project.setFixedWidth(30)
            self._btn_project.setFixedHeight(32)
            self._btn_project.setToolTip("Alternar para seleção de camada")
            self._btn_project.clicked.connect(self._on_project_clicked)
            layout.addWidget(self._btn_project, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── 📥 (origin — só output com parent) ──
        if self._show_origin_button:
            self._btn_origin = SimpleButtonWidget("📥")
            self._btn_origin.setFixedWidth(30)
            self._btn_origin.setFixedHeight(32)
            self._btn_origin.setToolTip("Usar mesmo diretório da origem")
            self._btn_origin.clicked.connect(self._on_origin_clicked)
            layout.addWidget(self._btn_origin, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── 🛠️ (suggested — só output) ──
        if self._mode_type == "output" and self._show_suggest_button:
            self._btn_suggest = SimpleButtonWidget("🛠️")
            self._btn_suggest.setFixedWidth(30)
            self._btn_suggest.setFixedHeight(32)
            self._btn_suggest.setToolTip("Usar pasta do projeto")
            self._btn_suggest.clicked.connect(self._on_suggest_clicked)
            layout.addWidget(self._btn_suggest, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── ➡️ (explorer — sempre visível por padrão) ──
        if self._show_explorer_button:
            self._btn_explorer = SimpleButtonWidget("➡️")
            self._btn_explorer.setFixedWidth(30)
            self._btn_explorer.setFixedHeight(32)
            self._btn_explorer.setToolTip("Abrir localização no Explorer")
            self._btn_explorer.clicked.connect(self._open_explorer)
            layout.addWidget(self._btn_explorer, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── CRS embutido (ao lado dos botões) ──
        if self._crs_enable:
            """
            Precisa implementar
            import CrsSelectorWidget
            self._crs_widget = CrsSelectorWidget(label=None, compact=True)
            self._crs_widget.setFixedWidth(150)
            layout.addWidget(self._crs_widget, 0, Qt.AlignmentFlag.AlignVCenter)
            """
    # ══════════════════════════════════════════════════════════════════
    # Display
    # ══════════════════════════════════════════════════════════════════

    def _update_display(self):
        """Atualiza o widget conforme o estado atual e o modo ativo."""
        self._updating_display = True
        try:
            if self._using_layer_combo:
                # Combo está ativo — mostra caminho da layer selecionada no line edit
                layer = self._combo.currentLayer()
                if layer:
                    src = layer.source()
                    if src:
                        # Extrai path do source (remove |layername=...)
                        layer_path = src.split("|")[0] if "|" in src else src
                        self._edit.setText(layer_path)
                        if not self._updating_display:
                            self._sync_from_edit()
                    else:
                        self._edit.setText("")
                else:
                    self._edit.setText("")
                self._stack.setCurrentIndex(1)  # mostra combo
            else:
                # Line edit está ativo
                if not self._selected_list:
                    self._edit.setText("")
                elif not self._multiple:
                    self._edit.setText(self._selected_list[0])
                else:
                    self._edit.setText("; ".join(self._selected_list))
                self._stack.setCurrentIndex(0)  # mostra line edit
        finally:
            self._updating_display = False

    # ══════════════════════════════════════════════════════════════════
    # Handlers
    # ══════════════════════════════════════════════════════════════════

    def _on_edit_text_changed(self, text: str):
        """Sincroniza digitação manual com estado interno."""
        if self._updating_display:
            return
        if not text:
            self._root_path = ""
            self._selected_list = []
            self._emit_path_change()
            return
        if not self._multiple:
            self._root_path = os.path.dirname(
                text) if os.path.isfile(text) else text
            self._selected_list = [text]
            self._emit_path_change()
        else:
            parts = [p.strip() for p in text.replace("; ", ";").split(";")]
            parts = [p for p in parts if p]
            if parts:
                first = parts[0]
                self._root_path = os.path.dirname(
                    first) if os.path.isfile(first) else first
                self._selected_list = parts
            else:
                self._root_path = ""
                self._selected_list = []
            self._emit_path_change()

    def _on_combo_layer_changed(self, index: int):
        """Quando a layer no combo muda, sincroniza o path."""
        if self._updating_display:
            return
        layer = self._combo.currentLayer()
        if layer:
            src = layer.source()
            if src:
                layer_path = src.split("|")[0] if "|" in src else src
                self._root_path = os.path.dirname(
                    layer_path) if os.path.isfile(layer_path) else layer_path
                self._selected_list = [layer_path]
                self._emit_path_change()

    def _sync_from_edit(self):
        """Sincroniza selected_list a partir do texto do line edit."""
        text = self._edit.text()
        if not text:
            self._root_path = ""
            self._selected_list = []
            self._emit_path_change()
            return
        if not self._multiple:
            self._root_path = os.path.dirname(
                text) if os.path.isfile(text) else text
            self._selected_list = [text]
        else:
            parts = [p.strip() for p in text.replace("; ", ";").split(";")]
            parts = [p for p in parts if p]
            if parts:
                first = parts[0]
                self._root_path = os.path.dirname(
                    first) if os.path.isfile(first) else first
                self._selected_list = parts
            else:
                self._root_path = ""
                self._selected_list = []
        self._emit_path_change()

    # ══════════════════════════════════════════════════════════════════
    # Handlers de busca
    # ══════════════════════════════════════════════════════════════════

    def _ensure_line_edit_mode(self):
        """Força o widget para o modo line edit (desativa combo)."""
        self._using_layer_combo = False
        self._update_display()

    def _browse_file(self):
        """Busca arquivo(s) — disparado pelo 🔍."""
        self._logger.info("🔍 clicado", code="COMPLEX_FILE_CLICKED")
        # Força line edit mode
        self._ensure_line_edit_mode()

        if self.on_browse_click:
            self.on_browse_click()

        initial_dir = ExplorerUtils.resolve_initial_dir(
            self._root_path or (
                self._selected_list[0] if self._selected_list else "")
        )

        if self._mode_type == "output":
            path = ExplorerUtils.save_file_dialog(
                "Salvar arquivo", initial_dir, self._file_filter, self,
            )
            if path:
                self._root_path = os.path.dirname(path)
                self._selected_list = [path]
                self._update_display()
                self._emit_path_change()
        elif self._multiple:
            paths = ExplorerUtils.open_files_dialog(
                "Selecionar arquivos", initial_dir, self._file_filter, self,
            )
            if paths:
                self._root_path = os.path.dirname(paths[0]) if paths else ""
                self._selected_list = list(paths)
                self._update_display()
                self._emit_path_change()
        else:
            path = ExplorerUtils.open_file_dialog(
                "Selecionar arquivo", initial_dir, self._file_filter, self,
            )
            if path:
                self._root_path = os.path.dirname(path)
                self._selected_list = [path]
                self._update_display()
                self._emit_path_change()

    def _browse_folder(self):
        """Busca pasta(s) — disparado pelo 📁."""
        self._logger.info("📁 clicado", code="COMPLEX_FOLDER_CLICKED")
        # Força line edit mode
        self._ensure_line_edit_mode()

        if self.on_browse_click:
            self.on_browse_click()

        initial_dir = ExplorerUtils.resolve_initial_dir(
            self._root_path or (
                self._selected_list[0] if self._selected_list else "")
        )

        if self._multiple:
            # Múltiplas pastas: abrir uma por vez? Simples: só single folder por enquanto
            path = ExplorerUtils.select_directory_dialog(
                "Selecionar pasta", initial_dir, self,
            )
            if path:
                self._root_path = path
                self._selected_list = [path]
                self._update_display()
                self._emit_path_change()
        else:
            path = ExplorerUtils.select_directory_dialog(
                "Selecionar pasta", initial_dir, self,
            )
            if path:
                self._root_path = path
                self._selected_list = [path]
                self._update_display()
                self._emit_path_change()

    # ══════════════════════════════════════════════════════════════════
    # ➡️ (explorer — abrir localização no Windows Explorer)
    # ══════════════════════════════════════════════════════════════════

    def _open_explorer(self):
        """Abre o Windows Explorer no diretório do path atual ou da layer."""
        target = None

        # Se está usando layer combo, pega o source da layer
        if self._using_layer_combo:
            layer = self._combo.currentLayer()
            if layer:
                src = layer.source()
                if src:
                    layer_path = src.split("|")[0] if "|" in src else src
                    if os.path.isdir(layer_path):
                        target = layer_path
                    else:
                        target = os.path.dirname(layer_path)
        elif self._selected_list:
            first = self._selected_list[0]
            if os.path.isdir(first):
                target = first
            else:
                target = os.path.dirname(first)

        if not target or not os.path.isdir(target):
            self._logger.info(
                "Nenhum diretório válido para abrir no Explorer",
                code="COMPLEX_EXPLORER_NO_DIR",
            )
            return

        self._logger.info(
            f"Abrindo Explorer em: {target}",
            code="COMPLEX_EXPLORER_OPEN",
            path=target,
        )
        try:
            if os.name == "nt":
                os.startfile(target)  # type: ignore[attr-defined]  # nosec B606  # Abre Explorer do Windows com caminho selecionado pelo usuario

        except Exception as e:
            self._logger.error(
                "Erro ao abrir Explorer",
                code="COMPLEX_EXPLORER_ERROR",
                error=str(e),
            )

    # ══════════════════════════════════════════════════════════════════
    # 📄 (project — só input, alterna entre line edit e combo)
    # ══════════════════════════════════════════════════════════════════

    def _on_project_clicked(self):
        """
        Alterna entre QLineEdit e QgsMapLayerComboBox.
        Quando clica no 📄:
          - Se estava em line edit → vai para combo
          - Se estava em combo → volta para line edit
        """
        self._logger.info("📄 clicado", code="COMPLEX_PROJECT_CLICKED")
        if self._mode_type == "output":
            return  # Não faz sentido em output

        self._using_layer_combo = not self._using_layer_combo

        if self._using_layer_combo:
            # Ativou combo — popula com layer atual se possível
            self._combo.setVisible(True)
            # Tenta selecionar camada baseada no path atual
            current_path = self.path()
            if current_path:
                for layer in QgsProject.instance().mapLayers().values():
                    src = layer.source()
                    if src and current_path in src:
                        self._combo.setLayer(layer)
                        break
            self._combo.setFocus()
        else:
            # Desativou combo — sincroniza o path da layer para o line edit
            self._combo.setVisible(False)
            self._sync_from_combo_back()

        self._update_display()

    def _sync_from_combo_back(self):
        """Quando sai do modo combo, pega o path da layer e coloca no line edit."""
        layer = self._combo.currentLayer()
        if layer:
            src = layer.source()
            if src:
                layer_path = src.split("|")[0] if "|" in src else src
                self._root_path = os.path.dirname(
                    layer_path) if os.path.isfile(layer_path) else layer_path
                self._selected_list = [layer_path]
                self._emit_path_change()

    # ══════════════════════════════════════════════════════════════════
    # 📥 (origin — botão de usar origem)
    # ══════════════════════════════════════════════════════════════════

    def _on_origin_clicked(self):
        """
        Disparado pelo 📥.
        Gera path baseado no parent_selector + suffix + extension + subfolder.
        """
        self._logger.info("📥 clicado (origin)", code="COMPLEX_ORIGIN_CLICKED")
        # Força line edit mode
        self._ensure_line_edit_mode()

        if self.on_origin_click:
            self.on_origin_click()
            return

        # Lógica embutida se não houver callback customizado
        if self._parent_selector:
            parent_paths = self._parent_selector.get_paths()
            if parent_paths:
                self._generate_from_parent(parent_paths)

    def _generate_from_parent(self, parent_paths: list[str]):
        """Gera path de output baseado no parent."""
        if not parent_paths:
            return

        parent_path = parent_paths[0]
        parent_dir = os.path.dirname(parent_path) if os.path.isfile(
            parent_path) else parent_path

        suffix = self._suffix or ""
        extension = self._extension or ""
        subfolder = self._subfolder or ""

        if suffix and extension:
            # parent_dir + parent_stem + suffix.extension
            parent_stem = os.path.splitext(os.path.basename(parent_path))[0]
            ext = extension if extension.startswith(".") else f".{extension}"
            output_name = f"{parent_stem}{suffix}{ext}"
            output_path = os.path.join(parent_dir, output_name)
        else:
            output_path = parent_dir

        if subfolder:
            output_path = os.path.join(parent_dir, subfolder)

        self._root_path = os.path.dirname(
            output_path) if os.path.isfile(output_path) else output_path
        self._selected_list = [output_path]
        self._update_display()
        self._emit_path_change()

        self._logger.info(
            f"Output gerado de parent: {output_path}",
            code="COMPLEX_ORIGIN_PATH",
            parent=parent_path,
            suffix=suffix,
            extension=extension,
            subfolder=subfolder,
        )

    def set_origin_callback(self, callback: Callable[[], None], tooltip: str = ""):
        """Define callback personalizado para o botão 📥."""
        if hasattr(self, '_btn_origin'):
            try:
                self._btn_origin.clicked.disconnect()
            except TypeError:
                pass
            self._btn_origin.clicked.connect(callback)
            if tooltip:
                self._btn_origin.setToolTip(tooltip)

    @property
    def show_origin_button(self) -> bool:
        return self._show_origin_button

    @show_origin_button.setter
    def show_origin_button(self, value: bool) -> None:
        self._show_origin_button = value
        btn = getattr(self, '_btn_origin', None)
        if btn:
            btn.setVisible(value)
            btn.setEnabled(value)

    # ══════════════════════════════════════════════════════════════════
    # 🛠️ (suggested — só output)
    # ══════════════════════════════════════════════════════════════════

    def _on_suggest_clicked(self):
        """
        Gera path de saída: ProjectUtils.get_project_dir() + subfolder + fixed_name.
        Se file=False (folder mode), carrega parent_dir + subfolder.
        """
        self._logger.info("🛠️ clicado (output)",
                          code="COMPLEX_SUGGEST_CLICKED")
        # Força line edit mode
        self._ensure_line_edit_mode()

        if self.on_suggest_click:
            self.on_suggest_click()

        project = QgsProject.instance()
        root_folder = ProjectUtils.get_project_dir(project) if project else ""

        if not root_folder:
            self._logger.warning("Nenhum projeto ativo",
                                 code="COMPLEX_NO_PROJECT")
            return

        if self._subfolder:
            output_dir = os.path.join(root_folder, self._subfolder)
        else:
            output_dir = root_folder

        if self._fixed_name:
            # Se tem extensão e não está no fixed_name, adiciona
            output_name = self._fixed_name
            if self._extension and not os.path.splitext(output_name)[1]:
                ext = self._extension if self._extension.startswith(
                    ".") else f".{self._extension}"
                output_name = f"{output_name}{ext}"
            output_path = os.path.join(output_dir, output_name)
        else:
            output_path = output_dir

        # Se selection_mode == "folder" ou não é file, trata como diretório
        if self._selection_mode == "folder" and not self._fixed_name:
            self._root_path = output_path
            self._selected_list = [output_path]
        else:
            self._root_path = output_dir
            self._selected_list = [output_path]

        self._update_display()
        self._emit_path_change()

        self._logger.info(
            f"Output: {output_path}",
            code="COMPLEX_SUGGEST_PATH",
            root=root_folder,
            subfolder=self._subfolder,
            fixed_name=self._fixed_name,
        )

    # ══════════════════════════════════════════════════════════════════
    # Callback
    # ══════════════════════════════════════════════════════════════════

    def _emit_path_change(self):
        """Dispara callback de path change."""
        if self.on_path_change:
            self.on_path_change(self._selected_list)
        self.pathChanged.emit(self._selected_list)

        # ── CRS: detecção automática se for input ──
        if self._crs_enable and self._mode_type == "input" and self._crs_widget:
            self._auto_detect_crs()

    def _auto_detect_crs(self):
        path = self.path()
        if not path or not os.path.isfile(path):
            return
        """Detecta CRS automaticamente ou pergunta para forçar (só input).
        path = self.path()
        if not path or not os.path.isfile(path):
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".las", ".laz"):
            return

        from utils.las.LasLayerProjection import LasLayerProjection

        crs = LasLayerProjection.get_crs(path)
        if crs:
            self._crs_widget.set_crs(crs)
            self._crs_widget.setToolTip(f"CRS detectado: {crs}")
            return

        from utils.MessageBox import MessageBox
        resposta = MessageBox.show_question(
            f"Não foi possível detectar a projeção do arquivo:\n{path}\n\n"
            "Deseja forçar uma projeção no arquivo?\n"
            "(será criado um arquivo .mdata)",
            title="Projeção não detectada",
            buttons=MessageBox.YES_NO,
            default_button=MessageBox.YES,
        )

        if resposta != MessageBox.YES:
            self._crs_widget.setToolTip("CRS não detectado")
            return

        from resources.widgets.crs.CrsSearchDialog import CrsSearchDialog
        dialog = CrsSearchDialog(
            parent=self.window() if self.window() else self)
        if dialog.exec():
            epsg = dialog.selected_epsg
            if epsg:
                LasLayerProjection.save_mdata(path, epsg)
                self._crs_widget.set_crs(epsg)
                self._crs_widget.setToolTip(f"CRS forçado: {epsg}")"""
        return

    # ══════════════════════════════════════════════════════════════════
    # API Pública
    # ══════════════════════════════════════════════════════════════════

    def get_root_path(self) -> str:
        return self._root_path

    def get_selected_list(self) -> list[str]:
        return self._selected_list.copy()

    def get_paths(self) -> list[str]:
        return self.get_selected_list()

    def get_path(self, index: int = 0) -> str:
        if 0 <= index < len(self._selected_list):
            return self._selected_list[index]
        return ""

    def path(self) -> str:
        return self.get_path(0)

    def paths(self) -> list[str]:
        return self.get_paths()

    def path_type(self) -> str:
        if self._multiple:
            return f"{self._selection_mode}s"
        return self._selection_mode

    def path_count(self) -> int:
        return len(self._selected_list)

    def is_multi(self) -> bool:
        return self._multiple

    def is_single(self) -> bool:
        return not self._multiple

    def is_folder_mode(self) -> bool:
        return self._selection_mode == "folder"

    def is_file_mode(self) -> bool:
        return self._selection_mode == "file"

    def set_path(self, path: str):
        """Define um path único e desativa combo."""
        self._using_layer_combo = False
        if path:
            self._root_path = os.path.dirname(
                path) if os.path.isfile(path) else path
            self._selected_list = [path]
        else:
            self._root_path = ""
            self._selected_list = []
        self._update_display()
        self._emit_path_change()

    def set_paths(self, paths: list[str]):
        """Define múltiplos paths e desativa combo."""
        self._using_layer_combo = False
        if paths:
            first = paths[0]
            self._root_path = os.path.dirname(
                first) if os.path.isfile(first) else first
            self._selected_list = list(paths)
        else:
            self._root_path = ""
            self._selected_list = []
        self._update_display()
        self._emit_path_change()

    def clear(self):
        """Limpa tudo."""
        self._using_layer_combo = False
        self._root_path = ""
        self._selected_list = []
        self._update_display()
        self._emit_path_change()

    def exists(self) -> bool:
        p = self.path()
        return bool(p) and os.path.exists(p)

    def is_file(self) -> bool:
        p = self.path()
        return bool(p) and os.path.isfile(p)

    def is_dir(self) -> bool:
        p = self.path()
        return bool(p) and os.path.isdir(p)

    def basename(self) -> str:
        return os.path.basename(self.path())

    def dirname(self) -> str:
        return os.path.dirname(self.path())

    def extension(self) -> str:
        return os.path.splitext(self.path())[1].lower()

    def has_extension(self, *exts: str) -> bool:
        if not self._selected_list:
            return False
        ext = self.extension()
        return any(ext == e.lower() for e in exts)

    # ── CRS embutido ───────────────────────────────────────────────

    @property
    def crs_widget(self):
        return self._crs_widget

    @property
    def crs(self) -> str:
        if self._crs_widget:
            return self._crs_widget.get_crs()
        return ""

    @crs.setter
    def crs(self, value: str) -> None:
        if self._crs_widget:
            self._crs_widget.set_crs(value)

    # ── Configuração ────────────────────────────────────────────────

    def set_suggested_path(self, suggested_rel_path: str):
        self._suggested_rel_path = suggested_rel_path

    def set_fixed_name(self, fixed_name: str):
        self._fixed_name = fixed_name
        self._logger.info(
            f"fixed_name: '{fixed_name}'",
            code="COMPLEX_FIXED_NAME_CHANGED",
        )

    def set_suggested_callback(self, callback: Callable[[], None], tooltip: str = ""):
        if hasattr(self, '_btn_suggest'):
            try:
                self._btn_suggest.clicked.disconnect()
            except TypeError:
                pass
            self._btn_suggest.clicked.connect(callback)
            if tooltip:
                self._btn_suggest.setToolTip(tooltip)

    def set_origin_config(self, *, suffix: str = "", extension: str = "", subfolder: str = ""):
        """Atualiza configuração do botão 📥."""
        if suffix:
            self._suffix = suffix
        if extension:
            self._extension = extension
        if subfolder:
            self._subfolder = subfolder

    @property
    def file_filter(self) -> str:
        return self._file_filter

    @file_filter.setter
    def file_filter(self, value: str) -> None:
        self._file_filter = value
        self._logger.info(
            f"file_filter: '{value}'", code="COMPLEX_FILE_FILTER_CHANGED")

    @property
    def edit(self) -> QLineEdit:
        return self._edit

    @property
    def combo(self) -> QgsMapLayerComboBox:
        return self._combo

    @property
    def mode_type(self) -> str:
        return self._mode_type

    @property
    def selection_mode(self) -> str:
        return self._selection_mode

    @selection_mode.setter
    def selection_mode(self, value: str) -> None:
        if value in ("file", "folder"):
            self._selection_mode = value

    # ── Dynamic Mode: allow_file / allow_folder ────────────────────

    @property
    def allow_file(self) -> bool:
        return self._allow_file

    @allow_file.setter
    def allow_file(self, value: bool) -> None:
        self._allow_file = value
        btn = getattr(self, '_btn_file', None)
        if btn:
            btn.setVisible(value)
            btn.setEnabled(value)

    @property
    def allow_folder(self) -> bool:
        return self._allow_folder

    @allow_folder.setter
    def allow_folder(self, value: bool) -> None:
        self._allow_folder = value
        btn = getattr(self, '_btn_folder', None)
        if btn:
            btn.setVisible(value)
            btn.setEnabled(value)

    def set_mode(self, *, allow_file: Optional[bool] = None, allow_folder: Optional[bool] = None, selection_mode: Optional[str] = None):
        if allow_file is not None:
            self.allow_file = allow_file
        if allow_folder is not None:
            self.allow_folder = allow_folder
        if selection_mode is not None:
            self.selection_mode = selection_mode
        if self._selection_mode == "file" and not self._allow_file:
            self._selection_mode = "folder"
        if self._selection_mode == "folder" and not self._allow_folder:
            self._selection_mode = "file"
        if hasattr(self, '_btn_file'):
            self._btn_file.setToolTip(
                "Selecionar arquivos" if self._multiple else "Selecionar arquivo"
            )
        if hasattr(self, '_btn_folder'):
            self._btn_folder.setToolTip(
                "Selecionar pastas" if self._multiple else "Selecionar pasta"
            )
        self._logger.info(
            f"Modo alterado: file={self._allow_file}, folder={self._allow_folder}, mode={self._selection_mode}",
            code="COMPLEX_MODE_CHANGED",
        )

    @property
    def using_layer_combo(self) -> bool:
        """Retorna se o widget está usando QgsMapLayerComboBox."""
        return self._using_layer_combo

    @property
    def current_layer(self):
        """Retorna a camada selecionada no combo, ou None."""
        return self._combo.currentLayer()
