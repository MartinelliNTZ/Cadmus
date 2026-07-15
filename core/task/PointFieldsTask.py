# -*- coding: utf-8 -*-
from .BaseTask import BaseTask


class PointFieldsTask(BaseTask):
    """
    Task assíncrona para calcular campos X e Y.

    Modifica o arquivo original (sem criar cópias):
    1. Abre layer em modo edição
    2. Adiciona campos X e Y se não existem
    3. Calcula coordenadas no arquivo original
    4. Commita mudanças (salva direto no arquivo)

    Resultado: on_success() apenas confirma (microsegundos, não trava UI)
    """

    def __init__(self, *, layer, field_map, tool_key: str, tmp_dir: str = None):
        super().__init__("Calculando campos de pontos", tool_key)
        self.layer = layer
        self.field_map = field_map

        self.logger.debug(f"PointFieldsTask.__init__: layer={layer.name()}")

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        self.logger.info(
            "PointFieldsTask._run: START - computing point coordinates (worker)"
        )

        # nudge progress bar immediately so pipeline bar moves
        self.setProgress(1)

        updates = {}
        total = self.layer.featureCount() or 0
        count = 0
        computed = 0
        last_pct = -1
        const_prec = 8

        for feat in self.layer.getFeatures():
            if self.isCanceled():
                self.logger.info("PointFieldsTask: cancelado durante cálculo")
                return False

            count += 1
            geom = feat.geometry()
            if geom and not geom.isEmpty():
                p = geom.asPoint()
                vals = {}
                if "x" in self.field_map:
                    vals[self.field_map["x"]] = round(p.x(), const_prec)
                if "y" in self.field_map:
                    vals[self.field_map["y"]] = round(p.y(), const_prec)

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
                    f"PointFieldsTask: PROGRESS - scanned {count} features, computed {computed}"
                )

        self.logger.info(
            f"PointFieldsTask._run: CONCLUÍDO - computed={computed} / scanned={count}"
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
