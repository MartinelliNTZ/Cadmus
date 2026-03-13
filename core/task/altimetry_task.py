# -*- coding: utf-8 -*-
from qgis.core import QgsTask
import json
import urllib.request


class AltimetriaTask(QgsTask):
    """
    Model puro:
    - Consulta altimetria (OpenTopoData / SRTM 90m)
    - Retorna altitude ou erro
    - NÃO interage com UI
    """

    def __init__(self, lat, lon, callback):
        super().__init__("Altimetria (SRTM 90m)", QgsTask.CanCancel)
        self.lat = lat
        self.lon = lon
        self.callback = callback
        self.result = None
        self.error = None

    # --------------------------------------------------
    # EXECUÇÃO
    # --------------------------------------------------
    def run(self):
        try:
            url = (
                "https://api.opentopodata.org/v1/srtm90m"
                f"?locations={self.lat},{self.lon}"
            )

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            if data.get("status") != "OK":
                self.error = "Resposta inválida da API"
                return False

            results = data.get("results") or []
            if not results:
                self.error = "Nenhum dado retornado"
                return False

            elevation = results[0].get("elevation")
            if elevation is None:
                self.error = "Elevação indisponível"
                return False

            self.result = float(elevation)
            return True

        except Exception as e:
            self.error = str(e)
            return False

    # --------------------------------------------------
    # CALLBACK FINAL
    # --------------------------------------------------
    def finished(self, success):
        # Backwards-compatible callback
        try:
            if success:
                if hasattr(self, 'on_success') and callable(getattr(self, 'on_success')):
                    try:
                        self.on_success(self.result)
                    except Exception:
                        pass
                if hasattr(self, 'callback') and callable(self.callback):
                    try:
                        self.callback(self.result, None)
                    except Exception:
                        pass
            else:
                if hasattr(self, 'on_error') and callable(getattr(self, 'on_error')):
                    try:
                        self.on_error(self.error)
                    except Exception:
                        pass
                if hasattr(self, 'callback') and callable(self.callback):
                    try:
                        self.callback(None, self.error)
                    except Exception:
                        pass
        except Exception:
            pass
