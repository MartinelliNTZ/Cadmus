# -*- coding: utf-8 -*-
from .BaseStep import BaseStep
from .ExecutionContext import ExecutionContext
from ..task.PhotoMetadataTask import PhotoMetadataTask
from ..config.LogUtils import LogUtils
from qgis.core import QgsField
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QApplication


class PhotoMetadataStep(BaseStep):
    """Step para aplicar metadados de fotos diretamente na camada."""

    def name(self) -> str:
        return "PhotoMetadataStep"

    def create_task(self, context: ExecutionContext):
        context.require(["layer", "base_folder", "recursive", "tool_key"])

        layer = context.get("layer")
        return PhotoMetadataTask(
            layer_id=layer.id() if layer else "",
            base_folder=context.get("base_folder"),
            recursive=context.get("recursive", True),
            tool_key=context.get("tool_key"),
        )

    def on_success(self, context: ExecutionContext, result):
        if not result or not isinstance(result, dict):
            return

        layer = context.get("layer")
        if layer is None:
            LogUtils(
                tool=context.get("tool_key"),
                class_name=self.__class__.__name__,
            ).error("Camada ausente no contexto durante aplicação de metadados")
            return

        updates = result.get("updates", {}) or {}
        field_names = result.get("field_names", []) or []

        if not updates:
            LogUtils(
                tool=context.get("tool_key"),
                class_name=self.__class__.__name__,
            ).info("Nenhuma atualização de metadados de fotos para aplicar")
            return

        LogUtils(
            tool=context.get("tool_key"),
            class_name=self.__class__.__name__,
        ).debug(f"Aplicando metadados em {len(updates)} itens. Campos esperados: {field_names}")

        # Adicionar campos faltantes
        missing_fields = [f for f in field_names if layer.fields().indexOf(f) == -1]
        started_editing = False
        if missing_fields:
            LogUtils(
                tool=context.get("tool_key"),
                class_name=self.__class__.__name__,
            ).debug(f"Adicionando campos faltantes: {missing_fields}")

            if not layer.isEditable():
                layer.startEditing()
                started_editing = True
            for field in missing_fields:
                layer.addAttribute(QgsField(field, QVariant.String))
            layer.updateFields()

        # Garantir modo de edição para aplicar valores
        if not layer.isEditable():
            layer.startEditing()
            started_editing = True

        # Mapear foto -> fid
        foto_to_fid = {}
        for feat in layer.getFeatures():
            foto_val = feat.attribute("foto")
            if foto_val is None:
                continue
            try:
                foto_to_fid[int(foto_val)] = feat.id()
            except Exception:
                continue

        # Aplicar valores por batch
        layer.blockSignals(True)
        try:
            for foto, vals in updates.items():
                fid = foto_to_fid.get(int(foto))
                if fid is None:
                    continue
                for field_name, value in vals.items():
                    idx = layer.fields().indexOf(field_name)
                    if idx == -1:
                        continue
                    try:
                        layer.changeAttributeValue(fid, idx, value)
                    except Exception:
                        pass
            # Comentar commit para manter no buffer de edição caso o usuário queira revisar
        finally:
            layer.blockSignals(False)

        if started_editing:
            try:
                layer.commitChanges()
            except Exception:
                pass

        try:
            layer.triggerRepaint()
        except Exception:
            pass

        LogUtils(
            tool=context.get("tool_key"),
            class_name=self.__class__.__name__,
        ).info(f"Metadados de fotos aplicados em {len(updates)} feições")
