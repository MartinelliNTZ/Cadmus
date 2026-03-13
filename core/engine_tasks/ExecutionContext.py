# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional


class ExecutionContext:
    """
    Armazena o estado compartilhado da execução da pipeline.
    """

    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        self._data: Dict[str, Any] = initial_data.copy() if initial_data else {}
        self._errors: List[Exception] = []
        self._is_cancelled: bool = False

    # -----------------------------
    # Basic access
    # -----------------------------

    def set(self, key: str, value: Any) -> "ExecutionContext":
        self._data[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._data

    def require(self, keys: List[str]) -> None:
        missing = [k for k in keys if k not in self._data]
        if missing:
            raise KeyError(f"ExecutionContext missing required keys: {missing}")

    # -----------------------------
    # Errors
    # -----------------------------

    def add_error(self, exc: Exception) -> None:
        self._errors.append(exc)

    def get_errors(self) -> List[Exception]:
        return self._errors.copy()

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    # -----------------------------
    # Cancel
    # -----------------------------

    def cancel(self) -> None:
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        return self._is_cancelled

    # -----------------------------
    # Reset
    # -----------------------------

    def clear(self) -> None:
        self._data.clear()
        self._errors.clear()
        self._is_cancelled = False