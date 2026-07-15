# -*- coding: utf-8 -*-
from qgis.core import QgsField, QgsFields, QgsVectorLayer, QgsFeature, QgsWkbTypes

from qgis.PyQt.QtCore import QVariant
from ...core.config.LogUtils import LogUtils


class VectorLayerAttributes:
    @staticmethod
    def ensure_fields(layer, field_specs, logger=None):
        """Garante a existência de campos e retorna nomes adicionados."""
        if not layer or not layer.isValid():
            return []

        if not layer.isEditable():
            layer.startEditing()

        added = []
        for spec in field_specs or []:
            if not spec:
                continue

            field_name = spec[0]
            field_type = spec[1] if len(spec) > 1 else QVariant.String
            field_len = spec[2] if len(spec) > 2 else 0
            field_prec = spec[3] if len(spec) > 3 else 0

            if layer.fields().lookupField(field_name) != -1:
                continue

            layer.addAttribute(
                QgsField(field_name, field_type, len=field_len, prec=field_prec)
            )
            added.append(field_name)

        if added:
            layer.updateFields()
            if logger:
                logger.debug(f"Campos adicionados: {added}")

        return added

    @staticmethod
    def apply_updates_by_field_name(layer, updates_by_fid, logger=None):
        """Aplica updates no buffer de edição usando nomes de campos."""
        if not layer or not layer.isValid() or not updates_by_fid:
            return 0

        if not layer.isEditable():
            layer.startEditing()

        name_to_idx = {field.name(): idx for idx, field in enumerate(layer.fields())}
        applied = 0

        for fid, field_map in updates_by_fid.items():
            for field_name, value in (field_map or {}).items():
                field_idx = name_to_idx.get(field_name)
                if field_idx is None:
                    if logger:
                        logger.warning(f"Campo ausente ao aplicar update: {field_name}")
                    continue
                if layer.changeAttributeValue(fid, field_idx, value):
                    applied += 1

        if logger:
            logger.debug(f"Total de updates aplicados: {applied}")
        return applied

    @staticmethod
    def generate_compatible_field_name(layer, base_name, max_length=255):
        """Gera nome compatível com limite do provider."""
        base = str(base_name or "").strip()
        if not base:
            base = "campo"

        if len(base) <= max_length and layer.fields().lookupField(base) == -1:
            return base

        suffix = 1
        trimmed = base[:max_length]
        candidate = trimmed
        while layer.fields().lookupField(candidate) != -1:
            suffix_text = f"_{suffix}"
            allowed = max(1, max_length - len(suffix_text))
            candidate = f"{base[:allowed]}{suffix_text}"
            suffix += 1
        return candidate

    @staticmethod
    def resolve_output_field_name(
        layer,
        base_name,
        *,
        conflict_resolver=None,
        max_length=255,
    ):
        """Resolve nome final do campo respeitando conflitos e limite do provider."""
        normalized = str(base_name or "").strip()[:max_length] or "campo"
        if layer.fields().lookupField(normalized) == -1:
            return normalized

        action = "replace"
        if conflict_resolver:
            action = conflict_resolver(normalized)

        if action == "cancel":
            return None
        if action == "replace":
            return normalized

        return VectorLayerAttributes.generate_compatible_field_name(
            layer,
            normalized,
            max_length=max_length,
        )

    @staticmethod
    def get_field_options(layer, include_empty=False, empty_key="", empty_label=""):
        """Retorna opcoes para seletores de campos no formato {key: label}."""
        options = {}

        if include_empty:
            options[empty_key] = empty_label or ""

        if not layer or not hasattr(layer, "fields"):
            return options

        try:
            for field in layer.fields():
                field_name = field.name()
                options[field_name] = field_name
        except Exception:
            return options

        return options

    @staticmethod
    def ensure_has_features(layer, logger=None):
        """Valida se a camada tem feições.
        Recebe: layer (QgsVectorLayer), logger.
        Retorna: bool.
        Não acessa iface nem exibe mensagens.
        """
        if logger:
            logger.debug(
                f"Verificando feições na camada: {layer.name()}. Total: {layer.featureCount()}"
            )
        return layer.featureCount() > 0

    @staticmethod
    def delete_fields_by_names(layer, field_names, logger=None):
        """Remove apenas os campos existentes informados."""
        if not layer or not layer.isValid():
            return 0

        field_indexes = []
        for field_name in field_names:
            idx = layer.fields().lookupField(field_name)
            if idx != -1:
                field_indexes.append(idx)

        if not field_indexes:
            if logger:
                logger.debug("Nenhum campo encontrado para remoção")
            return 0

        if logger:
            logger.debug(f"Removendo campos nos índices: {field_indexes}")

        if not layer.deleteAttributes(field_indexes):
            raise RuntimeError("Falha ao remover campos da camada")

        layer.updateFields()
        return len(field_indexes)

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
        if not layer or not layer.isValid():
            return []

        result = []
        for field in layer.fields():
            result.append(
                {
                    "name": field.name(),
                    "type": field.type(),
                    "type_name": field.typeName(),
                    "length": field.length(),
                    "precision": field.precision(),
                }
            )
        return result

    @staticmethod
    def copy_attributes(
        target_layer, source_layer, field_names=None, conflict_resolver=None
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

            if idx == -1:
                target_layer.addAttribute(
                    QgsField(
                        field.name(),
                        field.type(),
                        field.typeName(),
                        field.length(),
                        field.precision(),
                    )
                )
                continue

            action = "skip"
            if conflict_resolver:
                action = conflict_resolver(field.name())

            if action == "cancel":
                return False

            if action == "rename":
                new_name = VectorLayerAttributes._generate_field_name(
                    target_layer, field.name()
                )
                target_layer.addAttribute(
                    QgsField(
                        new_name,
                        field.type(),
                        field.typeName(),
                        field.length(),
                        field.precision(),
                    )
                )

        target_layer.updateFields()
        return True

    @staticmethod
    def _generate_field_name(layer, base):
        i = 1
        while layer.fields().indexOf(f"{base}_{i}") != -1:
            i += 1
        return f"{base}_{i}"

    def create_new_field(
        self,
        layer,
        field_name,
        field_type,
        field_width,
        external_tool_key="untraceable",
    ):
        """Cria um novo campo na camada com tipo e tamanho especificados."""
        pass

    def delete_field(self, layer, field_name, external_tool_key="untraceable"):
        """Remove um campo da camada."""
        pass

    def rename_field(
        self, layer, old_field_name, new_field_name, external_tool_key="untraceable"
    ):
        """Renomeia um campo existente na camada."""
        pass

    def get_field_values(self, layer, field_name, external_tool_key="untraceable"):
        """Obtém todos os valores únicos de um campo."""
        pass

    def calculate_field_statistics(
        self, layer, field_name, external_tool_key="untraceable"
    ):
        """Calcula estatísticas (min, max, média, etc) para um campo numérico."""
        pass

    def validate_field_data_type(
        self, layer, field_name, expected_type, external_tool_key="untraceable"
    ):
        """Verifica se os dados em um campo correspondem ao tipo esperado."""
        pass

    def update_field_values(
        self, layer, field_name, value_dict, external_tool_key="untraceable"
    ):
        """Atualiza valores de um campo com base em um dicionário de mapeamento."""
        pass

    def check_for_duplicate_values(
        self, layer, field_name, external_tool_key="untraceable"
    ):
        """Identifica valores duplicados em um campo."""
        pass

    def get_feature_attribute(
        self, feature, field_name, external_tool_key="untraceable"
    ):
        """Obtém o valor de um atributo específico de uma feição."""
        pass

    def set_feature_attribute(
        self, feature, field_name, value, external_tool_key="untraceable"
    ):
        """Define o valor de um atributo específico de uma feição."""
        pass

    def export_attributes_to_table(
        self, layer, output_path, external_tool_key="untraceable"
    ):
        """Exporta todos os atributos da camada para um arquivo tabular."""
        pass

    @staticmethod
    def reorder_fields_alphabetically(layer):
        """
        Cria uma nova layer com campos reordenados em ordem alfabética (case-insensitive).
        Compatível com QGIS 3.16+.

        A ordenação segue o padrão key=str.lower:
        - Case-insensitive: 'A' e 'a' na mesma sequência
        - Números e símbolos vêm antes das letras (ordem ASCII)
        - 'abacate', 'Alicate', 'arcelga': 'abacate' -> 'Alicate' -> 'arcelga'

        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial fonte

        Returns
        -------
        QgsVectorLayer or None
            Nova layer com campos ordenados, ou None em caso de erro
        """
        logger = LogUtils(tool="untraceable", class_name="VectorLayerAttributes")
        if not layer or not layer.isValid():
            logger.error("Camada inválida para reordenar campos")
            return None

        fields = layer.fields()
        if fields.count() <= 1:
            return layer

        field_names = [field.name() for field in fields]
        sorted_names = sorted(field_names, key=lambda x: str(x).lower())

        if sorted_names == field_names:
            return layer

        try:
            # 1. Construir QgsFields na ordem alfabética
            new_fields = QgsFields()
            for name in sorted_names:
                idx = fields.lookupField(name)
                if idx != -1:
                    new_fields.append(fields.at(idx))
            if new_fields.count() != fields.count():
                logger.error("Contagem de campos não corresponde após reordenação")
                return None

            # 2. Criar nova camada em memória com os campos ordenados
            wkb_type = layer.wkbType()
            crs = layer.crs()
            geom_type = QgsWkbTypes.displayString(wkb_type)
            new_uri = f"{geom_type}?crs={crs.authid()}"
            new_layer = QgsVectorLayer(new_uri, layer.name(), "memory")
            new_prov = new_layer.dataProvider()
            new_prov.addAttributes(new_fields)
            new_layer.updateFields()

            # 3. Copiar features com atributos mapeados para a nova ordem
            new_layer.startEditing()
            for feat in layer.getFeatures():
                new_feat = QgsFeature(new_fields)
                new_feat.setGeometry(feat.geometry())
                # Atribuir valores na ordem alfabetica (por nome de campo)
                for field_name in sorted_names:
                    attr_idx = fields.lookupField(field_name)
                    if attr_idx != -1:
                        new_feat[field_name] = feat.attributes()[attr_idx]
                new_layer.addFeature(new_feat)
            new_layer.commitChanges()

            logger.debug("Nova layer criada com campos reordenados alfabeticamente")
            return new_layer

        except Exception as e:
            logger.error(f"Erro ao reordenar campos: {e}")
            return None

    @staticmethod
    def create_point_coordinate_fields(
        layer, field_map, precision: int = 8, tool_key=None
    ):
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
        tool_key : str, optional
            ToolKey da ferramenta chamadora para rastreamento em logs

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
            logger = LogUtils(
                tool=tool_key or "untraceable",
                class_name="VectorLayerAttributes",
            )
            logger.error(f"Erro criando campos de coordenada: {e}")
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
            Nome do campo truncado se necessário
        """
        full_name = f"{base_name}{suffix}"
        if len(full_name) <= max_length:
            return full_name

        available_for_base = max_length - len(suffix)
        if available_for_base < 1:
            return full_name[:max_length]

        return f"{base_name[:available_for_base]}{suffix}"

    @staticmethod
    def resolve_field_names_for_calculation(
        layer,
        base_name,
        calculation_mode="Elipsoidal",
        cartesian_suffix="_car",
        ellipsoidal_suffix="_eli",
    ):
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
        """
        field_map = {}

        if calculation_mode == "Ambos":
            eli_name = VectorLayerAttributes.generate_field_name_with_suffix(
                base_name, ellipsoidal_suffix
            )
            car_name = VectorLayerAttributes.generate_field_name_with_suffix(
                base_name, cartesian_suffix
            )
            field_map["Elipsoidal"] = eli_name
            field_map["Cartesiana"] = car_name
        elif calculation_mode == "Elipsoidal":
            field_map[calculation_mode] = (
                VectorLayerAttributes.generate_field_name_with_suffix(
                    base_name, ellipsoidal_suffix
                )
            )
        elif calculation_mode == "Cartesiana":
            field_map[calculation_mode] = (
                VectorLayerAttributes.generate_field_name_with_suffix(
                    base_name, cartesian_suffix
                )
            )
        else:
            field_map[calculation_mode] = base_name

        return field_map
