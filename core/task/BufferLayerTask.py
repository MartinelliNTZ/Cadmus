from .BaseTask import BaseTask
from .TaskFeedback import TaskFeedback

from ...utils.vector.VectorLayerGeometry import VectorLayerGeometry


class BufferLayerTask(BaseTask):
    """
    Executa buffer em arquivo físico (GPKG).
    Seguro para grandes volumes.
    """

    def __init__(
        self,
        *,
        input_path: str,
        output_path: str,
        distance: float,
        segments: int = 5,
        end_cap_style: int = 1,
        join_style: int = 1,
        miter_limit: float = 2.0,
        dissolve: bool = False,
        tool_key: str,
    ):
        super().__init__("Gerando buffer (heavy)", tool_key)

        self.input_path = input_path
        self.output_path = output_path
        self.distance = distance
        self.segments = segments
        self.end_cap_style = end_cap_style
        self.join_style = join_style
        self.miter_limit = miter_limit
        self.dissolve = dissolve

        self.logger.debug(
            f"BufferLayerTask initialized: {input_path} -> {output_path}, distance={distance}"
        )

    def _run(self) -> bool:

        if self.isCanceled():
            self.logger.info("BufferLayerTask canceled before start")
            return False

        self.logger.info(
            f"Starting buffer task: {self.input_path} -> {self.output_path}"
        )
        feedback = TaskFeedback(self)

        try:
            VectorLayerGeometry.create_buffer_to_path_safe(
                input_path=self.input_path,
                output_path=self.output_path,
                distance=self.distance,
                segments=self.segments,
                end_cap_style=self.end_cap_style,
                join_style=self.join_style,
                miter_limit=self.miter_limit,
                dissolve=self.dissolve,
                external_tool_key=self.tool_key,
                feedback=feedback,
            )

        except Exception as e:
            self.logger.critical(f"Erro no buffer: {str(e)}")
            raise

        if self.isCanceled():
            self.logger.info("BufferLayerTask canceled after execution")
            return False

        self.result = self.output_path

        self.logger.info("BufferLayerTask completed successfully")

        return True
