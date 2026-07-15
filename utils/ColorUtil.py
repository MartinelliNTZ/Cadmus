# -*- coding: utf-8 -*-
import colorsys
from typing import List

from .BaseUtil import BaseUtil


class ColorUtil(BaseUtil):
    """Gera cores distintas e harmoniosas para grafos com multiplas series."""

    # Paleta base de cores de alto contraste (fallback se houver poucas series)
    BASE_COLORS_HEX = [
        "#FF6384",
        "#36A2EB",
        "#FFCE56",
        "#4BC0C0",
        "#9966FF",
        "#FF9F40",
        "#C9CBCF",
        "#FF6384",
        "#C71585",
        "#00CED1",
        "#FFD700",
        "#32CD32",
        "#FF4500",
        "#6A5ACD",
        "#20B2AA",
    ]

    @staticmethod
    def _hsv_to_hex(h: float, s: float, v: float) -> str:
        """Converte HSV (0-1) para string hex #RRGGBB."""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    @staticmethod
    def _lum(hex_color: str) -> float:
        """Calcula luminancia relativa de uma cor hex (#RRGGBB)."""
        h = hex_color.lstrip("#")
        r, g, b = (
            int(h[0:2], 16) / 255.0,
            int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0,
        )
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @staticmethod
    def _min_luminance_difference(
        colors_hex: List[str], new_color: str, min_diff: float = 0.3
    ) -> bool:
        """Verifica se new_color tem diferenca minima de luminancia contra todas as existentes."""
        new_lum = ColorUtil._lum(new_color)
        for c in colors_hex:
            if abs(ColorUtil._lum(c) - new_lum) < min_diff:
                return False
        return True

    @classmethod
    def generate(
        cls, count: int, saturation: float = 0.75, value: float = 0.85
    ) -> List[str]:
        """Gera `count` cores hex distintas com bom contraste entre si.

        Args:
            count: Numero de cores desejado.
            saturation: Saturação (0-1) – quanto maior, mais vivido.
            value: Valor/Brilho (0-1) – quanto maior, mais claro.

        Returns:
            Lista de strings hex (#RRGGBB) com `count` cores.
        """
        if count <= 0:
            return []
        if count <= len(cls.BASE_COLORS_HEX):
            return cls.BASE_COLORS_HEX[:count]

        # Gera cores via distribuição uniforme no matiz (HSV)
        # com verificação de contraste de luminancia para evitar tons muito proximos.
        colors: List[str] = []
        attempts = 0
        max_attempts = count * 50

        for i in range(count):
            # Distribui os matizes uniformemente no circulo cromatico
            hue = (i * (360.0 / count)) / 360.0
            color = cls._hsv_to_hex(hue, saturation, value)

            # Se houver poucas cores ou a nova cor tiver contraste suficiente, aceita
            if len(colors) < 2 or cls._min_luminance_difference(colors, color, 0.2):
                colors.append(color)
            else:
                # Tenta ajustar ligeiramente matiz e saturacao para obter contraste
                found = False
                for offset in range(1, 20):
                    adj_hue = (hue + offset * 0.05) % 1.0
                    adj_sat = max(
                        0.3, min(1.0, saturation + (-1 if offset % 2 == 0 else 1) * 0.1)
                    )
                    candidate = cls._hsv_to_hex(adj_hue, adj_sat, value)
                    if cls._min_luminance_difference(colors, candidate, 0.2):
                        colors.append(candidate)
                        found = True
                        break
                if not found:
                    colors.append(color)

            attempts += 1
            if attempts > max_attempts:
                break

        # Preenche faltantes com cores da base
        while len(colors) < count:
            colors.append(cls.BASE_COLORS_HEX[len(colors) % len(cls.BASE_COLORS_HEX)])

        return colors[:count]

    @classmethod
    def generate_with_labels(cls, labels: List[str], **kwargs) -> List[str]:
        """Gera cores indexadas pelos labels fornecidos.

        Returns:
            Lista de cores na mesma ordem dos labels.
        """
        return cls.generate(len(labels), **kwargs)

    @classmethod
    def to_rgba(cls, hex_color: str, alpha: float = 0.2) -> str:
        """Converte hex para rgba()."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
