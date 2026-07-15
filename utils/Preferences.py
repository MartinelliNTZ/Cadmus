# -*- coding: utf-8 -*-
import os
import json
from qgis.PyQt.QtCore import QStandardPaths
from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil

# module logger for preferences utils
logger = LogUtils(tool=BaseUtil.TOOL_KEY_UNTRACEABLE, class_name="Preferences")


def _resolve_app_data_path():
    """Retorna o caminho adequado para armazenar configurações entre Qt5/Qt6."""
    for candidate in (
        "AppDataLocation",
        "AppLocalDataLocation",
        "AppConfigLocation",
        "DataLocation",
        "GenericDataLocation",
    ):
        if hasattr(QStandardPaths, candidate):
            return QStandardPaths.writableLocation(getattr(QStandardPaths, candidate))

    # fallback mais básico se nenhum atributo estiver disponível.
    return os.path.expanduser("~")


class Preferences(BaseUtil):
    """Gerencia as preferências do plugin, armazenando em um JSON local."""

    PREF_FOLDER = os.path.join(_resolve_app_data_path(), "MTLTools")
    PREF_FILE = os.path.join(PREF_FOLDER, "mtl_prefs.json")

    def _ensure_pref_folder():
        os.makedirs(Preferences.PREF_FOLDER, exist_ok=True)
        if not os.path.exists(Preferences.PREF_FILE):
            with open(Preferences.PREF_FILE, "w", encoding="utf-8") as f:
                f.write("{}")

    def load_prefs():
        """Carrega todo o JSON de preferências."""
        Preferences._ensure_pref_folder()
        try:
            with open(Preferences.PREF_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar preferences file: {e}")
            return {}

    def save_prefs(data):
        """Salva o JSON inteiro de preferências."""
        Preferences._ensure_pref_folder()
        with open(Preferences.PREF_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_tool_prefs(tool_key):
        """Carrega apenas as prefs da ferramenta específica."""
        prefs = Preferences.load_prefs()
        return prefs.get(tool_key, {})

    @staticmethod
    def save_tool_prefs(tool_key, values: dict):
        """Salva prefs de uma ferramenta específica."""
        prefs = Preferences.load_prefs()
        prefs[tool_key] = values
        Preferences.save_prefs(prefs)

    @staticmethod
    def update_tool_prefs(tool_key, updates: dict):
        """
        Atualiza seletivamente chaves nas prefs de uma ferramenta,
        sem substituir o dicionário inteiro.

        Args:
            tool_key: Chave da ferramenta
            updates: Dict com as chaves/valores a atualizar
        """
        prefs = Preferences.load_prefs()
        tool_prefs = prefs.get(tool_key, {})
        tool_prefs.update(updates)
        prefs[tool_key] = tool_prefs
        Preferences.save_prefs(prefs)

    @staticmethod
    def load_pref_key_by_tool(pref_key):
        """
        Retorna {tool_key: valor} para todos os tools
        que possuem a chave informada.
        """
        prefs = Preferences.load_prefs()
        result = {}

        for tool_key, tool_prefs in prefs.items():
            if isinstance(tool_prefs, dict) and pref_key in tool_prefs:
                result[tool_key] = tool_prefs[pref_key]

        return result

    @staticmethod
    def set_value_for_all_tools(pref_key, value, filter_by=None):
        """
        Define um valor em chave específica para ferramentas, com filtro opcional.

        Exemplos:
            - set_value_for_all_tools("main_action", False)
              → seta main_action=False para TODOS
            - set_value_for_all_tools("main_action", False, filter_by={"category": "VECTOR"})
              → seta apenas onde category=="VECTOR"

        Args:
            pref_key (str): Chave a atualizar
            value: Novo valor
            filter_by (dict): Filtro opcional {chave: valor}

        Returns:
            int: Número de ferramentas modificadas
        """
        if filter_by is None:
            filter_by = {}

        prefs = Preferences.load_prefs()
        modified_count = 0

        for tool_key in list(prefs.keys()):
            if not isinstance(prefs[tool_key], dict):
                continue

            tool_prefs = prefs[tool_key]

            # Verificar filtro: TODAS as condições devem ser atendidas
            skip_tool = False
            if filter_by:
                for filter_key, filter_value in filter_by.items():
                    if tool_prefs.get(filter_key) != filter_value:
                        skip_tool = True
                        break

            if skip_tool:
                continue

            # Atualizar valor
            prefs[tool_key][pref_key] = value
            modified_count += 1

        Preferences.save_prefs(prefs)
        logger.debug(
            f"[set_value_for_all_tools] {modified_count} ferramentas atualizadas ('{pref_key}' → {value})"
        )

        return modified_count

    @staticmethod
    def delete_value_for_all_tools(pref_key, filter_by=None):
        """
        Deleta chave específica em ferramentas, com filtro opcional.

        Exemplos:
            - delete_value_for_all_tools("width")
              → deleta "width" de TODOS
            - delete_value_for_all_tools("width", filter_by={"category": "VECTOR"})
              → deleta apenas onde category=="VECTOR"

        Args:
            pref_key (str): Chave a deletar
            filter_by (dict): Filtro opcional {chave: valor}

        Returns:
            int: Número de ferramentas modificadas
        """
        if filter_by is None:
            filter_by = {}

        prefs = Preferences.load_prefs()
        deleted_count = 0

        for tool_key in list(prefs.keys()):
            if not isinstance(prefs[tool_key], dict):
                continue

            tool_prefs = prefs[tool_key]

            # Verificar filtro
            skip_tool = False
            if filter_by:
                for filter_key, filter_value in filter_by.items():
                    if tool_prefs.get(filter_key) != filter_value:
                        skip_tool = True
                        break

            if skip_tool:
                continue

            # Deletar chave se existir
            if pref_key in tool_prefs:
                tool_prefs.pop(pref_key)
                deleted_count += 1

        Preferences.save_prefs(prefs)
        logger.debug(
            f"[delete_value_for_all_tools] {deleted_count} ferramentas modificadas ('{pref_key}' deletado)"
        )

        return deleted_count


# DEPRECATED - manter funções abaixo para compatibilidade, mas usar as versões da classe Preferences acima.
PREF_FOLDER = os.path.join(_resolve_app_data_path(), "MTLTools")
PREF_FILE = os.path.join(PREF_FOLDER, "mtl_prefs.json")


def _ensure_pref_folder():
    """DEPRECATED USE Preferences._ensure_pref_folder() instead."""
    os.makedirs(PREF_FOLDER, exist_ok=True)
    if not os.path.exists(PREF_FILE):
        with open(PREF_FILE, "w", encoding="utf-8") as f:
            f.write("{}")


def load_prefs():
    """DEPRECATED USE Preferences.load_prefs() instead."""
    _ensure_pref_folder()
    try:
        with open(PREF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar deprecated preferences file: {e}")
        return {}


def save_prefs(data):
    """DEPRECATED USE Preferences.save_prefs() instead."""
    _ensure_pref_folder()
    with open(PREF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_tool_prefs(tool_key):
    """DEPRECATED USE Preferences.load_tool_prefs() instead."""
    prefs = load_prefs()
    return prefs.get(tool_key, {})


def save_tool_prefs(tool_key, values: dict):
    """DEPRECATED USE Preferences.save_tool_prefs() instead."""
    prefs = load_prefs()
    prefs[tool_key] = values
    save_prefs(prefs)


def load_pref_key_by_tool(pref_key):
    """DEPRECATED USE Preferences.load_pref_key_by_tool() instead."""
    return Preferences.load_pref_key_by_tool(pref_key)
