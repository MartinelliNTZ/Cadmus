# -*- coding: utf-8 -*-
"""
Centraliza o tema visual do plugin.
Responsável apenas por DEFINIR estilos, não por aplicar lógica.
"""


from .CoffeTheme import CoffeTheme


class BaseStyles:
    """
    Estilos base reutilizáveis entre diversos widgets.
    """
        # ==========================================================
    # TEMA (CORES)
    # ==========================================================

    COLOR_PRIMARY = CoffeTheme.COLOR_PRIMARY
    COLOR_PRIMARY_LIGHT = CoffeTheme.COLOR_PRIMARY_LIGHT
    COLOR_PRIMARY_DARK = CoffeTheme.COLOR_PRIMARY_DARK

    COLOR_BACKGROUND_MAIN = CoffeTheme.COLOR_BACKGROUND_MAIN
    COLOR_BACKGROUND_PANEL = CoffeTheme.COLOR_BACKGROUND_PANEL
    COLOR_BACKGROUND_SOFT = CoffeTheme.COLOR_BACKGROUND_SOFT
    COLOR_BACKGROUN_TRANSPARENT = CoffeTheme.COLOR_BACKGROUND_TRANSPARENT

    COLOR_TEXT_PRIMARY = CoffeTheme.COLOR_TEXT_PRIMARY
    COLOR_TEXT_SECONDARY = CoffeTheme.COLOR_TEXT_SECONDARY
    COLOR_BUTTON_TEXT = CoffeTheme.COLOR_BUTTON_TEXT

    COLOR_BORDER = CoffeTheme.COLOR_BORDER

    COLOR_APPBAR_INFO_BG = CoffeTheme.COLOR_APPBAR_INFO_BG
    COLOR_APPBAR_INFO_BG_HOVER = CoffeTheme.COLOR_APPBAR_INFO_BG_HOVER

    COLOR_LIST_SELECTION = CoffeTheme.COLOR_LIST_SELECTION
    COLOR_LIST_SELECTION_HOVER = CoffeTheme.COLOR_LIST_SELECTION_HOVER

    COLOR_COLLAPSIBLE_HEADER_START = CoffeTheme.COLOR_COLLAPSIBLE_HEADER_START
    COLOR_COLLAPSIBLE_HEADER_END = CoffeTheme.COLOR_COLLAPSIBLE_HEADER_END

    COLOR_COLLAPSIBLE_HEADER_HOVER_START = CoffeTheme.COLOR_COLLAPSIBLE_HEADER_HOVER_START
    COLOR_COLLAPSIBLE_HEADER_HOVER_END = CoffeTheme.COLOR_COLLAPSIBLE_HEADER_HOVER_END
    COLOR_CHECKBOX_BG = CoffeTheme.COLOR_CHECKBOX_BG

    # ==========================================================
    # FONTES
    # ==========================================================

    FONT_FAMILY_DEFAULT = CoffeTheme.FONT_FAMILY_DEFAULT
    FONT_SIZE_TITLE = CoffeTheme.FONT_SIZE_TITLE
    FONT_SIZE_NORMAL = CoffeTheme.FONT_SIZE_NORMAL
    FONT_SIZE_SMALL = CoffeTheme.FONT_SIZE_SMALL
    FONT_SIZE_BIG = CoffeTheme.FONT_SIZE_BIG

    # ==========================================================
    # DIMENSÕES
    # ==========================================================

    STANDARD_SIZE = CoffeTheme.STANDARD_SIZE

    INPUT_HEIGHT = CoffeTheme.INPUT_HEIGHT
    BUTTON_HEIGHT = CoffeTheme.BUTTON_HEIGHT

    ITEM_HEIGHT = CoffeTheme.ITEM_HEIGHT
    LAYOUT_V_SPACING = CoffeTheme.LAYOUT_V_SPACING
    LAYOUT_H_SPACING = CoffeTheme.LAYOUT_H_SPACING
    CONTENT_PADDING = CoffeTheme.CONTENT_PADDING    
    CHECKBOX_SIZE = CoffeTheme.CHECKBOX_SIZE
    RADIO_SIZE = CoffeTheme.RADIO_SIZE

    # ==========================================================
    # CHECKBOX
    # ==========================================================

    CHECKBOX_BORDER_RADIUS = CoffeTheme.CHECKBOX_BORDER_RADIUS
    CHECKBOX_BORDER_WIDTH = CoffeTheme.CHECKBOX_BORDER_WIDTH
    CHECKBOX_SPACING = CoffeTheme.CHECKBOX_SPACING

    # ==========================================================
    # RADIO BUTTON
    # ==========================================================

    RADIO_BORDER_RADIUS = CoffeTheme.RADIO_BORDER_RADIUS

    # ==========================================================
    # BOTÕES
    # ==========================================================

    BUTTON_BORDER_RADIUS = CoffeTheme.BUTTON_BORDER_RADIUS
    BUTTON_PADDING = CoffeTheme.BUTTON_PADDING

    # ==========================================================
    # INPUTS
    # ==========================================================

    INPUT_BORDER_RADIUS = CoffeTheme.INPUT_BORDER_RADIUS
    INPUT_PADDING = CoffeTheme.INPUT_PADDING

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def spinbox():
        return f"""
        QSpinBox,
        QDoubleSpinBox {{
            background: {BaseStyles.COLOR_BACKGROUND_PANEL};
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            font-family: {BaseStyles.FONT_FAMILY_DEFAULT};
            font-size: {BaseStyles.FONT_SIZE_NORMAL};
            border: 1px solid {BaseStyles.COLOR_BORDER};
            border-radius: {BaseStyles.INPUT_BORDER_RADIUS}px;
            min-height: {BaseStyles.INPUT_HEIGHT}px;
            padding: 2px 4px;
            padding-right: 18px;
        }}

        QSpinBox:hover,
        QDoubleSpinBox:hover {{
            border: 1px solid {BaseStyles.COLOR_PRIMARY_LIGHT};
        }}

        QSpinBox:focus,
        QDoubleSpinBox:focus {{
            border: 1px solid {BaseStyles.COLOR_PRIMARY};
        }}

        QSpinBox:disabled,
        QDoubleSpinBox:disabled {{
            background: {BaseStyles.COLOR_BACKGROUND_SOFT};
            color: {BaseStyles.COLOR_TEXT_SECONDARY};
        }}

        QSpinBox::up-button,
        QSpinBox::down-button,
        QDoubleSpinBox::up-button,
        QDoubleSpinBox::down-button {{
            width: 16px;
            height: {BaseStyles.INPUT_HEIGHT}px;
            border-radius: 2px;
            border-left: 1px solid {BaseStyles.COLOR_BORDER};
            background: {BaseStyles.COLOR_PRIMARY};
            padding: 0px;
            margin: 0px;
        }}

        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover,
        QDoubleSpinBox::down-button:hover {{
            background: {BaseStyles.COLOR_PRIMARY_LIGHT};
        }}

        QSpinBox::up-button:pressed,
        QSpinBox::down-button:pressed,
        QDoubleSpinBox::up-button:pressed,
        QDoubleSpinBox::down-button:pressed {{
            background: {BaseStyles.COLOR_PRIMARY_DARK};
        }}
        """
    @staticmethod
    def checkbox():
        return f"""
        QCheckBox {{
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            font-family: {BaseStyles.FONT_FAMILY_DEFAULT};
            font-size: {BaseStyles.FONT_SIZE_NORMAL};
            spacing: {BaseStyles.CHECKBOX_SPACING}px;
        }}

        QCheckBox::indicator {{
            width: {BaseStyles.CHECKBOX_SIZE}px;
            height: {BaseStyles.CHECKBOX_SIZE}px;
            border-radius: {BaseStyles.CHECKBOX_BORDER_RADIUS}px;
            border: {BaseStyles.CHECKBOX_BORDER_WIDTH}px solid {BaseStyles.COLOR_BORDER};
            background: {BaseStyles.COLOR_CHECKBOX_BG};
        }}

        QCheckBox::indicator:checked {{
            background: {BaseStyles.COLOR_PRIMARY};
            border: {BaseStyles.CHECKBOX_BORDER_WIDTH}px solid {BaseStyles.COLOR_PRIMARY_DARK};
        }}
        """

    @staticmethod
    def radio_button():
        return f"""
        QRadioButton {{
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            font-family: {BaseStyles.FONT_FAMILY_DEFAULT};
            font-size: {BaseStyles.FONT_SIZE_NORMAL};
            spacing: {BaseStyles.CHECKBOX_SPACING}px;
        }}

        QRadioButton::indicator {{
            width: {BaseStyles.RADIO_SIZE}px;
            height: {BaseStyles.RADIO_SIZE}px;
            border-radius: {BaseStyles.RADIO_BORDER_RADIUS}px;
            border: {BaseStyles.CHECKBOX_BORDER_WIDTH}px solid {BaseStyles.COLOR_BORDER};
            background: {BaseStyles.COLOR_BACKGROUND_PANEL};
        }}

        QRadioButton::indicator:checked {{
            background: {BaseStyles.COLOR_PRIMARY};
        }}
        """

    @staticmethod
    def button():
        
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {BaseStyles.COLOR_PRIMARY},
                stop:1 {BaseStyles.COLOR_PRIMARY_DARK});
            color: {BaseStyles.COLOR_BUTTON_TEXT};
            border: 1px solid {BaseStyles.COLOR_PRIMARY_DARK};
            border-radius: {BaseStyles.BUTTON_BORDER_RADIUS}px;
            padding: {BaseStyles.BUTTON_PADDING};
            min-height: {BaseStyles.BUTTON_HEIGHT}px;
        }}

        QPushButton:hover {{
            background: {BaseStyles.COLOR_PRIMARY_LIGHT};
        }}

        QPushButton:pressed {{
            background: {BaseStyles.COLOR_PRIMARY_DARK};
        }}

        QPushButton:disabled {{
            background: {BaseStyles.COLOR_BACKGROUND_SOFT};
            color: {BaseStyles.COLOR_TEXT_SECONDARY};
        }}
        """

    @staticmethod
    def label():
        return f"""
        QLabel {{
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            font-family: {BaseStyles.FONT_FAMILY_DEFAULT};
            font-size: {BaseStyles.FONT_SIZE_NORMAL};
        }}
        """

    @staticmethod
    def input():
        return f"""
        QLineEdit,
        QSpinBox,
        QDoubleSpinBox {{
            background: {BaseStyles.COLOR_BACKGROUND_PANEL};
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            border: 1px solid {BaseStyles.COLOR_BORDER};
            border-radius: {BaseStyles.INPUT_BORDER_RADIUS}px;
            padding: {BaseStyles.INPUT_PADDING};
            min-height: {BaseStyles.INPUT_HEIGHT}px;
        }}

        QLineEdit:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus {{
            border: 1px solid {BaseStyles.COLOR_PRIMARY};
        }}
        """

    @staticmethod
    def map_layer_combobox():
        return f"""
        QgsMapLayerComboBox {{
            background: {BaseStyles.COLOR_BACKGROUND_PANEL};
            color: {BaseStyles.COLOR_TEXT_PRIMARY};
            border: 1px solid {BaseStyles.COLOR_BORDER};
            border-radius: {BaseStyles.INPUT_BORDER_RADIUS}px;
            padding: {BaseStyles.INPUT_PADDING};
            min-height: {BaseStyles.INPUT_HEIGHT}px;
        }}

        QgsMapLayerComboBox:hover {{
            border: 1px solid {BaseStyles.COLOR_PRIMARY_LIGHT};
        }}
        """

    @staticmethod
    def scroll_area():
        return f"""
        QScrollArea {{
            border: none;
            background: transparent;
        }}

        QScrollBar:vertical {{
            width: 8px;
            background: transparent;
        }}

        QScrollBar::handle:vertical {{
            background: {BaseStyles.COLOR_PRIMARY};
            border-radius: 4px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {BaseStyles.COLOR_PRIMARY_LIGHT};
        }}
        """
