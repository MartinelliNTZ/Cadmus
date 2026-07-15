# -*- coding: utf-8 -*-
class CoffeTheme:

    # ==========================================================
    # UTILITÁRIO DE COR
    # ==========================================================

    @staticmethod
    def rgba(hex_color: str, alpha: int) -> str:
        """
        Converte HEX + alpha para rgba().
        Exemplo:
        rgba("#a6784f", 120) -> "rgba(166,120,79,120)"
        """

        hex_color = hex_color.lstrip("#")

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return f"rgba({r},{g},{b},{alpha})"

    # ==========================================================
    # CORES BASE (TEMA)
    # ==========================================================

    COLOR_PRIMARY = "#a6784f"
    COLOR_PRIMARY_LIGHT = "#c1936b"
    COLOR_PRIMARY_DARK = "#6b4a2f"

    COLOR_BACKGROUND_MAIN = "rgba(16, 14, 12, 255)"
    COLOR_BACKGROUND_PANEL = "rgba(34, 30, 26, 255)"
    COLOR_BACKGROUND_SOFT = "rgba(26, 22, 20, 220)"
    COLOR_BACKGROUND_TRANSPARENT = "transparent"

    COLOR_TEXT_PRIMARY = "#ece6df"
    COLOR_TEXT_SECONDARY = "#d2bca6"
    COLOR_BUTTON_TEXT = "#ffffff"

    COLOR_BORDER = "#a6784f"

    COLOR_CHECKBOX_BG = "#5a5a5a"

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
    FONT_SIZE_BIG = "12pt"
    FONT_SIZE_NORMAL = "9pt"
    FONT_SIZE_SMALL = "8pt"

    # ==========================================================
    # DIMENSÕES BASE
    # ==========================================================

    STANDARD_SIZE = 12

    INPUT_HEIGHT = STANDARD_SIZE
    BUTTON_HEIGHT = STANDARD_SIZE
    ITEM_HEIGHT = STANDARD_SIZE
    CHECKBOX_SIZE = STANDARD_SIZE
    RADIO_SIZE = STANDARD_SIZE
    COLOR_BUTTON_HEX_HEIGHT = 18
    COLOR_BUTTON_PICKER_HEIGHT = 18
    COLOR_BUTTON_COPY_SIZE = 20
    COLOR_BUTTON_COPY_ICON_SIZE = 10

    # ==========================================================
    # ESPAÇAMENTOS
    # ==========================================================

    LAYOUT_V_SPACING = 2
    LAYOUT_H_SPACING = 2
    CONTENT_PADDING = 2

    # ==========================================================
    # CHECKBOX
    # ==========================================================

    CHECKBOX_BORDER_RADIUS = 3
    CHECKBOX_BORDER_WIDTH = 1
    CHECKBOX_SPACING = 6

    # ==========================================================
    # RADIO BUTTON
    # ==========================================================

    RADIO_BORDER_RADIUS = 6

    # ==========================================================
    # BOTÕES
    # ==========================================================

    BUTTON_BORDER_RADIUS = 6
    BUTTON_PADDING = "4px 12px"

    # ==========================================================
    # INPUTS
    # ==========================================================

    INPUT_BORDER_RADIUS = 4
    INPUT_PADDING = "2px 8px"
