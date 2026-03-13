# -*- coding: utf-8 -*-
"""
DependenciesManager - Gerencia dependências externas (bibliotecas Python)

Responsável por:
- Verificar se módulos estão instalados
- Oferecer instalação automática via scripts .cmd/.bat
- Validação de dependências antes de processos
"""

import os
import subprocess
from pathlib import Path


class DependenciesManager:
    """Gerencia validação e instalação de dependências externas."""
    
    # Mapeamento de dependências: nome_requerimento -> (módulo_import, script_instalação)
    DEPENDENCIES = {
        'PyPDF2': {
            'import': 'PyPDF2',
            'script': 'install_pypdf2.bat',
            'description': 'Unir/mesclar arquivos PDF',
            'pip': 'PyPDF2'
        },
        'Pillow': {
            'import': 'PIL',
            'script': 'install_pillow.cmd',
            'description': 'Processar e converter imagens (PNG)',
            'pip': 'Pillow'
        }
    }
    
    @staticmethod
    def check_dependency(dependency_name: str) -> bool:
        """
        Verifica se uma dependência está instalada.
        
        Parameters
        ----------
        dependency_name : str
            Nome da dependência (ex: 'PyPDF2', 'Pillow')
        
        Returns
        -------
        bool
            True se instalada, False caso contrário
        
        Example
        -------
        if not DependenciesManager.check_dependency('PyPDF2'):
            print("PyPDF2 não está instalada")
        """
        if dependency_name not in DependenciesManager.DEPENDENCIES:
            return False
        
        dep_info = DependenciesManager.DEPENDENCIES[dependency_name]
        module_name = dep_info['import']
        
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_dependency_info(dependency_name: str) -> dict:
        """
        Retorna informações sobre uma dependência.
        
        Returns
        -------
        dict
            Dicionário com 'import', 'script', 'description', 'pip'
        """
        return DependenciesManager.DEPENDENCIES.get(dependency_name, {})
    
    @staticmethod
    def get_install_script_path(dependency_name: str) -> str:
        """
        Retorna caminho completo do script de instalação.
        
        Parameters
        ----------
        dependency_name : str
            Nome da dependência (ex: 'PyPDF2', 'Pillow')
        
        Returns
        -------
        str
            Caminho do script .cmd/.bat (ou vazio se não encontrado)
        """
        if dependency_name not in DependenciesManager.DEPENDENCIES:
            return ""
        
        dep_info = DependenciesManager.DEPENDENCIES[dependency_name]
        script_name = dep_info['script']
        
        # Procurar em caminhos padrão
        possible_paths = [
            # Relativo ao arquivo atual
            os.path.join(os.path.dirname(__file__), '..', 'core', 'lib', script_name),
            # Relativo ao projeto
            os.path.join(os.path.dirname(__file__), script_name),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        
        return ""
    
    @staticmethod
    def install_dependency(dependency_name: str) -> bool:
        """
        Tenta instalar uma dependência executando o script .cmd/.bat.
        
        Parameters
        ----------
        dependency_name : str
            Nome da dependência (ex: 'PyPDF2', 'Pillow')
        
        Returns
        -------
        bool
            True se instalação foi bem-sucedida, False caso contrário
        
        Example
        -------
        success = DependenciesManager.install_dependency('PyPDF2')
        if success:
            print("PyPDF2 instalada com sucesso")
        """
        script_path = DependenciesManager.get_install_script_path(dependency_name)
        
        if not script_path:
            return False
        
        try:
            subprocess.Popen([script_path], shell=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_dependencies(required_dependencies: list) -> dict:
        """
        Valida múltiplas dependências de uma vez.
        
        Parameters
        ----------
        required_dependencies : list
            Lista de nomes de dependências (ex: ['PyPDF2', 'Pillow'])
        
        Returns
        -------
        dict
            {
                'all_present': bool,  # True se todas instaladas
                'missing': [],         # Dependências faltantes
                'present': []          # Dependências presentes
            }
        
        Example
        -------
        result = DependenciesManager.validate_dependencies(['PyPDF2', 'Pillow'])
        if not result['all_present']:
            print(f"Faltam: {result['missing']}")
        """
        missing = []
        present = []
        
        for dep_name in required_dependencies:
            if DependenciesManager.check_dependency(dep_name):
                present.append(dep_name)
            else:
                missing.append(dep_name)
        
        return {
            'all_present': len(missing) == 0,
            'missing': missing,
            'present': present
        }
