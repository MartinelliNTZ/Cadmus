# -*- coding: utf-8 -*-
import re
from datetime import datetime

from qgis.core import QgsLayoutItemLabel, QgsProject

from ..core.config.LogUtils import LogUtils


class LayoutsUtils:
    """
    Processamento de layouts do QGIS.
    Não depende de UI.
    """

    @staticmethod
    def _build_matcher(old_text: str, new_text: str,
                       case_sensitive: bool,
                       full_replace: bool):
        """
        Retorna função match_and_replace(text) -> str | None
        """
        if not full_replace:
            # Substituição parcial
            if case_sensitive:
                def fn(text):
                    return text.replace(old_text, new_text) if old_text in text else None
                return fn
            else:
                pattern = re.compile(re.escape(old_text), re.IGNORECASE)
                low_old = old_text.lower()

                def fn(text):
                    if low_old in text.lower():
                        return pattern.sub(new_text, text)
                    return None
                return fn
        else:
            # Substituição total (modo chave)
            if case_sensitive:
                def fn(text):
                    return new_text if old_text in text else None
                return fn
            else:
                low_old = old_text.lower()

                def fn(text):
                    return new_text if low_old in text.lower() else None
                return fn

    @staticmethod
    def replace_text_in_layouts(
        project: QgsProject,
        tool_key: str,
        old_text: str,
        new_text: str,
        case_sensitive: bool = True,
        full_replace: bool = False
    ) -> dict:
        """
        Executa replace em QgsLayoutItemLabel.
        Retorna dicionário com resumo da operação.
        """

        if not old_text:
            raise ValueError("old_text vazio")

        matcher = LayoutsUtils._build_matcher(
            old_text, new_text, case_sensitive, full_replace
        )

        layouts = project.layoutManager().layouts()
        total_layouts = len(layouts)
        total_changes = 0
        logger = LogUtils(tool=tool_key, class_name="LayoutsUtils")

        logger.info("Iniciando replace em layouts")
        logger.info(f"Layouts encontrados: {total_layouts}")
        logger.info(f"Old text: '{old_text}' | New text: '{new_text}'")
        logger.info(f"Case sensitive: {case_sensitive}")
        logger.info(f"Full replace: {full_replace}")

        for layout in layouts:
            layout_name = layout.name()
            layout_changes = 0

            for item in layout.items():
                if not isinstance(item, QgsLayoutItemLabel):
                    continue

                original = item.text()
                replaced = matcher(original)

                if replaced is not None and replaced != original:
                    item.setText(replaced)
                    total_changes += 1
                    layout_changes += 1

                    logger.debug(
                        f"[{layout_name}] '{original}' -> '{replaced}'"
                    )

            if layout_changes:
                logger.debug(
                    f"[{layout_name}] alterações: {layout_changes}"
                )

        logger.info(f"Total de substituições: {total_changes}")
        logger.info(f"Finalizado em {datetime.now().isoformat()}")

        return {
            "total_layouts": total_layouts,
            "total_changes": total_changes
        }
