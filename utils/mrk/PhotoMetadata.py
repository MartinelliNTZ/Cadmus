# -*- coding: utf-8 -*-
import os
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsPointXY,
)

from ...core.config.LogUtils import LogUtils
from ...core.enum import MetadataFieldKey
from ...utils.ExplorerUtils import ExplorerUtils
from ...utils.JsonUtil import JsonUtil
from ...utils.ToolKeys import ToolKey
from ...utils.vector.VectorLayerProjection import VectorLayerProjection
from .CustomPhotosFieldsUtil import CustomPhotosFieldsUtil
from .ExifUtil import ExifUtil
from .InitialParamsUtil import InitialParamsUtil
from .MetadataFields import MetadataFields
from .MrkUtil import MrkUtil
from .XmpUtil import XmpUtil


class PhotoMetadata:
    """
    Orquestrador puro de metadados de fotos - Pipeline Pattern.

    RESPONSABILIDADE ÚNICA:
    Executa um pipeline linear de enriquecimentos sucessivos sobre as fotos.
    Cada etapa do pipeline pode ser ativada/desativada via flags.

    PIPELINE (etapas internas ao run_pipeline):
      Etapa 0 – Parsing MRK (opcional): se paths MRK fornecidos, parseia arquivos
      Etapa 1 – Esqueleto inicial (sempre): delega para InitialParamsUtil
      Etapa 2 – Enriquecimento MRK (opcional): cruza com pontos MRK
      Etapa 3 – EXIF (opcional): extrai metadados EXIF
      Etapa 4 – XMP (opcional): extrai metadados XMP
      Etapa 5 – Campos customizados (opcional): calcula campos derivados

    APÓS o pipeline, o JSON é construído e salvo via build_and_save_json().
    A task/step apenas invoca e obtém o caminho do JSON.

    NÃO faz:
    - Field filtering (responsabilidade da task/step que invoca)
    - Vetorização (responsabilidade do JsonVectorizationStep)
    """

    DJI_RE = re.compile(r"_(\d{4})_[A-Z]\.JPG$", re.IGNORECASE)

    # Cache de timestamps de extracao
    _timestamps: Dict[str, str] = {}

    # Cache da primeira foto com coordenadas (lat, lon raw)
    _first_photo_raw_coord: Optional[Dict[str, float]] = None

    @staticmethod
    def get_timestamps() -> Dict[str, str]:
        return dict(PhotoMetadata._timestamps)

    @staticmethod
    def clear_timestamps():
        PhotoMetadata._timestamps = {}
        PhotoMetadata._first_photo_raw_coord = None

    @staticmethod
    def _get_logger(tool_key: str) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="PhotoMetadata")

    # ─────────────────────────────────────────────
    # API PÚBLICA - Pipeline completo
    # ─────────────────────────────────────────────

    @staticmethod
    def run_pipeline(
        base_folder: str,
        points: Optional[List[Dict[str, Any]]] = None,
        recursive: bool = True,
        tool_key: str = "drone_coordinates",
        *,
        mrk_paths: Optional[List[str]] = None,
        enable_mrk: bool = False,
        enable_exif: bool = True,
        enable_xmp: bool = True,
        enable_custom_fields: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Pipeline unificado de enriquecimento de fotos.

        Args:
            base_folder: Pasta raiz onde as fotos estão localizadas
            points: Lista de pontos MRK (opcional, pré-parseados)
            recursive: Se deve varrer subpastas recursivamente
            tool_key: Chave da ferramenta para logging
            mrk_paths: Lista de caminhos de arquivos/pastas MRK para parsear
            enable_mrk: Habilita enriquecimento MRK
            enable_exif: Habilita extração EXIF
            enable_xmp: Habilita extração XMP
            enable_custom_fields: Habilita campos customizados

        Returns:
            Tuple de (lista de registros, dict de qualidade)
        """
        logger = PhotoMetadata._get_logger(tool_key)
        logger.info(
            "Iniciando pipeline de metadados",
            data={
                "base_folder": base_folder,
                "recursive": recursive,
                "has_points": len(points) if points else 0,
                "has_mrk_paths": len(mrk_paths) if mrk_paths else 0,
                "enable_mrk": enable_mrk,
                "enable_exif": enable_exif,
                "enable_xmp": enable_xmp,
                "enable_custom_fields": enable_custom_fields,
            },
        )

        PhotoMetadata.clear_timestamps()
        pipeline_start = datetime.now().isoformat()

        # ── Etapa 1: Esqueleto inicial via InitialParamsUtil (dict em memoria) ──
        initial_start = datetime.now().isoformat()
        initial_result = InitialParamsUtil.build_initial_json(
            base_folder=base_folder,
            tool_key=tool_key,
            recursive=recursive,
        )

        if not initial_result or initial_result.get("total_files", 0) == 0:
            logger.warning("Nenhuma foto encontrada no diretorio")
            return [], {
                "total_files": 0,
                "with_xmp": 0,
                "with_mrk": 0,
                "with_exif_gps": 0,
            }

        skeleton = initial_result.get("skeleton", {})

        if not skeleton:
            logger.warning("Nenhum registro valido no JSON inicial")
            return [], {
                "total_files": 0,
                "with_xmp": 0,
                "with_mrk": 0,
                "with_exif_gps": 0,
            }
        initial_end = datetime.now().isoformat()

        # ── Etapa 2: Enriquecimento MRK (opcional) ──
        mrk_start = datetime.now().isoformat()
        mrk_points = points or []
        if enable_mrk and mrk_paths and not mrk_points:
            mrk_points = PhotoMetadata._parse_mrk_paths(
                mrk_paths, recursive, tool_key)

        if enable_mrk and mrk_points:
            skeleton = PhotoMetadata._enrich_with_mrk(
                skeleton, mrk_points, base_folder, tool_key
            )
        mrk_end = datetime.now().isoformat()
        exif_start = datetime.now().isoformat()

        # ── Etapa 3: EXIF (opcional, padrão: True) ──
        if enable_exif:
            skeleton = PhotoMetadata._enrich_exif(skeleton, tool_key)
        exif_end = datetime.now().isoformat()

        xmp_start = datetime.now().isoformat()

        # ── Etapa 4: XMP (opcional, padrão: True) ──
        if enable_xmp:
            skeleton = PhotoMetadata._enrich_xmp(skeleton, tool_key)
        xmp_end = datetime.now().isoformat()

        # Converte dict para lista de records e normaliza coordenadas
        all_records = []
        quality = {
            "total_files": len(skeleton),
            "with_xmp": 0,
            "with_mrk": 0,
            "with_exif_gps": 0,
        }

        for filename, payload in skeleton.items():
            if not payload:
                continue

            merged = MetadataFields.normalize_record_to_keys(payload)

            # MRK já vem em Lat/Lon/Alt (decimais) - mantém como está
            # EXIF DMS→decimal já foi convertido em _enrich_exif() (GpsLatRef/GpsLongRef)
            # XMP GpsLatitude/GpsLongitude (float) já sobrescreveu se existir

            # Se GpsLatitude/GpsLongitude ainda são tupla DMS (sem XMP para coordenadas),
            # converte para float decimal usando GpsLatitudeRef/GpsLongitudeRef
            gps_lat = merged.get(MetadataFieldKey.GPS_LATITUDE.value)
            gps_lon = merged.get(MetadataFieldKey.GPS_LONGITUDE.value)

            if isinstance(gps_lat, (list, tuple)):
                dec_val = PhotoMetadata._to_float(
                    merged.get(MetadataFieldKey.GPS_LATITUDE_REF.value)
                )
                if dec_val is not None:
                    merged[MetadataFieldKey.GPS_LATITUDE.value] = dec_val
            if isinstance(gps_lon, (list, tuple)):
                dec_val = PhotoMetadata._to_float(
                    merged.get(MetadataFieldKey.GPS_LONGITUDE_REF.value)
                )
                if dec_val is not None:
                    merged[MetadataFieldKey.GPS_LONGITUDE.value] = dec_val

            # Heurísticas de qualidade
            has_mrk = merged.get(MetadataFieldKey.COORD_SOURCE.value) == "MRK"
            has_xmp = any(
                k in merged
                for k in [
                    MetadataFieldKey.ABSOLUTE_ALTITUDE.value,
                    MetadataFieldKey.RELATIVE_ALTITUDE.value,
                    MetadataFieldKey.GIMBAL_YAW_DEGREE.value,
                    MetadataFieldKey.RTK_FLAG.value,
                ]
            )
            has_exif_gps = (
                merged.get(MetadataFieldKey.GPS_LATITUDE.value) is not None
                or merged.get(MetadataFieldKey.GPS_LONGITUDE.value) is not None
            )

            merged["HasXmp"] = has_xmp
            merged["HasExifGps"] = has_exif_gps

            if has_xmp:
                quality["with_xmp"] += 1
            if has_mrk:
                quality["with_mrk"] += 1
            if has_exif_gps:
                quality["with_exif_gps"] += 1

            all_records.append(merged)

        # ── Etapa 6: Extrair coordenadas raw da primeira foto (sempre) ──
        # Percorre os records enriquecidos e salva lat/lon da primeira
        # foto que possui coordenadas válidas. Usado posteriormente por
        # ReverseGeocodeStep e AltimetryStep (via context).
        PhotoMetadata._first_photo_raw_coord = None
        for record in all_records:
            lat = PhotoMetadata._to_float(
                record.get(MetadataFieldKey.GPS_LATITUDE.value)
            )
            lon = PhotoMetadata._to_float(
                record.get(MetadataFieldKey.GPS_LONGITUDE.value)
            )
            if lat is not None and lon is not None:
                PhotoMetadata._first_photo_raw_coord = {"lat": lat, "lon": lon}
                logger.info(
                    "Etapa 6: primeira foto com coordenadas encontrada",
                    data={"lat": lat, "lon": lon},
                )
                break

        # Timestamps: inicio calculo campos custom
        custom_start = datetime.now().isoformat()

        # ── Etapa 5: Campos customizados (opcional, padrão: True) ──
        if enable_custom_fields:
            all_records = PhotoMetadata._calculate_custom_fields(
                all_records, tool_key, logger
            )

        # Timestamps: fim calculo campos custom
        custom_end = datetime.now().isoformat()

        # Determina a source com base nos dados processados
        has_mrk_data = enable_mrk and bool(mrk_points)
        source = "mrk+photo" if has_mrk_data else "photo"

        logger.info(
            "Pipeline concluido",
            data={
                "source": source,
                "total_records": len(all_records),
                "quality": quality,
            },
        )

        PhotoMetadata._timestamps = {
            "pipeline_start": pipeline_start,
            "initial_start": initial_start,
            "initial_end": initial_end,
            "mrk_start": mrk_start,
            "mrk_end": mrk_end,
            "exif_start": exif_start,
            "exif_end": exif_end,
            "xmp_start": xmp_start,
            "xmp_end": xmp_end,
            "custom_start": custom_start,
            "custom_end": custom_end,
        }

        return all_records, quality

    @staticmethod
    def build_and_save_json(
        records: List[Dict[str, Any]],
        source: str,
        base_folder: str,
        tool_key: str,
        recursive: bool = False,
        quality: Optional[Dict[str, Any]] = None,
        project_title: str = "",
        logo_path: str = "",
    ) -> str:
        """
        Constrói o JSON v2.0 a partir dos records enriquecidos e salva em disco.

        Args:
            records: Lista de registros (já filtrados e convertidos para PascalCase)
            source: Fonte dos dados (photo, mrk+photo)
            base_folder: Pasta base das fotos
            tool_key: Chave da ferramenta
            recursive: Se a busca foi recursiva
            quality: Dict opcional com estatísticas de qualidade
            project_title: Título do projeto (ex: "Fazenda Esperança")
            logo_path: Caminho da imagem/logo do projeto

        Returns:
            Caminho absoluto do arquivo JSON salvo
        """
        logger = PhotoMetadata._get_logger(tool_key)
        timestamps = PhotoMetadata.get_timestamps()

        # Constrói JSON v2.0
        json_data = JsonUtil.build(
            records=records,
            source=source,
            base_folder=base_folder,
            tool_key=tool_key,
            recursive=recursive,
            timestamps=timestamps if timestamps else None,
            project_title=project_title,
            logo_path=logo_path,
        )

        # Adiciona quality stats se fornecidas
        if quality:
            json_data["quality"] = quality

        # Define prefixo do nome do arquivo
        if source == "mrk+photo":
            prefix = "DPM"
        elif source == "photo":
            prefix = "PFM"
        else:
            prefix = "SKL"

        json_path = ExplorerUtils.create_temp_json(
            json_data,
            tool_key=tool_key,
            prefix=prefix,
            subfolder=os.path.join(
                ExplorerUtils.REPORTS_TEMP_FOLDER,
                ExplorerUtils.REPORTS_JSON_FOLDER,
            ),
            file_stem_hint=ExplorerUtils.build_report_json_stem(
                base_folder=base_folder,
                points_total=len(records),
            ),
        )

        logger.info(
            "JSON salvo via PhotoMetadata",
            data={
                "json_path": json_path,
                "source": source,
                "total_records": len(records),
            },
        )

        return json_path

    # ─────────────────────────────────────────────
    # ETAPA 0: Parsing MRK
    # ─────────────────────────────────────────────

    @staticmethod
    def _parse_mrk_paths(
        mrk_paths: List[str],
        recursive: bool,
        tool_key: str,
    ) -> List[Dict[str, Any]]:
        """
        Parseia paths de arquivos/pastas MRK e retorna lista de pontos.
        """
        logger = PhotoMetadata._get_logger(tool_key)
        all_records = []

        for path in mrk_paths:
            if os.path.isfile(path) and path.lower().endswith(".mrk"):
                records = MrkUtil.extract_records(path)
                logger.info(
                    f"Encontrados {len(records)} registros no arquivo {path}")
            else:
                base = path
                if os.path.isfile(path):
                    base = os.path.dirname(path)
                if not os.path.isdir(base):
                    continue
                records = MrkUtil.extract_folder(base, recursive=recursive)
                logger.info(f"Encontrados {len(records)} registros em {base}")

            all_records.extend(records)

        logger.info(f"Total de {len(all_records)} pontos extraidos de MRK")
        return all_records

    # ─────────────────────────────────────────────
    # ETAPA 2: Enriquecimento MRK
    # ─────────────────────────────────────────────

    @staticmethod
    def _enrich_with_mrk(
        skeleton: Dict[str, dict],
        points: List[Dict[str, Any]],
        base_folder: str,
        tool_key: str,
    ) -> Dict[str, dict]:
        """
        Etapa 2 – Enriquecimento MRK.

        Para cada ponto MRK, busca no skeleton a foto cujo filename
        contém a sequência correspondente. O match é feito pela
        sequência numérica extraída do filename (ex.: 0001 de
        DJI_..._0001_V.JPG).

        Diferente da abordagem anterior (que tentava filtrar por
        FolderLevel1), agora buscamos em TODAS as fotos do skeleton.
        Isso resolve o caso onde MRK e fotos estão em pastas diferentes
        mas com a mesma estrutura de numeração.
        """
        logger = PhotoMetadata._get_logger(tool_key)

        # Rastreia quais fotos do skeleton receberam MRK
        matched_filenames: set = set()
        matched_count = 0

        # Para cada ponto MRK, busca a foto correspondente no skeleton
        for point in points:
            foto = point.get(MetadataFieldKey.FOTO.value) or point.get("foto")
            if foto is None:
                continue

            try:
                seq = f"{int(foto):04d}"
            except (ValueError, TypeError) as e:
                logger.debug(f"Erro ao processar foto {foto}: {e}")
                continue

            # Extrai dados do MRK para log de diagnostico
            mrk_file = point.get(MetadataFieldKey.MRK_FILE.value) or "?"
            mrk_folder = point.get(MetadataFieldKey.MRK_FOLDER.value) or "?"
            logger.debug(
                f"Processando ponto MRK: {mrk_file} / {mrk_folder} / foto={foto} / seq={seq}")
            # Procura no skeleton por fotos cujo nome contenha a sequência
            for filename, record in skeleton.items():
                seq_match = PhotoMetadata.DJI_RE.search(filename)
                if not seq_match:
                    continue
                filename_seq = seq_match.group(1)

                if filename_seq == seq:
                    # Verifica se já foi enriquecido por MRK (evita sobrescrita)
                    if record.get(MetadataFieldKey.COORD_SOURCE.value) == "MRK":
                        continue

                    # Enriquece o registro com dados MRK
                    flight_context = PhotoMetadata._extract_flight_context(
                        point)
                    for k, v in flight_context.items():
                        if v is not None:
                            record[k] = v

                    # Garante CoordSource e QualityFlag para rastreabilidade
                    record[MetadataFieldKey.COORD_SOURCE.value] = "MRK"
                    record[MetadataFieldKey.QUALITY_FLAG.value] = "OK"

                    matched_filenames.add(filename)
                    matched_count += 1
                    break

        # ── LOG DE DIAGNÓSTICO: fotos que NÃO receberam MRK ──
        unmatched_count = 0
        for filename, record in skeleton.items():
            if record.get(MetadataFieldKey.COORD_SOURCE.value) != "MRK":
                unmatched_count += 1
                # Só loga as primeiras 20 unmatched para nao poluir
                if unmatched_count <= 20:
                    folder = record.get(
                        MetadataFieldKey.FOLDER_LEVEL_1.value, "?")
                    logger.debug(
                        "Foto SEM match MRK",
                        data={
                            "filename": filename,
                            "folder": folder,
                            "seq": PhotoMetadata.DJI_RE.search(filename).group(1)
                            if PhotoMetadata.DJI_RE.search(filename)
                            else "N/A",
                        },
                    )

        logger.info(
            "Enriquecimento MRK concluido",
            data={
                "total_points": len(points),
                "matched_photos": matched_count,
                "unmatched_photos": unmatched_count,
                "total_photos_in_skeleton": len(skeleton),
            },
        )

        return skeleton

    # ─────────────────────────────────────────────
    # ETAPA 3: EXIF
    # ─────────────────────────────────────────────

    @staticmethod
    def _enrich_exif(
        skeleton: Dict[str, dict],
        tool_key: str,
    ) -> Dict[str, dict]:
        """
        Etapa 3 – Extração EXIF.

        Além da extração padrão, converte coordenadas DMS (EXIF bruto) para decimal.

        Mapeamento final:
        - GpsLatitude (atributo "GpsLat"): mantém tupla DMS do EXIF (RAW)
        - GpsLatitudeRef (atributo "GpsLatRef"): S/N → convertido para decimal com sinal
        - GpsLongitude (atributo "GPSLong"): mantém tupla DMS do EXIF (RAW)
        - GpsLongitudeRef (atributo "GpsLongRef"): E/W → convertido para decimal com sinal

        A conversão é feita AQUI, ANTES do XMP, para que o XMP possa sobrescrever
        GpsLatitude/GpsLongitude sem perder a coordenada decimal do EXIF.
        """
        logger = PhotoMetadata._get_logger(tool_key)

        for filename, record in skeleton.items():
            image_path = record.get(MetadataFieldKey.PATH.value)
            if not image_path or not os.path.exists(image_path):
                continue

            try:
                exif_payload = ExifUtil.extract_metadata_exif(
                    image_path, tool_key=tool_key
                )
                os_payload = ExifUtil.extract_metadata_os(
                    image_path, tool_key=tool_key)
                image_payload = ExifUtil.extract_metadata_image(
                    image_path, tool_key=tool_key
                )

                for payload in [exif_payload, os_payload, image_payload]:
                    for k, v in payload.items():
                        if k not in record or record.get(k) in (
                            None,
                            "",
                            "None",
                            "null",
                        ):
                            record[k] = v

                # A conversão DMS→decimal já é feita pelo ExifUtil.extract_metadata_exif()
                # GpsLatRef / GpsLongRef já vêm como decimal com sinal
                # GpsLat / GpsLong mantêm a tupla DMS original (RAW)

                dt = PhotoMetadata._safe_parse_datetime(
                    record.get(MetadataFieldKey.DATE_TIME_ORIGINAL.value)
                    or record.get("DateTime")
                )
                if dt is not None:
                    if record.get(MetadataFieldKey.DATE_TIME_ORIGINAL.value) in (
                        None,
                        "",
                        "None",
                        "null",
                    ):
                        record[MetadataFieldKey.DATE_TIME_ORIGINAL.value] = dt.strftime(
                            "%Y:%m:%d %H:%M:%S"
                        )

            except Exception as exc:
                logger.warning(
                    f"Falha ao extrair EXIF de {filename}: {exc}", code="EXIF_EXTRACT_ERROR")

        return skeleton

    # ─────────────────────────────────────────────
    # ETAPA 4: XMP
    # ─────────────────────────────────────────────

    @staticmethod
    def _enrich_xmp(
        skeleton: Dict[str, dict],
        tool_key: str,
    ) -> Dict[str, dict]:
        """
        Etapa 4 – Extração XMP.

        Lê os metadados XMP de cada foto (quando disponíveis) e incorpora
        informações como altitude relativa, guinada do gimbal, flag RTK, etc.
        Os aliases DJI são resolvidos pelo XmpUtil.extract_metadata.

        Regras de sobrescrita:
        - GpsLat (GpsLatitude) / GPSLong (GpsLongitude):
            SEMPRE sobrescritos pelo XMP se disponíveis (float).
            Se não houver XMP, mantém a tupla DMS do EXIF.
        - GpsLatRef (GpsLatitudeRef) / GpsLongRef (GpsLongitudeRef):
            NUNCA sobrescritos pelo XMP. São EXCLUSIVOS do EXIF (decimal com sinal).
        """
        logger = PhotoMetadata._get_logger(tool_key)

        for filename, record in skeleton.items():
            image_path = record.get(MetadataFieldKey.PATH.value)
            if not image_path or not os.path.exists(image_path):
                continue

            try:
                xmp_payload = XmpUtil.extract_metadata(
                    image_path, tool_key=tool_key)
                # XmpUtil já resolve os aliases internamente

                # Mescla campos XMP (APENAS campos que não são do EXIF)
                # GpsLatRef/GpsLongRef são EXCLUSIVOS do EXIF, NUNCA sobrescritos
                exif_exclusive = {"GpsLatRef", "GpsLongRef"}

                for k, v in xmp_payload.items():
                    if k in exif_exclusive:
                        continue  # NUNCA sobrescreve campos exclusivos do EXIF
                    # Sobrescreve GpsLat/GPSLong com XMP (float sobrescreve tupla DMS)
                    if k in ("GpsLat", "GPSLong") and v is not None:
                        record[k] = v
                    elif k not in record or record.get(k) in (None, "", "None", "null"):
                        record[k] = v

            except Exception as exc:
                logger.warning(
                    f"Falha ao extrair XMP de {filename}: {exc}", code="XMP_EXTRACT_ERROR")

        return skeleton

    # ─────────────────────────────────────────────
    # ETAPA 5: Campos customizados
    # ─────────────────────────────────────────────

    @staticmethod
    def _calculate_custom_fields(
        all_records: List[Dict[str, Any]],
        tool_key: str,
        logger: LogUtils,
    ) -> List[Dict[str, Any]]:
        """
        Etapa 5 – Campos customizados.

        Agrupa por FolderLevel1 e calcula campos derivados.
        """
        try:
            grouped_records: Dict[str, List[Dict]] = {}
            for r in all_records:
                if r.get(MetadataFieldKey.DATE_TIME_ORIGINAL.value) in (None, ""):
                    continue
                group_key = str(
                    r.get(MetadataFieldKey.FOLDER_LEVEL_1.value) or "__NO_FOLDER__"
                )
                if group_key not in grouped_records:
                    grouped_records[group_key] = []
                grouped_records[group_key].append(r)

            for group_key, group in grouped_records.items():
                logger.debug(
                    f"Processando campos custom para grupo '{group_key}' ({len(group)} fotos)"
                )
                custom_ready = {
                    r.get(MetadataFieldKey.FILE.value): r for r in group}
                if custom_ready:
                    enriched = CustomPhotosFieldsUtil.calculate_all_custom_fields(
                        custom_ready, tool_key=tool_key
                    )
                    for fname, custom_values in enriched.items():
                        for record in all_records:
                            if record.get(MetadataFieldKey.FILE.value) == fname:
                                record.update(custom_values)
                                break

        except Exception as exc:
            logger.warning(
                f"Falha ao calcular campos custom: {exc}", code="CUSTOM_FIELDS_ERROR")

        return all_records

    # ─────────────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────────────

    @staticmethod
    def enrich_first_photo_coord(json_path: str) -> Optional[Dict[str, Any]]:
        """
        Enriquece as coordenadas da primeira foto com EPSG, zona UTM e hemisfério.

        Lê as coordenadas raw do cache (setadas pela Etapa 6 do run_pipeline()),
        chama VectorLayerProjection.get_coordinate_info() e salva no JSON via
        JsonUtil.update_json().

        Deve ser chamado no main thread (usa QgsPointXY / QgsCoordinateReferenceSystem).

        Args:
            json_path: Caminho do JSON de metadados

        Returns:
            Dict com lat, lon, epsg, zona_num, zona_letra, hemisferio, etc.,
            ou None se não houver coordenadas disponíveis.
        """
        raw_coord = PhotoMetadata._first_photo_raw_coord
        if not raw_coord:
            return None

        lat = raw_coord["lat"]
        lon = raw_coord["lon"]

        point = QgsPointXY(lon, lat)
        crs_wgs = QgsCoordinateReferenceSystem("EPSG:4326")

        coord_info = VectorLayerProjection.get_coordinate_info(point, crs_wgs)

        # Salva no JSON usando update_json() genérico
        if json_path and os.path.exists(json_path):
            try:
                JsonUtil.update_json(
                    json_path, {"first_photo_coord": coord_info})
            except Exception as e:
                LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PhotoMetadata").debug(
                    "Falha ao atualizar JSON do first_photo_coord", error=str(e)
                )

        return coord_info

    @staticmethod
    def _extract_flight_context(point: dict) -> dict:
        """Extrai contexto de voo de um ponto MRK."""
        canonical = MetadataFields.normalize_record_to_keys(point or {})
        return {
            MetadataFieldKey.FLIGHT_NUMBER.value: canonical.get(
                MetadataFieldKey.FLIGHT_NUMBER.value
            ),
            MetadataFieldKey.FLIGHT_NAME.value: canonical.get(
                MetadataFieldKey.FLIGHT_NAME.value
            ),
            MetadataFieldKey.MRK_FILE.value: canonical.get(
                MetadataFieldKey.MRK_FILE.value
            ),
            MetadataFieldKey.MRK_PATH.value: canonical.get(
                MetadataFieldKey.MRK_PATH.value
            ),
            MetadataFieldKey.MRK_FOLDER.value: canonical.get(
                MetadataFieldKey.MRK_FOLDER.value
            ),
            MetadataFieldKey.DATE_NAME.value: canonical.get(
                MetadataFieldKey.DATE_NAME.value
            ),
            MetadataFieldKey.FOTO.value: canonical.get(MetadataFieldKey.FOTO.value),
            MetadataFieldKey.LAT.value: canonical.get(MetadataFieldKey.LAT.value),
            MetadataFieldKey.LON.value: canonical.get(MetadataFieldKey.LON.value),
            MetadataFieldKey.ALT.value: canonical.get(MetadataFieldKey.ALT.value),
        }

    @staticmethod
    def _extract_position(
        merged_payload: dict,
    ) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
        """
        Extrai posição GPS do payload mesclado.
        Retorna (lat, lon, alt, source).

        Ordem de resolução:
        1. MRK (Lat/Lon) → já mapeado para GpsLatitude/GpsLongitude pelo pipeline
        2. XMP (drone-dji:AbsoluteAltitude, etc) → já mapeado para GpsLatitude/GpsLongitude
        3. EXIF DMS (tupla graus/min/seg) → convertido para decimal usando GpsLatitudeRef/GpsLongitudeRef
        """
        canonical = MetadataFields.normalize_record_to_keys(
            merged_payload or {})

        # --- Tentativa 1: Valor já é float (XMP ou MRK) ---
        lat_val = canonical.get(MetadataFieldKey.GPS_LATITUDE.value)
        lon_val = canonical.get(MetadataFieldKey.GPS_LONGITUDE.value)

        lat = PhotoMetadata._to_float(lat_val)
        lon = PhotoMetadata._to_float(lon_val)

        # --- Tentativa 2: Se é tupla/list (DMS do EXIF bruto), converte ---
        if lat is None and isinstance(lat_val, (list, tuple)) and len(lat_val) >= 3:
            lat_ref = canonical.get(
                MetadataFieldKey.GPS_LATITUDE_REF.value, "")
            lat = PhotoMetadata._extract_gps_decimal_from_dms(lat_val, lat_ref)
        if lon is None and isinstance(lon_val, (list, tuple)) and len(lon_val) >= 3:
            lon_ref = canonical.get(
                MetadataFieldKey.GPS_LONGITUDE_REF.value, "")
            lon = PhotoMetadata._extract_gps_decimal_from_dms(lon_val, lon_ref)

        if lat is not None and lon is not None:
            alt = PhotoMetadata._to_float(
                canonical.get(MetadataFieldKey.ABSOLUTE_ALTITUDE.value)
                or canonical.get("GPSAltitude")
            )
            has_dji = any("drone-dji:" in str(k)
                          for k in (merged_payload or {}).keys())
            coord_source = str(canonical.get(
                MetadataFieldKey.COORD_SOURCE.value) or "")
            if coord_source == "MRK":
                source = "MRK"
            elif has_dji:
                source = "XMP"
            else:
                source = "EXIF"
            return lat, lon, alt, source

        # --- Tentativa 3: Fallback DMS usando chaves RAW do merged_payload (para compatibilidade) ---
        lat = PhotoMetadata._extract_gps_decimal_from_dms(
            merged_payload.get("GPSLatitude"),
            merged_payload.get("GPSLatitudeRef"),
        )
        lon = PhotoMetadata._extract_gps_decimal_from_dms(
            merged_payload.get("GPSLongitude"),
            merged_payload.get("GPSLongitudeRef"),
        )
        alt = PhotoMetadata._to_float(merged_payload.get("GPSAltitude"))
        if lat is not None and lon is not None:
            return lat, lon, alt, "EXIF"

        return None, None, None, "NONE"

    @staticmethod
    def _extract_gps_decimal_from_dms(value, ref):
        if value is None:
            return None
        parts = list(value) if isinstance(value, (list, tuple)) else None
        if not parts or len(parts) < 3:
            return None

        def _part_to_float(p):
            if isinstance(p, (int, float)):
                return float(p)
            text = str(p).strip()
            if "/" in text:
                num, den = text.split("/", 1)
                return float(num) / float(den) if float(den) != 0 else 0.0
            return float(text)

        try:
            deg = _part_to_float(parts[0])
            minute = _part_to_float(parts[1])
            sec = _part_to_float(parts[2])
            dec = deg + (minute / 60.0) + (sec / 3600.0)
            ref_txt = str(ref or "").strip().upper()
            if ref_txt in ("S", "W"):
                dec = -dec
            return dec
        except Exception as e:
            LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PhotoMetadata").debug(
                "_extract_gps_decimal_from_dms falhou", error=str(e)
            )
            return None

    @staticmethod
    def _to_float(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().replace("+", "")
        if text in ("", "None", "null"):
            return None
        try:
            return float(text)
        except Exception as e:
            LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PhotoMetadata").debug(
                "_to_float falhou", error=str(e)
            )
            return None

    @staticmethod
    def _safe_parse_datetime(value):
        if not value:
            return None
        raw = str(value).strip()
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception as e:
            LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PhotoMetadata").debug(
                "_safe_parse_datetime falhou no formato", error=str(e)
            )
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y%m%d%H%M",
            "%Y%m%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(str(raw), fmt)
            except Exception as e:
                LogUtils(tool=ToolKey.UNTRACEABLE, class_name="PhotoMetadata").debug(
                    "_safe_parse_datetime strptime falhou", error=str(e)
                )
        return None
