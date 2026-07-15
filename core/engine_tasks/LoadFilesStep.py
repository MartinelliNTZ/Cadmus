# -*- coding: utf-8 -*-
from typing import Any
import time

from .BaseStep import BaseStep
from ..task.LoadFilesTask import LoadFilesTask
from ..config.LogUtils import LogUtils
from .ExecutionContext import ExecutionContext
import os
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QApplication

from ...utils.ExplorerUtils import ExplorerUtils
from ...utils.ProjectUtils import ProjectUtils
import threading
from ..ui.ProgressDialog import ProgressDialog


class LoadFilesStep(BaseStep):
    def name(self) -> str:
        return "load_files"

    def create_task(self, context: ExecutionContext):
        context.require(["records", "tool_key"])
        records = context.get("records")
        tool_key = context.get("tool_key")
        return LoadFilesTask(records=records, tool_key=tool_key)

    def on_success(self, context: ExecutionContext, result: Any) -> None:
        logger = LogUtils(
            tool=context.get("tool_key"), class_name=self.__class__.__name__
        )

        valid = []
        if isinstance(result, dict):
            valid = result.get("valid_records", [])
        elif isinstance(result, list):
            valid = result

        logger.info(
            f"Registros válidos={len(valid)} thread={threading.current_thread().name}"
        )

        # Agora, no thread principal, instanciar camadas e adicioná-las ao projeto
        project = QgsProject.instance()

        # Se o usuário marcou "missing_only", evita carregar arquivos já presentes no projeto
        already_loaded = set()
        if context.get("missing_only", False):
            for layer in project.mapLayers().values():
                already_loaded.add(ProjectUtils.normalize_layer_source(layer.source()))

        loaded = 0
        total = len(valid)
        chunk = 10
        progress = None

        try:
            parent = context.get("parent", None)
            try:
                progress = ProgressDialog(
                    "Carregando camadas...", "Cancelar", 0, total, parent
                )
                progress.show()
            except Exception as e:
                progress = None
                logger.debug(f"ProgressDialog unavailable: {e}")

            for i in range(0, total, chunk):
                time.sleep(0.1)  # pequeno delay para permitir UI responder
                if context.is_cancelled():
                    logger.info(
                        "LoadFilesStep.on_success: cancelado durante adição de layers"
                    )
                    break

                batch = valid[i: i + chunk]

                for rec in batch:
                    try:
                        # Se solicitado, não carregue arquivos que já estão no projeto
                        if context.get("missing_only", False):
                            rec_src = ProjectUtils.normalize_layer_source(
                                rec.get("path")
                            )
                            if rec_src in already_loaded:
                                logger.debug(
                                    f"LoadFilesStep: arquivo já carregado, pulando: {rec_src}"
                                )
                                continue

                        layer = ExplorerUtils.create_layer(rec, context.get("tool_key"))
                        if not layer or not layer.isValid():
                            logger.warning(
                                f"LoadFilesStep: camada inválida para {rec.get('path')}"
                            )
                            continue

                        folder = context.get("folder", "")
                        if context.get("preserve", False):
                            rel = os.path.relpath(
                                os.path.dirname(rec.get("path")), folder
                            )

                            # Se last_folder estiver ativo, descarta o último segmento
                            if context.get("last_folder", False) and rel not in (
                                ".",
                                "",
                            ):
                                parts = rel.split(os.sep)
                                if len(parts) > 1:
                                    rel = os.path.join(*parts[:-1])
                                else:
                                    rel = "."

                            if rel == ".":
                                ProjectUtils.add_layer(layer, add_to_root=True)
                            else:
                                try:
                                    group = ProjectUtils.ensure_group(rel)
                                    ProjectUtils.add_layer_to_group(layer, group)
                                except Exception as ge:
                                    logger.error(
                                        f"Erro adicionando camada ao grupo {rel}: {ge}"
                                    )
                                    ProjectUtils.add_layer(layer, add_to_root=True)
                        else:
                            ProjectUtils.add_layer(layer, add_to_root=True)

                        loaded += 1
                        # atualizar progresso se existir dialog
                        try:
                            if progress:
                                progress.set_value(loaded)
                                if progress.is_canceled():
                                    context.cancel()
                                    logger.info(
                                        "LoadFilesStep: cancelado pelo usuário via ProgressDialog"
                                    )
                                    break
                        except Exception as e:
                            logger.error(f"LoadFilesStep: progress update failed: {e}")
                    except Exception as e:
                        logger.error(
                            f"LoadFilesStep: erro ao criar/adicionar camada {rec.get('path')}: {e}"
                        )
                        continue

                # permitir UI responder entre lotes
                try:
                    QApplication.processEvents()
                except Exception as e:
                    logger.error(f"LoadFilesStep: processEvents failed: {e}")

                logger.info(
                    f"Batch {i}-{i + len(batch) - 1} adicionadas; progresso {loaded}/{total}"
                )
        finally:
            try:
                if progress:
                    progress.close()
            except Exception as e:
                logger.error(f"LoadFilesStep: closing progress dialog failed: {e}")

        context.set("loaded_count", loaded)
        logger.info(f"LoadFilesStep.on_success: terminada, loaded={loaded}")
