# -*- coding: utf-8 -*-
"""
PqiUtil - Photogrammetry Quality Index Calculator.

Calcula o PQI (0-100) baseado em múltiplos indicadores com pesos configuráveis.
Cada indicador é classificado em nível 1-5 via RangeMetadataManager (thresholds do config.yaml).
O nível é convertido para pontuação 0-100 e ponderado pelo peso do indicador.

Uso:
    from .PqiUtil import PqiUtil
    pqi, details = PqiUtil.calculate(data_record)
"""

from typing import Dict, List, Tuple, Optional
from ...core.enum import MetadataFieldKey
from ..report.RangeMetadataManager import RangeMetadataManager
from ..ToolKeys import ToolKey
from ...core.config.LogUtils import LogUtils
# Singleton do RangeMetadataManager
_range_manager = RangeMetadataManager()


# Configuração dos indicadores que compõem o PQI
# Cada item:
#   metadata_key: MetadataFieldKey usado para buscar o valor no record
#   threshold_name: Nome do threshold no config.yaml
#   weight: Peso do indicador na composição do PQI (default=1.0)
#           Pts = weight / sum(weights) * 100
#   value_extractor: Função opcional callable(record) -> float para extrair/transformar valor

PQI_INDICATORS: List[Dict] = [
    {
        "metadata_key": MetadataFieldKey.MOTION_BLUR_RISK,
        "threshold_name": "motion_blur_risk",
        "weight": 0.25,
    },
    {
        "metadata_key": MetadataFieldKey.F_OVERLAP,
        "threshold_name": "predicted_overlap",
        "weight": 0.25,
    },
    # === Velocidade 3D (lower_better, peso 0.5) ===
    {
        "metadata_key": MetadataFieldKey.THREE_D_SPEED,
        "threshold_name": "speed_3d_ms",
        "weight": 0.5,
    },
    # === EV Classification (categorical, peso 2.0) ===
    # Valor é textual (ex: "nublado"), extrator retorna o texto cru para o RangeMetadataManager classificar
    {
        "metadata_key": MetadataFieldKey.EV_CLASSIFICATION,
        "threshold_name": "ev_classification",
        "weight": 2.0,
        "value_extractor": lambda r: _extract_ev_classification_value(r),
    },
    # === Indicadores com value_extractor que já retornam o LEVEL (1-5) ===
    {
        "metadata_key": MetadataFieldKey.RTK_EFFECTIVE_PRECISION,
        "threshold_name": "rtk_effective_precision",
        "weight": 1.0,
        "value_extractor": lambda r: _extract_rtk_level(r),
        "bypass_classify": True,
    },
    {
        "metadata_key": MetadataFieldKey.XY_DIFFERENCE,
        "threshold_name": "xy_difference",
        "weight": 1.0,
    },
    {
        "metadata_key": MetadataFieldKey.Z_DIFFERENCE,
        "threshold_name": "z_difference",
        "weight": 1.0,
    },
    {
        "metadata_key": MetadataFieldKey.DEWARP_FLAG,
        "threshold_name": "dewarp_flag",
        "weight": 2.0,
        "value_extractor": lambda r: _extract_dewarp_value(r),
        "bypass_classify": True,
    },
    {
        "metadata_key": MetadataFieldKey.RTK_DIFF_AGE,
        "threshold_name": "rtk_diff_age",
        "weight": 1.5,
    },
]


def _extract_rtk_level(record: Dict) -> float:
    """
    Extrai o nível RTK de 1-5 como valor numérico para classificação.
    Usa o RangeMetadataManager para classificar o avg_std.
    """
    logger = LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PqiUtil")
    # Tenta obter avg_std dos RTK STD
    rtk_stds = []
    for key in ["RtkStdLon", "RtkStdLat", "RtkStdHgt"]:
        raw = record.get(key)
        if raw is not None:
            try:
                rtk_stds.append(float(str(raw).replace(",", ".")))
            except (ValueError, TypeError) as e:
                logger.debug(f"_extract_rtk_level: falha ao converter {key}={raw}", error=str(e))
    if len(rtk_stds) >= 2:
        avg_std = sum(rtk_stds) / len(rtk_stds)
        level, _ = _range_manager.classify("rtk_effective_precision", avg_std)
        return float(level)
    return 3.0  # fallback


def _extract_dewarp_value(record: Dict) -> float:
    """
    DewarpFlag no padrao DJI XMP:
      '0' = SEM DEWARP (imagem bruta/distorcida) → nivel 1 (critico)
      None/null/""/ausente = DEWARP APLICADO (imagem corrigida) → nivel 5 (excelente)
    Nao existe valor '1' no padrao DJI — se nao e 0, e dewarp aplicado.
    """
    raw = record.get(MetadataFieldKey.DEWARP_FLAG.value)
    if raw is None:
        return 5.0  # Ausente/sem flag = dewarp aplicado = excelente
    flag_str = str(raw).strip()
    if flag_str in ("", "None", "null"):
        return 5.0  # Vazio = dewarp aplicado = excelente
    if flag_str == "0":
        return 1.0  # 0 = sem dewarp = critico
    return 5.0  # Qualquer outro valor = dewarp aplicado = excelente


def _extract_ev_classification_value(record: Dict) -> str:
    """
    Extrai o texto do EV Classification (ex: "nublado", "luz solar normal").
    Retorna o texto cru para o RangeMetadataManager classificar como categorical.
    Se ausente, retorna "Unknown" que mapeia para nivel 3 no config.yaml.
    """
    raw = record.get(MetadataFieldKey.EV_CLASSIFICATION.value)
    if raw is None:
        return "Unknown"
    return str(raw).strip()


def _level_to_score(level: int) -> float:
    """
    Converte nível (1-5) para pontuação (0-100).

    Nível 1 (crítico) → 0 pontos
    Nível 2 (ruim)    → 25 pontos
    Nível 3 (regular) → 50 pontos
    Nível 4 (bom)     → 75 pontos
    Nível 5 (excelente) → 100 pontos
    """
    mapping = {1: 0.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 100.0}
    return mapping.get(level, 0.0)


def _extract_value(record: Dict, indicator: Dict) -> Optional[float]:
    """
    Extrai o valor numérico de um indicador a partir do record.

    Suporta:
    - Busca direta por metadata_key.value
    - Transformações customizadas via value_extractor
    """
    logger = LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PqiUtil")
    # Se tem extrator customizado, usa ele
    if "value_extractor" in indicator:
        try:
            return indicator["value_extractor"](record)
        except Exception as e:
            logger.debug("Falha ao executar value_extractor", error=str(e))
            return None

    # Busca padrão pela chave canônica
    metadata_key = indicator.get("metadata_key")
    if metadata_key:
        raw = record.get(metadata_key.value)
        if raw is not None:
            try:
                return float(str(raw).replace(",", "."))
            except (ValueError, TypeError) as e:
                logger.debug(f"Falha ao converter valor {raw}", error=str(e))

    return None


class PqiUtil:
    """Calculadora do Photogrammetry Quality Index (PQI) 0-100."""

    # Configuração padrão dos indicadores
    _indicators: List[Dict] = list(PQI_INDICATORS)

    @classmethod
    def configure(cls, indicators: List[Dict]):
        """
        Substitui a lista de indicadores (para testes ou customização).

        Cada item deve conter:
        - metadata_key: MetadataFieldKey (obrigatório)
        - threshold_name: str (nome no config.yaml)
        - weight: float (peso, default=1.0)
        - value_extractor: callable(record) -> float (opcional)
        """
        cls._indicators = list(indicators)

    @classmethod
    def get_indicators(cls) -> List[Dict]:
        """Retorna a configuração atual dos indicadores."""
        return list(cls._indicators)

    @staticmethod
    def calculate(
        record: Dict,
        tool_key: str = "pqi_util",
    ) -> Tuple[float, List[Dict]]:
        """
        Calcula o PQI para um record.

        Args:
            record: Dicionário contendo os campos calculados (custom fields + qualidade)
            tool_key: Chave para logging

        Returns:
            Tuple (pqi_score, details)
            - pqi_score: float (0-100)
            - details: Lista de dicts com detalhes de cada indicador
                [{"name": str, "level": int, "score_raw": float, "score_weighted": float, "threshold_msg": str}, ...]
        """
        logger = LogUtils(tool=tool_key, class_name="PqiUtil")
        # Garante que RangeMetadataManager está carregado
        try:
            _range_manager.load()
        except Exception as e:
            logger.warning("Falha ao carregar RangeMetadataManager", error=str(e))

        details = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for indicator in PqiUtil._indicators:
            metadata_key = indicator.get("metadata_key")
            threshold_name = indicator.get("threshold_name", "")
            weight = float(indicator.get("weight", 1.0))

            # Extrai o valor do record
            value = _extract_value(record, indicator)

            # Verifica se o valor já é o nível (bypass_classify) ou precisa classificar
            bypass = indicator.get("bypass_classify", False)
            if value is None:
                # Valor não disponível → nível 3 (50%)
                level = 3
                threshold_msg = "Indisponivel (OK default)"
            elif bypass:
                # value já é o nível (1-5) — usa diretamente
                level = int(round(value))
                level = max(1, min(5, level))
                threshold_msg = f"Nivel {level} (bypass)"
            else:
                # Classifica usando RangeMetadataManager
                level, threshold_msg = _range_manager.classify(threshold_name, value)

            # Converte nível para pontuação 0-100
            score_raw = _level_to_score(level)
            score_weighted = score_raw * weight

            total_weighted_score += score_weighted
            total_weight += weight

            details.append(
                {
                    "name": metadata_key.value if metadata_key else threshold_name,
                    "level": level,
                    "value": value,
                    "score_raw": round(score_raw, 2),
                    "score_weighted": round(score_weighted, 2),
                    "weight": weight,
                    "threshold_msg": threshold_msg,
                }
            )

        # Calcula PQI final (0-100)
        pqi_score = (
            round(total_weighted_score / total_weight, 2) if total_weight > 0 else 50.0
        )
        pqi_score = max(0.0, min(100.0, pqi_score))

        return pqi_score, details

    @staticmethod
    def interpret(pqi_score: float) -> str:
        """
        Retorna interpretação textual do PQI.

        Args:
            pqi_score: Pontuação PQI (0-100)

        Returns:
            String com interpretação
        """
        if pqi_score >= 90:
            return "Excelente"
        elif pqi_score >= 80:
            return "Muito boa"
        elif pqi_score >= 70:
            return "Aceitável"
        elif pqi_score >= 50:
            return "Risco moderado"
        else:
            return "Problemática"
