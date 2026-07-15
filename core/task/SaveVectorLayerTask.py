# -*- coding: utf-8 -*-
from .BaseTask import BaseTask
from ...utils.vector.VectorLayerSource import VectorLayerSource
from ...core.config.LogUtils import LogUtils
from typing import Optional


class SaveVectorLayerTask(BaseTask):
    """
    Task responsável por salvar camada em disco e/ou projeto.
    Operação considerada pesada por envolver I/O.
    """

    def __init__(
        self,
        *,
        layer,
        output_path: Optional[str],
        save_to_folder: bool,
        output_name: str,
        decision: str = "rename",
        tool_key: str,
    ):
        super().__init__("Salvando camada", tool_key)

        self.layer = layer
        self.output_path = output_path
        self.save_to_folder = save_to_folder
        self.output_name = output_name
        self.decision = decision

    def _run(self) -> bool:

        if self.isCanceled():
            return False

        try:
            result_layer = VectorLayerSource.save_vector_layer(
                layer=self.layer,
                output_path=self.output_path,
                save_to_folder=self.save_to_folder,
                output_name=self.output_name,
                decision=self.decision,
                external_tool_key=self.tool_key,
            )

            if not result_layer:
                raise Exception("Falha ao salvar camada.")

            self.result = result_layer

        except Exception as e:
            logger = LogUtils(tool=self.tool_key, class_name=self.__class__.__name__)
            logger.critical(f"Erro no SaveLayerTask: {str(e)}")
            raise

        return True
