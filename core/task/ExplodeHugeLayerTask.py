from .BaseTask import BaseTask

from ...utils.vector.VectorLayerGeometry import VectorLayerGeometry


class ExplodeHugeLayerTask(BaseTask):
    """
    Explode linhas usando processing em arquivo físico.
    Seguro para milhões de feições.
    """

    def __init__(self, *, input_path: str, output_path: str, tool_key: str):
        super().__init__("Explodindo linhas (heavy)", tool_key)
        self.input_path = input_path
        self.output_path = output_path
        self.logger.debug(
            f"ExplodeTask initialized for {self.input_path} -> {self.output_path}"
        )

    def _run(self) -> bool:
        if self.isCanceled():
            self.logger.info("ExplodeHugeLayerTask canceled before start")
            return False
        self.logger.info(
            f"Starting explode task for {self.input_path} -> {self.output_path}"
        )
        ok = VectorLayerGeometry.explode_lines_to_path(
            input_path=self.input_path,
            output_path=self.output_path,
            external_tool_key=self.tool_key,
        )

        if not ok:
            return False

        self.result = self.output_path
        return True
