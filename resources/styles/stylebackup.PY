# -*- coding: utf-8 -*-
"""
Centraliza o tema visual do plugin.
Responsável apenas por DEFINIR estilos, não por aplicar lógica.
"""


class Styles:
    # ==========================================================
    # CORES BASE (TEMA)
    # ==========================================================

    COLOR_PRIMARY = "#a6784f"
    COLOR_PRIMARY_LIGHT = "#c1936b"
    COLOR_PRIMARY_DARK = "#6b4a2f"

    COLOR_BACKGROUND_MAIN = "rgba(16, 14, 12, 255)"
    COLOR_BACKGROUND_PANEL = "rgba(34, 30, 26, 255)"
    COLOR_BACKGROUND_SOFT = "rgba(26, 22, 20, 220)"

    COLOR_TEXT_PRIMARY = "#ece6df"
    COLOR_TEXT_SECONDARY = "#d2bca6"
    COLOR_BUTTON_TEXT = "#ffffff"
    COLOR_CHECKBOX_BG = "#5a5a5a"

    COLOR_BORDER = "#a6784f"

    # Cores auxiliares
    COLOR_APPBAR_INFO_BG = "rgba(255, 255, 255, 20)"
    COLOR_APPBAR_INFO_BG_HOVER = "rgba(255, 255, 255, 40)"
    COLOR_LIST_SELECTION = "rgba(166, 120, 79, 120)"
    COLOR_LIST_SELECTION_HOVER = "rgba(166, 120, 79, 60)"
    COLOR_COLLAPSIBLE_HEADER_START = "rgba(106, 74, 47, 100)"
    COLOR_COLLAPSIBLE_HEADER_END = "rgba(166, 120, 79, 100)"
    COLOR_COLLAPSIBLE_HEADER_HOVER_START = "rgba(106, 74, 47, 140)"
    COLOR_COLLAPSIBLE_HEADER_HOVER_END = "rgba(166, 120, 79, 140)"


    # ==========================================================
    # FONTES
    # ==========================================================

    FONT_FAMILY_DEFAULT = "'Segoe UI', Arial, sans-serif"
    FONT_SIZE_TITLE = "20pt"
    FONT_SIZE_NORMAL = "9.0pt"
    FONT_SIZE_SMALL = "8.0pt"

    # ==========================================================
    # LAYOUT SPACING (DIMENSÕES PADRÃO)
    # ==========================================================
    
    STANDARD_SIZE = 12  # Valor base para tamanhos de componentes (px)

    ITEM_HEIGHT = STANDARD_SIZE  # Altura padrão de cada item (px)
    ITEM_SPACING = 2  # Espaçamento entre itens no layout (px)
    ITEM_MARGIN = 2   # Margin interna padrão (px)
    CONTENT_PADDING = 2  # Padding do conteúdo (px)
    LAYOUT_H_SPACING = 0  # Spacing horizontal padrão (px)
    LAYOUT_V_SPACING = 2  # Spacing vertical padrão (px)

    # ==========================================================
    # TAMANHOS DE WIDGETS (ALTURA PADRÃO)
    # ==========================================================
    
    INPUT_HEIGHT = STANDARD_SIZE  # Altura para QLineEdit, QComboBox (px)
    BUTTON_HEIGHT = STANDARD_SIZE  # Altura para QPushButton (px)
    CHECKBOX_SIZE = STANDARD_SIZE  # Tamanho de checkbox/radio (px)
    RADIO_SIZE = STANDARD_SIZE  # Tamanho de radio button (px)

    # ==========================================================
    # PADRÕES DE ESTILO (PARÂMETROS REUSÁVEIS)
    # ==========================================================
    # Valores utilizados em múltiplos QSS para manter consistência
    CHECKBOX_BORDER_RADIUS = 3
    CHECKBOX_BORDER_WIDTH = 1
    CHECKBOX_SPACING = 6

    RADIO_BORDER_RADIUS = 6

    BUTTON_BORDER_RADIUS = 6
    BUTTON_PADDING = "4px 12px"
    BUTTON_PADDING_SMALL = "4px 10px"
    BUTTON_PADDING_ICON = "2px 6px"

    INPUT_BORDER_RADIUS = 4
    INPUT_PADDING = "2px 8px"

    @staticmethod
    def calc_checkbox_grid_height(num_items: int, items_per_row: int = 1) -> int:
        """
        Calcula a altura de um grid de checkboxes.
        
        Parameters
        ----------
        num_items : int
            Número de checkboxes
        items_per_row : int
            Quantos itens por linha (padrão: 1)
        
        Returns
        -------
        int
            Altura total em px
        """
        rows = (num_items + items_per_row - 1) // items_per_row
        return (rows * Styles.ITEM_HEIGHT) + ((rows - 1) * Styles.LAYOUT_V_SPACING)

    @staticmethod
    def base_checkbox():
        """Estilo base para checkboxes (todos os widgets)."""
        return f"""
        QCheckBox {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            spacing: {Styles.CHECKBOX_SPACING}px;
            background: transparent;
        }}

        QCheckBox::indicator {{
            width: {Styles.CHECKBOX_SIZE}px;
            height: {Styles.CHECKBOX_SIZE}px;
            border-radius: {Styles.CHECKBOX_BORDER_RADIUS}px;
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_BORDER};
            background: {Styles.COLOR_CHECKBOX_BG};
        }}

        QCheckBox::indicator:unchecked {{
            background: {Styles.COLOR_CHECKBOX_BG};
        }}

        QCheckBox::indicator:unchecked:hover {{
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QCheckBox::indicator:checked {{
            background: {Styles.COLOR_PRIMARY};
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_PRIMARY_DARK};
        }}

        QCheckBox::indicator:checked:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QCheckBox::indicator:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_BORDER};
        }}

        QCheckBox:disabled {{
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}

        QCheckBox::indicator:checked:disabled {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}
        """

    @staticmethod
    def base_radio_button():
        """Estilo base para radio buttons (todos os widgets)."""
        return f"""
        QRadioButton {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            spacing: {Styles.CHECKBOX_SPACING}px;
            background: transparent;
        }}

        QRadioButton::indicator {{
            width: {Styles.RADIO_SIZE}px;
            height: {Styles.RADIO_SIZE}px;
            border-radius: {Styles.RADIO_BORDER_RADIUS}px;
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_BORDER};
            background: {Styles.COLOR_BACKGROUND_PANEL};
        }}

        QRadioButton::indicator:unchecked:hover {{
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QRadioButton::indicator:checked {{
            background: {Styles.COLOR_PRIMARY};
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_PRIMARY_DARK};
        }}

        QRadioButton::indicator:checked:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QRadioButton::indicator:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            border: {Styles.CHECKBOX_BORDER_WIDTH}px solid {Styles.COLOR_BORDER};
        }}

        QRadioButton:disabled {{
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}
        """

    @staticmethod
    def base_button():
        """Estilo base para botões (hover/pressed/disabled padronizados)."""
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Styles.COLOR_PRIMARY},
                stop:1 {Styles.COLOR_PRIMARY_DARK});
            color: {Styles.COLOR_BUTTON_TEXT};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_PRIMARY_DARK};
            border-radius: {Styles.BUTTON_BORDER_RADIUS}px;
            padding: {Styles.BUTTON_PADDING};
            min-height: {Styles.BUTTON_HEIGHT}px;
        }}

        QPushButton:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QPushButton:pressed {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}

        QPushButton:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
            border: 1px solid {Styles.COLOR_BORDER};
        }}
        """

    @staticmethod
    def base_label():
        """Estilo base para QLabel."""
        return f"""
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            background: transparent;
        }}
        """

    @staticmethod
    def base_input():
        """Estilo base para campos de entrada e comboboxes."""
        return f"""
        QLineEdit,
        QSpinBox,
        QDoubleSpinBox {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.INPUT_BORDER_RADIUS}px;
            min-height: {Styles.INPUT_HEIGHT}px;
            padding: {Styles.INPUT_PADDING};
        }}

        QLineEdit:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
        }}
        QLineEdit:disabled,
        QSpinBox:disabled,
        QDoubleSpinBox:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}

        QSpinBox::up-button,
        QSpinBox::down-button,
        QDoubleSpinBox::up-button,
        QDoubleSpinBox::down-button {{
            width: 16px;
            height: {Styles.STANDARD_SIZE}px;
            border-radius: 2px;
            border-left: 1px solid {Styles.COLOR_BORDER};
            background: {Styles.COLOR_PRIMARY};
            padding: 0px;
            margin: 0px;
        }}

        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover,
        QDoubleSpinBox::down-button:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QSpinBox::up-button:pressed,
        QSpinBox::down-button:pressed,
        QDoubleSpinBox::up-button:pressed,
        QDoubleSpinBox::down-button:pressed {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}
        """

    @staticmethod
    def base_map_layer_combobox():
        """Estilo base para QgsMapLayerComboBox (utilizado em diversos widgets)."""
        return f"""
        QgsMapLayerComboBox {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.INPUT_BORDER_RADIUS}px;
            min-height: {Styles.INPUT_HEIGHT}px;
            padding: {Styles.INPUT_PADDING};
        }}

        QgsMapLayerComboBox:hover {{
            border: 1px solid {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QgsMapLayerComboBox:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
        }}

        QgsMapLayerComboBox:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}

        QgsMapLayerComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        """

    # ==========================================================
    # ESTILOS GERAIS (APLICAÇÃO INTEIRA)
    # ==========================================================

    @staticmethod
    def main_application():
        """
        Estilo base aplicado no dialog/janela principal.
        """
        return f"""
        #main_container {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {Styles.COLOR_BACKGROUND_MAIN},
                stop:0.5 {Styles.COLOR_BACKGROUND_PANEL},
                stop:1 {Styles.COLOR_BACKGROUND_MAIN});
            border: 3px solid {Styles.COLOR_BORDER};
            border-radius: 8px;
        }}

        {Styles.base_label()}
        {Styles.base_checkbox()}
        {Styles.base_radio_button()}
        {Styles.base_button()}
        {Styles.base_input()}
        {Styles.base_map_layer_combobox()}
        {Styles.scroll_area()}
        """
    @staticmethod
    def app_bar():
        return f"""
        #app_bar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Styles.COLOR_PRIMARY_DARK},
                stop:1 {Styles.COLOR_PRIMARY});
            border-bottom: 1px solid {Styles.COLOR_BORDER};
            border-radius: 8px;
            min-height: 35px;
        }}

        #app_bar_title {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-size: 10.5pt;
            font-weight: bold;
            font-family: {Styles.FONT_FAMILY_DEFAULT};
        }}

        QPushButton#app_bar_btn_run {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Styles.COLOR_PRIMARY},
                stop:1 {Styles.COLOR_PRIMARY_LIGHT});
            color: {Styles.COLOR_BUTTON_TEXT};
            border: 1px solid {Styles.COLOR_PRIMARY_DARK};
            border-radius: 4px;
            padding: 4px 14px;
            font-weight: bold;
            font-size: {Styles.FONT_SIZE_SMALL};
        }}

        QPushButton#app_bar_btn_run:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QPushButton#app_bar_btn_info {{
            background: {Styles.COLOR_APPBAR_INFO_BG};
            color: {Styles.COLOR_TEXT_SECONDARY};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: 4px;
            padding: 4px 12px;
            font-size: {Styles.FONT_SIZE_SMALL};
        }}

        QPushButton#app_bar_btn_info:hover {{
            background: {Styles.COLOR_APPBAR_INFO_BG_HOVER};
        }}

        QPushButton#app_bar_btn_close {{
            background: transparent;
            color: {Styles.COLOR_TEXT_SECONDARY};
            font-size: 14pt;
            border: none;
            padding: 0px 8px;
        }}

        QPushButton#app_bar_btn_close:hover {{
            background: rgba(166, 120, 79, 120);
            color: {Styles.COLOR_BUTTON_TEXT};
            border-radius: 3px;
        }}
        """


    # ==========================================================
    # CONTAINERS / PAINÉIS
    # ==========================================================

    @staticmethod
    def panel():
        """
        Para widgets container (MainLayout, frames, cards, etc.)
        """
        return f"""
        QFrame {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            border-radius: 6px;
            padding: 8px;
        }}
        """
    
    @staticmethod
    def file_selector():
        return f"""
        QLineEdit {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: 4px;
            min-height: {Styles.INPUT_HEIGHT}px;
            padding: 2px 8px;
        }}

        QLineEdit:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}

        {Styles.base_button()}

        QPushButton {{
            border-radius: 4px;
            min-width: {Styles.BUTTON_HEIGHT}px;
            min-height: {Styles.BUTTON_HEIGHT}px;
            padding: 2px 6px;
            font-weight: bold;
        }}
        """
    # ==========================================================
    # SEPARADORES
    # ==========================================================

    @staticmethod
    def separator():
        return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Styles.COLOR_BACKGROUND_PANEL}, 
                stop:0.5 {Styles.COLOR_PRIMARY},
                stop:1 {Styles.COLOR_BACKGROUND_PANEL});
            height: 3px;
            border: none;
            margin: 4px 0px;
        }}
        """


    @staticmethod
    def attribute_selector():
        """
        Estilo exclusivo para AttributeSelectorWidget
        """
        return f"""
        /* =========================
        TÍTULO
        ========================= */
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-weight: bold;
            background: transparent;
        }}

        /* =========================
        CHECKBOX "USAR TODOS"
        ========================= */
        /* Checkboxes are styled via Styles.base_checkbox() */

        /* =========================
        LISTA DE ATRIBUTOS
        ========================= */
        QListWidget {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: 6px;
            padding: 4px;
            outline: none;
        }}

        QListWidget:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}

        QListWidget::item {{
            padding: 4px 6px;
            border-radius: 3px;
        }}

        QListWidget::item:selected {{
            background: {Styles.COLOR_LIST_SELECTION};
            color: {Styles.COLOR_TEXT_PRIMARY};
        }}

        QListWidget::item:hover {{
            background: {Styles.COLOR_LIST_SELECTION_HOVER};
        }}

        /* =========================
        CHECKBOX DOS ITENS
        ========================= */
        QListWidget::indicator {{
            width: 14px;
            height: 14px;
        }}

        QListWidget::indicator:unchecked {{
            border: 1px solid {Styles.COLOR_BORDER};
            background: transparent;
        }}

        QListWidget::indicator:checked {{
            background: {Styles.COLOR_PRIMARY};
            border: 1px solid {Styles.COLOR_PRIMARY_DARK};
        }}

        /* =========================
        BOTÕES (Selecionar / Remover / Inverter)
        ========================= */
        {Styles.base_button()}

        QPushButton {{
            font-size: {Styles.FONT_SIZE_SMALL};
            padding: 4px 10px;
        }}
        """
    # ==========================================================
    # COLLAPSIBLE PARAMETERS WIDGET
    # ==========================================================

    @staticmethod
    def collapsible_parameters():
        """
        Estilo para CollapsibleParametersWidget (parâmetros avançados expansíveis).
        
        Componentes:
        - Header: background degradado, borda inferior
        - Ícone: seta direcionável (→ ↓)
        - Título: bold, texto primário
        - Conteúdo: fundo ligeiramente mais claro
        """
        return f"""
        /* ================== HEADER (SEMPRE VISÍVEL) ================== */
        #collapsible_header {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Styles.COLOR_COLLAPSIBLE_HEADER_START},
                stop:1 {Styles.COLOR_COLLAPSIBLE_HEADER_END});
            border-bottom: 1px solid {Styles.COLOR_BORDER};
            border-radius: 6px 6px 0px 0px;
        }}

        #collapsible_header:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Styles.COLOR_COLLAPSIBLE_HEADER_HOVER_START},
                stop:1 {Styles.COLOR_COLLAPSIBLE_HEADER_HOVER_END});
        }}

        /* ================== ÍCONE DE EXPANSÃO ================== */
        #collapsible_icon {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-weight: bold;
            font-size: 12pt;
            qproperty-alignment: AlignCenter;
        }}

        /* ================== TÍTULO ================== */
        #collapsible_title {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-weight: bold;
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            background: transparent;
        }}

        /* ================== BOTÃO HEADER (INVISÍVEL) ================== */
        #collapsible_header_btn {{
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}

        /* ================== CONTEÚDO (ANIMADO) ================== */
        #collapsible_content {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            border-bottom: 1px solid {Styles.COLOR_BORDER};
            border-left: 1px solid {Styles.COLOR_BORDER};
            border-right: 1px solid {Styles.COLOR_BORDER};
            border-radius: 0px 0px 6px 6px;
        }}
        """

    @staticmethod
    def scroll_area():
        """
        Estilo customizado para QScrollArea.
        Integrado com tema do software.
        """
        return f"""
        QScrollArea {{
            background: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
        }}

        /* ================== SCROLLBAR VERTICAL ================== */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 0px;
            padding: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {Styles.COLOR_PRIMARY};
            border-radius: 4px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QScrollBar::handle:vertical:pressed {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}

        QScrollBar::up-arrow:vertical,
        QScrollBar::down-arrow:vertical {{
            background: none;
        }}

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        /* ================== SCROLLBAR HORIZONTAL ================== */
        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            margin: 0px;
            padding: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {Styles.COLOR_PRIMARY};
            border-radius: 4px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QScrollBar::handle:horizontal:pressed {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}

        QScrollBar::left-arrow:horizontal,
        QScrollBar::right-arrow:horizontal {{
            background: none;
        }}

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
        """

    # ==========================================================
    # PATH SELECTOR WIDGET
    # ==========================================================

    @staticmethod
    def path_selector_widget():
        """
        Estilo para PathSelectorWidget (seletor de pastas/arquivos com radios internos).
        Componentes:
        - Radios: alternancia Pasta ↔ Arquivos
        - QLineEdit: campo de entrada
        - QPushButton: botão browse "..."
        """
        return f"""
        /* ================== RADIOS INTERNOS ================== */
        /* Radio buttons are styled via Styles.base_radio_button() */

        /* ================== INPUT + BOTÃO ================== */
        {Styles.base_input()}

        {Styles.base_button()}

        QPushButton {{
            border-radius: 4px;
            min-width: {Styles.BUTTON_HEIGHT}px;
            min-height: {Styles.BUTTON_HEIGHT}px;
            padding: 2px 6px;
        }}
        """
    # ==========================================================
    # LAYER INPUT WIDGET
    # ===========================================================

    @staticmethod
    def layer_input_widget():
        """
        Estilo para LayerInputWidget (combo de camadas + checkbox de seleção).
        Componentes:
        - QLabel: rótulo
        - QgsMapLayerComboBox: seletor de camada
        - QCheckBox: apenas selecionados
        """
        return f"""
        /* ================== LABEL ================== */
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            background: transparent;
        }}

        /* ================== COMBO BOX ================== */
        QgsMapLayerComboBox {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: 4px;
            padding: 2px 8px;
            min-height: {Styles.INPUT_HEIGHT}px;
        }}

        QgsMapLayerComboBox:hover {{
            border: 1px solid {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QgsMapLayerComboBox:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
            background: {Styles.COLOR_BACKGROUND_PANEL};
        }}

        QgsMapLayerComboBox:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
            border: 1px solid {Styles.COLOR_BORDER};
        }}

        QgsMapLayerComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        /* ================== CHECKBOX "APENAS SELECIONADOS" ================== */
        /* Checkboxes are styled via Styles.base_checkbox() */
        """

    # ==========================================================
    # RADIO BUTTON GRID WIDGET
    # ==========================================================

    @staticmethod
    def radio_button_grid_widget():
        """
        Estilo para RadioButtonGridWidget (grid de radios exclusivos).
        Componentes:
        - QLabel: título opcional
        - QRadioButton: opções em grid
        """
        return f"""
        /* ================== TÍTULO ================== */
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-weight: bold;
            background: transparent;
        }}

        /* ================== RADIOS ================== */
        /* Radio buttons are styled via Styles.base_radio_button() */
        """

    # ==========================================================
    # BOTTOM ACTION BUTTONS WIDGET
    # ==========================================================

    @staticmethod
    def bottom_action_buttons_widget():
        """
        Estilo para BottomActionButtonsWidget (botões inferiores: Run, Close, Info).
        Componentes:
        - QPushButton: Run (ação principal)
        - QPushButton: Close (fechar)
        - QPushButton: Info (informações)
        """
        return f"""
        /* ================== BOTÃO RUN (PRINCIPAL) ================== */
        {Styles.base_button()}

        QPushButton {{
            padding: 4px 16px;
            font-weight: bold;
        }}
        """

    # ==========================================================
    # INPUT FIELDS WIDGET
    # ==========================================================

    @staticmethod
    def input_fields_widget():
        """
        Estilo para InputFieldsWidget (múltiplos campos de input).
        Componentes:
        - QLabel: rótulos
        - QLineEdit: entrada de texto
        - QSpinBox: entrada de números inteiros
        - QDoubleSpinBox: entrada de números decimais
        """
        return f"""
        /* ================== LABEL ================== */
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            background: transparent;
        }}

        {Styles.base_input()}
        """

    # ==========================================================
    # SIMPLE BUTTON WIDGET
    # ==========================================================

    @staticmethod
    def simple_button_widget():
        """Estilo para SimpleButtonWidget (botão simples que ocupa a tela)."""
        return f"""
        {Styles.base_button()}

        QPushButton {{
            padding: 8px 16px;
            min-height: 16px;
            font-weight: bold;
        }}
        """

    @staticmethod
    def label():
        """Estilo para QLabel."""
        return f"""
        QLabel {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            background: transparent;
        }}"""
