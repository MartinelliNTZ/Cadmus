# -*- coding: utf-8 -*-
from typing import List, Optional
from .BaseTask import BaseTask
from ..config.LogUtils import LogUtils
from ..enum import MetadataFieldKey
from ...utils.mrk.PhotoMetadata import PhotoMetadata
from ...utils.mrk.MetadataFields import MetadataFields


class PhotoEnrichmentTask(BaseTask):
    """
    Task unificada para enriquecimento de metadados de fotos.

    Utiliza o pipeline linear do PhotoMetadata.run_pipeline() com flags
    de habilitação de cada etapa.

    O PhotoMetadata.run_pipeline() agora é responsável por:
    - Fazer o parsing de MRK (se source="mrk+photo")
    - Executar todas as etapas de enriquecimento (esqueleto, MRK, EXIF, XMP, custom)
    - Retornar os records enriquecidos

    Após o pipeline, esta task:
    - Aplica filtro de campos selecionados (selected_keys)
    - Converte records para PascalCase (formato JSON v2.0)
    - Delega a criação e salvamento do JSON ao PhotoMetadata.build_and_save_json()

    NÃO vetoriza (vetorização é do JsonVectorizationStep posterior)
    """

    def __init__(
        self,
        base_folder: str,
        recursive: bool,
        source: str = "photo",
        paths: Optional[List[str]] = None,
        json_path: str = None,
        source_points: list = None,
        layer_id: str = "",
        selected_required_fields: list = None,
        selected_custom_fields: list = None,
        selected_mrk_fields: list = None,
        tool_key: str = None,
        enable_mrk: bool = False,
        enable_exif: bool = True,
        enable_xmp: bool = True,
        enable_custom_fields: bool = True,
        project_title: str = "",
        logo_path: str = "",
    ):
        super().__init__("Enriquecendo fotos", tool_key)
        self.base_folder = base_folder
        self.recursive = recursive
        self.source = source
        self.paths = paths or []
        self.json_path = json_path
        self.source_points = source_points or []
        self.layer_id = layer_id
        self.selected_required_fields = selected_required_fields or []
        self.selected_custom_fields = selected_custom_fields or []
        self.selected_mrk_fields = selected_mrk_fields or []
        self.project_title = project_title
        self.logo_path = logo_path

        # Flags do pipeline
        self.enable_mrk = enable_mrk
        self.enable_exif = enable_exif
        self.enable_xmp = enable_xmp
        self.enable_custom_fields = enable_custom_fields

    def _get_selected_keys(self) -> set:
        """Constrói conjunto de chaves selecionadas pelo usuário."""
        selected = set(self.selected_required_fields)
        selected.update(self.selected_custom_fields)
        selected.update(self.selected_mrk_fields)
        return selected

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        logger = LogUtils(tool=self.tool_key, class_name=self.__class__.__name__)

        # Determina se há dados MRK baseado no source
        has_mrk_source = "mrk" in self.source if self.source else False
        has_mrk_data = (
            has_mrk_source
            or bool(self.paths)
            or bool(self.json_path)
            or bool(self.source_points)
            or bool(self.layer_id)
        )

        # Se enable_mrk foi explicitamente passado como False, não usa MRK
        use_mrk = self.enable_mrk and has_mrk_data

        if use_mrk:
            logger.info(
                "Modo mrk+photo",
                data={
                    "base_folder": self.base_folder,
                    "has_paths": len(self.paths) > 0,
                    "has_source_points": len(self.source_points) > 0,
                    "enable_exif": self.enable_exif,
                    "enable_xmp": self.enable_xmp,
                    "enable_custom_fields": self.enable_custom_fields,
                },
            )
            records, quality = self._run_pipeline_with_mrk(logger)
            source = "mrk+photo"
        else:
            logger.info(
                "Modo photo",
                data={
                    "base_folder": self.base_folder,
                    "enable_exif": self.enable_exif,
                    "enable_xmp": self.enable_xmp,
                    "enable_custom_fields": self.enable_custom_fields,
                },
            )
            records, quality = PhotoMetadata.run_pipeline(
                base_folder=self.base_folder,
                points=None,
                recursive=self.recursive,
                tool_key=self.tool_key,
                enable_mrk=False,
                enable_exif=self.enable_exif,
                enable_xmp=self.enable_xmp,
                enable_custom_fields=self.enable_custom_fields,
            )
            source = "photo"

        if not records:
            logger.error("Nenhum registro gerado no enriquecimento")
            self.exception = "Nenhuma imagem encontrada no diretório"
            return False

        # Aplica filtro de campos selecionados
        selected_keys = self._get_selected_keys()
        if selected_keys:
            filtered = []
            skip_keys = {
                MetadataFieldKey.COORD_SOURCE.value,
                MetadataFieldKey.QUALITY_FLAG.value,
                "HasXmp",
                "HasExifGps",
            }
            for record in records:
                filtered_record = {
                    k: v
                    for k, v in record.items()
                    if k in selected_keys or k in skip_keys
                }
                if filtered_record:
                    filtered.append(filtered_record)
            records = filtered

        if not records:
            logger.warning(
                "Todos os registros foram filtrados pelas chaves selecionadas"
            )
            self.exception = "Nenhuma imagem encontrada no diretório"
            return False

        # Converte records para PascalCase (formato JSON v2.0)
        key_to_json_key = {
            key: field.key.value
            for key, field in MetadataFields.all_fields().items()
            if field.key is not None
        }
        json_records = []
        for record in records:
            json_record = {}
            for k, v in record.items():
                if isinstance(v, dict):
                    continue
                if isinstance(k, MetadataFieldKey):
                    json_record[k.value] = v
                else:
                    canonical_key = MetadataFields.resolve_key(str(k))
                    mapped_key = key_to_json_key.get(canonical_key, canonical_key)
                    json_record[mapped_key] = v
            json_records.append(json_record)

        # Delega a criação e salvamento do JSON ao PhotoMetadata
        json_path = PhotoMetadata.build_and_save_json(
            records=json_records,
            source=source,
            base_folder=self.base_folder,
            tool_key=self.tool_key,
            recursive=self.recursive,
            quality=quality,
            project_title=self.project_title,
            logo_path=self.logo_path,
        )

        if not json_path:
            logger.error("Falha ao salvar JSON via PhotoMetadata")
            self.exception = "Falha ao salvar JSON dos metadados das imagens"
            return False

        self.result = {
            "json_path": json_path,
            "source": source,
            "total_points": len(json_records),
        }

        logger.info(
            "JSON enriquecido salvo",
            data={
                "json_path": json_path,
                "source": source,
                "total_points": len(json_records),
            },
        )

        return True

    def _run_pipeline_with_mrk(self, logger: LogUtils) -> tuple:
        """
        Modo mrk+photo: extrai pontos MRK e executa pipeline completo.

        Os pontos MRK podem vir de 3 fontes:
        1. self.paths → PhotoMetadata parseia os arquivos MRK diretamente
        2. layer_id → camada QGIS existente com pontos MRK
        3. source_points / json_path → pontos pré-parseados
        """
        from qgis.core import QgsProject

        # Prioridade 1: se tem paths, passa para o PhotoMetadata parsear
        if self.paths and "mrk" in self.source:
            logger.info(
                "Usando paths para parsing de MRK via PhotoMetadata",
                data={"paths": self.paths},
            )
            records, quality = PhotoMetadata.run_pipeline(
                base_folder=self.base_folder,
                points=None,
                mrk_paths=self.paths,  # PhotoMetadata usa parametro interno mrk_paths
                recursive=self.recursive,
                tool_key=self.tool_key,
                enable_mrk=True,
                enable_exif=self.enable_exif,
                enable_xmp=self.enable_xmp,
                enable_custom_fields=self.enable_custom_fields,
            )
            return records, quality

        # Prioridade 2: se tem layer_id, extrai pontos da camada QGIS
        pontos = []
        layer = QgsProject.instance().mapLayer(self.layer_id) if self.layer_id else None

        if layer and layer.isValid():
            photo_field_name = MetadataFields.get_attribute("foto", "foto")
            mrk_folder_field_name = MetadataFields.get_attribute(
                "mrk_folder", "mrk_folder"
            )
            for feat in layer.getFeatures():
                foto = feat.attribute(photo_field_name)
                if foto is None:
                    continue
                try:
                    foto_int = int(foto)
                except Exception as e:
                    logger.warning(f"Erro ao converter foto para inteiro: {e}")
                    continue
                ponto = {"foto": foto_int}
                for field in feat.fields():
                    name = field.name()
                    if name == photo_field_name:
                        continue
                    ponto[MetadataFields.resolve_key(name)] = feat.attribute(name)
                if feat.fieldNameIndex(mrk_folder_field_name) != -1:
                    mrk_folder = feat.attribute(mrk_folder_field_name)
                    if mrk_folder:
                        ponto["mrk_folder"] = mrk_folder
                pontos.append(ponto)
        else:
            # Prioridade 3: usa source_points ou json_path
            src = self.source_points
            if not src and self.json_path:
                from ...utils.JsonUtil import JsonUtil

                src = JsonUtil.load_records(self.json_path)
            for s in src:
                canonical = MetadataFields.normalize_record_to_keys(s or {})
                foto = canonical.get("Foto") or canonical.get("foto")
                if foto is None:
                    continue
                try:
                    ponto = {"foto": int(foto)}
                    for k, v in canonical.items():
                        ponto[k] = v
                    mrk_folder = canonical.get("MrkFolder")
                    if mrk_folder:
                        ponto["mrk_folder"] = mrk_folder
                    pontos.append(ponto)
                except Exception as e:
                    logger.warning(f"Erro ao converter foto para inteiro: {e}")
                    continue

        # Preenche atributos faltantes dos source_points
        source_by_key = {}
        for p in self.source_points:
            try:
                source_by_key[
                    (str(p.get("mrk_folder", "")).strip(), int(p.get("foto")))
                ] = p
            except Exception as e:
                logger.warning(f"Erro ao converter foto para inteiro: {e}")
                continue
        for p in pontos:
            key = (str(p.get("mrk_folder", "")).strip(), p.get("foto"))
            src = source_by_key.get(key)
            if src:
                for k, v in src.items():
                    if k not in p or p.get(k) in (None, ""):
                        p[k] = v

        logger.info("Pontos extraidos", data={"total": len(pontos)})

        # Executa pipeline com MRK habilitado
        records, quality = PhotoMetadata.run_pipeline(
            base_folder=self.base_folder,
            points=pontos,
            recursive=self.recursive,
            tool_key=self.tool_key,
            enable_mrk=True,
            enable_exif=self.enable_exif,
            enable_xmp=self.enable_xmp,
            enable_custom_fields=self.enable_custom_fields,
        )

        return records, quality
