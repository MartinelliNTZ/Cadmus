# -*- coding: utf-8 -*-
"""
Cadmus.logic.attribute_statistics_model
Lógica reutilizável para cálculo de estatísticas de atributos.
Projetado para ser independente da view/GUI e reaproveitável por outras ferramentas.
"""

import math
import statistics
from typing import Dict, List, Iterable, Tuple, Any


def _percentile(sorted_vals: List[float], q: float) -> float:
    """Calcula percentil (interpolado). Retorna nan se lista vazia."""
    if not sorted_vals:
        return float("nan")
    n = len(sorted_vals)
    if n == 1:
        return float(sorted_vals[0])
    pos = (q / 100.0) * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[int(pos)])
    weight = pos - lo
    return float(sorted_vals[lo] * (1 - weight) + sorted_vals[hi] * weight)



class StatsCalculator:
    """
    Classe com métodos estáticos para calcular estatísticas sobre listas numéricas.
    - compute_field_stats: recebe uma lista de valores e um dicionário stats_enabled
      e devolve dicionário label->valor (raw floats ou nan/None).
    - projetada para ser independente do QGIS; aceita listas de float.
    """
    DEFAULT_STATS_ORDER = [
        ("MEAN_ABS", "mean_abs"),
        ("MEAN", "mean"),
        ("STD_POP", "std_pop"),
        ("STD_SAMP", "std_samp"),
        ("MIN", "min"),
        ("MAX", "max"),
        ("RANGE", "range"),
        ("MEDIAN", "median"),
        ("P5", "p5"),
        ("P95", "p95"),
        ("MODE", "mode"),
        ("VARIANCE", "variance"),
        ("SUM", "sum"),
        ("CV", "cv"),
        ("SKEW", "skew"),
        ("KURT", "kurt")
    ]

    @staticmethod
    def compute_field_stats(values: Iterable[float], stats_enabled: Dict[str, bool]) -> Dict[str, float]:
        vals = sorted(float(x) for x in values)
        n = len(vals)
        res = {}

        if n == 0:
            # Todos vazios
            for key, _ in StatsCalculator.DEFAULT_STATS_ORDER:
                if stats_enabled.get(key, False):
                    res[key] = float("nan")
            return res

        # Helpers
        mean = sum(vals) / n
        pvariance = statistics.pvariance(vals) if n >= 1 else float("nan")
        pstdev = statistics.pstdev(vals) if n >= 1 else float("nan")
        # MEDIAN and percentiles
        if stats_enabled.get("P5", False):
            res["P5"] = _percentile(vals, 5)
        if stats_enabled.get("P95", False):
            res["P95"] = _percentile(vals, 95)
        if stats_enabled.get("MEDIAN", False):
            res["MEDIAN"] = _percentile(vals, 50)

        # Now compute conditionally (order doesn't matter)
        if stats_enabled.get("MEAN_ABS", False):
            res["MEAN_ABS"] = sum(abs(x) for x in vals) / n
        if stats_enabled.get("MEAN", False):
            res["MEAN"] = mean
        if stats_enabled.get("STD_POP", False):
            res["STD_POP"] = math.sqrt(sum((x - mean) ** 2 for x in vals) / n)
        if stats_enabled.get("STD_SAMP", False):
            res["STD_SAMP"] = math.sqrt(sum((x - mean) ** 2 for x in vals) / (n - 1)) if n > 1 else float("nan")
        if stats_enabled.get("MIN", False):
            res["MIN"] = vals[0]
        if stats_enabled.get("MAX", False):
            res["MAX"] = vals[-1]
        if stats_enabled.get("RANGE", False):
            res["RANGE"] = vals[-1] - vals[0]
        if stats_enabled.get("MODE", False):
            try:
                res["MODE"] = statistics.mode(vals)
            except Exception:
                res["MODE"] = float("nan")
        if stats_enabled.get("VARIANCE", False):
            res["VARIANCE"] = pvariance
        if stats_enabled.get("SUM", False):
            res["SUM"] = sum(vals)
        if stats_enabled.get("CV", False):
            if mean != 0:
                res["CV"] = pstdev / mean
            else:
                res["CV"] = float("nan")
        if stats_enabled.get("SKEW", False):
            sd = pstdev
            if sd > 0:
                skew = sum((x - mean) ** 3 for x in vals) / (n * sd ** 3)
                res["SKEW"] = skew
            else:
                res["SKEW"] = float("nan")
        if stats_enabled.get("KURT", False):
            sd = pstdev
            if sd > 0:
                kurt = sum((x - mean) ** 4 for x in vals) / (n * sd ** 4) - 3
                res["KURT"] = kurt
            else:
                res["KURT"] = float("nan")

        return res


class AttributeStatisticsModel:
    """
    Orquestrador que conecta extração de campos/valores com StatsCalculator e Preferences.
    Esta classe é a API que a view (QGIS ProcessingAlgorithm) deve usar.
    """
    STATS_LABELS = {
        "MEAN": "Media",
        "MEAN_ABS": "Media Absoluta",
        "STD_POP": "Desvio Padrao (Pop.)",
        "STD_SAMP": "Desvio Padrao (Amostra)",
        "MIN": "Minimo",
        "MAX": "Maximo",
        "RANGE": "Amplitude",
        "MEDIAN": "Mediana",
        "P5": "Percentil 5%",
        "P95": "Percentil 95%",
        "MODE": "Moda",
        "VARIANCE": "Variancia",
        "SUM": "Soma",
        "CV": "Coeficiente de Variaçao",
        "SKEW": "Assimetria",
        "KURT": "Curtose"
    }

    def __init__(self, stats_calculator: StatsCalculator = None):
      
        self._calc = stats_calculator or StatsCalculator()

    def extract_numeric_fields(self, qgis_fields) -> List[str]:
        """
        Recebe iterable de QgsFields (ou similar com .typeName() e .name()) e retorna lista de nomes numéricos.
        """
        numeric = []
        for f in qgis_fields:
            fn = f.name()
            t = f.typeName().lower()
            if "int" in t or "float" in t or "real" in t or "double" in t or "numeric" in t:
                numeric.append(fn)
        return numeric

    def collect_values(self, features: Iterable, numeric_field_names: List[str]) -> Dict[str, List[float]]:
        """
        features: iterable de QgsFeature (indexável por nome do campo).
        Retorna dicionário field -> lista de floats (apenas valores finitos).
        """
        values_by_field = {fn: [] for fn in numeric_field_names}
        for feat in features:
            for fn in numeric_field_names:
                v = feat[fn]
                if v is None:
                    continue
                try:
                    val = float(v)
                    if math.isfinite(val):
                        values_by_field[fn].append(val)
                except Exception:
                    # valores não numéricos são ignorados
                    pass
        return values_by_field

    def compute_all(self, values_by_field: Dict[str, List[float]], stats_enabled: Dict[str, bool]) -> Dict[str, Dict[str, float]]:
        """
        Para cada campo calcula as estatísticas habilitadas.
        Retorna dict: campo -> {STAT_KEY: valor}
        """
        result = {}
        for fn, vals in values_by_field.items():
            result[fn] = self._calc.compute_field_stats(vals, stats_enabled)
        return result

    # API de formatação para export (opcional, a view pode formatar por conta própria)
    def format_value(self, value: float, precision: int, dec_point: str = ".") -> str:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return ""
        txt = str(round(value, precision))
        if dec_point != ".":
            txt = txt.replace(".", dec_point)
        return txt
