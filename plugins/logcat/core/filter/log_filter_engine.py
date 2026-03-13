"""
Motor de filtros para logs.

Suporta filtros por texto livre, coluna específica, e intervalos de tempo.
"""
from typing import List, Set, Optional, Callable
from datetime import datetime
import re
import json
from ..model.log_entry import LogEntry


class LogFilterEngine:
    """
    Aplica múltiplos filtros a uma lista de entradas de log.
    
    Suporta:
    - Filtro de texto livre (busca em todos os campos)
    - Filtros por coluna (level, tool, class, etc)
    - Filtro de intervalo de tempo
    """
    
    def __init__(self):
        """Inicializa o motor com filtros vazios."""
        self.text_filter = ""
        self.level_filter: Set[str] = set()
        self.tool_filter: Set[str] = set()
        self.class_filter: Set[str] = set()
        self.time_start: Optional[datetime] = None
        self.time_end: Optional[datetime] = None
        self._use_regex = False
    
    def set_text_filter(self, text: str, use_regex: bool = False) -> None:
        """
        Define filtro de texto livre.
        
        Args:
            text: Texto ou regex a buscar
            use_regex: Se True, interpreta como regex
        """
        self.text_filter = text
        self._use_regex = use_regex
    
    def set_level_filter(self, levels: Set[str]) -> None:
        """Define filtro de níveis de log."""
        self.level_filter = set(levels)
    
    def set_tool_filter(self, tools: Set[str]) -> None:
        """Define filtro de ferramentas."""
        self.tool_filter = set(tools)
    
    def set_class_filter(self, classes: Set[str]) -> None:
        """Define filtro de classes."""
        self.class_filter = set(classes)
    
    def set_time_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> None:
        """Define intervalo de tempo."""
        self.time_start = start
        self.time_end = end
    
    def clear_all(self) -> None:
        """Limpa todos os filtros."""
        self.text_filter = ""
        self.level_filter.clear()
        self.tool_filter.clear()
        self.class_filter.clear()
        self.time_start = None
        self.time_end = None
    
    def apply(self, entries: List[LogEntry]) -> List[LogEntry]:
        """
        Aplica todos os filtros às entradas.
        
        Retorna apenas entradas que passam em TODOS os filtros.
        """
        result = entries
        
        # Filtro de texto
        if self.text_filter:
            result = self._filter_text(result)
        
        # Filtro de nível
        if self.level_filter:
            result = [e for e in result if e.level in self.level_filter]
        
        # Filtro de tool
        if self.tool_filter:
            result = [e for e in result if e.tool in self.tool_filter]
        
        # Filtro de classe
        if self.class_filter:
            result = [e for e in result if e.class_name in self.class_filter]
        
        # Filtro de tempo
        if self.time_start or self.time_end:
            result = self._filter_time(result)
        
        return result
    
    def _filter_text(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Filtra por texto livre em todos os campos."""
        result = []
        
        for entry in entries:
            if self._matches_text(entry):
                result.append(entry)
        
        return result
    
    def _matches_text(self, entry: LogEntry) -> bool:
        """Verifica se uma entrada contém o texto do filtro."""
        if not self.text_filter:
            return True
        
        text = self.text_filter
        
        # Campos a buscar
        search_fields = [
            entry.ts or "",
            entry.level,
            entry.plugin,
            entry.tool,
            entry.class_name,
            entry.msg,
            str(entry.pid),
            entry.thread,
            json.dumps(entry.data, ensure_ascii=False)
        ]
        
        search_text = " ".join(search_fields).lower()
        
        if self._use_regex:
            try:
                return bool(re.search(text, search_text, re.IGNORECASE))
            except re.error:
                return True  # Regex inválido: não filtra
        else:
            return text.lower() in search_text
    
    def _filter_time(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Filtra por intervalo de tempo."""
        result = []
        
        for entry in entries:
            dt = entry.get_timestamp_dt()
            if not dt:
                continue  # Entrada sem timestamp: não inclui
            
            if self.time_start and dt < self.time_start:
                continue
            
            if self.time_end and dt > self.time_end:
                continue
            
            result.append(entry)
        
        return result
    
    def get_unique_levels(self, entries: List[LogEntry]) -> Set[str]:
        """Retorna todos os níveis únicos presentes nas entradas."""
        return {e.level for e in entries}
    
    def get_unique_tools(self, entries: List[LogEntry]) -> Set[str]:
        """Retorna todas as ferramentas únicas presentes nas entradas."""
        return {e.tool for e in entries}
    
    def get_unique_classes(self, entries: List[LogEntry]) -> Set[str]:
        """Retorna todas as classes únicas presentes nas entradas."""
        return {e.class_name for e in entries}
