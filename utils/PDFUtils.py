# -*- coding: utf-8 -*-
"""
PDFUtils - Utilitários para manipulação de PDFs e imagens

Responsável por:
- Merger de PDFs (PyPDF2)
- Merger de PNGs para PDF (Pillow)
- Logging detalhado de todas operações
"""

import os
from ..core.config.LogUtils import LogUtils
from .DependenciesManager import DependenciesManager


class PDFUtils:
    """Utilitários para manipulação de PDFs e conversão de imagens."""
    
    # Instância do logger
    _logger = None
    
    @classmethod
    def _get_logger(cls):
        """Retorna instância do logger."""
        if cls._logger is None:
            try:
                cls._logger = LogUtils(tool="pdf_utils", class_name="PDFUtils", level=LogUtils.DEBUG)
            except Exception as e:
                # Fallback: criar logger simples se falhar
                import sys
                class SimpleLogger:
                    def debug(self, msg):
                        print(f"[DEBUG] {msg}")
                    def info(self, msg):
                        print(f"[INFO] {msg}")
                    def warning(self, msg):
                        print(f"[WARNING] {msg}")
                    def error(self, msg):
                        print(f"[ERROR] {msg}")
                cls._logger = SimpleLogger()
        return cls._logger
    
    @staticmethod
    def merge_pdfs(pdf_list: list, output_pdf: str) -> tuple:
        """
        Mescla múltiplos arquivos PDF em um único arquivo.
        
        Parameters
        ----------
        pdf_list : list
            Lista de caminhos para arquivos PDF
        
        output_pdf : str
            Caminho do arquivo PDF de saída
        
        Returns
        -------
        tuple:
            (success: bool, message: str)
        
        Example
        -------
        success, message = PDFUtils.merge_pdfs(
            ['/path/file1.pdf', '/path/file2.pdf'],
            '/path/output.pdf'
        )
        """
        logger = PDFUtils._get_logger()
        
        try:
            # Validação de dependência
            if not DependenciesManager.check_dependency('PyPDF2'):
                msg = "PyPDF2 não está instalada"
                logger.error(msg)
                return False, msg
            
            if not pdf_list:
                msg = "Nenhum PDF foi informado para união"
                logger.warning(msg)
                return False, msg
            
            logger.debug(f"Iniciando merge de {len(pdf_list)} PDFs")
            
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            pdfs_adicionados = 0
            
            for pdf in pdf_list:
                if os.path.exists(pdf):
                    logger.debug(f"Adicionando PDF: {pdf}")
                    merger.append(pdf)
                    pdfs_adicionados += 1
                else:
                    logger.warning(f"Arquivo PDF não encontrado: {pdf}")
            
            if pdfs_adicionados == 0:
                msg = "Nenhum arquivo PDF válido foi encontrado"
                logger.error(msg)
                return False, msg
            
            logger.debug(f"Criando diretório de saída (se necessário): {os.path.dirname(output_pdf)}")
            os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
            
            logger.debug(f"Escribendo PDF final em: {output_pdf}")
            merger.write(output_pdf)
            merger.close()
            
            msg = f"PDF final criado em: {output_pdf}"
            logger.info(f"✓ {msg}")
            return True, msg
        
        except ImportError as ie:
            msg = f"Erro de importação PyPDF2: {str(ie)}"
            logger.error(msg)
            return False, msg
        
        except Exception as e:
            msg = f"Erro ao mesclar PDFs: {str(e)}"
            logger.error(msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, msg
    
    @staticmethod
    def merge_pngs_to_pdf(png_list: list, output_pdf: str, max_width: int = 3500) -> tuple:
        """
        Mescla múltiplas imagens PNG em um arquivo PDF.
        
        Parameters
        ----------
        png_list : list
            Lista de caminhos para arquivos PNG
        
        output_pdf : str
            Caminho do arquivo PDF de saída
        
        max_width : int
            Largura máxima em pixels (redimensiona se necessário)
        
        Returns
        -------
        tuple:
            (success: bool, message: str)
        
        Example
        -------
        success, message = PDFUtils.merge_pngs_to_pdf(
            ['/path/img1.png', '/path/img2.png'],
            '/path/output.pdf',
            max_width=3500
        )
        """
        logger = PDFUtils._get_logger()
        
        try:
            # Validação de dependência
            if not DependenciesManager.check_dependency('Pillow'):
                msg = "Pillow não está instalada"
                logger.error(msg)
                return False, msg
            
            if not png_list:
                msg = "Nenhum PNG foi informado para união"
                logger.warning(msg)
                return False, msg
            
            logger.debug(f"Iniciando merge de {len(png_list)} PNGs em PDF (max_width={max_width}px)")
            
            from PIL import Image
            
            pil_images = []
            pngs_processados = 0
            
            for i, path in enumerate(png_list, 1):
                if not os.path.exists(path):
                    logger.warning(f"Arquivo PNG não encontrado: {path}")
                    continue
                
                logger.debug(f"Processando PNG {i}/{len(png_list)}: {path}")
                
                try:
                    img = Image.open(path).convert("RGB")
                    w, h = img.size
                    logger.debug(f"  Dimensões originais: {w}x{h}px")
                    
                    if w > max_width:
                        logger.debug(f"  Redimensionando: largura {w} > max_width {max_width}")
                        ratio = max_width / float(w)
                        new_h = int(h * ratio)
                        img = img.resize((max_width, new_h), Image.LANCZOS)
                        logger.debug(f"  Novas dimensões: {max_width}x{new_h}px")
                    
                    pil_images.append(img)
                    pngs_processados += 1
                
                except Exception as e:
                    logger.warning(f"Erro ao processar PNG {path}: {str(e)}")
                    continue
            
            if not pil_images:
                msg = "Nenhuma imagem PNG válida foi encontrada"
                logger.error(msg)
                return False, msg
            
            logger.debug(f"Total de imagens processadas: {pngs_processados}/{len(png_list)}")
            
            logger.debug(f"Criando diretório de saída (se necessário): {os.path.dirname(output_pdf)}")
            os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
            
            logger.debug(f"Salvando PDF final em: {output_pdf}")
            first, rest = pil_images[0], pil_images[1:]
            first.save(output_pdf, save_all=True, append_images=rest)
            
            msg = f"PDF unido a partir de {pngs_processados} PNG(s) criado em: {output_pdf}"
            logger.info(f"✓ {msg}")
            return True, msg
        
        except ImportError as ie:
            msg = f"Erro de importação PIL: {str(ie)}"
            logger.error(msg)
            return False, msg
        
        except Exception as e:
            msg = f"Erro ao mesclar PNGs: {str(e)}"
            logger.error(msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, msg
