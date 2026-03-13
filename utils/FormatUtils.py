import time
class FormatUtils:

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