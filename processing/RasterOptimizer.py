# -*- coding: utf-8 -*-
import os
import shutil
import subprocess  # nosec B404  # Necessário para executar gdalinfo/gdaladdo
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from qgis.core import (
    QgsProcessing,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingAlgorithm,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm

OVERVIEW_LEVELS_DEFAULT = ["2", "4", "8", "16", "32", "64", "128", "256"]
OVERVIEW_LEVEL_ALL = OVERVIEW_LEVELS_DEFAULT
logger = LogUtils(tool="Untraceable", class_name="None")
RESAMPLING_METHODS = [
    "average",
    "nearest",
    "gauss",
    "cubic",
    "cubicspline",
    "lanczos",
    "mode",
]

COMPRESSION_METHODS = [
    "LZW",
    "DEFLATE",
    "ZSTD",
]

PREDICTOR_VALUES = [
    "1 (Default)",
    "2 (Horizontal)",
    "3 (Vertical)",
]

# Fator de estimativa de espaço para overviews internos
# Overviews internos somam ~33% do tamanho original (pirâmide geométrica)
OVERVIEW_DISK_FACTOR = 0.34

# Número máximo de processos gdaladdo executados em paralelo
MAX_WORKERS = 4


def _estimate_overview_size(raster_path):
    """
    Estima o espaço necessário para overviews internos.
    A soma de uma pirâmide geométrica converge para ~1/3 do tamanho original.
    """
    try:
        return int(os.path.getsize(raster_path) * OVERVIEW_DISK_FACTOR)
    except OSError:
        return 0


def _free_disk_space(path):
    """Retorna espaço livre em disco no mesmo volume do arquivo."""
    try:
        total, used, free = shutil.disk_usage(os.path.dirname(os.path.abspath(path)))
        return free
    except OSError:
        return None


def _has_internal_overviews(raster_path):
    """
    Verifica se o raster já possui overviews internos usando gdalinfo.
    Retorna (tem_overviews: bool, níveis: list[str])
    """
    try:
        result = subprocess.run(  # nosec B603 B607  # gdalinfo é ferramenta do sistema, caminho controlado
            ["gdalinfo", raster_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = result.stdout.splitlines()
        levels = [line.strip() for line in lines if "Overview" in line and "x" in line]
        return len(levels) > 0, levels
    except Exception as e:
        logger.debug(f"_has_internal_overviews: failed with error: {e}")
        return False, []


def _run_gdaladdo(cmd, raster_path, feedback_queue):
    """
    Executa gdaladdo via subprocess.Popen em uma thread separada.
    Retorna (raster_path, success: bool, error_msg: str)
    """
    name = os.path.basename(raster_path)
    try:
        process = subprocess.Popen(  # nosec B603  # cmd construído com parâmetros controlados, sem shell=True
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Ler stdout em tempo real
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                feedback_queue.append(f"  [{name}] {line}")

        stdout, stderr = process.communicate()

        if stderr and stderr.strip():
            # gdaladdo costuma mandar progresso no stderr também
            for line in stderr.strip().splitlines():
                stripped = line.strip()
                if stripped:
                    feedback_queue.append(f"  [{name}] {stripped}")

        if process.returncode != 0:
            error_msg = (
                stderr.strip()
                if stderr and stderr.strip()
                else f"Código de retorno {process.returncode}"
            )
            return (raster_path, False, error_msg)

        return (raster_path, True, None)

    except Exception as e:
        return (raster_path, False, str(e))


class RasterOptimizer(BaseProcessingAlgorithm):

    TOOL_KEY = ToolKey.RASTER_OPTIMIZER
    ALGORITHM_NAME = "raster_optimizer"
    ALGORITHM_DISPLAY_NAME = STR.RASTER_OPTIMIZER_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    INSTRUCTIONS_FILE = "raster_optimizer.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="RasterOptimizer", level="DEBUG")
    ICON = im.RASTER_OPTIMIZER

    # Parameter names
    INPUT_RASTERS = "INPUT_RASTERS"
    INPUT_FOLDER = "INPUT_FOLDER"
    RECURSIVE = "RECURSIVE"
    OVERVIEW_LEVELS = "OVERVIEW_LEVELS"
    RESAMPLING = "RESAMPLING"
    COMPRESSION = "COMPRESSION"
    PREDICTOR = "PREDICTOR"
    ZLEVEL = "ZLEVEL"
    DELETE_EXISTING = "DELETE_EXISTING"
    BIGTIFF = "BIGTIFF"
    SKIP_IF_HAS_OVERVIEWS = "SKIP_IF_HAS_OVERVIEWS"

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo RasterOptimizer...")

        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                STR.INPUT_RASTER_LAYERS,
                QgsProcessing.TypeRaster,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                STR.INPUT_RASTER_FOLDER,
                behavior=QgsProcessingParameterFile.Folder,
                optional=True,
                defaultValue=self.prefs.get("last_folder", ""),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RECURSIVE,
                STR.USE_RECURSIVE_SEARCH,
                defaultValue=self.prefs.get("recursive", True),
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OVERVIEW_LEVELS,
                STR.OVERVIEW_LEVELS,
                options=OVERVIEW_LEVEL_ALL,
                allowMultiple=True,
                defaultValue=self.prefs.get(
                    "overview_levels", [0, 1, 2, 3, 4, 5, 6, 7]
                ),
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                STR.RESAMPLING_METHOD,
                options=RESAMPLING_METHODS,
                defaultValue=self.prefs.get("resampling", 0),
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.COMPRESSION,
                STR.COMPRESS_OVERVIEW,
                options=COMPRESSION_METHODS,
                defaultValue=self.prefs.get("compression", 0),  # LZW
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PREDICTOR,
                STR.PREDICTOR,
                options=PREDICTOR_VALUES,
                defaultValue=self.prefs.get("predictor", 1),  # 1 (Default)
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ZLEVEL,
                STR.ZLEVEL,
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=self.prefs.get("zlevel", 9),
                minValue=1,
                maxValue=9,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DELETE_EXISTING,
                STR.DELETE_EXISTING_OVERVIEWS,
                defaultValue=self.prefs.get("delete_existing", False),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.BIGTIFF,
                STR.BIGTIFF_YES,
                defaultValue=self.prefs.get("bigtiff", True),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SKIP_IF_HAS_OVERVIEWS,
                (
                    STR.SKIP_IF_HAS_OVERVIEWS
                    if hasattr(STR, "SKIP_IF_HAS_OVERVIEWS")
                    else "Pular rasters que já possuem overviews internos"
                ),
                defaultValue=self.prefs.get("skip_if_has_overviews", True),
            )
        )

    def flags(self):
        """
        Garante que o algoritmo rode em background thread (QgsTask).
        Isso evita travar a UI do QGIS durante o processamento.
        """
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def processAlgorithm(self, params, context, feedback):
        if feedback.isCanceled():
            return {}

        raster_layers = self.parameterAsLayerList(params, self.INPUT_RASTERS, context)
        input_folder = self.parameterAsString(params, self.INPUT_FOLDER, context)
        recursive = self.parameterAsBool(params, self.RECURSIVE, context)
        selected_levels = self.parameterAsEnums(params, self.OVERVIEW_LEVELS, context)
        resampling_idx = self.parameterAsEnum(params, self.RESAMPLING, context)
        compression_idx = self.parameterAsEnum(params, self.COMPRESSION, context)
        predictor_idx = self.parameterAsEnum(params, self.PREDICTOR, context)
        zlevel = self.parameterAsInt(params, self.ZLEVEL, context)
        delete_existing = self.parameterAsBool(params, self.DELETE_EXISTING, context)
        bigtiff = self.parameterAsBool(params, self.BIGTIFF, context)
        skip_if_has_overviews = self.parameterAsBool(
            params, self.SKIP_IF_HAS_OVERVIEWS, context
        )

        self.logger.debug(
            f"Parametros: folder={input_folder}, recursive={recursive}, "
            f"levels={selected_levels}, resampling={RESAMPLING_METHODS[resampling_idx]}, "
            f"compression={COMPRESSION_METHODS[compression_idx]}, "
            f"predictor={predictor_idx + 1}, zlevel={zlevel}, bigtiff={bigtiff}, "
            f"skip_if_has_overviews={skip_if_has_overviews}"
        )

        # ── Coletar rasters ────────────────────────────────────────────────

        raster_paths = []

        if raster_layers:
            for rl in raster_layers:
                path = rl.source()
                if path.lower().endswith((".tif", ".tiff")):
                    if path not in raster_paths:
                        raster_paths.append(path)
                    self.logger.debug(f"Raster de camada adicionado: {path}")

        if input_folder and os.path.isdir(input_folder):
            self.logger.debug(
                f"Buscando rasters em: {input_folder} (recursive={recursive})"
            )
            for root, dirs, files in os.walk(input_folder):
                for f in files:
                    if f.lower().endswith((".tif", ".tiff")):
                        full_path = os.path.join(root, f)
                        if full_path not in raster_paths:
                            raster_paths.append(full_path)
                if not recursive:
                    break

        if not raster_paths:
            feedback.pushInfo("Nenhum raster encontrado para processar.")
            self.logger.warning("Nenhum raster encontrado.")
            return {}

        # ── Converter índices de níveis para valores reais ─────────────────

        level_values = [OVERVIEW_LEVEL_ALL[i] for i in selected_levels]

        total = len(raster_paths)
        self.logger.info(f"Total de rasters para processar: {total}")
        feedback.pushInfo(f"Total de rasters encontrados: {total}")
        feedback.pushInfo(f"Níveis de overview: {', '.join(level_values)}")
        feedback.pushInfo(f"Compressão: {COMPRESSION_METHODS[compression_idx]}")
        feedback.pushInfo(f"Reamostragem: {RESAMPLING_METHODS[resampling_idx]}")
        feedback.pushInfo(f"Processos paralelos: {MAX_WORKERS}")
        feedback.pushInfo("-" * 60)

        # ── Salvar preferências ────────────────────────────────────────────

        self.prefs.update(
            {
                "last_folder": input_folder,
                "recursive": bool(recursive),
                "overview_levels": selected_levels,
                "resampling": resampling_idx,
                "compression": compression_idx,
                "predictor": predictor_idx,
                "zlevel": zlevel,
                "delete_existing": bool(delete_existing),
                "bigtiff": bool(bigtiff),
                "skip_if_has_overviews": bool(skip_if_has_overviews),
            }
        )
        self.save_preferences()

        # ── Pré-processamento: filtrar rasters inválidos ──────────────────

        raster_paths_valid = []
        for raster_path in raster_paths:
            if feedback.isCanceled():
                feedback.pushInfo("Processamento cancelado pelo usuário.")
                return {}

            if not os.path.exists(raster_path):
                feedback.pushInfo(f"  IGNORADO — arquivo não encontrado: {raster_path}")
                self.logger.warning(f"Arquivo não encontrado: {raster_path}")
                continue

            if skip_if_has_overviews and not delete_existing:
                has_ovr, existing_levels = _has_internal_overviews(raster_path)
                if has_ovr:
                    feedback.pushInfo(
                        f"  PULADO — já possui overviews internos: "
                        f"{', '.join(existing_levels[:4])}{'...' if len(existing_levels) > 4 else ''}"
                    )
                    self.logger.debug(f"Pulado (já tem overviews): {raster_path}")
                    continue

            raster_paths_valid.append(raster_path)

        total_valid = len(raster_paths_valid)
        if total_valid == 0:
            feedback.pushInfo("Nenhum raster válido para processar após filtros.")
            return {}

        feedback.pushInfo(f"Rasters para processar após filtros: {total_valid}")
        feedback.pushInfo("-" * 60)

        # ── Montar comandos ────────────────────────────────────────────────

        raster_tasks = []
        for raster_path in raster_paths_valid:
            if feedback.isCanceled():
                feedback.pushInfo("Processamento cancelado pelo usuário.")
                return {}

            # Verificação de espaço em disco
            needed = _estimate_overview_size(raster_path)
            free = _free_disk_space(raster_path)
            skip_disk = False
            if free is not None:
                needed_mb = needed / (1024**2)
                free_mb = free / (1024**2)
                feedback.pushInfo(
                    f"  {os.path.basename(raster_path)} → "
                    f"estimado: {needed_mb:.1f} MB, livre: {free_mb:.1f} MB"
                )
                if free < needed * 1.2:  # margem de segurança de 20%
                    msg = (
                        f"  IGNORADO — espaço insuficiente. "
                        f"Necessário: {needed_mb:.1f} MB, disponível: {free_mb:.1f} MB."
                    )
                    feedback.pushInfo(msg)
                    self.logger.warning(msg)
                    skip_disk = True

            if skip_disk:
                continue

            # Deletar overviews existentes se solicitado
            if delete_existing:
                self._delete_overviews(raster_path, feedback)

            resampling = RESAMPLING_METHODS[resampling_idx]
            compression = COMPRESSION_METHODS[compression_idx]
            predictor_value = str(predictor_idx + 1)

            cmd = [
                "gdaladdo",
                "-r",
                resampling,
                "--config",
                "COMPRESS_OVERVIEW",
                compression,
                "--config",
                "PREDICTOR_OVERVIEW",
                predictor_value,
                "--config",
                "ZLEVEL_OVERVIEW",
                str(zlevel),
                "--config",
                "USE_RRD",
                "NO",
                "--config",
                "GDAL_TIFF_OVR_BLOCKSIZE",
                "512",
            ]

            if bigtiff:
                cmd += ["--config", "BIGTIFF_OVERVIEW", "YES"]

            cmd += [raster_path, *level_values]
            raster_tasks.append((raster_path, cmd))

        total_tasks = len(raster_tasks)
        if total_tasks == 0:
            feedback.pushInfo("Nenhum raster para processar após verificações.")
            return {}

        feedback.pushInfo(
            f"Enviando {total_tasks} tarefas para pool (max {MAX_WORKERS} paralelos)..."
        )
        feedback.pushInfo("-" * 60)

        # ── Execução paralela com ThreadPoolExecutor ──────────────────────
        # Usamos uma lista compartilhada para acumular mensagens de feedback
        # das threads, e no loop principal drenamos essa lista periodicamente.
        # Isso evita chamar feedback.pushInfo() de dentro das threads (não
        # é garantido ser thread-safe) e mantém a UI responsiva.

        count_ok = 0
        count_failed = 0
        t_start = time.time()
        feedback_queue = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submeter todas as tarefas
            future_to_raster = {}
            for raster_path, cmd in raster_tasks:
                if feedback.isCanceled():
                    break
                self.logger.debug(f"Submetendo: {' '.join(cmd)}")
                future = executor.submit(
                    _run_gdaladdo, cmd, raster_path, feedback_queue
                )
                future_to_raster[future] = raster_path

            # Processar resultados à medida que ficam prontos
            completed_count = 0
            for future in as_completed(future_to_raster):
                completed_count += 1

                # Drenar fila de feedback das threads
                while feedback_queue:
                    msg = feedback_queue.pop(0)
                    feedback.pushInfo(msg)

                # Verificar cancelamento
                if feedback.isCanceled():
                    feedback.pushInfo(
                        "CANCELADO pelo usuário — terminando processos..."
                    )
                    # Cancelar futures pendentes
                    for f in future_to_raster:
                        f.cancel()
                    break

                # Obter resultado
                try:
                    raster_path, success, error_msg = future.result()
                    name = os.path.basename(raster_path)

                    if success:
                        count_ok += 1
                        feedback.pushInfo(f"  ✅ OK — {name}")
                        self.logger.debug(
                            f"Overviews criadas com sucesso: {raster_path}"
                        )
                    else:
                        count_failed += 1
                        feedback.pushInfo(f"  ❌ FALHA — {name}: {error_msg[:200]}")
                        self.logger.error(
                            f"Falha ao processar {raster_path}: {error_msg}"
                        )

                except Exception as e:
                    count_failed += 1
                    feedback.pushInfo(f"  ❌ ERRO inesperado: {e}")

                # Atualizar progresso
                now = time.time()
                progress = int(completed_count / total_tasks * 100)
                feedback.setProgress(min(progress, 99))
                elapsed = now - t_start
                feedback.pushInfo(
                    f"  📊 Progresso: {completed_count}/{total_tasks} "
                    f"({progress}%) — {elapsed:.0f}s decorridos"
                )

        # ── Drenar feedback residual ───────────────────────────────────────
        while feedback_queue:
            msg = feedback_queue.pop(0)
            feedback.pushInfo(msg)

        # ── Relatório final ────────────────────────────────────────────────

        elapsed = time.time() - t_start
        feedback.setProgress(100)
        feedback.pushInfo("=" * 60)
        feedback.pushInfo("RELATÓRIO FINAL")
        feedback.pushInfo("=" * 60)
        feedback.pushInfo(f"  Total encontrado      : {total}")
        feedback.pushInfo(f"  Válidos após filtros  : {total_valid}")
        feedback.pushInfo(f"  Processados (OK)      : {count_ok}")
        feedback.pushInfo(f"  Falhas                : {count_failed}")
        feedback.pushInfo(f"  Tempo total           : {elapsed:.1f}s")
        feedback.pushInfo(f"  Pool de processos     : {MAX_WORKERS} paralelos")
        feedback.pushInfo("=" * 60)

        self.logger.info(
            f"Otimização concluída. ok={count_ok}, falhas={count_failed}, "
            f"tempo={elapsed:.1f}s, workers={MAX_WORKERS}"
        )

        return {
            "PROCESSED": count_ok,
            "SKIPPED": total - total_valid,
            "FAILED": count_failed,
            "ELAPSED_SECONDS": round(elapsed, 1),
        }

    # ── _delete_overviews ──────────────────────────────────────────────────

    def _delete_overviews(self, raster_path, feedback):
        """
        Remove overviews internos do TIFF usando gdaladdo -clean.
        Também remove arquivo .ovr externo residual, se existir.
        """
        self.logger.debug(f"Limpando overviews existentes: {raster_path}")

        # Limpar overviews internos
        try:
            cmd = ["gdaladdo", "-clean", raster_path]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)  # nosec B603  # gdaladdo caminho fixo, sem shell=True
            feedback.pushInfo(
                f"  Overviews internos removidos: {os.path.basename(raster_path)}"
            )
            self.logger.debug(f"Overviews limpas: {raster_path}")
        except subprocess.CalledProcessError as e:
            self.logger.warning(
                f"Falha ao limpar overviews (pode ser ignorado): {e.stderr.strip()}"
            )
        except Exception as e:
            self.logger.warning(f"Erro ao limpar overviews: {e}")

        # Remover .ovr externo residual, se existir
        ovr_path = raster_path + ".ovr"
        if os.path.exists(ovr_path):
            try:
                os.remove(ovr_path)
                feedback.pushInfo(
                    f"  Arquivo externo .ovr residual removido: {os.path.basename(ovr_path)}"
                )
                self.logger.debug(f".ovr externo removido: {ovr_path}")
            except OSError as e:
                self.logger.warning(f"Não foi possível remover .ovr externo: {e}")
