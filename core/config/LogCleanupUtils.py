# -*- coding: utf-8 -*-
from pathlib import Path
from .LogUtils import LogUtils


class LogCleanupUtils:
    """
    Limpeza explícita de logs antigos.
    """

    @staticmethod
    def keep_last_n(plugin_root: Path, keep: int = 10):
        """
        Mantém apenas os últimos N arquivos de log.

        Args:
            plugin_root: Raiz do plugin
            keep: Número de arquivos a manter (padrão 10)
        """
        log_dir = plugin_root / "log"
        if not log_dir.exists():
            return

        logs = sorted(
            log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        for old in logs[keep:]:
            try:
                old.unlink()
            except Exception as e:
                LogUtils(tool="log_cleanup", class_name="LogCleanupUtils").error(
                    f"Falha ao remover log antigo {old}: {e}"
                )

    @staticmethod
    def clear_all_logs(plugin_root: Path) -> int:
        """
        Deleta TODOS os arquivos de log.

        Args:
            plugin_root: Raiz do plugin

        Returns:
            Número de arquivos deletados
        """
        log_dir = plugin_root / "log"
        if not log_dir.exists():
            return 0

        deleted_count = 0
        for log_file in log_dir.glob("*.log"):
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                LogUtils(tool="log_cleanup", class_name="LogCleanupUtils").error(
                    f"Falha ao remover arquivo de log {log_file}: {e}"
                )

        return deleted_count

    @staticmethod
    def clear_current_session(plugin_root: Path, session_id: str = None) -> bool:
        """
        Deleta os logs da sessão atual ou da sessão especificada.

        Usa a lógica de arquivos: o arquivo mais recente é a sessão atual.

        Args:
            plugin_root: Raiz do plugin
            session_id: (Opcional) ID da sessão a deletar.

        Returns:
            True se deletado com sucesso, False caso contrário
        """
        log_dir = plugin_root / "log"
        if not log_dir.exists():
            return False

        logs = sorted(
            log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        if not logs:
            return False

        # Pegar o arquivo mais recente (sessão atual)
        latest_log = logs[0]

        try:
            latest_log.unlink()
            return True
        except Exception as e:
            LogUtils(tool="log_cleanup", class_name="LogCleanupUtils").error(
                f"Falha ao remover arquivo de sessão {latest_log}: {e}"
            )
            return False
