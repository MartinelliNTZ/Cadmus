"""
Provedor de cores para ToolKeys.

Mapeamento configurável de ferramentas para cores.
Importa cores de ToolKey.TOOL_KEY_COLORS quando disponível.
"""
from typing import Dict, Optional


class ToolKeyColorProvider:
    """
    Fornece cores para diferentes ToolKeys.
    
    Usa dicionário configurável com fallback para cor padrão.
    Tenta importar cores de ToolKey.TOOL_KEY_COLORS primeiro.
    """
    
    # Mapeamento padrão (fallback se não conseguir importar ToolKey)
    DEFAULT_COLORS = {
        # === Toolbar / ações principais ===
        "Cadmus_plugin": "#804E0A",
        "export_all_layouts": "#4ECDC4",
        "drone_coordinates": "#45B7D1",
        "load_folder_layers": "#96CEB4",
        "replace_in_layouts": "#F8C471",
        "restart_qgis": "#FF6B6B",
        "gerar_rastro_implemento": "#82E0AA",
        "coord_click_tool": "#85C1E9",
        "copy_attributes": "#DDA0DD",
        
        # === Processing / análises ===
        "attribute_statistics": "#F7DC6F",
        "difference_fields_algorithm": "#BB8FCE",
        "my_algorithm": "#98D8C8",
        "provider": "#BFC9CA",
        "raster_mass_sampler": "#F1948A",
        "elevation_analisys": "#5DADE2",
        
        # === Logcat e sistema ===
        "logcat": "#9B59B6",
        "system": "#FF6B6B",
    }
    
    def __init__(self, custom_colors: Optional[Dict[str, str]] = None):
        """
        Inicializa com cores de ToolKey.TOOL_KEY_COLORS se disponível,
        senão usa DEFAULT_COLORS.
        
        Args:
            custom_colors: Dict opcional para sobrescrever cores padrão
        """
        # Tenta carregar do ToolKey primeiro
        self.colors = self._load_tool_key_colors() or self.DEFAULT_COLORS.copy()
        
        if custom_colors:
            self.colors.update(custom_colors)
        
        # Cor padrão para ferramentas não mapeadas
        self.default_color = "#D4D4D4"  # Cinza neutro
    
    @staticmethod
    def _load_tool_key_colors() -> Optional[Dict[str, str]]:
        """
        Tenta importar TOOL_KEY_COLORS de utils.tool_keys.ToolKey.
        
        Returns:
            Dict com cores ou None se falhar
        """
        try:
            from .....utils.ToolKeys import ToolKey
            return ToolKey.TOOL_KEY_COLORS.copy()
        except Exception:
            return None
    
    def get_color(self, tool_key: str) -> str:
        """
        Retorna cor para a ferramenta.
        
        Args:
            tool_key: Chave da ferramenta (ex: "Cadmus_plugin", "coord_click_tool")
        
        Returns:
            Cor em hexadecimal
        """
        # Normalizar para lowercase para ser mais resiliente
        tool_key_lower = tool_key.lower() if tool_key else ""
        return self.colors.get(tool_key_lower, self.default_color)
    
    def set_color(self, tool_key: str, color: str) -> None:
        """Configura cor para uma ferramenta."""
        self.colors[tool_key.lower()] = color
    
    def reset_to_defaults(self) -> None:
        """Restaura cores padrão."""
        self.colors = self.DEFAULT_COLORS.copy()
    
    def get_all_colors(self) -> Dict[str, str]:
        """Retorna dicionário completo de cores."""
        return self.colors.copy()
