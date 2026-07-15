# -*- coding: utf-8 -*-
"""
GridComplexSelector — Grade de ComplexSelectors configurados por dicionário,
com suporte a linking entre selectores e dynamic_parent.

Cada ComplexSelector com parent tem seu próprio botão 📥 nativo,
ao invés de um botão global por linha.

Uso:
    grid = GridComplexSelector({
        "Entrada": {
            "file_filter": "LAS/LAZ (*.las *.laz)",
            "mode_type": "input",
            "allow_file": True,
            "allow_folder": True,
            "multiple": False,
            "show_project_button": True,
        },
        "Saída": {
            "mode_type": "output",
            "parent": "Entrada",
            "dynamic_parent": True,
            "allow_file": True,
            "allow_folder": True,
            "fixed_name": "resultado.gpkg",
            "show_suggest_button": True,
            "suffix": "_converted",
            "extension": "gpkg",
            "subfolder": "output",
        },
    })

    grid["Entrada"].path()
    grid["Entrada"].get_root_path()
    grid["Entrada"].path_type()
    grid.use_origin("Saída")

    grid.set_on_input_changed(meu_callback)  # callback(label, paths)
    grid.set_on_changed("Entrada", meu_callback)  # callback(paths)
"""

from __future__ import annotations

import os
from functools import partial
from typing import Callable, Optional

from qgis.PyQt.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QLineEdit, QGroupBox,
)
from qgis.PyQt.QtCore import QTimer

from ....resources.widgets.simple.ComplexSelector import ComplexSelector

from ....core.config.LogUtils import LogUtils


class GridComplexSelector(QWidget):
    """
    Grade de ComplexSelectors configurados por dicionário.

    Suporta mode_type="input"/"output" com parent linking.
    dynamic_parent: filho adapta selection_mode conforme o pai.
    Cada output com parent exibe seu próprio botão 📥 nativo.

    Suporta parent cross-grid: parent="grid1.selector1" faz busca
    por um selector de outro GridComplexSelector registrado.
    """

    _KEYS_RESERVED = frozenset({
        "label_text", "parent", "mode_type",
        "dynamic_parent", "suffix", "extension",
        "show_origin_button",
    })

    # Registro global de grids, para suporte a parent cross-grid
    _grid_registry: dict[str, "GridComplexSelector"] = {}

    def __init__(
        self,
        specs: dict[str, dict],
        title: Optional[str] = None,
        columns: int = 1,
        grid_id: str = "",  # Identificador para cross-grid parent
        parent=None,
    ):
        super().__init__(parent)

        self._logger = LogUtils(
            tool="GridComplexSelector", class_name="GridComplexSelector")

        self._grid_id = grid_id or ""
        self._selectors: dict[str, ComplexSelector] = {}
        self._link_meta: dict[str, dict] = {}
        self._self_generated: dict[str, bool] = {}
        # Armazena callbacks registrados via set_on_path_change()
        self._user_callbacks: dict[str, Optional[Callable]] = {}
        # Flag para evitar loop de regeneração
        self._generating_output: set[str] = set()

        self._build(specs, title, columns)

        # Registra no registry global
        if self._grid_id:
            GridComplexSelector._grid_registry[self._grid_id] = self

    def __del__(self):
        """Limpa registro ao destruir."""
        if self._grid_id and self._grid_id in GridComplexSelector._grid_registry:
            del GridComplexSelector._grid_registry[self._grid_id]

    # ══════════════════════════════════════════════════════════════════
    # API Pública para Callbacks
    # ══════════════════════════════════════════════════════════════════

    def set_on_input_changed(self, callback: Optional[Callable[[str, list[str]], None]]):
        """
        Registra callback para quando QUALQUER selector de entrada mudar.
        O plugin NÃO precisa saber de parent-child relationships.
        """
        for label, selector in self._selectors.items():
            meta = self._link_meta.get(label, {})
            if meta.get("mode_type") == "output":
                continue
            if callback is not None:
                self._user_callbacks[label] = lambda paths, _label=label: callback(
                    _label, paths)
            else:
                self._user_callbacks[label] = None
            if not getattr(selector, '_grid_wrapper_installed', False):
                self._install_user_callback_wrapper(label, selector)

    def set_on_changed(self, label: str, callback: Optional[Callable[[list[str]], None]]):
        """
        Registra callback para quando o path de um selector específico mudar.
        Não quebra o chaining interno de linking/dynamic_parent.
        """
        self._user_callbacks[label] = callback
        selector = self._selectors.get(label)
        if selector and not getattr(selector, '_grid_wrapper_installed', False):
            self._install_user_callback_wrapper(label, selector)

    def _install_user_callback_wrapper(self, label: str, selector: ComplexSelector):
        """Instala um wrapper em on_path_change que preserva o chaining."""
        original_cb = selector.on_path_change

        def wrapper(paths: list[str]):
            if original_cb:
                original_cb(paths)
            user_cb = self._user_callbacks.get(label)
            if user_cb and user_cb is not original_cb:
                user_cb(paths)

        selector.on_path_change = wrapper
        selector._grid_wrapper_installed = True  # type: ignore[attr-defined]

    # ══════════════════════════════════════════════════════════════════
    # Build
    # ══════════════════════════════════════════════════════════════════

    def _build(self, specs: dict[str, dict], title: Optional[str], columns: int):
        if title:
            container = QGroupBox(title)
            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)
            outer.addWidget(container)
            inner = QVBoxLayout(container)
        else:
            inner = QVBoxLayout(self)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.setSpacing(6)

        inner.setSpacing(6)
        inner.setContentsMargins(6, 6, 6, 6)

        if columns <= 1:
            for label, kwargs in specs.items():
                selector = self._build_selector(label, kwargs)
                inner.addWidget(selector)
        else:
            grid = QGridLayout()
            grid.setSpacing(6)
            grid.setContentsMargins(6, 6, 6, 6)
            for i, (label, kwargs) in enumerate(specs.items()):
                row = i // columns
                col = i % columns
                selector = self._build_selector(label, kwargs)
                grid.addWidget(selector, row, col)
            grid_wrapper = QWidget()
            grid_wrapper.setLayout(grid)
            inner.addWidget(grid_wrapper)

    def _resolve_parent_selector(self, parent_key: str) -> Optional[ComplexSelector]:
        """
        Resolve um parent selector que pode ser:
        - Um label local: "Entrada"
        - Um label cross-grid: "grid1.selector1"
        """
        if parent_key in self._selectors:
            return self._selectors[parent_key]

        # Cross-grid: "grid_id.selector_label"
        if "." in parent_key:
            grid_id, sel_label = parent_key.split(".", 1)
            grid = GridComplexSelector._grid_registry.get(grid_id)
            if grid:
                return grid.get(sel_label)

        self._logger.warning(
            f"Parent '{parent_key}' não encontrado (local nem cross-grid)",
            code="GRID_PARENT_NOT_FOUND",
        )
        return None

    def _build_selector(self, label: str, kwargs: dict) -> ComplexSelector:
        """Constrói um ComplexSelector com show_origin_button se for output com parent."""
        mode_type = kwargs.get("mode_type", "input")
        parent_key = kwargs.get("parent", "")
        dynamic_parent = kwargs.get("dynamic_parent", False)

        suffix = kwargs.get("suffix", "")
        extension = kwargs.get("extension", "")
        subfolder = kwargs.get("subfolder", "")
        fixed_name = kwargs.get("fixed_name", "")

        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in self._KEYS_RESERVED
        }

        if "label_text" not in clean_kwargs:
            clean_kwargs["label_text"] = label

        # Garantir que mode_type seja passado (chave reservada removida acima)
        clean_kwargs["mode_type"] = mode_type

        # Resolve o parent_selector
        parent_selector = None
        if parent_key:
            parent_selector = self._resolve_parent_selector(parent_key)

        # Se for output (com ou sem parent)
        if mode_type == "output":
            clean_kwargs["subfolder"] = subfolder
            clean_kwargs["fixed_name"] = fixed_name
            clean_kwargs["suffix"] = suffix
            clean_kwargs["extension"] = extension
            clean_kwargs["show_suggest_button"] = True
            if parent_key:
                clean_kwargs["parent_selector"] = parent_selector
                # ✅ Botão nativo ativado
                clean_kwargs["show_origin_button"] = True

        selector = ComplexSelector(parent=self, **clean_kwargs)
        self._selectors[label] = selector

        if parent_key:
            self._link_meta[label] = {
                "parent": parent_key,
                "suffix": suffix,
                "extension": extension,
                "subfolder": subfolder,
                "mode_type": mode_type,
                "fixed_name": fixed_name,
                "dynamic_parent": dynamic_parent,
            }
            self._self_generated[label] = False

        if mode_type == "output" and parent_key and parent_selector:
            self._connect_output_listener(
                label, parent_selector, dynamic_parent)
            # Conecta o botão 📥 nativo à lógica de origem
            selector.set_origin_callback(
                partial(self._on_use_origin, label),
                tooltip="Usar mesmo diretório da origem",
            )

        return selector

    # ══════════════════════════════════════════════════════════════════
    # Listener Unificado
    # ══════════════════════════════════════════════════════════════════

    def _connect_output_listener(self, child_label: str, parent_selector: ComplexSelector, dynamic_parent: bool = False):
        """Instala wrapper no parent para reagir a mudanças + dynamic_parent."""
        child_selector = self._selectors.get(child_label)
        if not child_selector:
            return

        original_cb = parent_selector.on_path_change

        def unified_handler(paths: list[str]):
            if original_cb:
                original_cb(paths)
            if dynamic_parent:
                self._apply_dynamic_mode(child_label)
            if child_label not in self._generating_output:
                should_generate = (
                    self._self_generated.get(child_label, False)
                    or not child_selector.get_paths()
                )
                if should_generate:
                    self._generate_output(child_label, paths)

        parent_selector.on_path_change = unified_handler

    # ══════════════════════════════════════════════════════════════════
    # Dynamic Parent
    # ══════════════════════════════════════════════════════════════════

    def _apply_dynamic_mode(self, child_label: str):
        """Adapta selection_mode do filho conforme o pai."""
        meta = self._link_meta.get(child_label)
        if not meta:
            return

        parent_key = meta.get("parent", "")
        parent_selector = self._resolve_parent_selector(parent_key)
        child_selector = self._selectors.get(child_label)

        if not parent_selector or not child_selector:
            return

        parent_type = parent_selector.path_type()
        parent_count = parent_selector.path_count()

        is_single_file = (
            parent_count == 1
            and parent_type in ("file", "files")
        )
        if is_single_file:
            child_selector.set_mode(
                allow_file=True, allow_folder=False, selection_mode="file")
            child_selector.edit.setPlaceholderText("Arquivo de saída")
        else:
            child_selector.set_mode(
                allow_file=False, allow_folder=True, selection_mode="folder")
            child_selector.edit.setPlaceholderText("Pasta de saída")

        self._logger.info(
            f"Dynamic mode aplicado: '{child_label}' → "
            f"file={child_selector.allow_file}, folder={child_selector.allow_folder}, "
            f"mode={child_selector.selection_mode}",
            code="GRID_DYNAMIC_APPLIED",
        )

    # ══════════════════════════════════════════════════════════════════
    # Lógica de linking (USAR ORIGEM)
    # ══════════════════════════════════════════════════════════════════

    def _on_use_origin(self, label: str):
        """Gera output baseado no parent quando 📥 é clicado."""
        meta = self._link_meta.get(label)
        if not meta:
            self._logger.warning(
                f"'{label}' não tem metadados de linking",
                code="GRID_NO_LINK_META",
            )
            return

        parent_key = meta["parent"]
        parent_selector = self._resolve_parent_selector(parent_key)
        if not parent_selector:
            self._logger.warning(
                f"Parent '{parent_key}' não encontrado",
                code="GRID_PARENT_NOT_FOUND",
            )
            return

        parent_paths = parent_selector.get_paths()
        if not parent_paths:
            self._logger.warning(
                f"Parent '{parent_key}' vazio",
                code="GRID_PARENT_EMPTY",
            )
            return

        self._generate_output(label, parent_paths)
        self._self_generated[label] = True

    def set_output_extension(self, label: str, extension: str):
        """
        Atualiza a extensão do output para um selector.
        Sincroniza fixed_name no ComplexSelector para que 🛠️ use extensão atual.
        """
        meta = self._link_meta.get(label)
        if meta:
            meta["extension"] = extension
            selector = self._selectors.get(label)
            if selector:
                selector.set_origin_config(extension=extension)
                fixed_base = meta.get("fixed_name", "")
                if fixed_base and not fixed_base.endswith(f".{extension}"):
                    base_name = os.path.splitext(fixed_base)[0]
                    new_fixed_name = f"{base_name}.{extension}"
                    meta["fixed_name"] = new_fixed_name
                    selector.set_fixed_name(new_fixed_name)

    def set_output_suffix(self, label: str, suffix: str):
        """Atualiza o sufixo do output para um selector."""
        meta = self._link_meta.get(label)
        if meta:
            meta["suffix"] = suffix
            selector = self._selectors.get(label)
            if selector:
                selector.set_origin_config(suffix=suffix)

    # ══════════════════════════════════════════════════════════════════
    # API Pública para manipular selectors
    # ══════════════════════════════════════════════════════════════════

    def set_input_placeholder(self, label: str, placeholder: str):
        """Define o placeholder do QLineEdit de um selector."""
        selector = self._selectors.get(label)
        if selector:
            selector.edit.setPlaceholderText(placeholder)

    def set_input_file_filter(self, label: str, file_filter: str):
        """Define o filtro de arquivo de um selector."""
        selector = self._selectors.get(label)
        if selector:
            selector.file_filter = file_filter

    def suspend_callbacks(self) -> dict[str, Optional[Callable]]:
        """Suspende temporariamente os callbacks para set_path sem re-avaliação."""
        snapshot: dict[str, Optional[Callable]] = {}
        for label in list(self._user_callbacks.keys()):
            snapshot[label] = self._user_callbacks.get(label)
        for label in list(self._user_callbacks.keys()):
            self.set_on_changed(label, None)
        return snapshot

    def resume_callbacks(self, snapshot: dict[str, Optional[Callable]]):
        """Restaura callbacks suspensos por suspend_callbacks()."""
        for label, callback in snapshot.items():
            if callback is not None:
                self._user_callbacks[label] = callback
                selector = self._selectors.get(label)
                if selector and not getattr(selector, '_grid_wrapper_installed', False):
                    self._install_user_callback_wrapper(label, selector)

    def _generate_output(self, label: str, parent_paths: list[str]):
        """Gera path de output baseado no parent.

        O subfolder é usado APENAS pelo 🛠️.
        O 📥 (usar origem) gera o output no MESMO diretório do parent.
        """
        if label in self._generating_output:
            return
        self._generating_output.add(label)

        try:
            meta = self._link_meta.get(label)
            if not meta:
                return

            parent_key = meta["parent"]
            parent_selector = self._resolve_parent_selector(parent_key)
            if not parent_selector:
                return

            selector = self._selectors[label]
            parent_path = parent_paths[0] if parent_paths else ""

            if not parent_path:
                return

            parent_dir = os.path.dirname(parent_path) if os.path.isfile(
                parent_path) else parent_path
            fixed_name = meta.get("fixed_name", "")
            suffix = meta.get("suffix", "")
            extension = meta.get("extension", "")
            dynamic = meta.get("dynamic_parent", False)

            parent_type = parent_selector.path_type()
            parent_count = parent_selector.path_count()

            if dynamic:
                is_single_file = (
                    parent_count == 1
                    and parent_type in ("file", "files")
                )
                if is_single_file:
                    if suffix:
                        parent_stem = os.path.splitext(
                            os.path.basename(parent_path))[0]
                        ext = extension if extension.startswith(
                            ".") else f".{extension}" if extension else ""
                        output_name = f"{parent_stem}{suffix}{ext}" if extension else f"{parent_stem}{suffix}"
                    else:
                        output_name = fixed_name
                    output_path = os.path.join(parent_dir, output_name)
                    selector.set_path(output_path)
                    selector.set_mode(
                        allow_file=True, allow_folder=False, selection_mode="file")
                    selector.edit.setPlaceholderText("Arquivo de saída")
                else:
                    output_path = os.path.join(parent_path, "converted")
                    selector.set_path(output_path)
                    selector.set_mode(
                        allow_file=False, allow_folder=True, selection_mode="folder")
                    selector.edit.setPlaceholderText("Pasta de saída")
            else:
                if parent_selector.is_folder_mode():
                    output_path = os.path.join(parent_path, "converted")
                    selector.set_path(output_path)
                    selector.selection_mode = "folder"
                else:
                    output_name = fixed_name
                    if suffix and extension:
                        parent_stem = os.path.splitext(
                            os.path.basename(parent_path))[0]
                        ext = extension if extension.startswith(
                            ".") else f".{extension}" if extension else ""
                        output_name = f"{parent_stem}{suffix}{ext}"
                    elif extension and not os.path.splitext(fixed_name)[1]:
                        output_name = f"{fixed_name}.{extension}"
                    output_path = os.path.join(parent_dir, output_name)
                    selector.set_path(output_path)
                    selector.selection_mode = "file"

                if selector.is_folder_mode():
                    selector.edit.setPlaceholderText("Pasta de saída")
                else:
                    selector.edit.setPlaceholderText("Arquivo de saída")

            self._self_generated[label] = True

            self._logger.info(
                f"Output gerado '{label}': {selector.path()} "
                f"(dynamic={dynamic}, mode={selector.selection_mode})",
                code="GRID_OUTPUT_GENERATED",
            )
        finally:
            self._generating_output.discard(label)

    # ══════════════════════════════════════════════════════════════════
    # Erro visual
    # ══════════════════════════════════════════════════════════════════

    def show_error(self, label: str, message: str, duration_ms: int = 3000):
        """Exibe erro visual no selector (borda vermelha + tooltip)."""
        selector = self._selectors.get(label)
        if not selector:
            return

        edit = selector.edit
        if not edit:
            return

        if not hasattr(edit, '_saved_stylesheet'):
            edit._saved_stylesheet = edit.styleSheet()

        error_color = "#FF4444"
        radius = 4
        surface_2 = "#2D2D2D"
        text_medium = "#CCCCCC"

        edit.setStyleSheet(
            f"QLineEdit {{ border: 2px solid {error_color}; "
            f"border-radius: {radius}px; "
            f"background-color: {surface_2}; "
            f"color: {text_medium}; "
            f"padding: 2px 6px; }}"
        )
        edit.setToolTip(f"⚠ {message}")

        if duration_ms > 0:
            QTimer.singleShot(duration_ms, lambda: self._clear_error(edit))

    def _clear_error(self, edit: QLineEdit):
        """Limpa o estilo de erro de um QLineEdit."""
        if hasattr(edit, '_saved_stylesheet'):
            edit.setStyleSheet(edit._saved_stylesheet)
        else:
            edit.setStyleSheet("")

    # ══════════════════════════════════════════════════════════════════
    # API Pública
    # ══════════════════════════════════════════════════════════════════

    def get(self, label: str) -> Optional[ComplexSelector]:
        return self._selectors.get(label)

    def __getitem__(self, label: str) -> ComplexSelector:
        return self._selectors[label]

    def __contains__(self, label: str) -> bool:
        return label in self._selectors

    def items(self):
        return self._selectors.items()

    def selectors(self) -> dict[str, ComplexSelector]:
        return self._selectors.copy()

    def paths(self) -> dict[str, str]:
        return {label: sel.path() for label, sel in self._selectors.items()}

    def all_paths(self) -> list[str]:
        return [sel.path() for sel in self._selectors.values() if sel.path()]

    def get_input(self) -> dict[str, ComplexSelector]:
        inputs = {}
        for label, sel in self._selectors.items():
            meta = self._link_meta.get(label, {})
            if meta.get("mode_type") != "output":
                inputs[label] = sel
        return inputs

    def get_output(self) -> dict[str, ComplexSelector]:
        outputs = {}
        for label, sel in self._selectors.items():
            meta = self._link_meta.get(label, {})
            if meta.get("mode_type") == "output":
                outputs[label] = sel
        return outputs

    def use_origin(self, label: str):
        """Dispara a lógica de usar origem para um selector com parent."""
        selector = self._selectors.get(label)
        if selector and hasattr(selector, 'on_origin_click') and selector.on_origin_click:
            selector.on_origin_click()

    def use_origin_all(self):
        """Dispara usar origem para todos os selectors com parent."""
        for label in self._link_meta:
            self.use_origin(label)

    def refresh_links(self):
        """Reaplica output para todos os selectors com parent que têm parent com path."""
        for label, meta in self._link_meta.items():
            parent_key = meta["parent"]
            parent_selector = self._resolve_parent_selector(parent_key)
            if parent_selector and parent_selector.get_paths():
                self._generate_output(label, parent_selector.get_paths())

    def has_linked(self, label: str) -> bool:
        return label in self._link_meta

    def get_parent_of(self, label: str) -> Optional[str]:
        meta = self._link_meta.get(label)
        return meta.get("parent") if meta else None

    def is_dynamic(self, label: str) -> bool:
        """Verifica se um selector tem dynamic_parent ativo."""
        meta = self._link_meta.get(label, {})
        return meta.get("dynamic_parent", False)
