# -*- coding: utf-8 -*-
import time
import math
from datetime import datetime
from typing import Optional

from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil


class FormatUtils(BaseUtil):
    """Utilitário para formatação de valores para exibição ao usuário.

    Métodos estáticos, tool_key opcional para logging de erros de parsing.
    """

    @staticmethod
    def _get_logger(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="FormatUtils")

    @staticmethod
    def bytes(n: float) -> str:
        for u in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024 or u == "TB":
                return f"{n:.1f}{u}"
            n /= 1024

    @staticmethod
    def speed(bps: float) -> str:
        if bps <= 0:
            return "0B/s"
        return f"{FormatUtils.bytes(bps)}/s"

    @staticmethod
    def duration(seconds: float) -> str:
        if seconds <= 0:
            return "0s"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h{m}m"
        if m:
            return f"{m}m{s}s"
        return f"{s}s"

    @staticmethod
    def clock(ts: float) -> str:
        if not ts:
            return "--:--:--"
        return time.strftime("%H:%M:%S", time.localtime(ts))

    @staticmethod
    def pretty(value: float) -> str:
        if value <= 0:
            return "0"
        if value < 1:
            return f"{value:.2f}"
        if value < 10:
            return f"{value:.1f}"
        return f"{int(value)}"

    @staticmethod
    def fmt_num(value: float) -> str:
        if value == math.inf:
            return "inf"
        if value == -math.inf:
            return "-inf"
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")

    @staticmethod
    def format_duration(seconds: Optional[int]) -> str:
        if seconds is None:
            return "N/A"
        hh = seconds // 3600
        mm = (seconds % 3600) // 60
        ss = seconds % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}"

    @staticmethod
    def format_shutter_speed(seconds: Optional[float]) -> str:
        if seconds is None or seconds <= 0:
            return "N/A"
        if seconds >= 1:
            return f"{seconds:.2f}s"
        denom = round(1.0 / seconds)
        if denom <= 0:
            return "N/A"
        return f"1/{denom}s"

    @staticmethod
    def parse_capture_datetime(raw: str) -> Optional[datetime]:
        if not raw:
            return None
        text = str(raw).strip()
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            pass
        for fmt in (
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y%m%d%H%M",
        ):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None
