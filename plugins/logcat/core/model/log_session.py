# -*- coding: utf-8 -*-
"""
Modelo de domínio para uma sessão de log.

Uma sessão é um arquivo .log que agrupa eventos de uma única execução do QGIS.
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
import re


class LogSession:
    """
    Representa uma sessão de log (arquivo .log).

    Nomes de arquivo esperados: Cadmus_YYYYMMDD_HHMMSS_pidPPPPPP.log
    """

    # Regex para extrair timestamp e PID do nome do arquivo
    FILE_PATTERN = re.compile(r"Cadmus_(\d{8})_(\d{6})_pid(\d+)\.log")

    def __init__(self, log_file_path: Path):
        """
        Inicializa a sessão a partir do caminho do arquivo.

        Args:
            log_file_path: Path para o arquivo .log
        """
        self.log_file_path = Path(log_file_path)
        self.session_id: Optional[str] = None  # Será lido do primeiro evento
        self.first_event_timestamp: Optional[datetime] = None
        self.last_event_timestamp: Optional[datetime] = None
        self.entry_count = 0

        # Extrair informações do nome do arquivo
        self._extract_from_filename()

    def _extract_from_filename(self):
        """Extrai timestamp e PID do nome do arquivo."""
        match = self.FILE_PATTERN.match(self.log_file_path.name)
        if match:
            date_str, time_str, pid = match.groups()
            try:
                # Formato: YYYYMMDD_HHMMSS
                dt_str = f"{date_str} {time_str}"
                self.file_datetime = datetime.strptime(dt_str, "%Y%m%d %H%M%S")
                self.pid = int(pid)
            except ValueError:
                self.file_datetime = None
                self.pid = None
        else:
            self.file_datetime = None
            self.pid = None

    @property
    def name(self) -> str:
        """Retorna nome amigável da sessão."""
        if self.file_datetime:
            return (
                f"{self.file_datetime.strftime('%Y-%m-%d %H:%M:%S')} (PID {self.pid})"
            )
        return self.log_file_path.name

    @property
    def display_name(self) -> str:
        """Alias para name."""
        return self.name

    def exists(self) -> bool:
        """Verifica se o arquivo ainda existe."""
        return self.log_file_path.exists()

    def get_file_size(self) -> int:
        """Retorna o tamanho do arquivo em bytes."""
        if not self.exists():
            return 0
        return self.log_file_path.stat().st_size

    def get_modification_time(self) -> Optional[datetime]:
        """Retorna o tempo de última modificação."""
        if not self.exists():
            return None
        mtime = self.log_file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<LogSession {self.log_file_path.name} entries={self.entry_count}>"
