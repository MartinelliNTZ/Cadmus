# -*- coding: utf-8 -*-
from pathlib import Path
from qgis.core import (
            QgsVectorFileWriter,
            QgsProject,
            QgsVectorLayer,
            QgsCoordinateReferenceSystem,
            QgsCoordinateTransform,
            QgsFeature,
            QgsGeometry, 
            QgsPointXY,  
            QgsWkbTypes,
            QgsFeatureRequest,
            QgsField
        )
from qgis.core import (
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsProject,
    QgsCoordinateTransformContext
)
from pathlib import Path
import os
from typing import Optional
import processing
from qgis.PyQt.QtCore import QVariant


class VectorLayerAttributes:
    @staticmethod
    def ensure_has_features(layer, logger=None):
        """Valida se a camada tem feições.
        Recebe: layer (QgsVectorLayer), logger.
        Retorna: bool.
        Não acessa iface nem exibe mensagens.
        """
        if logger:
            logger.debug(f"Verificando feições na camada: {layer.name()}. Total: {layer.featureCount()}")
        return layer.featureCount() > 0
    """
    Responsável por campos e atributos de camadas vetoriais.
    
    Escopo:
    - Gerenciar campos e estrutura de dados
    - Criar, remover, renomear campos
    - Validar dados de atributos
    - Calcular valores para campos
    - Ponte entre dados espaciais e tabulares
    
    Responsabilidade Principal:
    - Orquestrar operações de dados tabulares da camada
    - Garantir integridade estrutural de atributos
    - Facilitar acesso e modificação de dados tabulares
    
    NÃO é Responsabilidade:
    - Transformar geometrias (use VectorLayerGeometry)
    - Calcular métricas espaciais (use VectorLayerMetrics)
    - Reprojetar (use VectorLayerProjection)
    - Carregar ou salvar (use VectorLayerSource)
    """

    def get_layer_fields(self, layer, external_tool_key="untraceable"):
        """Retorna lista com todos os campos da camada e seus tipos."""
        pass

    @staticmethod
    def copy_attributes(
        target_layer,
        source_layer,
        field_names=None,
        conflict_resolver=None
    ):
        """
        Copia estrutura de atributos da camada source para target.

        conflict_resolver(field_name) -> "skip" | "rename" | "cancel"
        """

        if not target_layer.isEditable():
            target_layer.startEditing()

        for field in source_layer.fields():

            if field_names and field.name() not in field_names:
                continue

            idx = target_layer.fields().indexOf(field.name())

            # campo não existe
            if idx == -1:
                target_layer.addAttribute(QgsField(
                    field.name(),
                    field.type(),
                    field.typeName(),
                    field.length(),
                    field.precision()
                ))
                continue

            # conflito
            action = "skip"
            if conflict_resolver:
                action = conflict_resolver(field.name())

            if action == "cancel":
                return False

            if action == "rename":
                new_name = VectorLayerAttributes._generate_field_name(
                    target_layer, field.name()
                )
                target_layer.addAttribute(QgsField(
                    new_name,
                    field.type(),
                    field.typeName(),
                    field.length(),
                    field.precision()
                ))

        target_layer.updateFields()
        return True
    
    @staticmethod
    def _generate_field_name(layer, base):
        i = 1
        while layer.fields().indexOf(f"{base}_{i}") != -1:
            i += 1
        return f"{base}_{i}"



    def create_new_field(self, layer, field_name, field_type, field_width, external_tool_key="untraceable"):
        """Cria um novo campo na camada com tipo e tamanho especificados."""
        pass

    def delete_field(self, layer, field_name, external_tool_key="untraceable"):
        """Remove um campo da camada."""
        pass

    def rename_field(self, layer, old_field_name, new_field_name, external_tool_key="untraceable"):
        """Renomeia um campo existente na camada."""
        pass

    def get_field_values(self, layer, field_name, external_tool_key="untraceable"):
        """Obtém todos os valores únicos de um campo."""
        pass

    def calculate_field_statistics(self, layer, field_name, external_tool_key="untraceable"):
        """Calcula estatísticas (min, max, média, etc) para um campo numérico."""
        pass

    def validate_field_data_type(self, layer, field_name, expected_type, external_tool_key="untraceable"):
        """Verifica se os dados em um campo correspondem ao tipo esperado."""
        pass

    def update_field_values(self, layer, field_name, value_dict, external_tool_key="untraceable"):
        """Atualiza valores de um campo com base em um dicionário de mapeamento."""
        pass

    def check_for_duplicate_values(self, layer, field_name, external_tool_key="untraceable"):
        """Identifica valores duplicados em um campo."""
        pass

    def get_feature_attribute(self, feature, field_name, external_tool_key="untraceable"):
        """Obtém o valor de um atributo específico de uma feição."""
        pass

    def set_feature_attribute(self, feature, field_name, value, external_tool_key="untraceable"):
        """Define o valor de um atributo específico de uma feição."""
        pass

    def export_attributes_to_table(self, layer, output_path, external_tool_key="untraceable"):
        """Exporta todos os atributos da camada para um arquivo tabular."""
        pass

    @staticmethod
    def create_point_coordinate_fields(layer, field_map, precision: int = 8):
        """
        Cria campos double para armazenar coordenadas de ponto.
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial para adicionar campos
        field_map : dict
            Mapeamento {"x": "x", "y": "y", "z": "z_1"} (z é opcional)
        precision : int
            Casas decimais para o campo
        
        Returns
        -------
        bool
            True se sucesso, False caso contrário
        """
        if not layer or not layer.isValid():
            return False
            
        if not layer.isEditable():
            layer.startEditing()
        
        try:
            for name in field_map.values():
                if layer.fields().lookupField(name) == -1:
                    layer.addAttribute(
                        QgsField(name, QVariant.Double, len=20, prec=precision)
                    )
            layer.updateFields()
            return True
        except Exception as e:
            return False

    @staticmethod
    def update_point_xy_coordinates(layer, field_map, precision: int = 8):
        """
        Atualiza campos X e Y com coordenadas do ponto.
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial de pontos
        field_map : dict
            Mapeamento {"x": "x", "y": "y"} com nomes dos campos
        precision : int
            Casas decimais para arredondamento das coordenadas
        """
        if not layer or not layer.isValid():
            return
            
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if geom and not geom.isEmpty():
                p = geom.asPoint()
                feat[field_map["x"]] = round(p.x(), precision)
                feat[field_map["y"]] = round(p.y(), precision)
                layer.updateFeature(feat)

    @staticmethod
    def update_feature_values(layer, z_values, z_field):
        """
        Atualiza campo de altimetria com valores calculados.
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial
        z_values : dict
            Mapeamento {feature_id: altitude_value}
        z_field : str
            Nome do campo de altitude
        """
        if not layer or not layer.isValid():
            return
            
        for fid, z in z_values.items():
            if z is not None:
                feat = layer.getFeature(fid)
                if feat.isValid():
                    feat[z_field] = z
                    layer.updateFeature(feat)

    @staticmethod
    def generate_field_name_with_suffix(base_name, suffix, max_length=10):
        """
        Gera nome de campo com sufixo respeitando limite de caracteres (SHP = 10).
        
        Parameters
        ----------
        base_name : str
            Nome base do campo (ex: 'length', 'area')
        suffix : str
            Sufixo a adicionar (ex: '_eli', '_car')
        max_length : int
            Comprimento máximo do nome (padrão: 10 para SHP)
            
        Returns
        -------
        str
            Nome do campo truncado se necessário (ex: 'len_eli' ao invés de 'length_eli')
        """
        full_name = f"{base_name}{suffix}"
        if len(full_name) <= max_length:
            return full_name
        
        # Truncar nome base para caber sufixo
        available_for_base = max_length - len(suffix)
        if available_for_base < 1:
            return full_name[:max_length]
        
        return f"{base_name[:available_for_base]}{suffix}"

    @staticmethod
    def resolve_field_names_for_calculation(layer, base_name, calculation_mode="Elipsoidal"):
        """
        Resolve nomes de campo baseado no modo de cálculo.
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial
        base_name : str
            Nome base do campo (ex: 'length', 'area')
        calculation_mode : str
            Modo de cálculo ('Elipsoidal', 'Cartesiana', 'Ambos')
            
        Returns
        -------
        dict
            Mapeamento de modo -> nome_do_campo
            Exemplo: {'Elipsoidal': 'length_eli'} ou 
                    {'Elipsoidal': 'length_eli', 'Cartesiana': 'length_car'}
        """
        field_map = {}
        
        if calculation_mode == "Ambos":
            # Criar campos para ambos os modos
            eli_name = VectorLayerAttributes.generate_field_name_with_suffix(base_name, "_eli")
            car_name = VectorLayerAttributes.generate_field_name_with_suffix(base_name, "_car")
            field_map["Elipsoidal"] = eli_name
            field_map["Cartesiana"] = car_name
        else:
            # Um único modo
            field_map[calculation_mode] = base_name
        
        return field_map
