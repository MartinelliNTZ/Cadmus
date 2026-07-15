# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ExecutionContext:
    """
    Shared state container between all pipeline steps.

    Canonical attributes (direct access):
        input_path: str           — Input directory with files to process
        output_path: str          — Base directory to save results
        files: list[str] | None   — Specific file list (None = all in input_path)
        tool_key: str             — ToolKey for logging
        json_path: str            — Path to JSON metadata file (heavily used across steps)
        lat: float | None         — Latitude (set by PhotoEnrichmentStep or CoordClickTool)
        lon: float | None         — Longitude (set by PhotoEnrichmentStep or CoordClickTool)
        errors: list[Exception]   — Error accumulator
        is_cancelled: bool        — Cancellation flag
        results: dict             — Step results storage (key: step name)

    Legacy access (DEPRECATED — kept for backward compatibility):
        context.set("key", value)   → Prefer canonical attributes or set_result()
        context.get("key", default) → Prefer canonical attributes or get_result()
    """

    # ── Canonical attributes ────────────────────────────────────
    input_path: str = ""
    """Input directory with files to process."""

    output_path: str = ""
    """Base directory where results will be saved."""

    files: list[str] | None = None
    """Specific file list to process. None = all files in input_path."""

    tool_key: str = ""
    """ToolKey for logging."""

    json_path: str = ""
    """Path to JSON metadata file. Used by multiple steps (PhotoEnrichment → JsonVectorization → Report)."""

    lat: float | None = None
    """Latitude (decimal). Set by PhotoEnrichmentStep or CoordClickTool. Consumed by AltimetryStep and ReverseGeocodeStep."""

    lon: float | None = None
    """Longitude (decimal). Set by PhotoEnrichmentStep or CoordClickTool. Consumed by AltimetryStep and ReverseGeocodeStep."""

    def __init__(
        self,
        initial_data: Optional[Dict[str, Any]] = None,
        *,
        input_path: str = "",
        output_path: str = "",
        files: Optional[list[str]] = None,
        tool_key: str = "",
        json_path: str = "",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ):
        # Internal data dict — used by legacy set()/get() and for step results
        self._data: Dict[str, Any] = initial_data.copy() if initial_data else {}
        self._errors: List[Exception] = []
        self._is_cancelled: bool = False

        # Step results storage
        self._results: Dict[str, Any] = {}

        # Set canonical attributes from keyword arguments
        if input_path:
            self.input_path = input_path
        if output_path:
            self.output_path = output_path
        if files is not None:
            self.files = files
        if tool_key:
            self.tool_key = tool_key
        if json_path:
            self.json_path = json_path
        if lat is not None:
            self.lat = lat
        if lon is not None:
            self.lon = lon

        # Import canonical attributes from legacy initial_data if present
        if initial_data:
            for key in ("input_path", "output_path", "files", "tool_key", "json_path", "lat", "lon"):
                if key in initial_data:
                    setattr(self, key, initial_data[key])

    # ── Step results ────────────────────────────────────────────

    def set_result(self, key: str, value: Any) -> "ExecutionContext":
        """Stores a step result (e.g. 'json_path', 'layer', 'report_payload')."""
        self._results[key] = value
        # Convenience: if key matches a canonical attribute, also update it
        if key in ("json_path", "tool_key", "input_path", "output_path", "lat", "lon"):
            setattr(self, key, value)
        return self

    def get_result(self, key: str, default: Any = None) -> Any:
        """Retrieves a step result."""
        return self._results.get(key, default)

    # ── Legacy access (DEPRECATED) ──────────────────────────────
    # Kept for backward compatibility with existing pipelines.
    # New code should use canonical attributes or set_result()/get_result().

    def set(self, key: str, value: Any) -> "ExecutionContext":
        """DEPRECATED: Prefer canonical attributes or set_result()."""
        self._data[key] = value
        # Sync canonical attributes for convenience
        if key in ("input_path", "output_path", "files", "tool_key", "json_path", "lat", "lon"):
            setattr(self, key, value)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """DEPRECATED: Prefer canonical attributes or get_result()."""
        # Check canonical attributes first
        if key in ("input_path", "output_path", "files", "tool_key", "json_path", "lat", "lon"):
            val = getattr(self, key, None)
            if val is not None:
                return val
        # Check results
        if key in self._results:
            return self._results[key]
        # Fallback to internal data
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """DEPRECATED: Prefer canonical attribute checks."""
        return key in self._data or key in self._results

    def require(self, keys: List[str]) -> None:
        """
        Validates that required keys/attributes exist.

        Raises KeyError if any are missing.
        """
        missing = []
        for key in keys:
            # Check canonical attributes
            if key in ("input_path", "output_path", "files", "tool_key", "json_path", "lat", "lon"):
                val = getattr(self, key, None)
                if val is None and key not in self._data:
                    missing.append(key)
            elif key not in self._data and key not in self._results:
                missing.append(key)
        if missing:
            raise KeyError(f"ExecutionContext missing required keys: {missing}")

    # ── Errors ──────────────────────────────────────────────────

    def add_error(self, exc: Exception) -> None:
        """Adds error to the error list."""
        self._errors.append(exc)

    def get_errors(self) -> List[Exception]:
        """Returns a copy of the error list."""
        return self._errors.copy()

    def has_errors(self) -> bool:
        """True if there were any errors."""
        return len(self._errors) > 0

    # ── Cancellation ────────────────────────────────────────────

    def cancel(self) -> None:
        """Marks context as cancelled."""
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Returns cancellation status."""
        return self._is_cancelled

    # ── Reset ───────────────────────────────────────────────────

    def clear(self) -> None:
        """Resets all state."""
        self.input_path = ""
        self.output_path = ""
        self.files = None
        self.tool_key = ""
        self.json_path = ""
        self.lat = None
        self.lon = None
        self._data.clear()
        self._results.clear()
        self._errors.clear()
        self._is_cancelled = False

    def __repr__(self) -> str:
        n_files = len(self.files) if self.files else 0
        return (
            f"<ExecutionContext "
            f"input_path='{self.input_path}', "
            f"output_path='{self.output_path}', "
            f"files={n_files}, "
            f"tool_key='{self.tool_key}', "
            f"json_path='{self.json_path}', "
            f"lat={self.lat}, "
            f"lon={self.lon}, "
            f"results={len(self._results)} keys, "
            f"errors={len(self._errors)}, "
            f"cancelled={self._is_cancelled}>"
        )
