# -*- coding: utf-8 -*-
"""
MathUtils — Utilitários matemáticos genéricos reutilizáveis
"""

import math
from typing import Any, Optional
from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil


class MathUtils(BaseUtil):
    # -------------------------------------------------------------------
    # Circular (sentido) — mantido para compatibilidade
    # -------------------------------------------------------------------

    TOOL_KEY_UNTRACEABLE: str = BaseUtil.TOOL_KEY_UNTRACEABLE

    @staticmethod
    def angular_diff(a: float, b: float) -> float:
        """Diferença angular mínima em [0, 180]."""
        d = abs(a - b) % 360.0
        return min(d, 360.0 - d)

    @staticmethod
    def circular_variance(angles: list[float]) -> float:
        """
        Variância circular (R-bar), em [0, 1].
        0 = todos iguais (mínima variância), 1 = máxima dispersão.
        Referência: Fisher (1993), Statistical Analysis of Circular Data.
        """
        if not angles:
            return 1.0
        n = len(angles)
        rad = [math.radians(a) for a in angles]
        s = sum(math.sin(r) for r in rad) / n
        c = sum(math.cos(r) for r in rad) / n
        r_bar = math.sqrt(s * s + c * c)
        return 1.0 - r_bar  # 0 = concentrado, 1 = disperso

    @staticmethod
    def circular_mean(angles: list[float]) -> float:
        """Média circular em graus."""
        if not angles:
            return 0.0
        rad = [math.radians(a) for a in angles]
        s = sum(math.sin(r) for r in rad)
        c = sum(math.cos(r) for r in rad)
        return math.degrees(math.atan2(s, c)) % 360.0

    @staticmethod
    def weighted_circular_mean(angles: list[float], weights: list[float]) -> float:
        """
        Média circular ponderada por velocidade.
        Pontos lentos (curva) têm peso menor, pontos rápidos (faixa) dominam.
        """
        if not angles:
            return 0.0
        total_w = sum(weights)
        if total_w == 0:
            return MathUtils.circular_mean(angles)
        rad = [math.radians(a) for a in angles]
        s = sum(math.sin(r) * w for r, w in zip(rad, weights)) / total_w
        c = sum(math.cos(r) * w for r, w in zip(rad, weights)) / total_w
        return math.degrees(math.atan2(s, c)) % 360.0

    # -------------------------------------------------------------------
    # Axial (rumo / direção sem sentido) — 0-180°
    # -------------------------------------------------------------------

    @staticmethod
    def normalize_bearing(azimuth: float) -> float:
        """
        Converte um azimute 0-360° para um rumo (bearing) 0-180°.
        90° e 270° representam a mesma direção axial → 90°.
        """
        az = float(azimuth) % 360.0
        if az > 180.0:
            az = az - 180.0
        return az

    @staticmethod
    def axial_diff(a: float, b: float) -> float:
        """
        Diferença angular mínima entre dois rumos axiais.
        Sempre retorna valor em [0, 90].
        """
        d = abs(a - b) % 180.0
        return min(d, 180.0 - d)

    @staticmethod
    def axial_mean(angles: list[float]) -> float:
        """
        Média axial (direção sem sentido) em graus, 0-180°.
        Algoritmo: dobra os ângulos, calcula média circular, divide por 2.
        Resolve o problema de média entre 1° e 179° não ser 90°.
        """
        if not angles:
            return 0.0
        doubled = [(a * 2.0) % 360.0 for a in angles]
        mean_doubled = MathUtils.circular_mean(doubled)
        return (mean_doubled / 2.0) % 180.0

    @staticmethod
    def weighted_axial_mean(angles: list[float], weights: list[float]) -> float:
        """
        Média axial ponderada em graus, 0-180°.
        """
        if not angles:
            return 0.0
        total_w = sum(weights)
        if total_w == 0:
            return MathUtils.axial_mean(angles)
        doubled = [(a * 2.0) % 360.0 for a in angles]
        rad = [math.radians(d) for d in doubled]
        s = sum(math.sin(r) * w for r, w in zip(rad, weights)) / total_w
        c = sum(math.cos(r) * w for r, w in zip(rad, weights)) / total_w
        mean_doubled = math.degrees(math.atan2(s, c)) % 360.0
        return (mean_doubled / 2.0) % 180.0

    @staticmethod
    def axial_variance(angles: list[float]) -> float:
        """
        Variância axial em [0, 1].
        0 = todos na mesma direção, 1 = máxima dispersão axial.
        """
        if not angles:
            return 1.0
        n = len(angles)
        doubled = [(a * 2.0) % 360.0 for a in angles]
        rad = [math.radians(d) for d in doubled]
        s = sum(math.sin(r) for r in rad) / n
        c = sum(math.cos(r) for r in rad) / n
        r_bar = math.sqrt(s * s + c * c)
        return 1.0 - r_bar

    # -------------------------------------------------------------------
    # Generic numeric parsers and validators
    # -------------------------------------------------------------------

    @staticmethod
    def parse_num(value: Any) -> float:
        """
        Converte qualquer valor para float com suporte a infinitos.

        Aceita: int, float, strings 'inf', '+infinity', '-inf', etc.
        Lança exceção se não for conversível.
        """
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().lower()
        if text in {
            "inf",
            "+inf",
            "infinity",
            "+infinity",
            "float('inf')",
            'float("inf")',
        }:
            return math.inf
        if text in {"-inf", "-infinity", "float('-inf')", 'float("-inf")'}:
            return -math.inf
        return float(text)

    @staticmethod
    def to_float_or_none(value: Any) -> Optional[float]:
        """
        Converte valor para float, retornando None quando não for possível.

        Exemplos:
            42      → 42.0
            '3.14'  → 3.14
            'abc'   → None
            None    → None
        """
        try:
            return MathUtils.parse_num(value)
        except Exception as e:
            logger = LogUtils(
                tool=MathUtils.TOOL_KEY_UNTRACEABLE, class_name="MathUtils"
            )
            logger.debug(f"to_float_or_none: failed with error: {e}")
            return None

    @staticmethod
    def is_zero_value(value: Any) -> bool:
        """
        Verifica se o valor representa zero (numérico ou textual '0').

        Exemplos:
            0.0     → True
            0       → True
            '0'     → True
            '0.0'   → True
            None    → False
            ''      → False
            5       → False
        """
        if value is None:
            return False
        text = str(value).strip()
        if text == "":
            return False
        try:
            return float(text) == 0.0
        except Exception as e:
            logger = LogUtils(
                tool=MathUtils.TOOL_KEY_UNTRACEABLE, class_name="MathUtils"
            )
            logger.debug(f"is_zero_value: failed with error: {e}")
            return text == "0"

    @staticmethod
    def is_missing_value(value: Any) -> bool:
        """
        Indica se o valor deve ser tratado como ausente.

        Exemplos:
            None       → True
            ''         → True
            '   '      → True
            'none'     → True
            'null'     → True
            'nan'      → True
            0          → False
            '0'        → False
            'abc'      → False
        """
        if value is None:
            return True
        text = str(value).strip().lower()
        return text in {"", "none", "null", "nan"}
