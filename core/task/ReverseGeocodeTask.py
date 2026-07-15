# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional
import json
from urllib.parse import urlparse, urljoin
import http.client

from .BaseTask import BaseTask
from ..config.LogUtils import LogUtils


class ReverseGeocodeTask(BaseTask):
    """
    Executa reverse geocode via BigDataCloud API.

    Herda de BaseTask para garantir:
    - Rastreabilidade via tool_key
    - Ciclo de vida gerenciado pela engine (on_success/on_error reservados)
    - Captura segura de exceções
    - Cancelamento cooperativo
    """

    def __init__(self, lat: float, lon: float, *, tool_key: str):
        super().__init__("Reverse Geocode (BigDataCloud)", tool_key=tool_key)
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
                "https://api.bigdatacloud.net/data/reverse-geocode-client"
                f"?latitude={self.lat}&longitude={self.lon}"
                "&localityLanguage=pt"
            )

            # Validação de segurança: aceitar apenas esquemas http/https
            parsed = urlparse(url)
            if parsed.scheme.lower() not in ("http", "https"):
                self.exception = Exception(
                    f"Invalid URL scheme: {parsed.scheme}")
                return False

            # Follow redirects (max 5) using http.client and validate scheme on redirects
            max_redirects = 5
            current_url = url
            data: Optional[Dict[str, Any]] = None

            for hop in range(max_redirects + 1):
                parsed = urlparse(current_url)
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
                    conn.request("GET", path, headers={
                                 "User-Agent": "MTL-Tools-QGIS"})
                    resp = conn.getresponse()
                    status = resp.status

                    if 300 <= status < 400:
                        # Redirect
                        location = resp.getheader("Location")
                        conn.close()
                        logger.info(
                            f"Redirect {status} -> {location}", code="REDIRECT_FOLLOW"
                        )
                        if not location:
                            logger.warning(
                                "Redirect without Location header",
                                code="REDIRECT_NO_LOCATION",
                            )
                            # Graceful: não aborta pipeline, retorna dados vazios
                            self.result = {}
                            return True
                        # Resolve relative redirects
                        new_parsed = urlparse(location)
                        if not new_parsed.scheme:
                            current_url = urljoin(current_url, location)
                        else:
                            current_url = location
                        # validate scheme
                        new_scheme = urlparse(current_url).scheme.lower()
                        if new_scheme not in ("http", "https"):
                            logger.warning(
                                f"Invalid redirect scheme: {new_scheme}",
                                code="REDIRECT_INVALID_SCHEME",
                            )
                            # Graceful: não aborta pipeline, retorna dados vazios
                            self.result = {}
                            return True
                        continue

                    elif status != 200:
                        logger.warning(
                            f"HTTP error {status} from reverse geocode API",
                            code="HTTP_ERROR",
                        )
                        # Graceful: não aborta pipeline, retorna dados vazios
                        self.result = {}
                        return True

                    else:
                        data = json.loads(resp.read().decode("utf-8"))
                        conn.close()
                        break

                except (TimeoutError, http.client.HTTPException, ConnectionError, OSError) as e:
                    logger.warning(
                        f"Reverse geocode API unavailable: {e}",
                        code="HTTP_REQUEST_ERROR",
                    )
                    # Graceful: timeout/falha de rede não aborta pipeline
                    self.result = {}
                    return True

                except Exception as e:
                    logger.exception(e, code="HTTP_REQUEST_ERROR")
                    self.exception = e
                    return False

            if data is None:
                logger.warning(
                    "No data received from reverse geocode API",
                    code="NO_DATA",
                )
                # Graceful: não aborta pipeline, retorna dados vazios
                self.result = {}
                return True

            admin = data.get("localityInfo", {}).get("administrative", [])

            municipio: Optional[str] = None
            state_district: Optional[str] = None
            state: Optional[str] = None
            region: Optional[str] = None
            country: Optional[str] = data.get("countryName")

            for item in admin:
                lvl = item.get("adminLevel")
                name = item.get("name")
                if not name:
                    continue
                if lvl == 8:
                    municipio = name
                elif lvl == 5:
                    state_district = name
                elif lvl == 4:
                    state = name
                elif lvl == 3:
                    region = name

            if not municipio:
                municipio = data.get("city") or data.get("locality")
            if not state:
                state = data.get("principalSubdivision")
            if not any([municipio, state, country]):
                self.exception = Exception(
                    "Dados administrativos indisponíveis")
                return False

            self.result = {
                "municipio": municipio,
                "state_district": state_district,
                "state": state,
                "region": region,
                "country": country,
            }
            return True

        except Exception as e:
            self.exception = e
            return False
