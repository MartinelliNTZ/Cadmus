# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..config.LogUtils import LogUtils
from ...utils.JsonUtil import JsonUtil


class JsonVectorizationStep(BaseStep):
    """
    Step que cria camada vetorial exclusivamente a partir do JSON canônico.

    Usa do ExecutionContext:
      - json_path: Caminho do JSON (set_result do step anterior)
      - tool_key: ToolKey para logging

    Parâmetros opcionais:
      - source: Identificador da fonte ("mrk+photo", "photo", etc.)
      - layer_name: Nome da camada (se não for passado, usa context.get_result)
    """

    def __init__(
        self,
        *,
        source: str = "",
        layer_name: str = "",
    ):
        self._source = source
        self._layer_name = layer_name

    def name(self) -> str:
        return "JsonVectorizationStep"

    def create_task(self, context: ExecutionContext):
        # Vetorizacao ocorre no on_success (sincrono), sem QgsTask dedicado.
        return None

    def should_run(self, context: ExecutionContext) -> bool:
        return bool(context.json_path or context.get_result("json_path"))

    def on_success(self, context: ExecutionContext, result):
        # Nao utilizado; a execucao real acontece em run_inline().
        pass

    def run_inline(self, context: ExecutionContext):
        tool_key = context.tool_key or context.get_result("tool_key")
        logger = LogUtils(tool=tool_key, class_name=self.__class__.__name__)

        json_path = context.json_path or context.get_result("json_path")
        if not json_path:
            raise ValueError("JsonVectorizationStep: json_path ausente no contexto")

        # Registra inicio da vetorizacao
        vectorization_start = datetime.now().isoformat()

        from ..translator.JsonToVectorTranslator import JsonToVectorTranslator
        from ...utils.vector.VectorLayerAttributes import VectorLayerAttributes
        from qgis.core import QgsProject

        layer_name = (
            self._layer_name
            or context.get_result("points_layer_name")
            or context.get_result("layer_name")
            or "Cadmus_Vector"
        )
        source = self._source or context.get_result("source")
        translator = JsonToVectorTranslator(tool_key=tool_key)
        try:
            layer = translator.translate(
                json_path=json_path,
                layer_name=layer_name,
                selected_keys=None,
                source=source,
            )
        except Exception as e:
            logger.error(
                "Falha na traducao do JSON para camada vetorial",
                data={
                    "json_path": json_path,
                    "layer_name": layer_name,
                    "source": source,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"Falha ao criar camada via JsonToVectorTranslator: {e}")

        if not layer or not layer.isValid():
            logger.error(
                "Camada criada mas invalida",
                data={
                    "json_path": json_path,
                    "layer_name": layer_name,
                    "source": source,
                },
            )
            raise RuntimeError("Falha ao criar camada via JsonToVectorTranslator: layer invalido")

        # Reordenar atributos em ordem alfabética (case-insensitive)
        reordered = VectorLayerAttributes.reorder_fields_alphabetically(layer)
        if reordered and reordered.isValid():
            layer = reordered
            logger.debug("Atributos reorganizados em ordem alfabética")
        else:
            logger.warning("Não foi possível reordenar atributos alfabeticamente, mantendo ordem original")

        QgsProject.instance().addMapLayer(layer)
        context.set_result("layer", layer)
        context.set_result("total_points", int(layer.featureCount()))

        # Registra fim da vetorizacao e persiste timestamps no JSON
        vectorization_end = datetime.now().isoformat()
        try:
            JsonUtil.update_timestamps(json_path, {
                "vectorization_start": vectorization_start,
                "vectorization_end": vectorization_end,
            })
            logger.debug(f"Timestamps de vetorizacao salvos no JSON: {json_path}")
        except Exception as e:
            logger.warning(f"Nao foi possivel salvar timestamps de vetorizacao no JSON: {e}")

        context.set_result("vectorization_start", vectorization_start)
        context.set_result("vectorization_end", vectorization_end)

        logger.info(
            "Camada vetorial criada a partir do JSON",
            data={
                "layer_name": layer.name(),
                "json_path": json_path,
                "total_points": int(layer.featureCount()),
                "source": source,
                "vectorization_end": vectorization_end,
            },
        )
