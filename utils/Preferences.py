import os
import json
from qgis.PyQt.QtCore import QStandardPaths

class Preferences:
    """Gerencia as preferências do plugin, armazenando em um JSON local."""
    
    PREF_FOLDER = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
        "MTLTools"
    )

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
        except Exception:
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

PREF_FOLDER = os.path.join(
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
    "MTLTools"
)

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
    except Exception:
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