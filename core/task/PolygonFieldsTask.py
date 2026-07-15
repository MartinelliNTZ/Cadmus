# -*- coding: utf-8 -*-
from qgis.core import QgsDistanceArea, QgsProject
from .BaseTask import BaseTask


class PolygonFieldsTask(BaseTask):
    """
    Task assíncrona para calcular área de polígonos.

    Modifica o arquivo original (sem criar cópias):
    1. Abre layer em modo edição
    2. Adiciona campos se necessário
    3. Calcula áreas no arquivo original
    4. Commita mudanças (salva direto no arquivo)

    Resultado: on_success() apenas confirma (microsegundos, não trava UI)
    """

    def __init__(
        self,
        *,
        layer,
        field_map,
        precision: int = 4,
        tool_key: str,
        tmp_dir: str = None,
    ):
        super().__init__("Calculando área de polígonos", tool_key)
        self.layer = layer
        self.field_map = field_map
        self.precision = precision

        self.logger.debug(
            f"PolygonFieldsTask.__init__: layer={layer.name()}, modes={list(field_map.keys())}"
        )

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        self.logger.info(
            "PolygonFieldsTask._run: START - calculando áreas no arquivo original"
        )

        # nudge progress bar immediately
        self.setProgress(1)

        # New approach: do not modify the layer in the worker thread.
        # Compute a mapping of feature id -> { field_name: value }
        updates = {}

        total = self.layer.featureCount() or 0
        count = 0
        computed = 0
        last_pct = -1

        for feat in self.layer.getFeatures():
            if self.isCanceled():
                self.logger.info("PolygonFieldsTask: cancelado durante cálculo")
                return False

            count += 1
            geom = feat.geometry()
            if geom and not geom.isEmpty():
                vals = {}
                # Elipsoidal
                if "Elipsoidal" in self.field_map:
                    d = QgsDistanceArea()
                    d.setSourceCrs(
                        self.layer.crs(), QgsProject.instance().transformContext()
                    )
                    ell = self.layer.crs().ellipsoidAcronym() or "WGS84"
                    d.setEllipsoid(ell)
                    area_m2 = d.measureArea(geom)
                    vals[self.field_map["Elipsoidal"]] = round(
                        area_m2 / 10000.0, self.precision
                    )
                # Cartesiana
                if "Cartesiana" in self.field_map:
                    area_m2 = geom.area()
                    vals[self.field_map["Cartesiana"]] = round(
                        area_m2 / 10000.0, self.precision
                    )

                if vals:
                    updates[feat.id()] = vals
                    computed += 1

            # report progress percentage
            if total > 0:
                pct = int(count * 100 / total)
                if pct != last_pct:
                    self.setProgress(pct)
                    last_pct = pct

            if count % 5000 == 0:
                self.logger.debug(
                    f"PolygonFieldsTask: PROGRESS - {count} features scanned, {computed} computed"
                )

        self.logger.info(
            f"PolygonFieldsTask._run: CONCLUÍDO - computed={computed} / scanned={count}"
        )

        # Return structured result for on_success to apply on main thread
        self.result = {
            "updates": updates,
            "missing_fields": [
                fname
                for fname in set(self.field_map.values())
                if fname not in [f.name() for f in self.layer.fields()]
            ],
        }
        self.setProgress(100)
        return True
