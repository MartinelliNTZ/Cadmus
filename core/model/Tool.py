# -*- coding: utf-8 -*-
from ..config.LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey


class Tool:
    """Abstração de ferramenta para menu/toolbar do plugin."""

    def __init__(
        self,
        tool_key,
        name,
        icon,
        category,
        tool_type,
        main_action=False,
        executor=None,
        tooltip=None,
        order=100,
        show_in_toolbar=True,
        registry_level=None,
    ):
        self.logger = LogUtils(tool=ToolKey.SYSTEM, class_name="Tool")

        self.tool_key = tool_key
        self.name = name
        self.icon = icon
        self.category = category
        self.tool_type = tool_type
        self.main_action = main_action
        self.executor = executor
        self.tooltip = tooltip
        self.order = order
        self.show_in_toolbar = show_in_toolbar
        self.registry_level = registry_level

        self.action = None  # Será criado pelo MenuManager

    def set_executor(self, executor):
        self.executor = executor
        if self.action is not None:
            try:
                self.action.triggered.disconnect()
            except Exception as e:
                self.logger.error(
                    f"Falha ao desconectar executor anterior: {e}")
            self.action.triggered.connect(executor)
