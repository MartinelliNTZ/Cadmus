#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CustomUtil - Calcula campos derivados CUSTOM_FIELDS.

Recebe output do Manager.collect_metadata() → adiciona campos custom calculados

Dependências:
- MetadataFields.CUSTOM_FIELDS
- math, datetime, numpy (haversine)
"""

import math
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from ...core.config.LogUtils import LogUtils
from ...core.enum import MetadataFieldKey, EvClassEnum
from ...core.enum.LightSourceEnum import LightSourceEnum
from ..ToolKeys import ToolKey
from ..report.RangeMetadataManager import range_metadata_manager
from .MetadataFields import MetadataFields
from .PqiUtil import PqiUtil

DECIMAL_PLACES = 2


class CustomPhotosFieldsUtil:
    """Calcula todos os campos CUSTOM_FIELDS para cada foto, validando sequências."""

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="CustomPhotosFieldsUtil")

    # Constantes
    MAX_DT_DIFF = 120  # segundos
    MAX_ALT_DIFF = 200  # metros
    MAX_SHUTTER_JUMP = 5000  # fotos (arrochado)
    IDEAL_OVERLAP = 60  # %
    ORTO_SCORE_WEIGHTS = {
        "rtk_high": 30,
        "incidence_low": 25,
        "dewarp": 20,
        "rtk_fresh": 15,
        "overlap_good": 10,
    }

    BLUR_THRESHOLD = 0.5  # motion blur in pixels
    COVERAGE_FACTOR = 1.45  # approx for 84° HFOV
    STRIP_CHANGE_THRESHOLD = 150  # degrees

    @staticmethod
    def _key(field_key: MetadataFieldKey) -> str:
        return field_key.value

    @staticmethod
    def _get(data: Dict, field_key: MetadataFieldKey, *legacy_keys, default=None):
        """
        Busca valor no dicionário testando múltiplas chaves.

        Ordem de busca:
        1. Chave canônica (field_key.value)
        2. Atributo mapeado em MetadataFields (field.attribute)
        3. Legacy keys passadas como argumentos
        4. Qualquer chave que resolva para o mesmo campo via resolve_key
        """
        if not data:
            return default

        # 1. Chave canônica
        canonical = field_key.value
        if canonical in data and data.get(canonical) is not None:
            return data.get(canonical)

        # 2. Atributo mapeado (ex: "GpsLat", "GPSLong")
        field_obj = MetadataFields.CUSTOM_FIELDS.get(field_key)
        if not field_obj:
            field_obj = MetadataFields.EXIF_FIELDS.get(field_key)
        if not field_obj:
            field_obj = MetadataFields.DJI_XMP_FIELDS.get(field_key)
        if (
            field_obj
            and field_obj.attribute in data
            and data.get(field_obj.attribute) is not None
        ):
            return data.get(field_obj.attribute)

        # 3. Legacy keys
        for legacy in legacy_keys:
            if legacy in data and data.get(legacy) is not None:
                return data.get(legacy)

        # 4. Busca por todo o dicionário usando resolve_key
        for key, value in data.items():
            if value is None:
                continue
            candidates = MetadataFields.resolve_candidates(key)
            if canonical in candidates:
                return value

        return default

    @staticmethod
    def _get_abs_speed(data: Dict, field_key: MetadataFieldKey, *legacy_keys) -> float:
        return abs(
            CustomPhotosFieldsUtil.safe_float(
                CustomPhotosFieldsUtil._get(
                    data, field_key, *legacy_keys, default=0.0)
            )
        )

    @staticmethod
    def _get_safe(
        data: Dict, field_key: MetadataFieldKey, *legacy_keys, default=0.0
    ) -> float:
        """
        Busca e converte para float seguro usando _get.
        """
        return CustomPhotosFieldsUtil.safe_float(
            CustomPhotosFieldsUtil._get(
                data, field_key, *legacy_keys, default=default),
            default=default if isinstance(default, (int, float)) else 0.0,
        )

    @staticmethod
    def _get_int(
        data: Dict, field_key: MetadataFieldKey, *legacy_keys, default=0
    ) -> int:
        """
        Busca e converte para int seguro usando _get.
        """
        raw = CustomPhotosFieldsUtil._get(
            data, field_key, *legacy_keys, default=default
        )
        if raw is None:
            return default
        return int(str(raw))

    @staticmethod
    def safe_float(val: any, default: float = 0.0) -> float:
        """Converte para float seguro (strings '+123.4' → 123.4)."""
        if val is None:
            return default
        return float(str(val).replace("+", ""))

    @staticmethod
    def safe_int(val: any, default: int = 0) -> int:
        """Converte para int seguro."""
        if val is None:
            return default
        return int(str(val))

    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        """Parse robusto de datetime com suporte a formatos EXIF/ISO."""
        if dt_str is None:
            return None
        raw = str(dt_str).strip()
        if not raw or raw.lower() in ("none", "null", "nan"):
            return None

        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except (ValueError, TypeError) as e:
            LogUtils(tool=ToolKey.UNTRACEABLE, class_name="CustomPhotosFieldsUtil").debug(
                "parse_datetime: fromisoformat falhou", error=str(e)
            )

        formats = (
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y%m%d%H%M",
            "%Y%m%d",
        )
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt)
            except (ValueError, TypeError) as e:
                LogUtils(tool=ToolKey.UNTRACEABLE, class_name="CustomPhotosFieldsUtil").debug(
                    f"parse_datetime: strptime falhou com formato {fmt}", error=str(e)
                )
                continue
        return None

    @staticmethod
    def resolve_capture_datetime(
        data: Dict,
    ) -> Tuple[Optional[datetime], Optional[str]]:
        """Resolve data/hora de captura usando fallback entre campos conhecidos."""
        candidates = (
            (
                MetadataFieldKey.DATE_TIME_ORIGINAL.value,
                data.get(MetadataFieldKey.DATE_TIME_ORIGINAL.value),
            ),
            ("DateTime", data.get("DateTime")),
            (
                MetadataFieldKey.UTC_AT_EXPOSURE.value,
                data.get(MetadataFieldKey.UTC_AT_EXPOSURE.value),
            ),
            (MetadataFieldKey.DT_FULL.value, data.get(
                MetadataFieldKey.DT_FULL.value)),
        )
        for source, value in candidates:
            parsed = CustomPhotosFieldsUtil.parse_datetime(value)
            if parsed is not None:
                return parsed, source

        dt_date = str(data.get(MetadataFieldKey.DT_DATE.value) or "").strip()
        dt_time = str(data.get(MetadataFieldKey.DT_TIME.value) or "").strip()
        if dt_date and dt_time and dt_date.lower() not in ("none", "null"):
            hhmm = dt_time.zfill(4)
            parsed = CustomPhotosFieldsUtil.parse_datetime(f"{dt_date}{hhmm}")
            if parsed is not None:
                return parsed, "DtDate+DtTime"

        return None, None

    @staticmethod
    def get_voo_id(data: Dict) -> str:
        """VOO_ID = drone_sn[:8] + camera_sn[:8] + YYYY-MM-DD."""
        drone_sn = CustomPhotosFieldsUtil._get(
            data, MetadataFieldKey.DRONE_SERIAL_NUMBER, default="UNKNOWN"
        )
        camera_sn = CustomPhotosFieldsUtil._get(
            data, MetadataFieldKey.CAMERA_SERIAL_NUMBER, default="UNKNOWN"
        )
        dt, _ = CustomPhotosFieldsUtil.resolve_capture_datetime(data)
        date_str = dt.strftime(
            "%Y-%m-%d") if dt is not None else "UNKNOWN_DATE"
        return f"{drone_sn[:8]}_{camera_sn[:8]}_{date_str}"

    @staticmethod
    def is_valid_sequence(
        curr_data: Dict, other_data: Dict, direction: str = "prev"
    ) -> bool:
        """Valida se 2 fotos são sequência válida (mesmo voo)."""
        if other_data is None:
            return False

        # 1. Mesmo VOO_ID
        voo_curr = CustomPhotosFieldsUtil.get_voo_id(curr_data)
        voo_other = CustomPhotosFieldsUtil.get_voo_id(other_data)
        if voo_curr != voo_other:
            return False

        # 2. dt_diff
        dt_curr, _ = CustomPhotosFieldsUtil.resolve_capture_datetime(curr_data)
        dt_other, _ = CustomPhotosFieldsUtil.resolve_capture_datetime(
            other_data)
        if dt_curr is None or dt_other is None:
            return False
        dt_diff = abs((dt_curr - dt_other).total_seconds())
        if dt_diff > CustomPhotosFieldsUtil.MAX_DT_DIFF:
            return False

        # 3. alt_diff
        alt_curr = CustomPhotosFieldsUtil._get_safe(
            curr_data, MetadataFieldKey.ABSOLUTE_ALTITUDE
        )
        alt_other = CustomPhotosFieldsUtil._get_safe(
            other_data, MetadataFieldKey.ABSOLUTE_ALTITUDE
        )
        alt_diff = abs(alt_curr - alt_other)
        if alt_diff > CustomPhotosFieldsUtil.MAX_ALT_DIFF:
            return False

        # 4. shutter_jump (arrochado)
        shutter_curr = CustomPhotosFieldsUtil._get_int(
            curr_data, MetadataFieldKey.SHUTTER_COUNT, default=0
        )
        shutter_other = CustomPhotosFieldsUtil._get_int(
            other_data, MetadataFieldKey.SHUTTER_COUNT, default=0
        )
        shutter_jump = (
            abs(shutter_curr - shutter_other) > CustomPhotosFieldsUtil.MAX_SHUTTER_JUMP
        )
        if shutter_jump:
            return False

        return True

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distância Haversine entre 2 pontos GPS (metros)."""
        R = 6371000  # Raio Terra

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def bearing_angle(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Azimute bearing entre 2 pontos (0=Norte)."""
        delta_lon = math.radians(lon2 - lon1)
        y = math.sin(delta_lon) * math.cos(math.radians(lat2))
        x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.cos(delta_lon)
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360

    @staticmethod
    def angle_difference(a: float, b: float) -> float:
        """Menor diferença angular entre dois azimutes (0-180)."""
        diff = abs((a - b) % 360)
        return diff if diff <= 180 else 360 - diff

    @staticmethod
    def _get_camera_params(data: Dict) -> Tuple[float, float, float, float, float]:
        """
        Obtém parâmetros da câmera a partir do dicionário CAMERA_MODEL_PARAMS.

        Returns:
            Tuple (sensor_width_mm, sensor_height_mm, focal_real_mm, img_w_px, img_h_px)
        """
        logger = CustomPhotosFieldsUtil._get_logger()
        logger.debug(
            f"Obtendo parâmetros da câmera para foto com dados: {data}")

        # Tenta obter modelo do drone/câmera
        model = CustomPhotosFieldsUtil._get(
            data, MetadataFieldKey.DRONE_MODEL, MetadataFieldKey.MODEL.value, default=""
        )
        model_str = str(model).strip() if model else ""
        logger.debug(f"Modelo identificado: '{model_str}'")

        # Busca nos parâmetros conhecidos
        if model_str and model_str in MetadataFields.CAMERA_MODEL_PARAMS:
            params = MetadataFields.CAMERA_MODEL_PARAMS[model_str]
            sensor_w = float(params["sensor_width_mm"])
            sensor_h = float(params["sensor_height_mm"])
            focal = float(params["focal_real_mm"])
            logger.debug(
                f"Parâmetros encontrados para '{model_str}': sensor={sensor_w}x{sensor_h}, focal={focal}"
            )
        else:
            # Fallback para M4E (valores mais comuns)
            sensor_w = 17.3
            sensor_h = 13.0
            focal = 12.29
            logger.debug(
                f"Modelo '{model_str}' não encontrado em CAMERA_MODEL_PARAMS. Usando fallback M4E: sensor={sensor_w}x{sensor_h}, focal={focal}"
            )

        # Resolução da imagem (usa valores do EXIF ou fallback)
        img_w = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.EXIF_IMAGE_WIDTH, default=5280
        )
        img_h = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.EXIF_IMAGE_HEIGHT, default=3956
        )

        # Se não veio do EXIF, tenta fallback dos parâmetros conhecidos
        if img_w <= 0 and model_str and model_str in MetadataFields.CAMERA_MODEL_PARAMS:
            res = MetadataFields.CAMERA_MODEL_PARAMS[model_str].get(
                "resolution_px", (5280, 3956)
            )
            if isinstance(res, (tuple, list)) and len(res) == 2:
                img_w, img_h = float(res[0]), float(res[1])
                logger.debug(
                    f"Usando resolução de CAMERA_MODEL_PARAMS: {img_w}x{img_h}"
                )

        if img_w <= 0:
            img_w = 5280
        if img_h <= 0:
            img_h = 3956

        # Focal length do EXIF ou fallback
        focal_exif = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.FOCAL_LENGTH, default=0
        )
        if focal_exif > 0:
            logger.debug(
                f"Focal do EXIF ({focal_exif:.2f}) sobrescrevendo focal padrão ({focal:.2f})"
            )
            focal = focal_exif

        logger.debug(
            f"Parâmetros finais da câmera: sensor={sensor_w}x{sensor_h} mm, focal={focal} mm, imagem={img_w}x{img_h} px"
        )
        return (sensor_w, sensor_h, focal, img_w, img_h)

    @staticmethod
    def _get_effective_height(data: Dict) -> float:
        """
        Obtém a altura efetiva (H) para cálculos de GSD e cobertura.

        Ordem de precedência:
        1. LRF_TARGET_DISTANCE (>0) → H = LRFDist * cos(incidence_angle_rad)
           O LRF mede a distância real até o alvo. Quando o gimbal está a nadir
           (pitch efetivo = -90°), LRFDist = altura. Com angulação, a altura
           efetiva é a projeção vertical: H = LRFDist * cos(incidence_angle).
        2. RelativeAltitude (>0)
        3. AbsoluteAltitude (>0)

        Returns:
            Altura efetiva em metros, ou 0.0 se nenhuma fonte disponível.
        """
        logger = CustomPhotosFieldsUtil._get_logger()

        # 1. Tenta LRF_TARGET_DISTANCE com correção do ângulo de incidência
        lrf_dist = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.LRF_TARGET_DISTANCE, default=0
        )
        if lrf_dist > 0:
            # Calcula incidence angle (mesma lógica de _calculate_quality_scores)
            gim_pitch = CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.GIMBAL_PITCH_DEGREE, default=0
            )
            flight_pitch = CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.FLIGHT_PITCH_DEGREE, default=0
            )
            effective_pitch = gim_pitch + flight_pitch
            # Incidence angle = ângulo entre a linha de visada da câmera e a vertical
            # Pitch -90° = nadir (apontando para baixo) → incidence = 0°
            inc_angle = abs(90.0 - abs(effective_pitch))
            inc_rad = math.radians(inc_angle)
            # Altura efetiva = distância real * cos(ângulo de incidência)
            h_effective = lrf_dist * math.cos(inc_rad)
            logger.debug(
                f"_get_effective_height via LRF: LRFDist={lrf_dist:.2f}m, "
                f"gim_pitch={gim_pitch:.1f}°, flight_pitch={flight_pitch:.1f}°, "
                f"inc_angle={inc_angle:.2f}°, H_effective={h_effective:.4f}m"
            )
            return h_effective

        # 2. Fallback: RelativeAltitude (altitude sobre o terreno)
        h_m = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.RELATIVE_ALTITUDE, default=0
        )
        if h_m > 0:
            logger.debug(
                f"_get_effective_height via RelativeAltitude: H={h_m:.4f}m")
            return h_m

        # 3. Fallback: AbsoluteAltitude
        h_m = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
        )
        if h_m > 0:
            logger.debug(
                f"_get_effective_height via AbsoluteAltitude: H={h_m:.4f}m")
            return h_m

        logger.debug(
            "_get_effective_height: nenhuma fonte de altura disponível, retornando 0.0"
        )
        return 0.0

    @staticmethod
    def calculate_estimated_coverage(data: Dict) -> Tuple[float, float]:
        """
        Estimativa de cobertura no solo (largura, altura) em metros.

        Fórmulas:
            Largura_solo = H * S_w / f
            Altura_solo  = H * S_h / f

        Onde:
            H = altura efetiva (LRF_TARGET_DISTANCE corrigido > RelativeAltitude > AbsoluteAltitude)
            S_w = largura física do sensor (mm)
            S_h = altura física do sensor (mm)
            f = distância focal real (mm)
        """
        # Usa altura efetiva com LRF como primário
        h_m = CustomPhotosFieldsUtil._get_effective_height(data)

        sensor_w, sensor_h, focal, _, _ = CustomPhotosFieldsUtil._get_camera_params(
            data
        )

        if h_m <= 0 or focal <= 0:
            return (round(0.0, DECIMAL_PLACES), round(0.0, DECIMAL_PLACES))

        logger = CustomPhotosFieldsUtil._get_logger()
        logger.debug(
            f"calculate_estimated_coverage: H={h_m:.4f} m, sensor={sensor_w}x{sensor_h} mm, focal={focal} mm"
        )

        # Largura no solo: H * S_w / f
        width_m = h_m * sensor_w / focal

        # Altura no solo: H * S_h / f
        height_m = h_m * sensor_h / focal

        logger.debug(
            f"Cobertura calculada: {width_m:.2f} x {height_m:.2f} m (área={width_m * height_m:.2f} m²)"
        )
        return (round(width_m, DECIMAL_PLACES), round(height_m, DECIMAL_PLACES))

    @staticmethod
    def _calculate_sequence_fields(
        data: Dict, other_data: Optional[Dict], valid_seq: bool, direction: str
    ) -> Dict:
        """Campos sequência (prev/next)."""
        if not valid_seq or other_data is None:
            prefix = f"{direction}_"
            return {
                f"{prefix}time_since": round(0.0, DECIMAL_PLACES),
                f"{prefix}geodesic_distance": round(0.0, DECIMAL_PLACES),
                f"{prefix}distance_3d": round(0.0, DECIMAL_PLACES),
                f"{prefix}avg_velocity": round(0.0, DECIMAL_PLACES),
                f"{prefix}displacement_direction": round(0.0, DECIMAL_PLACES),
            }

        dt_curr, _ = CustomPhotosFieldsUtil.resolve_capture_datetime(data)
        dt_other, _ = CustomPhotosFieldsUtil.resolve_capture_datetime(
            other_data)
        if dt_curr is None or dt_other is None:
            prefix = f"{direction}_"
            return {
                f"{prefix}time_since": round(0.0, DECIMAL_PLACES),
                f"{prefix}geodesic_distance": round(0.0, DECIMAL_PLACES),
                f"{prefix}distance_3d": round(0.0, DECIMAL_PLACES),
                f"{prefix}avg_velocity": round(0.0, DECIMAL_PLACES),
                f"{prefix}displacement_direction": round(0.0, DECIMAL_PLACES),
            }
        dt_diff = abs((dt_curr - dt_other).total_seconds())

        # GPS (haversine precisa lat/lon reais - usar LRFTarget se GPS None)
        lat_curr = CustomPhotosFieldsUtil._get_safe(
            data,
            MetadataFieldKey.GPS_LATITUDE,
            MetadataFieldKey.LRF_TARGET_LAT.value,
            default=0,
        )
        lon_curr = CustomPhotosFieldsUtil._get_safe(
            data,
            MetadataFieldKey.GPS_LONGITUDE,
            MetadataFieldKey.LRF_TARGET_LON.value,
            default=0,
        )
        lat_other = CustomPhotosFieldsUtil._get_safe(
            other_data,
            MetadataFieldKey.GPS_LATITUDE,
            MetadataFieldKey.LRF_TARGET_LAT.value,
            default=0,
        )
        lon_other = CustomPhotosFieldsUtil._get_safe(
            other_data,
            MetadataFieldKey.GPS_LONGITUDE,
            MetadataFieldKey.LRF_TARGET_LON.value,
            default=0,
        )

        geo_dist = CustomPhotosFieldsUtil.haversine(
            lat_curr, lon_curr, lat_other, lon_other
        )
        alt_curr = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
        )
        alt_other = CustomPhotosFieldsUtil._get_safe(
            other_data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
        )
        alt_diff = abs(alt_curr - alt_other)
        dist_3d = math.sqrt(geo_dist**2 + alt_diff**2)

        avg_vel = dist_3d / dt_diff if dt_diff > 0 else 0.0
        # direction="prev": bearing from OTHER (previous photo) to CURRENT (flight direction)
        if direction == "prev":
            dir_displ = CustomPhotosFieldsUtil.bearing_angle(
                lat_other, lon_other, lat_curr, lon_curr
            )
        else:
            dir_displ = CustomPhotosFieldsUtil.bearing_angle(
                lat_curr, lon_curr, lat_other, lon_other
            )

        prefix = f"{direction}_"
        return {
            f"{prefix}time_since": round(dt_diff, DECIMAL_PLACES),
            f"{prefix}geodesic_distance": round(geo_dist, DECIMAL_PLACES),
            f"{prefix}distance_3d": round(dist_3d, DECIMAL_PLACES),
            f"{prefix}avg_velocity": round(avg_vel, DECIMAL_PLACES),
            f"{prefix}displacement_direction": round(dir_displ, DECIMAL_PLACES),
        }

    @staticmethod
    def _calculate_individual_fields(data: Dict) -> Dict:
        """Campos custom individuais derivados - retorna chaves canônicas do MetadataFieldKey.value."""
        shutter_count = CustomPhotosFieldsUtil._get_int(
            data, MetadataFieldKey.SHUTTER_COUNT, default=0
        )
        shutter_life_pct = (shutter_count / 400000) * 100

        # Obtém parâmetros da câmera do dicionário CAMERA_MODEL_PARAMS
        sensor_w, sensor_h, focal, img_w, img_h = (
            CustomPhotosFieldsUtil._get_camera_params(data)
        )

        # Altura efetiva: LRF_TARGET_DISTANCE (corrigido) > RelativeAltitude > AbsoluteAltitude
        h_m = CustomPhotosFieldsUtil._get_effective_height(data)

        logger = CustomPhotosFieldsUtil._get_logger()
        logger.debug(
            f"_calculate_individual_fields: H={h_m:.4f} m, sensor={sensor_w}x{sensor_h} mm, focal={focal} mm, imagem={img_w}x{img_h} px"
        )

        # Cálculo do GSD usando fórmula clássica:
        # GSD = (H * S) / (f * I)
        # Onde:
        #   H = altura do voo (m)
        #   S = dimensão física do sensor (mm)
        #   f = distância focal real (mm)
        #   I = dimensão da imagem (pixels)

        # GSD horizontal (cm/pixel)
        gsd_x_cm = 0.0
        gsd_y_cm = 0.0
        if h_m > 0 and focal > 0 and img_w > 0 and img_h > 0:
            gsd_x_m = (h_m * sensor_w) / (focal * img_w)
            gsd_y_m = (h_m * sensor_h) / (focal * img_h)
            gsd_x_cm = gsd_x_m * 100
            gsd_y_cm = gsd_y_m * 100
            logger.debug(
                f"GSD X={gsd_x_cm:.4f} cm/px, GSD Y={gsd_y_cm:.4f} cm/px (fórmula: H*S/f/I)"
            )
        else:
            logger.debug(
                f"GSD não calculado - H={h_m}, focal={focal}, img_w={img_w}, img_h={img_h}"
            )

        # GSD final = média entre horizontal e vertical
        gsd_cm_px = (
            (gsd_x_cm + gsd_y_cm) / 2
            if gsd_x_cm > 0 and gsd_y_cm > 0
            else max(gsd_x_cm, gsd_y_cm)
        )
        gsd_m_px = gsd_cm_px / 100
        logger.debug(
            f"GSD final={gsd_cm_px:.4f} cm/pixel ({gsd_m_px:.6f} m/pixel)")

        # Heat index
        sens_temp = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.SENSOR_TEMPERATURE, default=0
        )
        lens_temp = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.LENS_TEMPERATURE, default=0
        )
        total_heat_index = (
            (sens_temp + lens_temp) / 2
            if sens_temp > 0 and lens_temp > 0
            else (sens_temp or lens_temp or 0.0)
        )

        # Speed 3D for blur risk (usa o mesmo calculo do 3DSpeed de _calculate_gimbal_3d)
        xspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_X_SPEED, "XSpeed"
        )
        yspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_Y_SPEED, "YSpeed"
        )
        zspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_Z_SPEED, "ZSpeed"
        )
        speed_3d = math.sqrt(xspd**2 + yspd**2 + zspd**2)
        logger.debug(
            f"Speed 3D: sqrt({xspd:.4f}²+{yspd:.4f}²+{zspd:.4f}²)={speed_3d:.4f} m/s"
        )

        # New fields
        exp_time = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.EXPOSURE_TIME, default=0
        )
        fnumber = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.F_NUMBER, default=2.8
        )

        motion_blur_risk = (speed_3d * exp_time /
                            gsd_m_px) if gsd_m_px > 0 else 0.0
        exposure_value_ev = math.log2(
            fnumber**2 / exp_time) if exp_time > 0 else 0.0

        # ── FOV (Field of View) ──────────────────────────────────────────
        # FOV = 2 * arctan(diagonal_sensor / (2 * focal_real))
        diagonal_sensor_mm = math.sqrt(sensor_w**2 + sensor_h**2)
        if focal > 0:
            fov_degrees = 2 * \
                math.degrees(math.atan(diagonal_sensor_mm / (2 * focal)))
        else:
            fov_degrees = 0.0
        logger.debug(
            f"FOV: sensor_diagonal={diagonal_sensor_mm:.4f}mm, focal={focal}mm → {fov_degrees:.2f}°"
        )

        # ── Circle of Confusion (CoC) ────────────────────────────────────
        # CoC (mm) = diagonal_sensor / 1730
        if diagonal_sensor_mm > 0:
            coc_mm = diagonal_sensor_mm / 1730.0
        else:
            coc_mm = 0.0
        logger.debug(
            f"CircleOfConfusion: diagonal={diagonal_sensor_mm:.4f}mm → CoC={coc_mm:.6f}mm"
        )

        # ── DOF (Depth of Field) ─────────────────────────────────────────
        # DOF = (2 * u² * N * C) / f²
        # Onde:
        #   u = distância de foco (FocusDistance) em mm
        #   N = número f (FNumber)
        #   C = Circle of Confusion em mm
        #   f = distância focal real em mm
        # Resultado em mm (dividido por 1000 p/ metros)
        focus_distance_m = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.FOCUS_DISTANCE, default=0
        )
        focus_distance_mm = focus_distance_m * 1000.0 if focus_distance_m > 0 else 0.0
        if focal > 0 and fnumber > 0 and coc_mm > 0 and focus_distance_mm > 0:
            dof_mm = (2.0 * focus_distance_mm**2 *
                      fnumber * coc_mm) / (focal**2)
            dof_m = dof_mm / 1000.0
        else:
            dof_m = 0.0
        logger.debug(
            f"DOF: u={focus_distance_mm:.2f}mm, N={fnumber}, C={coc_mm:.6f}mm, "
            f"f={focal}mm → DOF={dof_m:.4f}m"
        )

        # ── HyperfocalDistance ───────────────────────────────────────────
        # H (mm) = f² / (N × CoC)  →  convertido para metros
        if focal > 0 and fnumber > 0 and coc_mm > 0:
            hyperfocal_mm = (focal**2) / (fnumber * coc_mm)
            hyperfocal_m = hyperfocal_mm / 1000.0
        else:
            hyperfocal_m = 0.0
        logger.debug(
            f"HyperfocalDistance: f={focal}mm, N={fnumber}, CoC={coc_mm:.6f}mm → {hyperfocal_m:.4f}m"
        )

        # ── LightValue (LV / EV100) ──────────────────────────────────────
        # LV = log₂(N² × 100 / (t × ISO))
        # onde N = f-number, t = exposure_time (s), ISO = ISO speed
        iso = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.ISO_SPEED_RATINGS, default=100
        )
        light_value = 0.0
        if fnumber > 0 and exp_time > 0 and iso > 0:
            light_value = math.log2((fnumber**2 * 100.0) / (exp_time * iso))
        logger.debug(
            f"LightValue: N={fnumber}, t={exp_time:.6f}s, ISO={iso} → LV={light_value:.2f}"
        )

        # ── FocalLength35efl (equivalente 35mm) ──────────────────────────
        # FocalLength35efl = FocalLength * (diagonal_full_frame / diagonal_sensor)
        # diagonal full frame 35mm = sqrt(36² + 24²) = 43.2666 mm
        FULL_FRAME_DIAGONAL_MM = 43.2666
        if focal > 0 and diagonal_sensor_mm > 0:
            focal_35efl = focal * (FULL_FRAME_DIAGONAL_MM / diagonal_sensor_mm)
        else:
            focal_35efl = 0.0
        logger.debug(
            f"FocalLength35efl: focal={focal}mm, sensor_diag={diagonal_sensor_mm:.4f}mm → {focal_35efl:.2f}mm"
        )

        return {
            MetadataFieldKey.SHUTTER_LIFE_PCT.value: round(
                shutter_life_pct, DECIMAL_PLACES
            ),
            MetadataFieldKey.GROUND_SAMPLE_DISTANCE_CM.value: round(
                gsd_cm_px, DECIMAL_PLACES
            ),
            MetadataFieldKey.TOTAL_HEAT_INDEX.value: round(
                total_heat_index, DECIMAL_PLACES
            ),
            MetadataFieldKey.MOTION_BLUR_RISK.value: round(
                motion_blur_risk, DECIMAL_PLACES
            ),
            MetadataFieldKey.EXPOSURE_VALUE_EV.value: round(
                exposure_value_ev, DECIMAL_PLACES
            ),
            MetadataFieldKey.FOV.value: round(fov_degrees, DECIMAL_PLACES),
            MetadataFieldKey.CIRCLE_OF_CONFUSION.value: round(coc_mm, 6),
            MetadataFieldKey.DOF.value: round(dof_m, DECIMAL_PLACES),
            MetadataFieldKey.HYPERFOCAL_DISTANCE.value: round(
                hyperfocal_m, DECIMAL_PLACES
            ),
            MetadataFieldKey.LIGHT_VALUE.value: round(light_value, DECIMAL_PLACES),
            MetadataFieldKey.FOCAL_LENGTH_35EFL.value: round(
                focal_35efl, DECIMAL_PLACES
            ),
        }

    @staticmethod
    def _calculate_gimbal_offset(gim_yaw: float, flight_yaw: float) -> float:
        """Calcula o offset do gimbal baseado na diferença mínima com flight yaw."""
        # Normaliza ângulos para 0-360
        gim_yaw_norm = (gim_yaw % 360 + 360) % 360
        flight_yaw_norm = (flight_yaw % 360 + 360) % 360

        # Diferença absoluta
        diff = abs(gim_yaw_norm - flight_yaw_norm)
        if diff > 150 and diff < 300:
            diff = abs(180 - diff)
        elif diff > 300:
            diff = abs(360 - diff)
        # Ajuste para casos extremos (ex: 10° vs 190°)
        # Offset = |diff_min - 180|
        return abs(diff)

    @staticmethod
    def _calculate_gimbal_3d(data: Dict, prev_dir: float = None) -> Dict:
        """GimbalOffset, 3DSpeed + yaw_alignment_error - retorna chaves canônicas MetadataFields."""
        gim_yaw = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.GIMBAL_YAW_DEGREE, default=0
        )
        flight_yaw = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.FLIGHT_YAW_DEGREE, default=0
        )
        gimbal_offset = CustomPhotosFieldsUtil._calculate_gimbal_offset(
            gim_yaw, flight_yaw
        )

        xspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_X_SPEED, "XSpeed"
        )
        yspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_Y_SPEED, "YSpeed"
        )
        zspd = CustomPhotosFieldsUtil._get_abs_speed(
            data, MetadataFieldKey.FLIGHT_Z_SPEED, "ZSpeed"
        )
        speed_3d = math.sqrt(xspd**2 + yspd**2 + zspd**2)
        logger = CustomPhotosFieldsUtil._get_logger()
        logger.debug(
            f"Gimbal 3D Speed: sqrt({xspd:.4f}²+{yspd:.4f}²+{zspd:.4f}²)={speed_3d:.4f} m/s"
        )

        displacement_dir = prev_dir if prev_dir is not None else flight_yaw
        yaw_alignment_error = min(
            abs(flight_yaw - displacement_dir), 360 -
            abs(flight_yaw - displacement_dir)
        )

        return {
            MetadataFieldKey.GIMBAL_OFFSET.value: round(gimbal_offset, DECIMAL_PLACES),
            MetadataFieldKey.THREE_D_SPEED.value: round(speed_3d, DECIMAL_PLACES),
            MetadataFieldKey.SPEED_3D_KMH.value: round(speed_3d * 3.6, 1),
            MetadataFieldKey.YAW_ALIGNMENT_ERROR.value: round(
                yaw_alignment_error, DECIMAL_PLACES
            ),
        }

    @staticmethod
    def _get_light_source_label(light_source: any) -> str:
        """Retorna o texto da fonte de luz a partir do código LightSource EXIF."""
        code = CustomPhotosFieldsUtil.safe_int(light_source, default=0)
        return LightSourceEnum.get_label(code)

    @staticmethod
    def _get_rtk_type_label(rtk_flag: any) -> str:
        """
        Classifica o tipo de sinal RTK baseado no valor do RtkFlag.

        Tabela de classificação DJI:
          0       → Sem GPS         (~10-50 m)
          1-15    → RTK Desconhecido (valores não mapeados)
          16-33   → RTK Single       (~1-5 m)
          34-49   → RTK Float        (~0.1-1 m)
          50      → RTK Fixed        (~1-5 cm)
          others  → RTK Desconhecido
        """
        code = CustomPhotosFieldsUtil.safe_int(rtk_flag, default=0)
        if code == 0:
            return "Sem GPS"
        elif 1 <= code <= 15:
            return "RTK Desconhecido"
        elif 16 <= code <= 33:
            return "RTK Single"
        elif 34 <= code <= 49:
            return "RTK Float"
        elif code == 50:
            return "RTK Fixed"
        else:
            return "RTK Desconhecido"

    @staticmethod
    def _check_light_consistency(light_source: any, cct: any) -> str:
        """Verifica se o valor de CCT está coerente com a fonte de luz declarada."""
        code = CustomPhotosFieldsUtil.safe_int(light_source, default=0)
        cct_value = CustomPhotosFieldsUtil.safe_float(cct, default=0.0)
        if cct_value <= 0:
            return "Unknown"

        expected_ranges = {
            1: (5200, 6500),
            2: (3000, 6500),
            3: (2800, 3200),
            4: (4500, 6500),
            9: (6000, 7500),
            10: (6500, 7500),
            11: (7000, 10000),
            12: (5700, 7100),
            13: (4600, 5400),
            14: (3800, 4500),
            15: (3250, 3800),
            16: (2600, 3250),
            17: (2800, 3300),
            18: (5000, 6500),
            19: (5000, 6500),
            20: (5400, 5600),
            21: (6400, 6600),
            22: (7400, 7600),
            23: (4900, 5100),
            24: (3000, 3300),
        }

        expected = expected_ranges.get(code)
        if expected is None:
            label = CustomPhotosFieldsUtil._get_light_source_label(code)
            if "daylight" in label.lower():
                expected = (5200, 7500)
            elif "fluorescent" in label.lower():
                expected = (2600, 7100)
            elif "shade" in label.lower():
                expected = (7000, 10000)
            elif "tungsten" in label.lower():
                expected = (2600, 3300)
            elif "flash" in label.lower():
                expected = (4500, 6500)
            else:
                return "Unknown"

        low, high = expected
        return "Consistent" if low <= cct_value <= high else "Inconsistent"

    @staticmethod
    def _calculate_rtk_stability_from_absolute(avg_std: float, rtk_flag: any) -> float:
        """
        Calcula RTK Stability Score baseado APENAS nos valores absolutos atuais
        (fallback quando não há foto anterior válida).

        Regras:
          avg_std < 0.01  AND rtk_flag == "50" → 99.5  (fix excelente)
          avg_std < 0.02  AND rtk_flag == "50" → 95.0  (fix normal)
          avg_std < 0.02                       → 90.0  (fix sem confirmação)
          avg_std < 0.05                       → 80.0  (fix com degradação)
          avg_std < 0.10                       → 60.0  (float bom)
          avg_std < 1.00                       → 30.0  (float ruim)
          else                                 →  5.0  (sem RTK)
        """
        rtk_flag_str = str(rtk_flag or "").strip()
        if rtk_flag_str == "50" and avg_std < 0.01:
            return 99.5
        if rtk_flag_str == "50" and avg_std < 0.02:
            return 95.0
        if avg_std < 0.02:
            return 90.0
        if avg_std < 0.05:
            return 80.0
        if avg_std < 0.10:
            return 60.0
        if avg_std < 1.00:
            return 30.0
        return 5.0

    @staticmethod
    def _calculate_quality_scores(
        data: Dict,
        prev_data: Optional[Dict],
        valid_prev: bool,
        prev_seq: Optional[Dict] = None,
        coverage_width: float = 0.0,
        coverage_height: float = 0.0,
        yaw_alignment_error: float = 0.0,
        motion_blur_risk: float = 0.0,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Dict:
        """RTK precision, overlap, ortho score, estabilidade e índices."""
        logger = CustomPhotosFieldsUtil._get_logger(tool_key)
        if prev_seq is None:
            prev_seq = {
                "prev_time_since": 0.0,
                "prev_geodesic_distance": 0.0,
                "prev_distance_3d": 0.0,
                "prev_avg_velocity": 0.0,
                "prev_displacement_direction": 0.0,
            }

        # Garante que RangeMetadataManager está carregado
        try:
            range_metadata_manager.load()
        except Exception as e:
            logger.warning(
                "Falha ao carregar RangeMetadataManager", error=str(e))

        # RTK Precision classificada pelo config.yaml (5 níveis: Excelente, Alta, Média, Baixa, Critica)
        rtk_flag = CustomPhotosFieldsUtil._get(data, MetadataFieldKey.RTK_FLAG)
        rtk_stds = [
            CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.RTK_STD_LON, default=999
            ),
            CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.RTK_STD_LAT, default=999
            ),
            CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.RTK_STD_HGT, default=999
            ),
        ]
        avg_std = sum(rtk_stds) / 3

        # Usa avg_std como proxy da precisão RTK efetiva
        rtk_level, rtk_prec = range_metadata_manager.classify(
            "rtk_effective_precision", avg_std
        )
        logger.debug(
            f"RTK Effective Precision: avg_std={avg_std:.4f}, level={rtk_level}, label='{rtk_prec}'"
        )

        prev_avg_std = 0.0
        if valid_prev and prev_data is not None:
            prev_rtk_stds = [
                CustomPhotosFieldsUtil._get_safe(
                    prev_data, MetadataFieldKey.RTK_STD_LON, default=999
                ),
                CustomPhotosFieldsUtil._get_safe(
                    prev_data, MetadataFieldKey.RTK_STD_LAT, default=999
                ),
                CustomPhotosFieldsUtil._get_safe(
                    prev_data, MetadataFieldKey.RTK_STD_HGT, default=999
                ),
            ]
            prev_avg_std = sum(prev_rtk_stds) / 3
            rtk_stability_score = max(
                0.0,
                100.0 - min(100.0, abs(avg_std - prev_avg_std) * 100.0),
            )
            logger.debug(
                f"RTK Stability (comparativo): avg_std={avg_std:.4f}, prev_avg_std={prev_avg_std:.4f}, "
                f"diff={abs(avg_std - prev_avg_std):.4f}, score={rtk_stability_score:.1f}"
            )
        else:
            # Fallback absoluto: usa apenas os valores RTK atuais quando não há foto anterior válida
            rtk_stability_score = (
                CustomPhotosFieldsUtil._calculate_rtk_stability_from_absolute(
                    avg_std, rtk_flag
                )
            )
            logger.debug(
                f"RTK Stability (absoluto - fallback sem valid_prev): "
                f"avg_std={avg_std:.4f}, rtk_flag={rtk_flag}, score={rtk_stability_score:.1f}"
            )

        # Incidence angle
        gim_pitch = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.GIMBAL_PITCH_DEGREE, default=0
        )
        flight_pitch = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.FLIGHT_PITCH_DEGREE, default=0
        )
        # Effective pitch = gimbal pitch + flight pitch (DJI convention: -90° = nadir)
        # Incidence angle = angle between camera LOS and vertical = |90° - |effective_pitch||
        effective_pitch = gim_pitch + flight_pitch
        inc_angle = round(abs(90.0 - abs(effective_pitch)), DECIMAL_PLACES)

        # Predicted overlap (forward overlap)
        # Em orientação paisagem (landscape), a dimensão na direção do voo é sensor_h → coverage_height
        pred_overlap = 0.0
        if coverage_height > 0:
            if valid_prev:
                # Overlap real: calculado a partir da distância entre fotos consecutivas
                prev_geo = prev_seq.get("prev_geodesic_distance", 0.0)
                pred_overlap = max(
                    0.0,
                    min(
                        100.0,
                        (1.0 - prev_geo / coverage_height) * 100.0,
                    ),
                )
                logger.debug(
                    f"Predicted Overlap (real): geo_dist={prev_geo:.2f}m, cov_height={coverage_height:.2f}m, "
                    f"overlap={pred_overlap:.1f}%"
                )
            else:
                # Fallback sem foto anterior válida: assume 60% como valor esperado
                pred_overlap = float(CustomPhotosFieldsUtil.IDEAL_OVERLAP)
                logger.debug(
                    f"Predicted Overlap (fallback - sem valid_prev): assumindo {pred_overlap:.0f}% "
                    f"(coverage_height={coverage_height:.2f}m)"
                )

        # Ortho score - usa os níveis do RangeMetadataManager (5 classes)
        score = 0
        # rtk_level = 5 (Excelente) ou 4 (Alta)
        if rtk_level >= 4:
            score += 30
        elif rtk_level == 3:
            score += 15
        if inc_angle < 5:
            score += 25
        elif inc_angle < 15:
            score += 15
        # DewarpFlag=0 = SEM DEWARP (critico, nao pontua)
        # None/null/ausente/qualquer outro valor = DEWARP APLICADO (adiciona 20 pontos)
        dewarp_val = CustomPhotosFieldsUtil._get(
            data, MetadataFieldKey.DEWARP_FLAG, default=""
        )
        if str(dewarp_val).strip() != "0":
            score += 20
        if (
            CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.RTK_DIFF_AGE, default=999
            )
            < 2
        ):
            score += 15
        elif (
            CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.RTK_DIFF_AGE, default=999
            )
            < 5
        ):
            score += 8
        if pred_overlap > 70:
            score += 10
        elif pred_overlap > 50:
            score += 5
        ortho_potential = min(100, score)

        # Flags
        abrupt_flag = (
            # ratio default = 1.0 (sem mudança, atualizado no pós-processamento)
            1.0
        )
        ideal_overlap = pred_overlap >= CustomPhotosFieldsUtil.IDEAL_OVERLAP

        # Angular velocity gimbal
        gim_ang_vel = 0.0
        if (
            valid_prev
            and prev_data is not None
            and prev_seq.get("prev_time_since", 0.0) > 0
        ):
            prev_gim_yaw = CustomPhotosFieldsUtil._get_safe(
                prev_data, MetadataFieldKey.GIMBAL_YAW_DEGREE, default=0
            )
            curr_gim_yaw = CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.GIMBAL_YAW_DEGREE, default=0
            )
            yaw_diff = CustomPhotosFieldsUtil.angle_difference(
                curr_gim_yaw, prev_gim_yaw
            )
            gim_ang_vel = yaw_diff / prev_seq.get("prev_time_since", 1.0)

        # Vertical stability
        vertical_stability = 0.0
        if valid_prev and prev_data is not None:
            alt_curr = CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
            )
            alt_prev = CustomPhotosFieldsUtil._get_safe(
                prev_data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
            )
            vertical_stability = abs(alt_curr - alt_prev)

        # Speed variation
        speed_variation_index = 0.0
        if valid_prev and prev_data is not None:
            px = CustomPhotosFieldsUtil._get_abs_speed(
                prev_data, MetadataFieldKey.FLIGHT_X_SPEED, "XSpeed"
            )
            py = CustomPhotosFieldsUtil._get_abs_speed(
                prev_data, MetadataFieldKey.FLIGHT_Y_SPEED, "YSpeed"
            )
            pz = CustomPhotosFieldsUtil._get_abs_speed(
                prev_data, MetadataFieldKey.FLIGHT_Z_SPEED, "ZSpeed"
            )
            prev_speed = math.sqrt(px**2 + py**2 + pz**2)

            cx = CustomPhotosFieldsUtil._get_abs_speed(
                data, MetadataFieldKey.FLIGHT_X_SPEED, "XSpeed"
            )
            cy = CustomPhotosFieldsUtil._get_abs_speed(
                data, MetadataFieldKey.FLIGHT_Y_SPEED, "YSpeed"
            )
            cz = CustomPhotosFieldsUtil._get_abs_speed(
                data, MetadataFieldKey.FLIGHT_Z_SPEED, "ZSpeed"
            )
            current_speed = math.sqrt(cx**2 + cy**2 + cz**2)
            mean_speed = statistics.mean([prev_speed, current_speed])
            if mean_speed > 0:
                speed_variation_index = (
                    statistics.pstdev([prev_speed, current_speed]) / mean_speed
                )

        capture_efficiency = (
            prev_seq.get("prev_geodesic_distance", 0.0) / coverage_height
            if valid_prev and coverage_height > 0
            else 0.0
        )

        # PQI será calculado pelo PqiUtil no pós-processamento (calculate_all_custom_fields)
        # Placeholder: valor temporário que será sobrescrito

        return {
            MetadataFieldKey.RTK_EFFECTIVE_PRECISION.value: rtk_prec,
            MetadataFieldKey.INCIDENCE_ANGLE.value: inc_angle,
            MetadataFieldKey.F_OVERLAP.value: round(pred_overlap, DECIMAL_PLACES),
            MetadataFieldKey.IS_IDEAL_OVERLAP.value: ideal_overlap,
            MetadataFieldKey.ABRUPT_CHANGE_FLAG.value: abrupt_flag,
            MetadataFieldKey.GIMBAL_ANGULAR_VELOCITY.value: round(
                gim_ang_vel, DECIMAL_PLACES
            ),
            MetadataFieldKey.ORTHORECTIFICATION_POTENTIAL.value: round(
                ortho_potential, DECIMAL_PLACES
            ),
            MetadataFieldKey.VERTICAL_STABILITY.value: round(
                vertical_stability, DECIMAL_PLACES
            ),
            MetadataFieldKey.SPEED_VARIATION_INDEX.value: round(
                speed_variation_index, DECIMAL_PLACES
            ),
            MetadataFieldKey.RTK_STABILITY_SCORE.value: round(
                rtk_stability_score, DECIMAL_PLACES
            ),
            MetadataFieldKey.CAPTURE_EFFICIENCY.value: round(
                capture_efficiency, DECIMAL_PLACES
            ),
            # placeholder, atualizado no pós-processamento
            MetadataFieldKey.PHOTOGRAMMETRY_QUALITY_INDEX.value: 0.0,
        }

    @staticmethod
    def _calculate_mrk_differences(data: Dict) -> Dict:
        """
        Calcula as diferenças entre os dados do MRK e os metadados das imagens.

        Campos calculados:
        - X_DIFFERENCE: Diferença entre a Longitude do MRK e a Longitude do GPS do metadado.
        - Y_DIFFERENCE: Diferença entre a Latitude do MRK e a Latitude do GPS do metadado.
        - Z_DIFFERENCE: Diferença entre a Altitude do MRK e a Altitude Absoluta do metadado.
        - XY_DIFFERENCE: Distância planimétrica (2D) via Haversine entre posição MRK e posição do metadado.
        - THREE_D_DIFFERENCE: Distância tridimensional (3D) combinando XY + Z.
        """
        # MRK fields
        mrk_lat = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.LAT, default=0.0
        )
        mrk_lon = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.LON, default=0.0
        )
        mrk_alt = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.ALT, default=0.0
        )

        # Metadata GPS fields (valores reais de latitude e longitude, não as referências N/S, E/W)
        gps_lat = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.GPS_LATITUDE, default=0.0
        )
        gps_lon = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.GPS_LONGITUDE, default=0.0
        )
        abs_alt = CustomPhotosFieldsUtil._get_safe(
            data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0.0
        )

        # Y_DIFFERENCE = Latitude difference (Northing/Y - Norte-Sul)
        y_diff = round(mrk_lat - gps_lat, DECIMAL_PLACES)

        # X_DIFFERENCE = Longitude difference (Easting/X - Leste-Oeste)
        x_diff = round(mrk_lon - gps_lon, DECIMAL_PLACES)

        # Z_DIFFERENCE = Altitude difference (Z - vertical)
        z_diff = round(mrk_alt - abs_alt, DECIMAL_PLACES)

        # XY_DIFFERENCE = Haversine 2D distance between MRK and metadata positions
        xy_diff = 0.0
        if mrk_lat != 0.0 or mrk_lon != 0.0 or gps_lat != 0.0 or gps_lon != 0.0:
            xy_diff = round(
                CustomPhotosFieldsUtil.haversine(
                    mrk_lat, mrk_lon, gps_lat, gps_lon),
                DECIMAL_PLACES,
            )

        # THREE_D_DIFFERENCE = 3D distance combining XY + Z
        three_d_diff = round(math.sqrt(xy_diff**2 + z_diff**2), DECIMAL_PLACES)

        return {
            MetadataFieldKey.X_DIFFERENCE.value: x_diff,
            MetadataFieldKey.Y_DIFFERENCE.value: y_diff,
            MetadataFieldKey.Z_DIFFERENCE.value: z_diff,
            MetadataFieldKey.XY_DIFFERENCE.value: xy_diff,
            MetadataFieldKey.THREE_D_DIFFERENCE.value: three_d_diff,
        }

    @classmethod
    def calculate_all_custom_fields(
        cls,
        metadata_dict: Dict[str, Dict],
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Dict[str, Dict]:
        """Orquestra todos calculos custom."""
        logger = cls._get_logger(tool_key)
        logger.debug(
            f"Iniciando calculo de campos custom para {len(metadata_dict) if metadata_dict else 0} fotos"
        )
        if not metadata_dict:
            return {}

        dt_source_counts = {}
        missing_datetime_count = 0
        for _, data in metadata_dict.items():
            dt, source = cls.resolve_capture_datetime(data or {})
            if dt is None:
                missing_datetime_count += 1
                continue
            dt_source_counts[source] = dt_source_counts.get(source, 0) + 1
            if data.get(MetadataFieldKey.DATE_TIME_ORIGINAL.value) in (
                None,
                "",
                "None",
                "null",
            ):
                data[MetadataFieldKey.DATE_TIME_ORIGINAL.value] = dt.strftime(
                    "%Y:%m:%d %H:%M:%S"
                )
            if data.get(MetadataFieldKey.DT_FULL.value) in (None, "", "None", "null"):
                data[MetadataFieldKey.DT_FULL.value] = dt.strftime(
                    "%Y%m%d%H%M")
            if data.get(MetadataFieldKey.DT_DATE.value) in (None, "", "None", "null"):
                data[MetadataFieldKey.DT_DATE.value] = dt.strftime("%Y%m%d")
            if data.get(MetadataFieldKey.DT_TIME.value) in (None, "", "None", "null"):
                data[MetadataFieldKey.DT_TIME.value] = dt.strftime("%H%M")

        # Ordenar por datetime
        sorted_items = sorted(
            metadata_dict.items(),
            key=lambda x: cls.resolve_capture_datetime(x[1])[
                0] or datetime.max,
        )
        logger.info(
            "Fallback de datetime aplicado no calculo custom",
            code="CUSTOM_FIELDS_DATETIME_FALLBACK",
            data={
                "total_items": len(metadata_dict),
                "missing_datetime_count": missing_datetime_count,
                "datetime_sources": dt_source_counts,
            },
        )

        result = {}
        prev_segment_dir = None
        strip_id = 1
        prev_time_values: List[float] = []
        prev_geo_values: List[float] = []

        for i, (filename, data) in enumerate(sorted_items):
            prev_item = sorted_items[i - 1] if i > 0 else None
            prev_prev_item = sorted_items[i - 2] if i > 1 else None
            next_item = sorted_items[i +
                                     1] if i < len(sorted_items) - 1 else None

            prev_data = prev_item[1] if prev_item else None
            next_data = next_item[1] if next_item else None

            # Validações sequência
            valid_prev = cls.is_valid_sequence(data, prev_data)
            valid_next = cls.is_valid_sequence(
                next_data, data) if next_data else False

            # Logging de diagnóstico para sequência inválida
            if prev_data and not valid_prev:
                voo_curr = cls.get_voo_id(data)
                voo_prev = cls.get_voo_id(prev_data)
                dt_curr, _ = cls.resolve_capture_datetime(data)
                dt_prev, _ = cls.resolve_capture_datetime(prev_data)
                alt_curr = cls._get_safe(
                    data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
                )
                alt_prev = cls._get_safe(
                    prev_data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
                )
                shutter_curr = cls._get_int(
                    data, MetadataFieldKey.SHUTTER_COUNT, default=0
                )
                shutter_prev = cls._get_int(
                    prev_data, MetadataFieldKey.SHUTTER_COUNT, default=0
                )
                logger.debug(
                    f"Sequência inválida para '{filename}': "
                    f"voo_curr={voo_curr}, voo_prev={voo_prev}, "
                    f"dt_curr={dt_curr}, dt_prev={dt_prev}, "
                    f"alt_curr={alt_curr:.1f}, alt_prev={alt_prev:.1f}, "
                    f"shutter_curr={shutter_curr}, shutter_prev={shutter_prev}{prev_prev_item}{valid_next}"
                )

            # Sequência campos
            prev_seq = cls._calculate_sequence_fields(
                data, prev_data, valid_prev, "prev"
            )

            estimated_coverage = cls.calculate_estimated_coverage(data)
            coverage_width, coverage_height = estimated_coverage

            # Campos individuais NOVOS
            individual = cls._calculate_individual_fields(data)

            # Outros
            gim_3d = cls._calculate_gimbal_3d(
                data,
                prev_seq.get(
                    "prev_displacement_direction") if valid_prev else None,
            )
            quality = cls._calculate_quality_scores(
                data,
                prev_data,
                valid_prev,
                prev_seq,
                coverage_width,
                coverage_height,
                gim_3d[MetadataFieldKey.YAW_ALIGNMENT_ERROR.value],
                individual[MetadataFieldKey.MOTION_BLUR_RISK.value],
                tool_key=tool_key,
            )

            current_segment_dir = (
                prev_seq.get(
                    "prev_displacement_direction") if valid_prev else None
            )
            trajectory_smoothness = 0.0
            if current_segment_dir is not None and prev_segment_dir is not None:
                trajectory_smoothness = cls.angle_difference(
                    current_segment_dir, prev_segment_dir
                )
                if trajectory_smoothness > cls.STRIP_CHANGE_THRESHOLD:
                    strip_id += 1

            if current_segment_dir is not None:
                prev_segment_dir = current_segment_dir

            # Monta dicionário custom apenas com campos mapeados em MetadataFields.CUSTOM_FIELDS
            # FlightAltitude = altura efetiva (LRF corrigido > RelativeAltitude)
            fly_alt = CustomPhotosFieldsUtil._get_effective_height(data)

            # GroundElevation = AbsoluteAltitude - FlightAltitude
            # Com LRF: AbsZ - (LRFDist * cos(incidence))
            # Sem LRF: AbsZ - RelativeAltitude
            abs_alt = CustomPhotosFieldsUtil._get_safe(
                data, MetadataFieldKey.ABSOLUTE_ALTITUDE, default=0
            )
            ground_elevation = abs_alt - fly_alt if fly_alt > 0 and abs_alt > 0 else 0.0

            # EV Classification (texto)
            ev_calculated = individual.get(
                MetadataFieldKey.EXPOSURE_VALUE_EV.value, 0.0
            )
            ev_classification = EvClassEnum.get_label(ev_calculated)

            # MRK differences (MRK vs Metadata GPS)
            mrk_diffs = cls._calculate_mrk_differences(data)

            custom = {
                **individual,
                **quality,
                **mrk_diffs,
                MetadataFieldKey.GROUND_ELEVATION.value: round(
                    ground_elevation, DECIMAL_PLACES
                ),
                MetadataFieldKey.EV_CLASSIFICATION.value: ev_classification,
                MetadataFieldKey.GIMBAL_OFFSET.value: round(
                    gim_3d[MetadataFieldKey.GIMBAL_OFFSET.value], DECIMAL_PLACES
                ),
                MetadataFieldKey.THREE_D_SPEED.value: round(
                    gim_3d[MetadataFieldKey.THREE_D_SPEED.value], DECIMAL_PLACES
                ),
                MetadataFieldKey.SPEED_3D_KMH.value: round(
                    gim_3d[MetadataFieldKey.SPEED_3D_KMH.value], 1
                ),
                MetadataFieldKey.YAW_ALIGNMENT_ERROR.value: round(
                    gim_3d[MetadataFieldKey.YAW_ALIGNMENT_ERROR.value], DECIMAL_PLACES
                ),
                MetadataFieldKey.TIME_SINCE_PREVIOUS.value: round(
                    prev_seq.get("prev_time_since", 0.0), DECIMAL_PLACES
                ),
                MetadataFieldKey.GEODESIC_DISTANCE_PREVIOUS.value: round(
                    prev_seq.get("prev_geodesic_distance", 0.0), DECIMAL_PLACES
                ),
                MetadataFieldKey.DISTANCE_3D_PREVIOUS.value: round(
                    prev_seq.get("prev_distance_3d", 0.0), DECIMAL_PLACES
                ),
                MetadataFieldKey.AVG_VELOCITY_BETWEEN_PHOTOS.value: round(
                    prev_seq.get("prev_avg_velocity", 0.0), DECIMAL_PLACES
                ),
                MetadataFieldKey.DISPLACEMENT_DIRECTION.value: round(
                    prev_seq.get("prev_displacement_direction",
                                 0.0), DECIMAL_PLACES
                ),
                MetadataFieldKey.F_OVERLAP.value: round(
                    quality[MetadataFieldKey.F_OVERLAP.value], DECIMAL_PLACES
                ),
                MetadataFieldKey.COVERAGE_WIDTH.value: round(
                    coverage_width, DECIMAL_PLACES
                ),
                MetadataFieldKey.COVERAGE_HEIGHT.value: round(
                    coverage_height, DECIMAL_PLACES
                ),
                MetadataFieldKey.TRAJECTORY_SMOOTHNESS.value: round(
                    trajectory_smoothness, DECIMAL_PLACES
                ),
                MetadataFieldKey.STRIP_ID.value: strip_id,
                MetadataFieldKey.FLIGHT_ALTITUDE.value: round(fly_alt, DECIMAL_PLACES),
                MetadataFieldKey.LIGHT_SOURCE_CLASSIFICATION.value: cls._get_light_source_label(
                    data.get(MetadataFieldKey.LIGHT_SOURCE.value)
                ),
                MetadataFieldKey.LIGHT_CONSISTENCY.value: cls._get_light_source_label(
                    data.get(MetadataFieldKey.LIGHT_SOURCE.value)
                ),
                MetadataFieldKey.RTK_TYPE.value: cls._get_rtk_type_label(
                    data.get(MetadataFieldKey.RTK_FLAG.value)
                ),
            }

            # Nota: next_seq e validation NÃO são incluídos em custom pois não têm
            # entrada correspondente em MetadataFields.CUSTOM_FIELDS, evitando
            # campos-fantasma no shapefile.

            if valid_prev:
                prev_time_values.append(
                    custom[MetadataFieldKey.TIME_SINCE_PREVIOUS.value]
                )
                prev_geo_values.append(
                    custom[MetadataFieldKey.GEODESIC_DISTANCE_PREVIOUS.value]
                )

            result[filename] = {**data, **custom}

        # Garantir que os campos brutos de velocidade sejam absolutos (evitar valores negativos no output)
        for filename, item in result.items():
            for speed_key in (
                MetadataFieldKey.FLIGHT_X_SPEED.value,
                MetadataFieldKey.FLIGHT_Y_SPEED.value,
                MetadataFieldKey.FLIGHT_Z_SPEED.value,
                "XSpeed",
                "YSpeed",
                "ZSpeed",
            ):
                if speed_key in item and item[speed_key] is not None:
                    item[speed_key] = abs(
                        CustomPhotosFieldsUtil.safe_float(item[speed_key], 0.0)
                    )

        # Pós-processamento: PQI via PqiUtil e classifica AbruptChangeFlag
        try:
            range_metadata_manager.load()
        except Exception as e:
            logger.warning(
                "Falha ao carregar RangeMetadataManager no pos-processamento", error=str(e))
        median_time = statistics.median(
            prev_time_values) if prev_time_values else 0.0
        median_geo = statistics.median(
            prev_geo_values) if prev_geo_values else 0.0
        for filename, item in result.items():
            # 1. Calcula PQI via PqiUtil (score orquestrado por indicadores com pesos)
            try:
                pqi_score, pqi_details = PqiUtil.calculate(
                    item, tool_key=tool_key)
                item[MetadataFieldKey.PHOTOGRAMMETRY_QUALITY_INDEX.value] = pqi_score
            except Exception as exc:
                logger.warning(f"Falha ao calcular PQI para {filename}: {exc}")
                item[MetadataFieldKey.PHOTOGRAMMETRY_QUALITY_INDEX.value] = 0.0

            # 2. Classifica AbruptChangeFlag como texto
            time_ratio = 1.0
            geo_ratio = 1.0
            if median_time > 0:
                time_val = item.get(
                    MetadataFieldKey.TIME_SINCE_PREVIOUS.value, 0.0)
                time_ratio = time_val / median_time if time_val > 0 else 1.0
            if median_geo > 0:
                geo_val = item.get(
                    MetadataFieldKey.GEODESIC_DISTANCE_PREVIOUS.value, 0.0
                )
                geo_ratio = geo_val / median_geo if geo_val > 0 else 1.0
            abrupt_ratio = max(time_ratio, geo_ratio)
            _, abrupt_label = range_metadata_manager.classify(
                "abrupt_change_flag", abrupt_ratio
            )
            item[MetadataFieldKey.ABRUPT_CHANGE_FLAG.value] = abrupt_label

        return result
