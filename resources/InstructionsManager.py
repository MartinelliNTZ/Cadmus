# -*- coding: utf-8 -*-
from pathlib import Path
from ..i18n.TranslationManager import TM


class InstructionsManager:
    BASE_DIR = Path(__file__).parent
    _cache = {}

    @classmethod
    def _build_filename(cls, tool_key: str) -> str:
        return f"{tool_key.lower()}_help.md"

    @classmethod
    def get(cls, tool_key: str) -> str:
        if tool_key in cls._cache:
            return cls._cache[tool_key]

        filename = cls._build_filename(tool_key)

        locale = TM.locale  # ex: pt_BR

        candidates = [
            cls.BASE_DIR / "instructions" / locale / filename,
            cls.BASE_DIR / "instructions" / "pt_BR" / filename,
        ]

        for path in candidates:
            if path.exists():
                cls._cache[tool_key] = str(path)
                return cls._cache[tool_key]

        # fallback final
        fallback = cls.BASE_DIR / "instructions" / "pt_BR" / "standard.md"
        cls._cache[tool_key] = str(fallback)
        return cls._cache[tool_key]
