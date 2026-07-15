# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.PhotoEnrichmentTask import PhotoEnrichmentTask
from ..config.LogUtils import LogUtils
from ...utils.mrk.PhotoMetadata import PhotoMetadata


class PhotoEnrichmentStep(BaseStep):
    """
    Step unificado para enriquecer JSON com metadados de fotos.

    Todos os parâmetros de configuração são passados no __init__
    (nada via context). O context carrega apenas:
      - input_path: Diretório base para busca de arquivos
      - files: Lista de caminhos MRK (se houver)
      - tool_key: ToolKey para logging
      - json_path: Caminho do JSON (resultado de execução anterior)
    """

    def __init__(
        self,
        *,
        source: str = "photo",
        enable_mrk: bool = False,
        enable_exif: bool = True,
        enable_xmp: bool = True,
        enable_custom_fields: bool = True,
        selected_required_fields: Optional[List[str]] = None,
        selected_custom_fields: Optional[List[str]] = None,
        selected_mrk_fields: Optional[List[str]] = None,
        project_title: str = "",
        logo_path: str = "",
        recursive: bool = True,
        paths: Optional[List[str]] = None,
    ):
        self.source = source
        self.enable_mrk = enable_mrk
        self.enable_exif = enable_exif
        self.enable_xmp = enable_xmp
        self.enable_custom_fields = enable_custom_fields
        self.selected_required_fields = selected_required_fields or []
        self.selected_custom_fields = selected_custom_fields or []
        self.selected_mrk_fields = selected_mrk_fields or []
        self.project_title = project_title
        self.logo_path = logo_path
        self.recursive = recursive
        self.paths = paths or []

    def name(self) -> str:
        return "PhotoEnrichmentStep"

    def _resolve_base_folder(self, context: ExecutionContext) -> str:
        """Resolve o diretório base do context canônico."""
        base = context.input_path
        if base:
            return base
        raise KeyError(
            "ExecutionContext.input_path não definido. "
            "Defina input_path ao criar o ExecutionContext."
        )

    def _resolve_tool_key(self, context: ExecutionContext) -> str:
        """Resolve tool_key do context canônico."""
        tk = context.tool_key
        if tk:
            return tk
        raise KeyError(
            "ExecutionContext.tool_key não definido. "
            "Defina tool_key ao criar o ExecutionContext."
        )

    def _resolve_mrk_paths(self, context: ExecutionContext) -> list:
        """Resolve paths MRK: prioriza self.paths, depois context.files."""
        if self.paths:
            return self.paths
        if context.files:
            return context.files
        return []

    def create_task(self, context: ExecutionContext):
        tool_key = self._resolve_tool_key(context)
        base_folder = self._resolve_base_folder(context)
        mrk_paths = self._resolve_mrk_paths(context)

        return PhotoEnrichmentTask(
            base_folder=base_folder,
            recursive=self.recursive,
            source=self.source,
            paths=mrk_paths,
            json_path=context.json_path,
            source_points=context.get_result("points", []),
            layer_id=context.get_result("layer_id", ""),
            selected_required_fields=self.selected_required_fields,
            selected_custom_fields=self.selected_custom_fields,
            selected_mrk_fields=self.selected_mrk_fields,
            tool_key=tool_key,
            enable_mrk=self.enable_mrk,
            enable_exif=self.enable_exif,
            enable_xmp=self.enable_xmp,
            enable_custom_fields=self.enable_custom_fields,
            project_title=self.project_title,
            logo_path=self.logo_path,
        )

    def on_success(self, context: ExecutionContext, result):
        logger = LogUtils(
            tool=self._resolve_tool_key(context),
            class_name=self.__class__.__name__,
        )

        if not result or not isinstance(result, dict):
            logger.error("Resultado invalido do enriquecimento de fotos")
            return

        json_path = result.get("json_path")
        if not json_path:
            logger.error("json_path nao encontrado no resultado")
            return

        # Propaga json_path via set_result (canônico para comunicação entre steps)
        context.set_result("json_path", json_path)

        logger.info(
            "JSON enriquecido com metadados de foto",
            data={
                "json_path": json_path,
                "source": result.get("source", "photo"),
                "total_points": result.get("total_points", 0),
            },
        )

        # ── Enriquecer coordenadas da primeira foto com EPSG/zona/hemisfério ──
        # A Etapa 6 do PhotoMetadata.run_pipeline() já extraiu as coordenadas raw
        # (lat, lon) da primeira foto. Aqui (main thread) delegamos para
        # PhotoMetadata.enrich_first_photo_coord() que chama
        # VectorLayerProjection.get_coordinate_info() e salva no context + JSON.
        try:
            enrich_result = PhotoMetadata.enrich_first_photo_coord(
                json_path=json_path,
            )
            if enrich_result:
                # Seta lat/lon como atributos canônicos do context
                # (lido por AltimetryStep, ReverseGeocodeStep, etc.)
                context.lat = enrich_result["lat"]
                context.lon = enrich_result["lon"]
                context.set_result("first_photo_coord_info", enrich_result)
                logger.info(
                    "Coordenadas da primeira foto enriquecidas no context",
                    data={
                        "lat": enrich_result["lat"],
                        "lon": enrich_result["lon"],
                        "epsg": enrich_result.get("epsg"),
                        "zona": enrich_result.get("zona_num"),
                        "hemisferio": enrich_result.get("hemisferio"),
                    },
                )
            else:
                logger.info(
                    "Nenhuma coordenada raw disponível da primeira foto "
                    "(pipeline pode não ter fotos com GPS)"
                )
        except Exception as e:
            logger.warning(
                "Erro ao enriquecer coordenadas da primeira foto",
                data={"error": str(e)},
            )
