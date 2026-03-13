# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any
from qgis.core import QgsProject

from .BaseTask import BaseTask
from ..config.LogUtils import LogUtils
from ...utils.mrk.PhotoMetadata import PhotoMetadata


class PhotoMetadataTask(BaseTask):
    """Task que cruza metadados de fotos com atributos de uma camada de pontos."""

    def __init__(
        self,
        layer_id: str,
        base_folder: str,
        recursive: bool,
        tool_key: str,
    ):
        super().__init__("Cruzando fotos", tool_key)
        self.layer_id = layer_id
        self.base_folder = base_folder
        self.recursive = recursive

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        layer = QgsProject.instance().mapLayer(self.layer_id)
        if not layer or not layer.isValid():
            raise RuntimeError("Camada não encontrada para cruzamento de metadados")

        logger = LogUtils(tool=self.tool_key, class_name=self.__class__.__name__)
        
        # Extrair lista de fotos a serem cruzadas (campo 'foto')
        # 🔴 IMPORTANTE: Também extrair 'mrk_folder' se disponível (para múltiplos voos)
        pontos = []
        has_mrk_folder = False
        
        for feat in layer.getFeatures():
            foto = feat.attribute("foto")
            if foto is None:
                continue
            try:
                foto_int = int(foto)
            except Exception:
                continue
            
            ponto = {"foto": foto_int}
            
            # Verificar se o campo mrk_folder existe (adicionado por MrkParseTask)
            if feat.fieldNameIndex("mrk_folder") != -1:
                mrk_folder = feat.attribute("mrk_folder")
                if mrk_folder:
                    ponto["mrk_folder"] = mrk_folder
                    has_mrk_folder = True
            
            pontos.append(ponto)

        logger.info(f"Pontos extraídos da camada", data={
            "total_pontos": len(pontos),
            "com_mrk_folder": sum(1 for p in pontos if "mrk_folder" in p)
        })

        # Cruzar metadados
        # 🔴 O método enrich() agora processa cada grupo de pontos separadamente
        # baseado em seu mrk_folder, evitando conflito de numeração entre voos
        enriched = PhotoMetadata.enrich(
            pontos,
            base_folder=self.base_folder,
            recursive=self.recursive,
        )

        updates = {}
        field_names = set()
        for item in enriched:
            foto = item.get("foto")
            if foto is None:
                continue
            # Não incluir mrk_folder nos updates (é apenas campo de contexto)
            data = {k: v for k, v in item.items() if k not in ("foto", "mrk_folder")}
            updates[int(foto)] = data
            field_names.update(data.keys())

        logger.debug(
            f"Cruzamento completo: {len(pontos)} fotos processadas, {len(updates)} atualizações geradas"
        )

        # Diagnóstico adicional para identificar fotos que não foram encontradas
        not_found = len(pontos) - len(updates)
        if not_found > 0:
            logger.debug(f"Fotos sem metadados encontrados: {not_found}")

        self.result = {
            "updates": updates,
            "field_names": list(field_names),
        }
        return True
