# -*- coding: utf-8 -*-
import sys
import traceback
from pathlib import Path
from qgis.core import QgsMessageLog, Qgis, QgsApplication
from ...utils.ToolKeys import ToolKey
from ...utils.QgisMessageUtil import QgisMessageUtil
from ...processing.provider import MTLProvider
from .LogCleanupUtils import LogCleanupUtils
from .LogUtils import LogUtils
from ...utils.Preferences import Preferences

# Global logger for error handler
_logger_global = None


class PluginBootstrap:
    """
    Responsável pela inicialização crítica do plugin Cadmus.
    Encapsula a instalação do handler global de erros, inicialização de logs,
    limpeza de logs antigos, criação do logger e registro do provider de processamento.
    """

    def __init__(self, iface):
        self.iface = iface
        self.logger = None
        self.provider = None
        self.TOOL_KEY = ToolKey.SYSTEM
        self.PREFERENCES_VERSION = 2  # Incrementar se mudar estrutura de prefs globais

    def bootstrap(self, plugin_root: Path):
        """
        Executa a inicialização do plugin.

        :param plugin_root: Caminho raiz do plugin.
        :return: Tupla (logger, provider) configurados.
        """

        try:
            # Inicializar LogUtils primeiro
            log = LogUtils.init(plugin_root)

            # Criar logger global para handler
            global _logger_global
            _logger_global = LogUtils(
                tool=self.TOOL_KEY, class_name="GlobalHandler", level=LogUtils.DEBUG
            )

            # Instalar proteção global contra crashes
            self._install_global_error_handler()

            # Limpar logs antigos
            LogCleanupUtils.keep_last_n(plugin_root, keep=15)

            # Criar logger
            self.logger = LogUtils(
                tool=self.TOOL_KEY, class_name="PluginBootstrap", level=LogUtils.DEBUG
            )
            self.logger.info("Logger criado com sucesso")
            self.logger.info(
                "SYSTEM: Global error handler instalado para capturar crashes"
            )
            self.logger.debug("LogUtils inicializado")
            self.logger.debug("Limpeza de logs antigos executada")

            # Registrar provider de processamento
            self.prefs_version_check()  # Verificar e atualizar versão das preferências globais
            # Registrar provider de processamento
            self.provider = MTLProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
            self.logger.info("Processing Provider carregado com sucesso")

            QgsMessageLog.logMessage(
                f"Log {log}. Provider: {self.provider}. Plugin inicializado sem crashes.",
                "Cadmus",
                Qgis.Warning,
            )

            return self.provider

        except Exception as e:
            # Se logger ainda não foi criado, tentar criar um básico
            if self.logger is None:
                try:
                    LogUtils.init(plugin_root)
                    self.logger = LogUtils(
                        tool=self.TOOL_KEY, class_name="PluginBootstrap"
                    )
                except Exception as e2:
                    QgsMessageLog.logMessage(
                        f"Erro crítico no bootstrap e falha ao criar logger: {str(e)}. Logger error: {str(e2)}",
                        Qgis.Warning,
                    )
            if self.logger:
                self.logger.error(f"Erro crítico no bootstrap: {str(e)}")
            QgisMessageUtil.bar_critical(
                self.iface, f"Erro crítico na inicialização do plugin: {e}"
            )
            raise  # Re-raise para parar inicialização

    def prefs_version_check(self):
        """Verifica se as preferências globais estão na versão esperada."""
        prefs_system = Preferences.load_tool_prefs(ToolKey.SYSTEM)
        version = prefs_system.get("prefs_version", 0)
        if version < self.PREFERENCES_VERSION:
            self.logger.info(
                f"Versão de preferências antiga detectada: {version}. "
                f"Atualizando para versão {self.PREFERENCES_VERSION}."
            )
            prefs_gt = Preferences.load_tool_prefs("gerar_rastro_implemento")
            if prefs_gt:
                Preferences.save_tool_prefs(
                    ToolKey.GENERATE_TRAIL, prefs_gt
                )  # Re-salva para atualizar estrutura se necessário
            # Aqui você pode implementar migração de preferências se necessário
            prefs_system["prefs_version"] = self.PREFERENCES_VERSION
            Preferences.save_tool_prefs(ToolKey.SYSTEM, prefs_system)
            self.logger.debug("Preferências globais atualizadas para nova versão")

    def _install_global_error_handler(self):
        """Instala handler global para capturar exceções não tratadas."""

        def handle_exception(exc_type, exc_value, exc_traceback):
            error_msg = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            _logger_global.critical(
                f"UNCAUGHT EXCEPTION (possibly crash): {exc_type.__name__}: {str(exc_value)}",
                error_type=exc_type.__name__,
                traceback=error_msg,
            )

            # Chamar handler original
            _original_excepthook(exc_type, exc_value, exc_traceback)

        # Salvar handler original
        _original_excepthook = sys.excepthook
        sys.excepthook = handle_exception
