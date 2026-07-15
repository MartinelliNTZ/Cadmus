from typing import Dict, List, Any, Iterable
from dataclasses import is_dataclass


class StringAdapter:
    """Adapta dicionários de metacampos para saída mínima de UI."""

    @staticmethod
    def to_key_label_description(fields_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recebe um dicionário no formato de Strings.REQUIRED_FIELDS/CUSTOM_FIELDS
        e retorna uma lista contendo somente key, label e description.
        """
        if not isinstance(fields_dict, dict):
            return []

        output: List[Dict[str, Any]] = []
        for key, meta in fields_dict.items():
            if isinstance(meta, dict):
                label = meta.get("label")
                description = meta.get("description")
            elif is_dataclass(meta):
                label = getattr(meta, "label", None)
                description = getattr(meta, "description", None)
            else:
                label = None
                description = None
            output.append(
                {
                    "key": key,
                    "label": label,
                    "description": description,
                }
            )
        return output

    @staticmethod
    def unique_preserve_order(values: Iterable[Any]) -> List[Any]:
        """Remove duplicados preservando ordem de aparicao."""
        seen = set()
        result = []
        for value in values or []:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    @staticmethod
    def filter_known_keys(values: Iterable[str], fields_dict: Dict[str, Any]) -> List[str]:
        """Filtra lista de chaves para manter apenas as que existem no dicionario de campos."""
        if not isinstance(fields_dict, dict):
            return []
        keys = set(fields_dict.keys())
        return [value for value in (values or []) if value in keys]
