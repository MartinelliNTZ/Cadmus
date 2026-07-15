# -*- coding: utf-8 -*-
import os
from typing import List, Dict

from .BaseTask import BaseTask
from ..config.LogUtils import LogUtils


class LoadFilesTask(BaseTask):
    """Task que valida/filtra registros de arquivos em background.

    Não instancia camadas QGIS aqui — apenas verifica acessibilidade e
    prepara a lista que será criada no thread principal pelo Step.
    """

    def __init__(self, *, records: List[Dict], tool_key: str = "untraceable"):
        super().__init__("Load files task", tool_key)
        self.records = records or []
        self.logger = LogUtils(tool=self.tool_key, class_name=self.__class__.__name__)

    def _run(self) -> bool:
        if self.isCanceled():
            return False

        self.logger.info(
            f"LoadFilesTask: iniciando validação de {len(self.records)} registros"
        )

        valid = []
        for idx, rec in enumerate(self.records):
            if self.isCanceled():
                self.logger.info("LoadFilesTask: cancelado")
                return False

            path = rec.get("path")
            try:
                if path and os.path.exists(path):
                    valid.append(rec)
                else:
                    self.logger.warning(
                        f"LoadFilesTask: arquivo não encontrado, pulando: {path}"
                    )
            except Exception as e:
                self.logger.error(f"LoadFilesTask: erro acessando {path}: {e}")

            # report progress
            if len(self.records) > 0:
                pct = int((idx + 1) * 100 / len(self.records))
                self.setProgress(pct)

        self.result = {"valid_records": valid}
        self.setProgress(100)
        self.logger.info(f"LoadFilesTask: validação concluída, válidos={len(valid)}")
        return True
