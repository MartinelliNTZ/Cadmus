# -*- coding: utf-8 -*-
from qgis.core import QgsTask
import json
import urllib.request


class ReverseGeocodeTask(QgsTask):
    """
    Model puro:
    - Executa reverse geocode
    - Retorna dados ou erro
    - NÃO interage com UI
    """

    def __init__(self, lat, lon, callback):
        super().__init__("Reverse Geocode (BigDataCloud)", QgsTask.CanCancel)
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
                "https://api.bigdatacloud.net/data/reverse-geocode-client"
                f"?latitude={self.lat}&longitude={self.lon}"
                "&localityLanguage=pt"
            )

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "MTL-Tools-QGIS"}
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            admin = data.get("localityInfo", {}).get("administrative", [])

            municipio = state_district = state = region = None
            country = data.get("countryName")

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
                self.error = "Dados administrativos indisponíveis"
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
            self.error = str(e)
            return False

    # --------------------------------------------------
    # CALLBACK FINAL
    # --------------------------------------------------
    def finished(self, success):
        # Backwards-compatible callback + pipeline hooks
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
