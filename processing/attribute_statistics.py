# -*- coding: utf-8 -*-
import os
import math
from datetime import datetime
from typing import Dict, Any


from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessing,
    QgsProcessingParameterDefinition,
    QgsProcessingException,
    QgsVectorLayer,
    QgsProject
)

# Preferências
from ..utils.Preferences import load_tool_prefs, save_tool_prefs
from ..utils.ToolKeys import ToolKey


# Import do model
from .model.attribute_statistics_model import  AttributeStatisticsModel

TOOL_KEY = ToolKey.ATTRIBUTE_STATISTICS


class PreferencesManager:
    """
    Wrapper simples para carregar/salvar preferências de ferramenta.
    Mantém a dependência com utils.preferences centralizada aqui para que
    o model possa ser testado substituindo essas funções (injeção).
    """
    def __init__(self, load_tool_prefs_func, save_tool_prefs_func, tool_key: str):
        self._load = load_tool_prefs_func
        self._save = save_tool_prefs_func
        self.tool_key = tool_key

    def load(self) -> Dict[str, Any]:
        prefs = self._load(self.tool_key) or {}
        return {
            "precision": int(prefs.get("precision", 4)),
            "exclude_fields": prefs.get("exclude_fields", []),
            "last_output_folder": prefs.get("last_output_folder", ""),
            "last_layer_source": prefs.get("last_layer_source", ""),
            "force_ptbr": bool(prefs.get("force_ptbr", False)),
            "load_after": bool(prefs.get("load_after", False)),
            "stats_enabled": prefs.get("stats_enabled", {})
        }

    def save(self, **kwargs):
        self._save(self.tool_key, kwargs)

class AttributeStatisticsAlgorithm(QgsProcessingAlgorithm):

    INPUT_LAYER = "INPUT_LAYER"
    EXCLUDE_FIELDS = "EXCLUDE_FIELDS"
    PRECISION = "PRECISION"
    PTBR_FORMAT = "PTBR_FORMAT"
    LOAD_AFTER = "LOAD_AFTER"
    OUTPUT = "OUTPUT"

    # Rótulos (usados na UI e para decidir colunas)
    STATS = {
        "MEAN": "Media",
        "MEAN_ABS": "Media Absoluta",
        "STD_POP": "Desvio Padrao (Pop.)",
        "STD_SAMP": "Desvio Padrao (Amostra)",
        "MIN": "Minimo",
        "MAX": "Maximo",
        "RANGE": "Amplitude",
        "MEDIAN": "Mediana",
        "P5": "Percentil 5%",
        "P95": "Percentil 95%",
        "MODE": "Moda",
        "VARIANCE": "Variancia",
        "SUM": "Soma",
        "CV": "Coeficiente de Variaçao",
        "SKEW": "Assimetria",
        "KURT": "Curtose"
    }

    def name(self):
        return "attribute_statistics_mtl"

    def displayName(self):
        return "Estatísticas de Atributos (Cadmus)"

    def group(self):
        return "Estatística"

    def groupId(self):
        return "estatistica"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources","icons", "attribute_stats.ico")
        return QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

    def createInstance(self):
        return AttributeStatisticsAlgorithm()

    # ----------------------------------------------------
    # INIT: parâmetros -> aqui apenas constrói UI usando prefs do PreferencesManager
    # ----------------------------------------------------
    def initAlgorithm(self, config=None):

        prefs_manager = PreferencesManager(load_tool_prefs, save_tool_prefs, TOOL_KEY)
        prefs = prefs_manager.load()
        self._prefs_manager = prefs_manager
        self._model = AttributeStatisticsModel()

        # Camada de entrada
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                "Camada de entrada",
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # Campos a excluir
        self.addParameter(
            QgsProcessingParameterField(
                self.EXCLUDE_FIELDS,
                "Campos a excluir (opcional)",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                allowMultiple=True,
                optional=True
            )
        )

        # Precisão
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PRECISION,
                "Precisão (casas decimais)",
                type=QgsProcessingParameterNumber.Integer,
                minValue=0,
                maxValue=12,
                defaultValue=prefs["precision"]
            )
        )

        # Avançados: carregar após, forçar PT-BR
        p_load = QgsProcessingParameterBoolean(
            self.LOAD_AFTER,
            "Carregar CSV automaticamente após execução",
            defaultValue=prefs["load_after"]
        )
        p_load.setFlags(p_load.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_load)

        p_force_ptbr = QgsProcessingParameterBoolean(
            self.PTBR_FORMAT,
            "Forçar CSV no formato PT-BR (usar ; e ,)",
            defaultValue=prefs["force_ptbr"]
        )
        p_force_ptbr.setFlags(p_force_ptbr.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_force_ptbr)

        # Checkboxes de estatísticas (marcados conforme prefs)
        enabled_stats = prefs.get("stats_enabled", {})
        for key, label in self.STATS.items():
            p = QgsProcessingParameterBoolean(
                key,
                f"Calcular: {label}",
                defaultValue=enabled_stats.get(key, True)
            )
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        # Output (arquivo CSV) — default folder do último usado
        last_folder = prefs.get("last_output_folder", "")
        last_name = "atributos_estatistica.csv"
        default_output = os.path.join(last_folder, last_name) if last_folder else None

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Arquivo CSV de saída",
                fileFilter="CSV (*.csv)",
                defaultValue=default_output
            )
        )

    # ----------------------------------------------------
    # PROCESSAMENTO: usa AttributeStatisticsModel para toda a lógica
    # ----------------------------------------------------
    def processAlgorithm(self, parameters, context, feedback):

        # recarrega prefs antes de executar (estado antes)
        prefs_before = self._prefs_manager.load()

        layer = self.parameterAsLayer(parameters, self.INPUT_LAYER, context)
        if layer is None:
            raise QgsProcessingException("Camada inválida.")

        exclude_fields = self.parameterAsFields(parameters, self.EXCLUDE_FIELDS, context) or []
        precision = int(self.parameterAsInt(parameters, self.PRECISION, context))
        ptbr_format = bool(self.parameterAsBool(parameters, self.PTBR_FORMAT, context))
        load_after = bool(self.parameterAsBool(parameters, self.LOAD_AFTER, context))
        stats_enabled = {k: self.parameterAsBool(parameters, k, context) for k in self.STATS.keys()}

        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        out_folder = os.path.dirname(output_path)

        # Extrair campos numéricos (model faz isso)
        numeric_fields = self._model.extract_numeric_fields(layer.fields())
        # remover os excluídos pelo usuário
        numeric_fields = [f for f in numeric_fields if f not in exclude_fields]

        if not numeric_fields:
            feedback.pushInfo("Nenhum campo numérico encontrado.")
            return {self.OUTPUT: output_path}

        # coletar valores (model)
        total = layer.featureCount()
        # Para alimentar progress bar, iteramos e adicionamos features a uma lista generator.
        # O model aceita um iterable de features.
        features_iter = layer.getFeatures()
        values_by_field = {fn: [] for fn in numeric_fields}

        for i, feat in enumerate(features_iter):
            for fn in numeric_fields:
                v = feat[fn]
                if v is None:
                    continue
                try:
                    val = float(v)
                    if math.isfinite(val):
                        values_by_field[fn].append(val)
                except:
                    pass
            if total:
                feedback.setProgress(int(100 * i / total))

        # formato CSV (ptbr)
        force_ptbr = bool(self.parameterAsBool(parameters, self.PTBR_FORMAT, context))
        if force_ptbr:
            sep = ";"
            dec = ","
        else:
            sep = ";" if ptbr_format else ","
            dec = "," if ptbr_format else "."

        # Cabeçalhos
        headers = ["Campo", "Contagem"]
        for key, label in self.STATS.items():
            if stats_enabled.get(key, False):
                headers.append(label)

        def fmt(v):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return ""
            txt = str(round(v, precision))
            return txt.replace(".", dec)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sep.join(headers) + "\n")

                # calcular estatísticas usando model
                computed = self._model.compute_all(values_by_field, stats_enabled)

                for fn in numeric_fields:
                    vals = sorted(values_by_field[fn])
                    n = len(vals)
                    row = [fn, str(n)]

                    if n == 0:
                        row += [""] * (len(headers) - 2)
                        f.write(sep.join(row) + "\n")
                        continue

                    # Mantivemos a mesma ordem lógica do arquivo original.
                    for key in self.STATS.keys():
                        if stats_enabled.get(key, False):
                            v = computed.get(fn, {}).get(key, float("nan"))
                            row.append(fmt(v))

                    f.write(sep.join(row) + "\n")

        except Exception as e:
            raise QgsProcessingException(f"Erro ao salvar CSV: {e}")

        # salvar preferências via PreferencesManager
        self._prefs_manager.save(
            precision=precision,
            exclude_fields=exclude_fields,
            last_output_folder=out_folder,
            last_layer_source=layer.source(),
            force_ptbr=force_ptbr,
            load_after=load_after,
            stats_enabled=stats_enabled
        )

        # Carregar CSV automaticamente (mesmo comportamento)
        if load_after and output_path:
            uri = (
                f"file:///{output_path}"
                f"?type=csv&delimiter={sep}&detectTypes=yes&decimalPoint={dec}"
            )
            vl = QgsVectorLayer(uri, os.path.basename(output_path), "delimitedtext")
            if vl.isValid():
                context.temporaryLayerStore().addMapLayer(vl)
                QgsProject.instance().addMapLayer(vl)
                feedback.pushInfo(f"Arquivo carregado como camada: {output_path}")

        if output_path:
            feedback.pushInfo(f"Arquivo CSV gerado: file:///{output_path}")

        clickable = f"<a href=\"file:///{out_folder}\">{out_folder}</a>"
        feedback.pushInfo(f"Arquivo salvo em: {clickable}")

        return {self.OUTPUT: output_path}
