# -*- coding: utf-8 -*-
"""
Ferramenta: Salvar, Fechar e Reabrir Projeto
Autor: Matheus Martinelli
Parte do plugin: Cadmus

Responsabilidades:
- UI: Exibir diálogos e mensagens via QgisMessageUtil
- Lógica de Projeto: Delegada a ProjectUtils
- Execução do Script: Gerenciada por _RestartExecutor
- Logging: Estruturado via LogUtilsNew
"""

import os
import subprocess
import tempfile
from typing import Optional

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QCoreApplication

from ..core.config.LogUtils import LogUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ProjectUtils import ProjectUtils

logger = LogUtils(tool="restart_qgis", class_name="RestartQGIS")



class _RestartExecutor:
    """Responsável pela execução do restart do QGIS.
    
    Separação de responsabilidades:
    - Criar script .bat
    - Executar script de forma segura
    - Gerenciar sinais Qt para fechar a aplicação
    """
    
    @staticmethod
    def get_qgis_executable() -> Optional[str]:
        """Obtém o executável real do QGIS diretamente do Qt.
        
        Returns:
            Caminho do executável ou None se não encontrado.
        """
        exe = QCoreApplication.applicationFilePath()
        if exe and os.path.exists(exe):
            logger.debug("QGIS executable found", qgis_exe=exe)
            return exe
        
        logger.warning("QGIS executable not found", exe=exe)
        return None
    
    @staticmethod
    def create_restart_script(project_path: str) -> Optional[str]:
        """Cria script .bat temporário para reabrir QGIS com o projeto.
        
        Args:
            project_path: Caminho completo do arquivo .qgz
            
        Returns:
            Caminho do script .bat ou None se falhar.
        """
        qgis_exec = _RestartExecutor.get_qgis_executable()
        if not qgis_exec:
            logger.error(
                "Cannot create restart script: QGIS executable not found",
                code="RESTART_NO_EXEC"
            )
            return None
        
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "restart_qgis.bat")
            
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("PING 127.0.0.1 -n 2 >NUL\n")
                f.write(f'start "" "{qgis_exec}" "{project_path}"\n')
            
            logger.info(
                "Restart script created",
                code="RESTART_SCRIPT_OK",
                bat_path=bat_path
            )
            return bat_path
            
        except Exception as e:
            logger.error(
                "Failed to create restart script",
                code="RESTART_SCRIPT_ERROR",
                error=str(e)
            )
            return None
    
    @staticmethod
    def execute_restart(bat_path: str) -> None:
        """Executa o script .bat e fecha a aplicação QGIS.
        
        Args:
            bat_path: Caminho do script .bat a executar.
        """
        def _run_script():
            try:
                subprocess.Popen(bat_path, shell=True)
                logger.info(
                    "Restart script executed",
                    code="RESTART_EXECUTED",
                    bat_path=bat_path
                )
            except Exception as e:
                logger.critical(
                    "Failed to execute restart script",
                    code="RESTART_EXEC_ERROR",
                    error=str(e)
                )
        
        app = QCoreApplication.instance()
        app.aboutToQuit.connect(_run_script)
        logger.info("Restart queued: will execute on QGIS shutdown", code="RESTART_QUEUED")


def run_restart_qgis(iface) -> None:
    """Fluxo principal: Salvar projeto, criar script restart e fechar QGIS.
    
    Responsabilidades delegadas:
    - ProjectUtils: Verificação de projeto salvo, save/write do projeto
    - QgisMessageUtil: Exibição de mensagens e diálogos UI
    - _RestartExecutor: Criação e execução do script de restart
    - logger: Logging estruturado de cada etapa
    
    Args:
        iface: QgisInterface do QGIS
    """
    project = QgsProject.instance()
    project_path = project.fileName()
    
    logger.info("Restart QGIS initiated", code="RESTART_START", project_path=project_path or "<unsaved>")
    
    # 1) Verificar se o projeto está salvo
    if not project_path:
        logger.warning("Project not saved, asking user to save", code="RESTART_NO_SAVE")
        
        # Usar QgisMessageUtil para diálogo
        save_now = QgisMessageUtil.confirm(
            iface,
            (
                "O projeto ainda não foi salvo.\n\n"
                "Para reiniciar o QGIS, é necessário salvar o arquivo.\n"
                "Deseja salvar agora?"
            ),
            title="Projeto não salvo"
        )
        
        if not save_now:
            logger.info("User cancelled restart", code="RESTART_CANCELLED_NO_SAVE")
            QgisMessageUtil.bar_warning(
                iface,
                "Sem salvar o projeto, o QGIS não pode ser reaberto automaticamente.",
                title="Ação cancelada"
            )
            return
        
        # Solicitar caminho do arquivo
        save_path, _ = iface.getSaveFileName(
            iface.mainWindow(),
            "Salvar Projeto",
            "",
            "Projetos QGIS (*.qgz)"
        )
        
        if not save_path:
            logger.info("User cancelled save dialog", code="RESTART_CANCELLED_SAVE_DIALOG")
            return
        
        # Usar ProjectUtils para salvar (delegação de responsabilidade)
        try:
            project.write(save_path)
            project_path = save_path
            logger.info("Project saved successfully", code="RESTART_SAVED", path=save_path)
        except Exception as e:
            logger.error("Failed to save project", code="RESTART_SAVE_ERROR", error=str(e))
            QgisMessageUtil.modal_error(
                iface,
                f"Erro ao salvar projeto: {str(e)}",
                title="Erro"
            )
            return
    
    # 2) Gravar alterações antes de fechar
    try:
        project.write(project_path)
        logger.info("Project changes saved", code="RESTART_CHANGES_SAVED", path=project_path)
    except Exception as e:
        logger.error("Failed to save project changes", code="RESTART_SAVE_CHANGES_ERROR", error=str(e))
        QgisMessageUtil.modal_error(
            iface,
            f"Erro ao salvar alterações: {str(e)}",
            title="Erro"
        )
        return
    
    # 3) Criar script .bat para reabrir QGIS
    bat_path = _RestartExecutor.create_restart_script(project_path)
    
    if not bat_path:
        logger.critical(
            "Cannot restart: failed to create restart script",
            code="RESTART_NO_SCRIPT"
        )
        QgisMessageUtil.modal_error(
            iface,
            "Não foi possível encontrar o executável do QGIS.\n"
            "O reinício automático não será executado.",
            title="Erro"
        )
        return
    
    # 4) Executar restart
    logger.info("Executing restart sequence", code="RESTART_EXECUTING", bat_path=bat_path)
    _RestartExecutor.execute_restart(bat_path)
    
    # 5) Fechar QGIS
    logger.info("Closing QGIS to start restart", code="RESTART_CLOSING")
    QgisMessageUtil.bar_info(
        iface,
        "QGIS será reiniciado em alguns segundos...",
        title="Reiniciando",
        duration=2
    )
    iface.mainWindow().close()