# -*- coding: utf-8 -*-


from qgis.core import QgsDistanceArea, QgsProject

from .BaseTask import BaseTask


class LineFieldsTask(BaseTask):
    """
    Task assíncrona para calcular comprimento de linhas.

    Esta implementação é "compute-only" e NÃO modifica a camada diretamente.
    Ela retorna um dicionário com o formato:
      { 'updates': { fid: { field_name: value, ... }, ... }, 'missing_fields': [field_name, ...] }
    O Step correspondente aplica as mudanças no thread principal.
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
        super().__init__("Calculando comprimento de linhas", tool_key)
        self.layer = layer
        self.field_map = field_map
        self.precision = precision

        self.logger.debug(
            f"LineFieldsTask.__init__: layer={layer.name()}, modes={list(field_map.keys())}"
        )

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        self.logger.info("LineFieldsTask._run: START - computing line lengths (worker)")

        # nudge progress bar immediately
        self.setProgress(1)

        updates = {}
        total = self.layer.featureCount() or 0
        count = 0
        computed = 0
        last_pct = -1

        d = QgsDistanceArea()
        d.setSourceCrs(self.layer.crs(), QgsProject.instance().transformContext())
        ell = self.layer.crs().ellipsoidAcronym() or "WGS84"
        d.setEllipsoid(ell)

        for feat in self.layer.getFeatures():
            if self.isCanceled():
                self.logger.info("LineFieldsTask: cancelado durante cálculo")
                return False

            count += 1
            geom = feat.geometry()
            if geom and not geom.isEmpty():
                vals = {}
                if "Elipsoidal" in self.field_map:
                    length_m = d.measureLength(geom)
                    vals[self.field_map["Elipsoidal"]] = round(length_m, self.precision)
                if "Cartesiana" in self.field_map:
                    vals[self.field_map["Cartesiana"]] = round(
                        geom.length(), self.precision
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
                    f"LineFieldsTask: PROGRESS - scanned {count} features, computed {computed}"
                )

        self.logger.info(
            f"LineFieldsTask._run: FINISHED - computed={computed} / scanned={count}"
        )

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
