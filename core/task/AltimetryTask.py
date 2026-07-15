# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse
import http.client

from .BaseTask import BaseTask
from ..config.LogUtils import LogUtils


class AltimetriaTask(BaseTask):
    """
    Task de altimetria (SRTM 90m via OpenTopoData).

    Herda de BaseTask para garantir:
    - Rastreabilidade via tool_key
    - Ciclo de vida gerenciado pela engine (on_success/on_error reservados)
    - Captura segura de exceções
    - Cancelamento cooperativo
    """

    def __init__(self, lat: float, lon: float, *, tool_key: str):
        super().__init__("Altimetria (SRTM 90m)", tool_key=tool_key)
        self.lat = lat
        self.lon = lon

    # --------------------------------------------------
    # EXECUÇÃO (chamado por BaseTask.run())
    # --------------------------------------------------
    def _run(self) -> bool:
        logger = LogUtils(tool=self.tool_key,
                          class_name=self.__class__.__name__)
        try:
            url = (
                "https://api.opentopodata.org/v1/srtm90m"
                f"?locations={self.lat},{self.lon}"
            )

            # Validação de segurança: aceitar apenas esquemas http/https
            parsed = urlparse(url)
            if parsed.scheme.lower() not in ("http", "https"):
                self.exception = Exception(
                    f"Invalid URL scheme: {parsed.scheme}")
                return False

            host = parsed.hostname
            port = parsed.port
            path = parsed.path or "/"
            if parsed.query:
                path = path + "?" + parsed.query

            if self.isCanceled():
                return False

            try:
                if parsed.scheme.lower() == "https":
                    conn = http.client.HTTPSConnection(
                        host, port=port, timeout=15)
                else:
                    conn = http.client.HTTPConnection(
                        host, port=port, timeout=15)
                conn.request(
                    "GET", path, headers={"User-Agent": "Cadmus-Altimetry-Task"}
                )
                resp = conn.getresponse()
                if resp.status != 200:
                    self.exception = Exception(f"HTTP error {resp.status}")
                    conn.close()
                    return False
                data = json.loads(resp.read().decode("utf-8"))
                conn.close()
            except Exception as e:
                logger.exception(e, code="HTTP_REQUEST_ERROR")
                self.exception = e
                return False

            if data.get("status") != "OK":
                self.exception = Exception("Resposta inválida da API")
                return False

            results = data.get("results") or []
            if not results:
                self.exception = Exception("Nenhum dado retornado")
                return False

            elevation = results[0].get("elevation")
            if elevation is None:
                self.exception = Exception("Elevação indisponível")
                return False

            self.result = float(elevation)
            return True

        except Exception as e:
            self.exception = e
            return False
