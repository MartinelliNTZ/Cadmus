# -*- coding: utf-8 -*-
"""
Centraliza o tema visual do plugin.
Responsável apenas por DEFINIR estilos, não por aplicar lógica.
"""

from .BaseStyles import BaseStyles


class Styles(BaseStyles):

    @staticmethod
    def calc_checkbox_grid_height(num_items: int, items_per_row: int = 1) -> int:
        rows = (num_items + items_per_row - 1) // items_per_row
        return (rows * Styles.ITEM_HEIGHT) + ((rows - 1) * Styles.LAYOUT_V_SPACING)

    # ==========================================================
    # ESTILO GLOBAL
    # ==========================================================

    @staticmethod
    def main_application():

        return f"""
        #main_container {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Styles.COLOR_BACKGROUND_MAIN},
                stop:0.5 {Styles.COLOR_BACKGROUND_PANEL},
                stop:1 {Styles.COLOR_BACKGROUND_MAIN});
            border:3px solid {Styles.COLOR_BORDER};
            border-radius:8px;
        }}

        {Styles.label()}
        {Styles.checkbox()}
        {Styles.radio_button()}
        {Styles.button()}
        {Styles.input()}
        {Styles.map_layer_combobox()}
        {Styles.scroll_area()}
        """

    # ==========================================================
    # APP BAR
    # ==========================================================

    @staticmethod
    def app_bar():

        return f"""
        #app_bar {{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {Styles.COLOR_PRIMARY_DARK},
                stop:1 {Styles.COLOR_PRIMARY});
            border-bottom:1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.RADIO_BORDER_RADIUS};
            min-height:35px;
        }}

        #app_bar_title {{
            color:{Styles.COLOR_TEXT_PRIMARY};
            font-weight:bold;
            font-size:10.5pt;
        }}

        QPushButton#app_bar_btn_run {{
            background:{Styles.COLOR_PRIMARY};
            border:1px solid {Styles.COLOR_PRIMARY_DARK};
            padding:4px 14px;
            font-weight:bold;
            font-size:{Styles.FONT_SIZE_SMALL};
        }}

        QPushButton#app_bar_btn_run:hover {{
            background:{Styles.COLOR_PRIMARY_LIGHT};
        }}

        QPushButton#app_bar_btn_info {{
            background:{Styles.COLOR_APPBAR_INFO_BG};
            color:{Styles.COLOR_TEXT_SECONDARY};
            border:1px solid {Styles.COLOR_BORDER};
        }}

        QPushButton#app_bar_btn_info:hover {{
            background:{Styles.COLOR_APPBAR_INFO_BG_HOVER};
        }}

        QPushButton#app_bar_btn_close {{
            background:transparent;
            border:none;
            font-size:14pt;
        }}
        """

    # ==========================================================
    # PAINÉIS
    # ==========================================================

    @staticmethod
    def panel():

        return f"""
        QFrame {{
            background:{Styles.COLOR_BACKGROUND_SOFT};
            border-radius:6px;
            padding:8px;
        }}
        """

    # ==========================================================
    # SEPARADOR
    # ==========================================================

    @staticmethod
    def separator():

        return f"""
        QFrame {{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {Styles.COLOR_BACKGROUND_PANEL},
                stop:0.5 {Styles.COLOR_PRIMARY},
                stop:1 {Styles.COLOR_BACKGROUND_PANEL});
            height:3px;
            border:none;
            margin:4px 0px;
        }}
        """

    # ==========================================================
    # ATTRIBUTE SELECTOR
    # ==========================================================

    @staticmethod
    def attribute_selector():

        return f"""
        QListWidget {{
            background:{Styles.COLOR_BACKGROUND_PANEL};
            color:{Styles.COLOR_TEXT_PRIMARY};
            border:1px solid {Styles.COLOR_BORDER};
            border-radius:{Styles.RADIO_BORDER_RADIUS}px;
            padding:4px;
        }}

        QListWidget::item:selected {{
            background:{Styles.COLOR_LIST_SELECTION};
        }}

        QListWidget::item:hover {{
            background:{Styles.COLOR_LIST_SELECTION_HOVER};
        }}

        {Styles.button()}
        {Styles.checkbox()}
        /* =========================
        CHECKBOX DOS ITENS
        ========================= */
        QListWidget::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }}

        QListWidget::indicator:unchecked {{
            border: 1px solid {Styles.COLOR_BORDER};
            background: transparent;
        }}

        QListWidget::indicator:checked {{
            background: {Styles.COLOR_PRIMARY};
            border: 1px solid {Styles.COLOR_PRIMARY_DARK};
        }}
        """

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
            font-size: {Styles.FONT_SIZE_BIG};
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
            background:{Styles.COLOR_BACKGROUN_TRANSPARENT};
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

    # ==========================================================
    # WIDGETS
    # ==========================================================

    @staticmethod
    def path_selector_widget():

        return f"""
        {Styles.input()}
        {Styles.button()}
        QPushButton {{
            background: {Styles.COLOR_PRIMARY};
            font-weight: bold;
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            border-radius: 4px;
            min-width: {Styles.BUTTON_HEIGHT}px;
            min-height: {Styles.BUTTON_HEIGHT}px;
            padding: 2px 4px;
        }}
        """

    @staticmethod
    def layer_input_widget():

        return f"""
        {Styles.label()}
        {Styles.map_layer_combobox()}
        {Styles.checkbox()}
        """

    @staticmethod
    def radio_button_grid_widget():

        return f"""
        {Styles.label()}
        {Styles.radio_button()}
        """

    @staticmethod
    def grid_checkboxes():

        return f"""
        {Styles.label()}
        {Styles.checkbox()}
        margin: 4px;
        """

    @staticmethod
    def bottom_action_buttons_widget():

        return f"""
        {Styles.button()}
        QPushButton {{
            padding:4px 16px;
            font-weight:bold;
        }}
        """

    @staticmethod
    def input_fields_widget():

        return f"""
        {Styles.label()}
        {Styles.input()}
        {Styles.spinbox()}
        """

    @staticmethod
    def dropdown_selector_widget():

        return f"""
        {Styles.label()}
        QComboBox {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.INPUT_BORDER_RADIUS}px;
            padding: {Styles.INPUT_PADDING};
            min-height: {Styles.INPUT_HEIGHT}px;
        }}

        QComboBox:hover {{
            border: 1px solid {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QComboBox:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
        }}
        """

    @staticmethod
    def simple_button_widget():

        return f"""
        {Styles.button()}
        QPushButton {{
            padding:8px 16px;
            font-weight:bold;
            margin: 2px ;
        }}
        """

    @staticmethod
    def color_button_widget():

        return f"""
        #color_button_widget QLabel#color_button_title {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-weight: bold;
        }}

        #color_button_widget QLineEdit#color_button_hex_input {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: Consolas, 'Courier New', monospace;
            font-size: {Styles.FONT_SIZE_SMALL};
            padding: 1px 6px;
            background: {Styles.COLOR_BACKGROUND_PANEL};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.INPUT_BORDER_RADIUS}px;
            min-height: {Styles.COLOR_BUTTON_HEX_HEIGHT}px;
            max-height: {Styles.COLOR_BUTTON_HEX_HEIGHT}px;
        }}

        #color_button_widget QLineEdit#color_button_hex_input:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
        }}

        #color_button_widget QPushButton#color_button_copy {{
            padding: 0px;
            margin: 0px;
            min-width: {Styles.COLOR_BUTTON_COPY_SIZE}px;
            max-width: {Styles.COLOR_BUTTON_COPY_SIZE}px;
            min-height: {Styles.COLOR_BUTTON_COPY_SIZE}px;
            max-height: {Styles.COLOR_BUTTON_COPY_SIZE}px;
            border-radius: 4px;
        }}
        """

    @staticmethod
    def project_name_dialog():
        """Retorna o estilo dedicado ao dialogo de nome de projeto."""
        return f"""
        QDialog#project_name_dialog {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: 8px;
        }}

        QDialog#project_name_dialog QLabel#project_name_info_label {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
        }}

        QDialog#project_name_dialog QLabel#project_name_field_label {{
            color: {Styles.COLOR_TEXT_PRIMARY};
            font-family: {Styles.FONT_FAMILY_DEFAULT};
            font-size: {Styles.FONT_SIZE_NORMAL};
            font-weight: bold;
        }}

        QDialog#project_name_dialog QLineEdit#project_name_input {{
            background: {Styles.COLOR_BACKGROUND_PANEL};
            color: {Styles.COLOR_TEXT_PRIMARY};
            border: 1px solid {Styles.COLOR_BORDER};
            border-radius: {Styles.INPUT_BORDER_RADIUS}px;
            padding: {Styles.INPUT_PADDING};
            min-height: {Styles.INPUT_HEIGHT}px;
        }}

        QDialog#project_name_dialog QLineEdit#project_name_input:focus {{
            border: 1px solid {Styles.COLOR_PRIMARY};
        }}

        QDialog#project_name_dialog QPushButton#project_name_btn_ok,
        QDialog#project_name_dialog QPushButton#project_name_btn_cancel {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Styles.COLOR_PRIMARY},
                stop:1 {Styles.COLOR_PRIMARY_DARK});
            color: {Styles.COLOR_BUTTON_TEXT};
            border: 1px solid {Styles.COLOR_PRIMARY_DARK};
            border-radius: {Styles.BUTTON_BORDER_RADIUS}px;
            padding: {Styles.BUTTON_PADDING};
            min-height: {Styles.BUTTON_HEIGHT}px;
            min-width: 84px;
            font-weight: bold;
        }}

        QDialog#project_name_dialog QPushButton#project_name_btn_ok:hover,
        QDialog#project_name_dialog QPushButton#project_name_btn_cancel:hover {{
            background: {Styles.COLOR_PRIMARY_LIGHT};
        }}

        QDialog#project_name_dialog QPushButton#project_name_btn_ok:pressed,
        QDialog#project_name_dialog QPushButton#project_name_btn_cancel:pressed {{
            background: {Styles.COLOR_PRIMARY_DARK};
        }}

        QDialog#project_name_dialog QPushButton#project_name_btn_ok:disabled,
        QDialog#project_name_dialog QPushButton#project_name_btn_cancel:disabled {{
            background: {Styles.COLOR_BACKGROUND_SOFT};
            color: {Styles.COLOR_TEXT_SECONDARY};
        }}
        """
