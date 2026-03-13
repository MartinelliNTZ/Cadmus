"""
Provedor de cores determinístico para classes.

Gera automaticamente cores únicas e legíveis para cada classe,
de forma consistente (mesma classe = mesma cor sempre).
"""
from typing import Dict
import hashlib


class ClassColorProvider:
    """
    Gera cores automaticamente para classes de forma determinística.
    
    Usa hash da classe para gerar cores consistentes e com bom contraste.
    Paleta vibrant com Saturation=70% e Lightness=50% para máxima legibilidade.
    """
    
    # Cores base para gerar paleta (HSL-friendly)
    # Valores otimizados para contraste e legibilidade em fundo escuro
    _HUE_STEP = 30  # Graus no espaço HSL (12 cores bem distribuídas)
    _SATURATION = 70  # 0-100 (mais saturado = mais vibrante)
    _LIGHTNESS = 50   # 0-100 (luminosidade média = bom contraste)
    
    def __init__(self):
        """Inicializa o provedor."""
        self._cache: Dict[str, str] = {}
    
    @staticmethod
    def _hash_to_hue(class_name: str) -> int:
        """
        Converte nome da classe em um valor de hue (0-359).
        Determinístico.
        """
        # Garantir que class_name não é None
        if class_name is None:
            class_name = "UnknownClass"
        
        # Usar hash SHA256 para boa distribuição
        h = hashlib.sha256(class_name.encode("utf-8")).hexdigest()
        # Pegar primeiros 8 caracteres hexadecimais
        hash_val = int(h[:8], 16)
        # Mapear para 0-359
        return hash_val % 360
    
    @staticmethod
    def _hsl_to_hex(hue: int, saturation: int, lightness: int) -> str:
        """
        Converte HSL para hexadecimal RGB.
        
        Implementação simplificada mas funcional.
        Hue: 0-359
        Saturation: 0-100
        Lightness: 0-100
        """
        # Normalizar
        h = hue / 360.0
        s = saturation / 100.0
        l = lightness / 100.0
        
        if s == 0:
            # Sem saturação = cinza
            v = int(l * 255)
            return f"#{v:02X}{v:02X}{v:02X}"
        
        # Fórmula HSL -> RGB
        def hue2rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)
        
        return "#{:02X}{:02X}{:02X}".format(
            int(round(r * 255)),
            int(round(g * 255)),
            int(round(b * 255))
        )
    
    def get_color(self, class_name: str) -> str:
        """
        Retorna cor hexadecimal para a classe.
        Sempre a mesma cor para a mesma classe.
        Tolerante a None: usa "UnknownClass" como fallback.
        """
        # Garantir que class_name não é None
        if class_name is None:
            class_name = "UnknownClass"
        
        if class_name in self._cache:
            return self._cache[class_name]
        
        hue = self._hash_to_hue(class_name)
        color = self._hsl_to_hex(hue, self._SATURATION, self._LIGHTNESS)
        
        self._cache[class_name] = color
        return color
    
    def clear_cache(self) -> None:
        """Limpa o cache (pouco útil, mas pode ser handy)."""
        self._cache.clear()
