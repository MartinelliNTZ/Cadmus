# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.AltimetryTask import AltimetriaTask
from ...utils.JsonUtil import JsonUtil


class AltimetryStep(BaseStep):
    """
    Step que executa altimetria (SRTM 90m) para obter altitude a partir de coordenadas.

    Lê lat/lon do context (atributos canônicos), independente de cenário:
      - Pipeline de drone: PhotoEnrichmentStep.on_success() seta context.lat/context.lon
      - CoordClickTool: seta context.lat/context.lon diretamente

    Se context.json_path existir, persiste altitude e timestamps no JSON.
    """

    def __init__(self):
        super().__init__()

    def name(self) -> str:
        return "altimetry"

    # --------------------------------------------------
    # Condicional
    # --------------------------------------------------
    def should_run(self, context: ExecutionContext) -> bool:
        self._init_logger(context)
        if context.lat is not None and context.lon is not None:
            return True
        self.logger.info(
            "AltimetryStep pulado: lat/lon não disponíveis no context"
        )
        return False

    # --------------------------------------------------
    # Task factory
    # --------------------------------------------------
    def create_task(self, context: ExecutionContext) -> Optional[AltimetriaTask]:
        self._init_logger(context)
        tool_key = context.tool_key

        if context.lat is not None and context.lon is not None:
            self.logger.info(
                "AltimetryStep: coordenadas do context",
                data={"lat": context.lat, "lon": context.lon},
            )
            return AltimetriaTask(context.lat, context.lon, tool_key=tool_key)

        self.logger.info("AltimetryStep pulado: coordenadas indisponíveis")
        return None

    # --------------------------------------------------
    # Sucesso
    # --------------------------------------------------
    def on_success(self, context: ExecutionContext, result) -> None:
        self._init_logger(context)
        try:
            context.set_result("altitude", result)
            self.logger.info(
                "AltimetryStep: resultado armazenado",
                data={"altitude": result},
            )

            # Persiste no JSON se json_path existir (independente de cenário)
            if result is not None:
                json_path = context.json_path
                if json_path and os.path.exists(json_path):
                    alt_start = context.get_result("altimetry_start")
                    alt_end = datetime.now().isoformat()
                    if alt_start:
                        JsonUtil.update_timestamps(json_path, {
                            "altimetry_start": alt_start,
                            "altimetry_end": alt_end,
                        })
                        self.logger.info(
                            "Timestamps de altimetria salvos no JSON",
                            data={"json_path": json_path},
                        )

                    JsonUtil.update_json(
                        json_path, {"altitude": float(result)})
                    self.logger.info(
                        "Altitude adicionada ao JSON de metadados",
                        data={"json_path": json_path, "altitude": result},
                    )

        except Exception as e:
            self.logger.exception(e, code="ALTIMETRY_ON_SUCCESS_ERROR")

    # --------------------------------------------------
    # Erro
    # --------------------------------------------------
    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        self._init_logger(context)
        self.logger.warning(f"Altimetry failed: {exception}")
        json_path = context.json_path
        if json_path and os.path.exists(json_path):
            try:
                JsonUtil.update_timestamps(json_path, {
                    "altimetry_error": str(exception),
                    "altimetry_end": datetime.now().isoformat(),
                })
            except Exception as e:
                self.logger.warning(
                    f"Erro ao salvar timestamp de falha no JSON: {e}")
