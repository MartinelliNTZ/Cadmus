# -*- coding: utf-8 -*-
"""
DronePipelineService - Serviço único de orquestração do pipeline de drone.

UNIFICA a lógica de pipeline que antes estava duplicada em:
  - DroneCoordinates.execute_tool()      (plugins/DroneCoordinates.py)
  - DroneCoordinatesRunner.run_mrk_file() (core/services/DroneCoordinatesRunner.py)
  - MrkDropHandler.handleFileDrop()      (core/services/MrkDropHandler.py)

Uso:
    DronePipelineService.execute(iface, input_path="/path/to/photos")
    DronePipelineService.execute(iface, input_path="/path", file_path="/path/file.mrk")
"""

import os
from typing import Any, Callable, Dict, List, Optional

from qgis.core import QgsProject

from ..engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..engine_tasks.ExecutionContext import ExecutionContext
from ..engine_tasks.PhotoEnrichmentStep import PhotoEnrichmentStep
from ..engine_tasks.JsonVectorizationStep import JsonVectorizationStep
from ..engine_tasks.ReverseGeocodeStep import ReverseGeocodeStep
from ..engine_tasks.AltimetryStep import AltimetryStep
from ...i18n.TranslationManager import STR
from ...utils.ExplorerUtils import ExplorerUtils
from ...utils.Preferences import Preferences
from ...utils.ProjectUtils import ProjectUtils
from ...utils.QgisMessageUtil import QgisMessageUtil
from ...utils.ToolKeys import ToolKey
from ...utils.mrk.MetadataFields import MetadataFields
from ...utils.vector.VectorLayerGeometry import VectorLayerGeometry
from ...utils.vector.VectorLayerSource import VectorLayerSource
from ..config.LogUtils import LogUtils


class DronePipelineService:
    """
    Serviço único do pipeline de drone.

    Responsabilidades:
      - Carregar preferências com defaults centralizados
      - Montar steps com parâmetros corretos
      - Gerenciar callbacks on_success / on_error
      - Pós-processamento (GPKG, QML, track layer, report)

    Todas as operações são STATELESS (métodos estáticos).
    """

    # ── Defaults centralizados (antes espalhados em 3 classes) ──────
    DEFAULTS: Dict[str, Any] = {
        "photos": True,
        "use_mrk": True,
        "recursive": True,
        "generate_report": True,
        "apply_style_points": False,
        "apply_style_track": False,
    }

    # Nível mínimo de licença exigido para gerar relatórios
    REGISTRY_LEVEL: int = 3

    # ── API PÚBLICA ────────────────────────────────────────────────

    @staticmethod
    def execute(
        iface,
        input_path: str,
        file_path: Optional[str] = None,
        *,
        paths: Optional[List[str]] = None,
        on_finished: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> bool:
        """
        Constrói e inicia o pipeline de drone a partir das preferências salvas.

        Args:
            iface: Interface QGIS (para callbacks de UI)
            input_path: Diretório base onde as fotos estão localizadas
            file_path: Caminho do arquivo MRK (opcional — None = modo UI com paths)
            paths: Lista de caminhos (usado pelo DroneCoordinates UI)
            on_finished: Callback customizado (opcional)
            on_error: Callback customizado (opcional)

        Returns:
            True se o pipeline foi iniciado com sucesso
        """
        logger = LogUtils(tool=ToolKey.DRONE_COORDINATES,
                          class_name="DronePipelineService")
        prefs = DronePipelineService._load_safe_prefs()

        # ── Carregar campos selecionados ──────────────────────────
        exif_selected = prefs.get("exif_fields_selected", [])
        xmp_selected = prefs.get("xmp_fields_selected", [])
        selected_required = MetadataFields.normalize_selected_keys(
            exif_selected + xmp_selected,
            allowed_keys=MetadataFields.required_keys(),
        )
        selected_custom = MetadataFields.normalize_selected_keys(
            prefs.get("custom_fields_selected", []),
            allowed_keys=MetadataFields.custom_keys(),
        )
        selected_mrk = MetadataFields.normalize_selected_keys(
            prefs.get("mrk_fields_selected", []),
            allowed_keys=MetadataFields.mrk_keys(),
        )

        use_mrk = prefs.get("use_mrk", True)
        source = "mrk+photo" if use_mrk else "photo"
        enable_mrk = use_mrk
        apply_photos = prefs.get("photos", True)

        # ── Montar ExecutionContext ───────────────────────────────
        context = ExecutionContext(
            input_path=input_path,
            tool_key=ToolKey.DRONE_COORDINATES,
            files=[file_path] if (enable_mrk and file_path) else (paths or []),
        )

        # ── Montar Steps ──────────────────────────────────────────
        enable_exif = apply_photos
        enable_xmp = apply_photos
        enable_custom = apply_photos and bool(selected_custom)
        project_title = prefs.get("project_title", "")
        logo_path = prefs.get("logo_path", "") if prefs.get(
            "logo_enabled", False) else ""

        resolve_paths = [file_path] if (
            enable_mrk and file_path) else (paths or [])

        steps: list = [
            PhotoEnrichmentStep(
                source=source,
                enable_mrk=enable_mrk,
                enable_exif=enable_exif,
                enable_xmp=enable_xmp,
                enable_custom_fields=enable_custom,
                selected_required_fields=selected_required,
                selected_custom_fields=selected_custom,
                selected_mrk_fields=selected_mrk,
                project_title=project_title,
                logo_path=logo_path,
                recursive=prefs.get("recursive", True),
                paths=resolve_paths,
            ),
            # ReverseGeocodeStep e AltimetryStep consomem context.lat/context.lon
            # (setados pelo PhotoEnrichmentStep.on_success() via atributos canônicos)
            # e persistem dados no JSON se context.json_path existir.
            ReverseGeocodeStep(),
            AltimetryStep(),
            JsonVectorizationStep(source=source),
        ]
        should_generate_report = prefs.get("generate_report", True)
        if should_generate_report:
            try:
                from ..config.RegistryManager import RegistryManager
                reg_mgr = RegistryManager(tool_key=ToolKey.DRONE_COORDINATES)
                if reg_mgr.has_minimum_level(DronePipelineService.REGISTRY_LEVEL):
                    # Import lazy: ReportGenerationStep só é importado se houver licença
                    # Isso permite que o pipeline funcione em modo free sem o módulo
                    from ..engine_tasks.ReportGenerationStep import ReportGenerationStep
                    steps.append(ReportGenerationStep())
                else:
                    logger.warning(
                        f"Licença sem nível mínimo {DronePipelineService.REGISTRY_LEVEL} — relatório não será gerado"
                    )
            except Exception as e:
                logger.error(f"Falha ao verificar licença: {e}")

        # ── Dados extras para callback (modo MRK) ─────────────────
        if file_path:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            context.set_result("points_layer_name",
                               f"{base_name}_{STR.POINTS}")
            context.set_result("track_layer_name", f"{base_name}_{STR.TRACK}")
            context.set_result(
                "auto_points_output_path",
                ExplorerUtils.build_suffixed_output_path(
                    file_path, STR.POINTS.lower()),
            )
            context.set_result(
                "auto_track_output_path",
                ExplorerUtils.build_suffixed_output_path(
                    file_path, STR.TRACK.lower()),
            )
            context.set_result("source_mrk_file", file_path)

        # ── Callbacks ─────────────────────────────────────────────
        def _on_finished(ctx: ExecutionContext):
            DronePipelineService._on_pipeline_finished(
                iface, ctx, on_finished=on_finished)

        def _on_error(errors):
            error_msg = str(errors[0]) if errors else "Erro desconhecido"
            QgisMessageUtil.bar_critical(iface, error_msg)
            if callable(on_error):
                on_error(errors)

        # ── Iniciar Engine ────────────────────────────────────────
        engine = AsyncPipelineEngine(
            steps=steps,
            context=context,
            on_finished=_on_finished,
            on_error=_on_error,
        )
        engine.start()

        logger.info(
            "Pipeline de drone iniciado",
            data={
                "input_path": input_path,
                "source": source,
                "steps": [s.name() for s in steps],
                "enable_mrk": enable_mrk,
                "enable_exif": enable_exif,
                "enable_xmp": enable_xmp,
                "enable_custom": enable_custom,
                "recursive": prefs.get("recursive", True),
            },
        )
        return True

    # ── CALLBACK DE SUCESSO (único) ───────────────────────────────

    @staticmethod
    def _on_pipeline_finished(
        iface,
        context: ExecutionContext,
        *,
        on_finished: Optional[Callable] = None,
    ):
        """
        Callback único de sucesso do pipeline.
        Gerencia pós-processamento: GPKG, QML, track layer, relatório.
        """
        logger = LogUtils(tool=ToolKey.DRONE_COORDINATES,
                          class_name="DronePipelineService")

        layer = context.get_result("layer") or context.get("layer")
        if not layer or not layer.isValid():
            QgisMessageUtil.modal_error(iface, STR.ERROR_LAYER_NOT_FOUND)
            return

        points_output_path = context.get_result("auto_points_output_path")
        track_output_path = context.get_result("auto_track_output_path")
        points_layer_name = context.get_result("points_layer_name", STR.POINTS)
        track_layer_name = context.get_result("track_layer_name", STR.TRACK)

        # ── Pontos: adicionar ao projeto ──────────────────────────
        if points_output_path:
            points_layer = DronePipelineService._save_and_load(
                layer, points_output_path, fallback_name=points_layer_name,
            )
        else:
            points_layer = layer
            QgsProject.instance().addMapLayer(layer)

        # ── Pontos: aplicar QML ───────────────────────────────────
        DronePipelineService._apply_qml_if_configured(
            points_layer, "apply_style_points", "qml_path_points",
        )

        # ── Traço ─────────────────────────────────────────────────
        line_layer = None
        if points_layer and points_layer.isValid():
            order_field = DronePipelineService._resolve_track_order_field(
                points_layer)
            group_fields = DronePipelineService._resolve_track_group_fields(
                points_layer)
            line_layer = VectorLayerGeometry.create_line_layer_from_points(
                list(points_layer.getFeatures()),
                order_by_field=order_field,
                name=track_layer_name,
                group_by_fields=group_fields,
                attribute_fields=MetadataFields.default_track_attribute_keys(),
            )

        track_layer = None
        if line_layer and line_layer.isValid():
            if track_output_path:
                track_layer = DronePipelineService._save_and_load(
                    line_layer, track_output_path, fallback_name=track_layer_name,
                )
            else:
                track_layer = line_layer
                QgsProject.instance().addMapLayer(line_layer)

            DronePipelineService._apply_qml_if_configured(
                track_layer, "apply_style_track", "qml_path_track",
            )

        # ── Relatório ─────────────────────────────────────────────
        json_path = context.json_path or context.get_result("json_path")
        report_payload = None
        if json_path and Preferences.load_tool_prefs(ToolKey.DRONE_COORDINATES).get("generate_report", False):
            try:
                from ..config.RegistryManager import RegistryManager
                reg_mgr = RegistryManager(tool_key=ToolKey.DRONE_COORDINATES)
                if reg_mgr.has_minimum_level(DronePipelineService.REGISTRY_LEVEL):
                    # Import lazy: ReportGenerationService só é importado se houver licença
                    # Permite que o pipeline funcione em modo free sem o módulo
                    from .ReportGenerationService import ReportGenerationService
                    report_payload = ReportGenerationService(
                        tool_key=ToolKey.DRONE_COORDINATES
                    ).generate_from_json(json_path)
                else:
                    logger.warning(
                        f"Licença sem nível mínimo {DronePipelineService.REGISTRY_LEVEL} — relatório não será gerado no pós-processamento"
                    )
            except Exception as e:
                logger.error(f"Falha ao gerar report: {e}")

        # ── Notificação ───────────────────────────────────────────
        if points_output_path:
            QgisMessageUtil.bar_success(
                iface, STR.CONVERT_FILE_SUCCESS, duration=4)
        else:
            QgisMessageUtil.bar_success(iface, STR.SUCCESS_MESSAGE)

        # ── Callback customizado ──────────────────────────────────
        if callable(on_finished):
            on_finished({
                "file_path": context.get_result("source_mrk_file"),
                "points_layer": points_layer,
                "track_layer": track_layer if line_layer else None,
                "report_payload": report_payload,
            })

    # ── MÉTODOS AUXILIARES ────────────────────────────────────────

    @staticmethod
    def _load_safe_prefs() -> dict:
        """Carrega preferências garantindo defaults. (STATELESS)"""
        raw = Preferences.load_tool_prefs(ToolKey.DRONE_COORDINATES)
        result = dict(DronePipelineService.DEFAULTS)
        result.update(raw)
        return result

    @staticmethod
    def _save_and_load(layer, output_path, *, fallback_name: str):
        """
        Salva layer em GPKG e carrega no projeto.
        Se o arquivo já existir, carrega o existente.
        """
        existing = VectorLayerSource.load_existing_vector_layer(
            output_path, tool_key=ToolKey.DRONE_COORDINATES,
        )
        if existing:
            existing.setName(fallback_name)
            ProjectUtils.add_layer_if_missing(existing)
            return existing

        saved = VectorLayerSource.save_and_load_layer(
            layer, output_path,
            tool_key=ToolKey.DRONE_COORDINATES,
            decision="overwrite",
        )
        if saved and saved.isValid():
            saved.setName(fallback_name)
            ProjectUtils.add_layer_if_missing(saved)
            return saved

        layer.setName(fallback_name)
        ProjectUtils.add_layer_if_missing(layer)
        return layer

    @staticmethod
    def _apply_qml_if_configured(layer, enabled_key: str, path_key: str):
        """Aplica estilo QML se configurado nas preferências."""
        if not layer or not layer.isValid():
            return
        prefs = DronePipelineService._load_safe_prefs()
        if not prefs.get(enabled_key, False):
            return
        qml_path = prefs.get(path_key, "").strip()
        if qml_path and os.path.exists(qml_path):
            ok = layer.loadNamedStyle(qml_path)
            if isinstance(ok, tuple):
                ok = ok[0]
            if ok:
                layer.triggerRepaint()

    @staticmethod
    def _resolve_track_order_field(layer):
        """Resolve campo de ordenação para criar trilha."""
        candidates = [
            "Foto", "foto", "PhotoNum",
            MetadataFields.resolve_output_name("Foto"),
            "mrk_index", "id",
        ]
        for name in candidates:
            if name and layer.fields().lookupField(name) != -1:
                return name
        return layer.fields().field(0).name()

    @staticmethod
    def _resolve_track_group_fields(layer):
        """Resolve campos de agrupamento para criar trilha."""
        pairs = [
            ("MrkPath", "MrkFile"),
            ("mrk_path", "mrk_file"),
            (
                MetadataFields.resolve_output_name("MrkPath"),
                MetadataFields.resolve_output_name("MrkFile"),
            ),
        ]
        for a, b in pairs:
            if layer.fields().lookupField(a) != -1 and layer.fields().lookupField(b) != -1:
                return [a, b]
        fallback = [
            "FolderLevel1", "FolderL1",
            MetadataFields.resolve_output_name("FolderLevel1"),
        ]
        for name in fallback:
            if name and layer.fields().lookupField(name) != -1:
                return [name]
        return None
