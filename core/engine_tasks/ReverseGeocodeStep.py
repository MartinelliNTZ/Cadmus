# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.ReverseGeocodeTask import ReverseGeocodeTask
from ...utils.JsonUtil import JsonUtil


class ReverseGeocodeStep(BaseStep):
    """
    Step que executa reverse geocode para obter endereço a partir de coordenadas.

    Lê lat/lon do context (atributos canônicos), independente de cenário:
      - Pipeline de drone: PhotoEnrichmentStep.on_success() seta context.lat/context.lon
      - CoordClickTool: seta context.lat/context.lon diretamente

    Se context.json_path existir, persiste dados de geolocalização e timestamps no JSON.
    """

    def __init__(self):
        super().__init__()

    def name(self) -> str:
        return "reverse_geocode"

    # --------------------------------------------------
    # Condicional
    # --------------------------------------------------
    def should_run(self, context: ExecutionContext) -> bool:
        self._init_logger(context)
        if context.lat is not None and context.lon is not None:
            return True
        self.logger.info(
            "ReverseGeocodeStep pulado: lat/lon não disponíveis no context"
        )
        return False

    # --------------------------------------------------
    # Task factory
    # --------------------------------------------------
    def create_task(self, context: ExecutionContext) -> Optional[ReverseGeocodeTask]:
        self._init_logger(context)
        tool_key = context.tool_key

        if context.lat is not None and context.lon is not None:
            self.logger.info(
                "ReverseGeocodeStep: coordenadas do context",
                data={"lat": context.lat, "lon": context.lon},
            )
            return ReverseGeocodeTask(context.lat, context.lon, tool_key=tool_key)

        self.logger.info("ReverseGeocodeStep pulado: coordenadas indisponíveis")
        return None

    # --------------------------------------------------
    # Sucesso
    # --------------------------------------------------
    def on_success(self, context: ExecutionContext, result) -> None:
        self._init_logger(context)
        try:
            context.set_result("address_data", result)
            self.logger.info(
                "ReverseGeocodeStep: resultado armazenado",
                data={"address_data": result},
            )

            # Persiste no JSON se json_path existir (independente de cenário)
            if result:
                json_path = context.json_path
                if json_path and os.path.exists(json_path):
                    geocode_start = context.get_result("geocode_start")
                    geocode_end = datetime.now().isoformat()
                    if geocode_start:
                        JsonUtil.update_timestamps(json_path, {
                            "geocode_start": geocode_start,
                            "geocode_end": geocode_end,
                        })
                        self.logger.info(
                            "Timestamps de geocode salvos no JSON",
                            data={"json_path": json_path},
                        )

                    geocode_payload = {
                        "municipio": result.get("municipio", ""),
                        "state_district": result.get("state_district", ""),
                        "state": result.get("state", ""),
                        "region": result.get("region", ""),
                        "country": result.get("country", ""),
                    }
                    JsonUtil.update_json(json_path, {"geocode": geocode_payload})
                    self.logger.info(
                        "Geocode adicionado ao JSON de metadados",
                        data={"json_path": json_path, **geocode_payload},
                    )

        except Exception as e:
            self.logger.exception(e, code="REVERSE_GEOCODE_ON_SUCCESS_ERROR")

    # --------------------------------------------------
    # Erro
    # --------------------------------------------------
    def on_error(self, context: ExecutionContext, exception: Exception) -> None:
        self._init_logger(context)
        self.logger.warning(f"Reverse geocode failed: {exception}")
        json_path = context.json_path
        if json_path and os.path.exists(json_path):
            try:
                JsonUtil.update_timestamps(json_path, {
                    "geocode_error": str(exception),
                    "geocode_end": datetime.now().isoformat(),
                })
            except Exception as e:
                self.logger.warning(f"Erro ao salvar timestamp de falha no JSON: {e}")
