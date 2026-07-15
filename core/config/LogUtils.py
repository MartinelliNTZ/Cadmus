# -*- coding: utf-8 -*-
# utils/log_utils_new.py
import json
import threading
import uuid
import os
from pathlib import Path
from datetime import datetime
import traceback

from ...utils.ToolKeys import ToolKey
from .log_sync import LOG_FILE_LOCK

try:
    from qgis.core import QgsMessageLog, Qgis

    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class LogUtils:
    # C:\Users\<usuario>\AppData\Roaming\QGIS\QGIS3\Cadmus
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    # Cores para níveis de log
    LEVEL_COLORS = {
        "DEBUG": "#9CA3AF",  # Cinza (suave)
        "INFO": "#10B981",  # Verde (informação)
        "WARNING": "#F59E0B",  # Âmbar (atenção)
        "ERROR": "#DC2626",  # Vermelho forte (erro)
        "CRITICAL": "#991B1B",  # Vermelho escuro muito forte (crítico)
    }
    LEVEL_ORDER = [DEBUG, INFO, WARNING, ERROR, CRITICAL]

    _session_id = None
    _log_file = None
    _plugin_name = "Cadmus"
    _plugin_version = "unknown"
    _initialized = False

    # ---------- init global (igual conceito da antiga) ----------
    @classmethod
    def _get_default_plugin_root(cls):
        # O arquivo está em <plugin>/core/config/LogUtils.py.
        # Usar a raiz do plugin para garantir log em local gravável do plugin.
        plugin_root = Path(__file__).resolve().parents[3]
        if plugin_root.exists():
            return plugin_root
        # fallback mais seguro para home do usuário
        return Path.home() / "Cadmus"

    @classmethod
    def init(cls, plugin_root: Path = None):
        if cls._initialized:
            # return f"LogUtils já inicializado. Log file: {cls._log_file}, Session ID: {cls._session_id}"
            cls._initialized = False  # Forçar reinicialização para testes

        if plugin_root is None:
            plugin_root = cls._get_default_plugin_root()

        cls._session_id = str(uuid.uuid4())
        cls._plugin_version = cls._read_plugin_version(plugin_root)

        log_dir = plugin_root / "log"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Caso o plugin seja chamado de diretório protegido (ex: system32), usar fallback no home do usuário.
            fallback = Path.home() / "Cadmus" / "log"
            try:
                fallback.mkdir(parents=True, exist_ok=True)
                log_dir = fallback
            except Exception as fallback_error:
                # Falha total no log, preserva o funcionamento do plugin sem saída de arquivo.
                cls._log_file = None
                cls._initialized = True
                return f"LogUtils initialized without file (fallback failed): {fallback_error}"

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pid = os.getpid()
        cls._log_file = log_dir / f"cadmus_{ts}_pid{pid}.log"

        cls._initialized = True

        cls._write_event(
            level="INFO",
            msg="Log session started",
            tool=ToolKey.SYSTEM,
            class_name="LogUtils",
            code="LOG_START",
            data={},
        )
        return f"LogUtils initialized. Log file: {cls._log_file}, Session ID: {cls._session_id}. pid: {pid}"

    # ---------- instância ----------
    def __init__(self, *, tool, class_name, level=INFO):
        self.tool = tool
        self.class_name = class_name
        self.level = level

    def set_level(self, level):
        self.level = level

    # ---------- API ----------
    def log(self, msg, *, level=INFO, code=None, **data):
        if not self._allow(level):
            return
        self._ensure_ready()
        self._write_event(level, msg, self.tool, self.class_name, code, data)

    def debug(self, msg, *, code=None, **data):
        self.log(msg, level=self.DEBUG, code=code, **data)

    def info(self, msg, *, code=None, **data):
        self.log(msg, level=self.INFO, code=code, **data)

    def warning(self, msg, *, code=None, **data):
        self.log(msg, level=self.WARNING, code=code, **data)

    def error(self, msg, *, code=None, **data):
        self.log(msg, level=self.ERROR, code=code, **data)

    def critical(self, msg, *, code=None, **data):
        self.log(msg, level=self.CRITICAL, code=code, **data)

    def exception(self, exc: Exception, *, code=None, **data):
        if not self._allow(self.ERROR):
            return
        self._ensure_ready()

        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        data["exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": tb,
        }

        self._write_event(
            self.ERROR, "Unhandled exception", self.tool, self.class_name, code, data
        )

    # ---------- internos ----------
    def _allow(self, level):
        return self.LEVEL_ORDER.index(level) >= self.LEVEL_ORDER.index(self.level)

    @classmethod
    def _ensure_ready(cls):
        if cls._initialized:
            return
        # fallback: cria sessão mínima baseado na raiz do plugin ou home do usuário
        plugin_root = cls._get_default_plugin_root()
        cls.init(plugin_root)

    @classmethod
    def _write_event(cls, level, msg, tool, class_name, code, data):
        event = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "level": level,
            "plugin": cls._plugin_name,
            "plugin_version": cls._plugin_version,
            "session_id": cls._session_id,
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
            "tool": tool or "unknown_tool",
            "class": class_name or "UnknownClass",
            "code": code,
            "msg": msg,
            "data": data or {},
        }

        with LOG_FILE_LOCK:
            if cls._log_file is None:
                # Log file não disponível (ex: erro de permissão em criação). Emitir via QGIS ou stderr.
                if QGIS_AVAILABLE:
                    QgsMessageLog.logMessage(
                        f"LogUtils sem arquivo. Evento: {event}",
                        cls._plugin_name,
                        Qgis.Warning,
                    )
                else:
                    import sys
                    sys.stderr.write(f"Cadmus LogUtils missing file: {event}\n")
                return
            try:
                with open(cls._log_file, "a", encoding="utf-8") as f:
                    json.dump(event, f, ensure_ascii=False)
                    f.write("\n")
            except Exception as e:
                try:
                    if QGIS_AVAILABLE:
                        # registrar falha de escrita no log do QGIS
                        QgsMessageLog.logMessage(
                            f"Falha ao gravar log do Cadmus: {e}",
                            cls._plugin_name,
                            Qgis.Warning,
                        )
                    else:
                        # fallback simples para stderr
                        import sys

                        sys.stderr.write(f"Cadmus LogUtils write error: {e}\n")
                except Exception:
                    # Último fallback: evitar que falha no sistema de log quebre o plugin
                    return
        # Registrar CRITICAL e ERROR também no QgsMessageLog oficial do QGIS
        if QGIS_AVAILABLE and level in (cls.CRITICAL, cls.ERROR):
            full_msg = f"[{tool}:{class_name}] {msg}"
            qgis_level = Qgis.Critical if level == cls.CRITICAL else Qgis.Warning
            QgsMessageLog.logMessage(full_msg, cls._plugin_name, qgis_level)

    @staticmethod
    def _read_plugin_version(plugin_root: Path) -> str:
        meta = plugin_root / "metadata.txt"
        if not meta.exists():
            return "unknown"
        for line in meta.read_text(encoding="utf-8").splitlines():
            if line.startswith("version="):
                return line.split("=", 1)[1].strip()
        return "unknown"
