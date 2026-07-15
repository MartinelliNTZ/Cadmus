# -*- coding: utf-8 -*-
"""
Widget de grid de radio buttons com exclusividade.
Permite selecionar apenas uma opção por vez.
"""

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QLabel,
    QButtonGroup,
)

from ...core.config.LogUtils import LogUtils


class RadioButtonGridWidget(QWidget):
    """
    Grid de radio buttons exclusivos (apenas um pode estar selecionado).

    Parâmetros:
    -----------
    items : list[str]
        Lista de itens a exibir como opções de radio

    columns : int
        Número de colunas no grid (padrão: 3)

    title : str
        Título do grupo de radios (opcional)

    checked_index : int
        Índice do item pré-selecionado (-1 para nenhum)

    tool_key : str
        Chave da ferramenta para logging

    parent : QWidget
        Widget pai
    """

    def __init__(
        self,
        *,
        items: list,
        columns: int = 3,
        title: str = None,
        checked_index: int = -1,
        tool_key: str = None,
        parent=None,
    ):
        super().__init__(parent)

        self.items = items or []
        self.columns = max(1, columns)
        self.title = title
        self.tool_key = tool_key
        self.logger = LogUtils(
            tool=self.tool_key or "system", class_name="RadioButtonGridWidget"
        )

        self.logger.info(
            f"Criando RadioButtonGridWidget com {len(self.items)} items, {self.columns} colunas"
        )

        # Grupo de radios para exclusividade
        self.button_group = QButtonGroup(self)
        self.radios = {}

        self._build_ui(checked_index)

    def _build_ui(self, checked_index: int):
        """Constrói a interface com grid de radios."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Título opcional
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("font-weight: bold;")
            main_layout.addWidget(title_label)

        # Grid de radios
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(5)

        row_layout = None
        col_count = 0

        for idx, item in enumerate(self.items):
            # Criar novo radio
            radio = QRadioButton(item)

            # Conectar ao grupo
            self.button_group.addButton(radio, idx)
            self.radios[idx] = radio

            # Pré-selecionar se necessário
            if idx == checked_index:
                radio.setChecked(True)
                self.logger.debug(f"Item '{item}' pré-selecionado (index={idx})")

            # Nova linha se necessário
            if col_count == 0:
                row_layout = QHBoxLayout()
                grid_layout.addLayout(row_layout)

            row_layout.addWidget(radio)
            col_count += 1

            # Quebra de linha ao atingir número de colunas
            if col_count >= self.columns:
                col_count = 0

        # Preencher espaço restante na última linha
        if row_layout and col_count > 0:
            row_layout.addStretch()

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        self.logger.debug("RadioButtonGridWidget construído com sucesso")

    def get_selected_index(self) -> int:
        """Retorna o índice do item selecionado (-1 se nenhum)."""
        button_id = self.button_group.checkedId()
        self.logger.debug(f"get_selected_index() -> {button_id}")
        return button_id

    def get_selected_text(self) -> str:
        """Retorna o texto do item selecionado (vazio se nenhum)."""
        idx = self.get_selected_index()
        if idx >= 0 and idx in self.radios:
            text = self.radios[idx].text()
            self.logger.debug(f"get_selected_text() -> '{text}'")
            return text
        self.logger.debug("get_selected_text() -> '' (nenhum selecionado)")
        return ""

    def set_selected_index(self, index: int):
        """Define qual radio deve estar selecionado."""
        if 0 <= index < len(self.items) and index in self.radios:
            self.radios[index].setChecked(True)
            self.logger.debug(f"set_selected_index({index}) -> '{self.items[index]}'")
        else:
            self.logger.warning(f"set_selected_index({index}) -> índice inválido")

    def set_enabled_all(self, enabled: bool):
        """Habilita/desabilita todos os radios."""
        for radio in self.radios.values():
            radio.setEnabled(enabled)
        self.logger.debug(f"set_enabled_all({enabled})")
