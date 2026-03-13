"""
Carregador de logs com suporte a leitura incremental.

Lê apenas linhas novas, sem reler o arquivo inteiro.
"""
from pathlib import Path
from typing import List, Optional
from ..model.log_entry import LogEntry

# Import do lock global para sincronizar com LogUtils
try:
    from .....core.config.log_sync import LOG_FILE_LOCK
except ImportError:
    # Fallback se import relativo falhar
    import threading
    LOG_FILE_LOCK = threading.Lock()


class LogLoader:
    """
    Carrega entradas de log de um arquivo com suporte incremental.
    
    Mantém offset para não reler linhas já processadas.
    Thread-safe.
    """
    
    def __init__(self, log_file_path: Path):
        """
        Inicializa o loader.
        
        Args:
            log_file_path: Path para o arquivo .log
        """
        self.log_file_path = Path(log_file_path)
        self._offset = 0  # Próxima posição a ler
        self._line_count = 0  # Total de linhas vistas
    
    def load_all(self) -> List[LogEntry]:
        """
        Carrega TODAS as entradas do arquivo.
        Reinicializa o offset.
        """
        entries = []
        
        with LOG_FILE_LOCK:
            if not self.log_file_path.exists():
                return entries
            
            try:
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    line_number = 0
                    for line_number, line in enumerate(f, start=1):
                        entry = LogEntry.from_json_line(line, line_number)
                        if entry:
                            entries.append(entry)
                    
                    self._offset = f.tell()
                    self._line_count = line_number
            except Exception:
                pass  # Log nunca quebra a aplicação
        
        return entries
    
    def load_incremental(self) -> List[LogEntry]:
        """
        Carrega apenas NOVAS linhas desde a última leitura.
        Retorna lista vazia se não houver novas linhas.
        Tolerante a escrita simultânea: ignora linhas inválidas/JSON incompleto.
        """
        entries = []
        
        with LOG_FILE_LOCK:
            if not self.log_file_path.exists():
                return entries
            
            try:
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    # Verificar se offset é válido (arquivo pode ter sido truncado)
                    file_size = f.seek(0, 2)  # Vai para final
                    if self._offset > file_size:
                        # Arquivo foi truncado/reset, reiniciar do início
                        self._offset = 0
                        self._line_count = 0
                    
                    # Ir para onde paramos
                    f.seek(self._offset)
                    
                    # Ler novas linhas
                    for line in f:
                        self._line_count += 1
                        entry = LogEntry.from_json_line(line, self._line_count)
                        if entry:
                            entries.append(entry)
                        # Se linha for inválida, ignorar silenciosamente
                    
                    # Atualizar offset
                    self._offset = f.tell()
            except Exception:
                pass  # Log nunca quebra a aplicação
        
        return entries
    
    def reset(self) -> None:
        """Reinicializa o offset para reler desde o início."""
        with LOG_FILE_LOCK:
            self._offset = 0
            self._line_count = 0
    
    def get_position(self) -> int:
        """Retorna posição atual (byte offset)."""
        with LOG_FILE_LOCK:
            return self._offset
    
    def get_line_count(self) -> int:
        """Retorna número total de linhas vistas."""
        with LOG_FILE_LOCK:
            return self._line_count
