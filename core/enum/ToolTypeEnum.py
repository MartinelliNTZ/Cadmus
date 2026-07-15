from enum import Enum


class ToolTypeEnum(str, Enum):
    INSTANT = "INSTANT"
    DIALOG = "DIALOG"
    MAP_TOOL = "MAP_TOOL"
    BACKGROUND = "BACKGROUND"
    PROCESSING = "PROCESSING"
