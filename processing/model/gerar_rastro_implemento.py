# -*- coding: utf-8 -*-
"""
Model runner wrapper for the model 'MTL- Gerar_Rastro_Implemento'.
This class is intentionally small and generic: it will try to run the model
registered in Processing as `model:MTL- Gerar_Rastro_Implemento`. If the model
is not registered, it reports an error to the caller.

Preferences: saves last used input layer id and tamanhoimplemento using
`load_tool_prefs` / `save_tool_prefs`.
"""
import os
from pathlib import Path
import processing
from typing import Optional
from qgis.core import QgsProject
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes
from .utils.QgisMessageUtil import QgisMessageUtil

from .utils.preferences import load_tool_prefs, save_tool_prefs
from .utils.ToolKeys import ToolKey


class GerarRastroModel:
    """Execução direta do fluxo: explodir linhas -> buffer com metade do tamanho.

    Recebe uma camada de linhas ou um ID de camada e um valor numérico `tamanhoimplemento`.
    Salva preferências simples (última camada/tamanho) usando o sistema de prefs.
    """
    TOOL_KEY = ToolKey.GERAR_RASTRO_IMPLEMENTO

    def __init__(self, plugin_root: str = None):
        if plugin_root:
            self.plugin_root = Path(plugin_root)
        else:
            self.plugin_root = Path(__file__).resolve().parents[2]

    def load_prefs(self):
        return load_tool_prefs(self.TOOL_KEY)

    def save_prefs(self, data: dict):
        save_tool_prefs(self.TOOL_KEY, data)

    def run(self, input_layer,
            tamanhoimplemento,
            save_to_folder: bool = False,
            output_folder: Optional[str] = None,
            output_name: Optional[str] = None,
            output_path: Optional[str] = None,
            only_selected = False,
            feedback=None):

        """Executa explodir linhas e gerar buffer.

        Retorna o caminho/identificador do layer resultante quando possível.
        """
        
        if only_selected:
            input_layer, err = self.get_selected_features(layer)
            if err:
                QgisMessageUtil.modal_error(
                    self.iface,
                    "Erro ao selecionar feições. Erro: "+ err
                )
                return None

        # resolver objeto de camada
        layer = None
        try:
            if isinstance(input_layer, QgsVectorLayer):
                layer = input_layer
            else:
                layer = QgsProject.instance().mapLayer(input_layer)
        except Exception:
            layer = None

        if layer is None:
            raise ValueError("Camada de input não encontrada")

        # validar geometria: somente linhas
        geom_type = QgsWkbTypes.geometryType(layer.wkbType())
        if geom_type != QgsWkbTypes.LineGeometry:
            raise ValueError("A camada de entrada precisa conter apenas feições de LINHA.")

        # persistir prefs simples
        try:
            prefs = {"last_input_layer_id": layer.id(), "last_tamanhoimplemento": float(tamanhoimplemento)}
            self.save_prefs(prefs)
        except Exception:
            pass

        # 1) explodir linhas
        expl_params = {
            'INPUT': layer,
            'OUTPUT': 'memory:'
        }
        expl = processing.run('native:explodelines', expl_params, feedback=feedback)
        expl_out = expl.get('OUTPUT')

        # 2) buffer com metade do tamanho
        distance = float(tamanhoimplemento) / 2.0
        buff_params = {
            'INPUT': expl_out,
            'DISTANCE': distance,
            'SEGMENTS': 5,
            'END_CAP_STYLE': 1,
            'JOIN_STYLE': 1,
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': 'memory:'
        }

        # if user requested saving to a specific path, use it
        if save_to_folder and output_path:
            try:
                outp = Path(output_path)
                outp.parent.mkdir(parents=True, exist_ok=True)
                buff_params['OUTPUT'] = str(outp)
            except Exception:
                pass
        else:
            # if user requested saving to folder, prepare a shapefile path
            if save_to_folder and output_folder:
                try:
                    ts = int(__import__('time').time())
                    out_folder = Path(output_folder)
                    out_folder.mkdir(parents=True, exist_ok=True)
                    out_path = str(out_folder / f"Rastro_Implemento_{ts}.shp")
                    buff_params['OUTPUT'] = out_path
                except Exception:
                    pass

        # run buffer
        buff = processing.run('native:buffer', buff_params, feedback=feedback)
        buff_out = buff.get('OUTPUT')

        # Determine output layer name and try to load/apply style
        out_layer = None
        desired_name = output_name or 'Rastro_Implemento'

        try:
            # If saved to file, buff_out should be path
            if save_to_folder and isinstance(buff_out, str) and os.path.exists(buff_out):
                layer_name = Path(buff_out).stem if output_name is None else Path(output_name).stem
                out_layer = QgsVectorLayer(buff_out, layer_name, 'ogr')
                if out_layer and out_layer.isValid():
                    QgsProject.instance().addMapLayer(out_layer)
            else:
                # memory output: try loading with provider 'memory'
                if isinstance(buff_out, str) and buff_out.startswith('memory'):
                    out_layer = QgsVectorLayer(buff_out, desired_name, 'memory')
                    if out_layer and out_layer.isValid():
                        QgsProject.instance().addMapLayer(out_layer)
                elif isinstance(buff_out, QgsVectorLayer):
                    out_layer = buff_out
                    try:
                        out_layer.setName(desired_name)
                    except Exception:
                        pass
                    QgsProject.instance().addMapLayer(out_layer)
        except Exception:
            out_layer = None

        # Fallback: if still not loaded, load results (will run algorithm again)
        if out_layer is None or not out_layer.isValid():
            processing.runAndLoadResults('native:buffer', buff_params, feedback=feedback)
            # try to find by desired_name
            layers = QgsProject.instance().mapLayersByName(desired_name)
            if layers:
                out_layer = layers[0]
            else:
                # try generic name
                layers = QgsProject.instance().mapLayersByName('Rastro_Implemento')
                if layers:
                    out_layer = layers[0]

        if out_layer is None:
            return None

        # set final name
        try:
            final_name = output_name if output_name else 'Rastro_Implemento'
            out_layer.setName(final_name)
        except Exception:
            pass

        return out_layer
 