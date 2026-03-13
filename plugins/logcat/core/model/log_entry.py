"""
Modelo de domínio para uma entrada de log.

LogEntry representa uma linha JSON de log desserializada,
tolerante a campos ausentes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import json


@dataclass
class LogEntry:
    """Representa uma única entrada de log JSONL."""
    
    ts: Optional[str] = None
    level: str = "UNKNOWN"
    plugin: str = "Unknown"
    plugin_version: str = "unknown"
    session_id: Optional[str] = None
    pid: int = 0
    thread: str = "Unknown"
    tool: str = "unknown_tool"
    class_name: str = "UnknownClass"
    msg: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Campos calculados internamente
    line_number: int = 0  # Número da linha no arquivo original
    raw_json: str = ""    # JSON original para debugging
    
    @classmethod
    def from_json_line(cls, line: str, line_number: int = 0) -> Optional['LogEntry']:
        """
        Parse uma linha JSON em um LogEntry.
        Tolerante a campos ausentes.
        Retorna None se o JSON for inválido.
        """
        line = line.strip()
        if not line:
            return None
        
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # Extrair campos com defaults seguros
        return cls(
            ts=obj.get("ts"),
            level=obj.get("level", "UNKNOWN"),
            plugin=obj.get("plugin", "Unknown"),
            plugin_version=obj.get("plugin_version", "unknown"),
            session_id=obj.get("session_id"),
            pid=obj.get("pid", 0),
            thread=obj.get("thread", "Unknown"),
            tool=obj.get("tool", "unknown_tool"),
            class_name=obj.get("class", "UnknownClass"),
            msg=obj.get("msg", ""),
            data=obj.get("data", {}),
            line_number=line_number,
            raw_json=line
        )
    
    def get_timestamp_dt(self) -> Optional[datetime]:
        """
        Parse o timestamp ISO para datetime.
        Retorna None se inválido.
        """
        if not self.ts:
            return None
        try:
            return datetime.fromisoformat(self.ts)
        except (ValueError, TypeError):
            return None
    
    def get_short_message(self, max_length: int = 100) -> str:
        """
        Retorna mensagem truncada para exibição em tabela.
        """
        msg = self.msg.replace("\n", " ")
        if len(msg) > max_length:
            return msg[:max_length - 3] + "..."
        return msg
    
    def get_full_message(self) -> str:
        """
        Retorna a mensagem completa, incluindo traceback se houver.
        """
        lines = [self.msg]
        
        if "exception" in self.data:
            exc = self.data["exception"]
            lines.append("\n--- Exception Details ---")
            if "type" in exc:
                lines.append(f"Type: {exc['type']}")
            if "message" in exc:
                lines.append(f"Message: {exc['message']}")
            if "traceback" in exc:
                lines.append("\n--- Traceback ---")
                lines.append(exc["traceback"])
        
        # Adicionar outros dados relevantes
        if self.data:
            exc_data = self.data.copy()
            exc_data.pop("exception", None)
            if exc_data:
                lines.append("\n--- Additional Data ---")
                lines.append(json.dumps(exc_data, indent=2, ensure_ascii=False))
        
        return "\n".join(lines)
    
    def get_full_details(self) -> str:
        """
        Retorna todos os detalhes da entrada (para debug/cópia).
        """
        details = [
            f"Timestamp: {self.ts}",
            f"Level: {self.level}",
            f"Plugin: {self.plugin} ({self.plugin_version})",
            f"Session ID: {self.session_id}",
            f"PID: {self.pid}",
            f"Thread: {self.thread}",
            f"Tool: {self.tool}",
            f"Class: {self.class_name}",
            f"Line #{self.line_number}",
            "",
            f"Message:\n{self.get_full_message()}",
            "",
            f"Raw JSON:\n{self.raw_json}"
        ]
        return "\n".join(details)
