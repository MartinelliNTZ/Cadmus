# -*- coding: utf-8 -*-
"""
DependenciesManager - Gerencia dependências externas (bibliotecas Python)

Responsável por:
- Verificar se módulos estão instalados
- Instalar bibliotecas via pip sem scripts externos
- Validar dependências antes de processos
"""

import importlib
import shutil
import sys
from pathlib import Path
from qgis.PyQt.QtCore import QProcess
from qgis.PyQt.QtWidgets import QProgressDialog
from ..core.config.LogUtils import LogUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..i18n.TranslationManager import STR
from .BaseUtil import BaseUtil


class DependenciesManager(BaseUtil):
    """Gerencia validação e instalação de dependências externas."""

    _active_processes = []

    DEPENDENCIES = {
        "PyPDF2": {
            "import": "PyPDF2",
            "description": "Unir/mesclar arquivos PDF",
            "pip": "PyPDF2",
        },
        "Pillow": {
            "import": "PIL",
            "description": "Processar e converter imagens (PNG)",
            "pip": "Pillow",
        },
    }

    @staticmethod
    def _get_logger(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="DependenciesManager")

    @staticmethod
    def _get_dependency_config(
        dependency_name: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> dict:
        logger = DependenciesManager._get_logger(tool_key)
        dep_info = DependenciesManager.DEPENDENCIES.get(dependency_name)

        if dep_info:
            config = dict(dep_info)
            config["mapped"] = True
            logger.debug(
                "Dependência encontrada no mapeamento",
                code="DEPENDENCY_CONFIG_MAPPED",
                dependency_name=dependency_name,
                pip_name=config.get("pip"),
                import_name=config.get("import"),
            )
            return config

        logger.warning(
            "Dependência não mapeada; usando fallback direto para import e pip",
            code="DEPENDENCY_CONFIG_FALLBACK",
            dependency_name=dependency_name,
        )
        return {
            "import": dependency_name,
            "description": dependency_name,
            "pip": dependency_name,
            "mapped": False,
        }

    @staticmethod
    def _is_python_candidate(path_value: str) -> bool:
        if not path_value:
            return False

        path = Path(path_value)
        name = path.name.lower()
        return path.exists() and name.startswith("python") and name.endswith(".exe")

    @staticmethod
    def _find_python_executable(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> str:
        logger = DependenciesManager._get_logger(tool_key)
        current_executable = Path(sys.executable).resolve() if sys.executable else None
        candidates = []

        def _add_candidate(candidate):
            if not candidate:
                return
            candidate_str = str(candidate)
            if candidate_str not in candidates:
                candidates.append(candidate_str)

        if current_executable:
            logger.debug(
                "Executável atual do processo identificado",
                code="PYTHON_DISCOVERY_CURRENT_EXECUTABLE",
                current_executable=str(current_executable),
            )

            if DependenciesManager._is_python_candidate(str(current_executable)):
                _add_candidate(current_executable)
            else:
                logger.warning(
                    "Executável atual não parece ser python; tentando localizar interpretador real",
                    code="PYTHON_DISCOVERY_NON_PYTHON_EXECUTABLE",
                    current_executable=str(current_executable),
                )

            _add_candidate(current_executable.parent / "python.exe")
            _add_candidate(current_executable.parent / "python3.exe")
            _add_candidate(current_executable.parent.parent / "python.exe")
            _add_candidate(current_executable.parent.parent / "python3.exe")
            _add_candidate(current_executable.parent.parent / "bin" / "python.exe")

            for parent in current_executable.parents:
                apps_dir = parent / "apps"
                if apps_dir.exists():
                    for python_dir in sorted(apps_dir.glob("Python*")):
                        _add_candidate(python_dir / "python.exe")
                    _add_candidate(parent / "bin" / "python.exe")

        _add_candidate(Path(sys.exec_prefix) / "python.exe")
        _add_candidate(Path(sys.base_exec_prefix) / "python.exe")

        for command_name in ("python", "python3"):
            resolved = shutil.which(command_name)
            if resolved:
                _add_candidate(resolved)

        for candidate in candidates:
            logger.debug(
                "Verificando candidato de interpretador Python",
                code="PYTHON_DISCOVERY_CANDIDATE",
                candidate_path=candidate,
            )
            if DependenciesManager._is_python_candidate(candidate):
                logger.info(
                    "Interpretador Python encontrado para instalação de dependências",
                    code="PYTHON_DISCOVERY_SUCCESS",
                    python_executable=candidate,
                )
                return candidate

        logger.error(
            "Nenhum interpretador Python válido foi encontrado para instalar dependências",
            code="PYTHON_DISCOVERY_FAILED",
            sys_executable=str(current_executable) if current_executable else "",
            sys_exec_prefix=sys.exec_prefix,
            sys_base_exec_prefix=sys.base_exec_prefix,
        )
        return ""

    @staticmethod
    def get_dependency_info(
        dependency_name: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> dict:
        dep_info = DependenciesManager._get_dependency_config(dependency_name, tool_key)
        return {
            "import": dep_info["import"],
            "description": dep_info["description"],
            "pip": dep_info["pip"],
        }

    @staticmethod
    def check_dependency(
        dependency_name: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> bool:
        logger = DependenciesManager._get_logger(tool_key)
        dep_info = DependenciesManager._get_dependency_config(dependency_name, tool_key)
        module_name = dep_info["import"]

        logger.debug(
            "Verificando dependência",
            code="DEPENDENCY_CHECK_START",
            dependency_name=dependency_name,
            module_name=module_name,
        )

        try:
            importlib.import_module(module_name)
            logger.info(
                "Dependência encontrada",
                code="DEPENDENCY_PRESENT",
                dependency_name=dependency_name,
                module_name=module_name,
            )
            return True
        except ImportError as e:
            logger.warning(
                "Dependência ausente",
                code="DEPENDENCY_MISSING",
                dependency_name=dependency_name,
                module_name=module_name,
                error=str(e),
            )
            return False
        except Exception as e:
            logger.exception(
                e, code="DEPENDENCY_CHECK_ERROR", dependency_name=dependency_name
            )
            return False

    @staticmethod
    def install_dependency(
        dependency_name: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> bool:
        logger = DependenciesManager._get_logger(tool_key)
        dep_info = DependenciesManager._get_dependency_config(dependency_name, tool_key)
        pip_name = dep_info["pip"]
        python_exe = DependenciesManager._find_python_executable(tool_key)

        if not python_exe:
            logger.error(
                "Instalação cancelada por ausência de interpretador Python válido",
                code="INSTALL_DEPENDENCY_NO_PYTHON",
                dependency_name=dependency_name,
                pip_name=pip_name,
            )
            return False

        logger.info(
            "Iniciando instalação assíncrona de dependência via pip",
            code="INSTALL_DEPENDENCY_START",
            dependency_name=dependency_name,
            pip_name=pip_name,
            python_executable=python_exe,
        )

        try:
            started = QProcess.startDetached(
                python_exe,
                [
                    "-m",
                    "pip",
                    "install",
                    "--user",
                    "--disable-pip-version-check",
                    pip_name,
                ],
            )

            if isinstance(started, tuple):
                started = bool(started[0])
            else:
                started = bool(started)

            if started:
                logger.info(
                    "Processo de instalação iniciado",
                    code="INSTALL_DEPENDENCY_STARTED",
                    dependency_name=dependency_name,
                    pip_name=pip_name,
                    python_executable=python_exe,
                )
                return True

            logger.error(
                "Falha ao iniciar processo de instalação",
                code="INSTALL_DEPENDENCY_START_FAILED",
                dependency_name=dependency_name,
                pip_name=pip_name,
                python_executable=python_exe,
            )
            return False
        except Exception as e:
            logger.exception(
                e, code="INSTALL_DEPENDENCY_EXCEPTION", dependency_name=dependency_name
            )
            return False

    @staticmethod
    def install_dependency_gui(
        dependency_name: str, iface, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> bool:
        logger = DependenciesManager._get_logger(tool_key)
        dep_info = DependenciesManager._get_dependency_config(dependency_name, tool_key)
        pip_name = dep_info["pip"]
        python_exe = DependenciesManager._find_python_executable(tool_key)

        if not python_exe:
            logger.error(
                "Instalação GUI cancelada por ausência de interpretador Python válido",
                code="INSTALL_GUI_NO_PYTHON",
                dependency_name=dependency_name,
                pip_name=pip_name,
            )
            return False

        logger.info(
            "Preparando instalação GUI de dependência",
            code="INSTALL_GUI_START",
            dependency_name=dependency_name,
            pip_name=pip_name,
            python_executable=python_exe,
        )

        try:
            parent = iface.mainWindow() if iface else None
            progress = QProgressDialog(
                STR.INSTALLING_DEPENDENCY + " " + dep_info["description"],
                STR.CANCEL,
                0,
                0,
                parent,
            )
            progress.setWindowTitle(STR.INSTALLING_DEPENDENCIES)
            progress.setAutoClose(True)
            progress.setModal(True)
            progress.show()

            proc = QProcess(parent)
            DependenciesManager._active_processes.append(proc)

            def _cleanup_process():
                if proc in DependenciesManager._active_processes:
                    DependenciesManager._active_processes.remove(proc)
                    logger.debug(
                        "Processo removido da lista de processos ativos",
                        code="INSTALL_GUI_PROCESS_CLEANUP",
                        dependency_name=dependency_name,
                        active_processes=len(DependenciesManager._active_processes),
                    )

            def _on_finished(exit_code, exit_status):
                del exit_status
                progress.close()
                _cleanup_process()
                if exit_code == 0:
                    logger.info(
                        "Instalação GUI concluída com sucesso",
                        code="INSTALL_GUI_FINISHED_SUCCESS",
                        dependency_name=dependency_name,
                        pip_name=pip_name,
                    )
                    QgisMessageUtil.modal_info(
                        iface,
                        STR.DEPENDENCY
                        + " "
                        + dep_info["description"]
                        + " "
                        + STR.INSTALLED_SUCCESSFULLY,
                        STR.SUCCESS,
                    )
                else:
                    logger.error(
                        "Instalação GUI concluída com erro",
                        code="INSTALL_GUI_FINISHED_ERROR",
                        dependency_name=dependency_name,
                        pip_name=pip_name,
                        exit_code=exit_code,
                    )

            def _on_error(err):
                progress.close()
                _cleanup_process()
                logger.error(
                    "Erro ao iniciar instalação GUI",
                    code="INSTALL_GUI_PROCESS_ERROR",
                    dependency_name=dependency_name,
                    pip_name=pip_name,
                    qprocess_error=str(err),
                )

            proc.finished.connect(_on_finished)
            proc.errorOccurred.connect(_on_error)
            proc.start(
                python_exe,
                [
                    "-m",
                    "pip",
                    "install",
                    "--user",
                    "--disable-pip-version-check",
                    pip_name,
                ],
            )

            started = True
            if hasattr(proc, "waitForStarted"):
                started = proc.waitForStarted(3000)
            elif hasattr(proc, "state") and hasattr(QProcess, "NotRunning"):
                started = proc.state() != QProcess.NotRunning

            if not started:
                progress.close()
                _cleanup_process()
                logger.error(
                    "Processo GUI não iniciou",
                    code="INSTALL_GUI_NOT_STARTED",
                    dependency_name=dependency_name,
                    pip_name=pip_name,
                    python_executable=python_exe,
                )
                return False

            logger.info(
                "Processo GUI iniciado com sucesso",
                code="INSTALL_GUI_STARTED",
                dependency_name=dependency_name,
                pip_name=pip_name,
                python_executable=python_exe,
            )
            return True
        except Exception as e:
            logger.exception(
                e, code="INSTALL_GUI_EXCEPTION", dependency_name=dependency_name
            )
            return False

    @staticmethod
    def validate_dependencies(
        required_dependencies: list, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> dict:
        logger = DependenciesManager._get_logger(tool_key)
        logger.info(
            "Validando conjunto de dependências",
            code="VALIDATE_DEPENDENCIES_START",
            required_dependencies=required_dependencies,
            total_dependencies=len(required_dependencies),
        )

        missing = []
        present = []

        for dep_name in required_dependencies:
            if DependenciesManager.check_dependency(dep_name, tool_key):
                present.append(dep_name)
            else:
                missing.append(dep_name)

        result = {
            "all_present": len(missing) == 0,
            "missing": missing,
            "present": present,
        }

        logger.info(
            "Validação de dependências concluída",
            code="VALIDATE_DEPENDENCIES_FINISH",
            result=result,
        )
        return result
