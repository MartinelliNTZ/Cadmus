# -*- coding: utf-8 -*-
import os
from PyQt5.QtGui import QIcon

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterCrs,
    QgsFeatureSink,
    QgsProcessing
)
import os
import re
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsFields, QgsField, QgsFeature, QgsCoordinateTransform
)


# Preferências
from ..utils.Preferences import load_tool_prefs, save_tool_prefs

# Lógicas externas
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
import re
from ..utils.ToolKeys import ToolKey


TOOL_KEY = ToolKey.RASTER_MASS_SAMPLER


class RasterMassSampler(QgsProcessingAlgorithm):

    """
        QgsProcessingAlgorithm: Amostragem massiva de rasters para pontos.

        Este algoritmo recebe uma camada de pontos e uma lista de rasters (ou camadas raster),
        amostra o valor de cada raster no local de cada ponto e retorna uma nova camada
        com os atributos originais dos pontos mais colunas com os valores amostrados.

        Design e responsabilidade:
        - `processAlgorithm` orquestra o fluxo (validação, construção de campos, amostragem, escrita)
        - `build_output_fields` cria os `QgsFields` de saída e gera nomes de campo a partir
            do `layer.name()` dos rasters (sanitizado, truncado e garantindo unicidade)
        - `_sanitize_field_name` encapsula as regras de normalização e garantia de unicidade
        - `build_transforms` prepara transforms CRS para amostragem (pontos -> raster CRS)
        - `sample_features` itera sobre os pontos e realiza a amostragem usando `dataProvider().sample`
        - `write_sink` escreve o resultado no sink de saída e persiste preferências quando aplicável

        Observações:
        - Prefira reutilizar utilitários existentes em `utils.vector` e `utils.raster`; aqui
            usamos `VectorLayerProjection.reproject_features` para reprojeção final quando solicitado.
        - Os nomes de campos são limitados a 10 caracteres para compatibilidade com formatos legados.
        """

    INPUT_POINTS = "INPUT_POINTS"
    INPUT_RASTERS = "INPUT_RASTERS"
    OUTPUT_CRS = "OUTPUT_CRS"
    OUTPUT = "OUTPUT"

    def name(self):
        return "raster_mass_sampler"

    def displayName(self):
        return "Amostragem Massiva de Rasters"

    def createInstance(self):
        return RasterMassSampler()

    # -------------------------- INIT -------------------------
    def initAlgorithm(self, config=None):

        prefs = load_tool_prefs(TOOL_KEY)

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                "Pontos de entrada",
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                "Rasters",
                QgsProcessing.TypeRaster
            )
        )

        # Agora só existe CRS DE SAÍDA
        self.addParameter(
            QgsProcessingParameterCrs(
                self.OUTPUT_CRS,
                "Reprojetar camada de saída (opcional)",
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Valores_Amostrados"
            )
        )

    # ----------------------- PROCESS -------------------------
    def processAlgorithm(self, params, context, feedback):
        pts = self.parameterAsSource(params, self.INPUT_POINTS, context)
        rasters = self.parameterAsLayerList(params, self.INPUT_RASTERS, context)

        # ----------------- CRS DE SAÍDA -----------------
        output_crs = None
        output_crs = self.parameterAsCrs(params, self.OUTPUT_CRS, context)
        if not output_crs.isValid():
            output_crs = None

        feedback.pushInfo(f"CRS de saída: {output_crs.authid() if output_crs else 'None'}")

        # Construir campos de saída e nomes de campo raster
        out_fields, raster_fields = self.build_output_fields(pts, rasters)

        # Preparar transforms CRS (pontos -> raster)
        transforms = self.build_transforms(pts, rasters, context)

        # Executar amostragem
        features = self.sample_features(pts, rasters, transforms, out_fields, feedback)

        # ----------------- REPROJEÇÃO SE NECESSÁRIO -----------------
        if output_crs:
            source_crs = pts.sourceCrs()

            features = VectorLayerProjection.reproject_features(
                features,
                source_crs,
                output_crs,
                context
            )

        final_crs = output_crs if output_crs else pts.sourceCrs()

        # ----------------- SINK -----------------
        sink, dest = self.parameterAsSink(
            params,
            self.OUTPUT,
            context,
            out_fields,
            pts.wkbType(),
            final_crs
        )

        for f in features:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        # ----------------- LINK E PREFERÊNCIAS DE SAÍDA -----------------
        if dest and isinstance(dest, str) and not dest.startswith("memory:"):
            out_folder = os.path.dirname(dest)
            clickable = f"<a href=\"file:///{out_folder}\">{out_folder}</a>"
            feedback.pushInfo(f"Arquivo salvo em: {clickable}")

            prefs = load_tool_prefs(TOOL_KEY)
            prefs["last_output_folder"] = out_folder
            prefs["last_output_file"] = dest
            save_tool_prefs(TOOL_KEY, prefs)

        return {self.OUTPUT: dest}

    # ------------------------ UI INFO ------------------------
    def icon(self):
        path = os.path.join(os.path.dirname(__file__), "..", "resources","icons", "raster_mass.ico")
        return QIcon(path)

    def group(self):
        return "Estatistica"

    def groupId(self):
        return "estatistica"

    # ---------------------- Helpers ----------------------
    def build_output_fields(self, pts, rasters, max_len: int = 10):
        """
        Cria e retorna (out_fields, raster_field_names).

        - Copia os campos de `pts` para `out_fields`.
        - Gera nomes de campo a partir de `r.name()` para cada raster,
          sanitiza, trunca e garante unicidade.
        """
        out_fields = QgsFields()
        try:
            for f in pts.fields():
                out_fields.append(f)
        except Exception:
            if isinstance(pts, QgsFields):
                for f in pts:
                    out_fields.append(f)

        raster_fields = []
        for ras in rasters:
            layer_name = ras.name() if hasattr(ras, 'name') else str(ras)
            candidate = self._sanitize_field_name(layer_name, raster_fields, max_len=max_len)
            raster_fields.append(candidate)
            out_fields.append(QgsField(candidate, QVariant.Double))

        return out_fields, raster_fields

    def _sanitize_field_name(self, layer_name: str, existing: list, max_len: int = 10) -> str:
        """
        Sanitiza `layer_name` para um identificador de campo válido:
        - substituir caracteres inválidos por `_`
        - truncar para `max_len`
        - quando já existir, acrescentar sufixo numérico garantindo unicidade
        """
        field_base = re.sub(r"[^0-9A-Za-z_]", "_", layer_name)
        candidate = field_base[:max_len]
        if candidate in existing:
            i = 1
            while True:
                suffix = f"_{i}"
                avail_len = max_len - len(suffix)
                new_candidate = (field_base[:avail_len] + suffix) if avail_len > 0 else (field_base[:max_len])
                if new_candidate not in existing:
                    candidate = new_candidate
                    break
                i += 1
        return candidate

    def build_transforms(self, pts, rasters, context):
        """Cria lista de QgsCoordinateTransform do CRS dos pontos para o CRS de cada raster."""
        effective_pts_crs = None
        try:
            effective_pts_crs = pts.sourceCrs()
        except Exception:
            effective_pts_crs = None

        transforms = []
        for ras in rasters:
            transforms.append(
                QgsCoordinateTransform(
                    effective_pts_crs,
                    ras.crs(),
                    context.transformContext()
                )
            )
        return transforms

    def sample_features(self, pts, rasters, transforms, out_fields, feedback):
        """
        Itera sobre os pontos e amostra cada raster, retornando lista de QgsFeature.
        Usa `dataProvider().sample()` para ler valores.
        """
        result = []
        for feat in pts.getFeatures():
            geom = feat.geometry()
            if geom is None:
                continue

            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(geom)
            attrs = feat.attributes()

            for i, ras in enumerate(rasters):
                try:
                    pt = transforms[i].transform(geom.asPoint())
                    val = ras.dataProvider().sample(pt, 1)[0]
                except Exception:
                    val = None

                feedback.pushInfo(f"[DEBUG] Ponto {feat.id()}, Raster {ras.name()} = {val}")
                attrs.append(float(val) if val is not None else None)

            out_feat.setAttributes(attrs)
            result.append(out_feat)

        return result

    def write_sink(self, params, context, out_fields, features, pts, feedback):
        """Escreve `features` no sink configurado pelos `params` e persiste preferências."""
        sink, dest = self.parameterAsSink(
            params,
            self.OUTPUT,
            context,
            out_fields,
            pts.wkbType(),
            pts.sourceCrs()
        )

        for f in features:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        if dest and isinstance(dest, str) and not dest.startswith("memory:"):
            out_folder = os.path.dirname(dest)
            clickable = f"<a href=\"file:///{out_folder}\">{out_folder}</a>"
            feedback.pushInfo(f"Arquivo salvo em: {clickable}")

            prefs = load_tool_prefs(TOOL_KEY)
            prefs["last_output_folder"] = out_folder
            prefs["last_output_file"] = dest
            save_tool_prefs(TOOL_KEY, prefs)

        return {self.OUTPUT: dest}
