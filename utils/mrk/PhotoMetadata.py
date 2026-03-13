# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from PIL import Image, ExifTags
from PyQt5.QtCore import QVariant
from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey

TOOL_KEY = ToolKey.DRONE_COORDINATES


class PhotoMetadata:
    FIELDS_PHOTO = {
            "nome_arq":QVariant.String,
            "tam_mb":QVariant.Double,
            "tipo_arq":QVariant.String,

            # datas texto
            "dt_criacao":QVariant.String,
            "dt_full":QVariant.String,
            "dt_date":QVariant.String,
            "dt_time":QVariant.String,

            "cam_model":QVariant.String,
            "bit_depth":QVariant.Int,
            "larg_px":QVariant.Int,
            "alt_px":QVariant.Int,
            "res_h_dpi":QVariant.Double,
            "res_v_dpi":QVariant.Double,
            "focal_mm":QVariant.Double,
            "focal35mm":QVariant.Int,
            "iso":QVariant.Int,
            "abert_f":QVariant.Double,
    }


    # DJI_20251107021601_0002_V.JPG
    DJI_RE = re.compile(r"_(\d{4})_[A-Z]\.JPG$", re.IGNORECASE)
    @staticmethod
    def _format_dates(dt):
        """
        Recebe datetime e devolve strings padronizadas
        """
        return {
            "dt_criacao": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "dt_full": dt.strftime("%Y%m%d%H%M"),
            "dt_date": dt.strftime("%Y%m%d"),
            "dt_time": dt.strftime("%H%M"),
        }


    @staticmethod
    def enrich(points, base_folder, recursive=True, mrk_folder=None):
        logger = LogUtils(tool=TOOL_KEY, class_name="PhotoMetadata")
        logger.info("Iniciando enriquecimento de metadados de fotos", code="PHOTO_ENRICH_START", data={
            "base_folder": base_folder,
            "recursive": recursive,
            "mrk_folder": mrk_folder,
            "total_points": len(points),
            "pontos_com_mrk_folder": sum(1 for p in points if p.get("mrk_folder"))
        })

        # 🔴 PROCESSAMENTO POR PASTA: agrupar pontos por sua pasta de origem (mrk_folder)
        # Isso evita conflito de numeração quando há múltiplos voos com números iguais
        points_by_folder = {}
        for p in points:
            # Se o ponto tem mrk_folder, usar; senão usar base_folder
            folder = p.get("mrk_folder") or base_folder
            if folder not in points_by_folder:
                points_by_folder[folder] = []
            points_by_folder[folder].append(p)

        logger.info("Pontos agrupados por pasta", code="PHOTO_GROUPING", data={
            "total_folders": len(points_by_folder),
            "folder_distribution": {f: len(pts) for f, pts in list(points_by_folder.items())[:5]}
        })

        success_count = 0
        partial_count = 0
        failed_count = 0
        missing_count = 0
        
        # Processar cada grupo de pontos com sua pasta correspondente
        for folder, folder_points in points_by_folder.items():
            logger.info(f"Processando grupo de fotos", code="PHOTO_FOLDER_PROCESSING", data={
                "folder": folder,
                "point_count": len(folder_points)
            })
            
            # Indexar fotos APENAS dessa pasta (não recursivamente para evitar conflito)
            photo_index = PhotoMetadata._index_photos(folder, recursive=False)
            
            logger.info(f"Fotos indexadas para pasta", code="PHOTO_INDEX_COMPLETE", data={
                "folder": folder,
                "total_indexed": len(photo_index),
                "sample_keys": list(photo_index.keys())[:5] if photo_index else []
            })
            
            # Enriquecer os pontos desse grupo
            for i, p in enumerate(folder_points):
                foto = p.get("foto")
                if foto is None:
                    continue

                key = f"{int(foto):04d}"
                meta = photo_index.get(key)

                if not meta:
                    missing_count += 1
                    logger.debug(f"Foto não encontrada no índice", code="PHOTO_MATCH_FAILED", data={
                        "folder": folder,
                        "foto_numero": foto,
                        "chave_buscada": key
                    })
                    continue

                # Verificar quantos campos EXIF foram preenchidos
                exif_fields = ["cam_model", "iso", "focal_mm", "focal35mm", "abert_f", "bit_depth", "larg_px", "alt_px"]
                exif_filled = sum(1 for f in exif_fields if meta.get(f) is not None)
                
                if exif_filled >= 5:  # Sucesso: 5+ campos EXIF preenchidos
                    success_count += 1
                    logger.debug(f"Metadata enriquecida com sucesso", code="PHOTO_MATCH_SUCCESS", data={
                        "folder": folder,
                        "foto_numero": foto,
                        "foto_encontrada": meta.get("nome_arq"),
                        "campos_exif_preenchidos": exif_filled,
                        "camera_model": meta.get("cam_model")
                    })
                elif exif_filled >= 1:  # Sucesso parcial: 1-4 campos EXIF
                    partial_count += 1
                    logger.debug(f"Metadata enriquecida parcialmente", code="PHOTO_MATCH_PARTIAL", data={
                        "folder": folder,
                        "foto_numero": foto,
                        "foto_encontrada": meta.get("nome_arq"),
                        "campos_exif_preenchidos": exif_filled
                    })
                else:  # Falha: apenas filesystem, sem EXIF
                    failed_count += 1
                    logger.warning(f"Falha ao extrair EXIF de foto", code="PHOTO_EXIF_FAILED", data={
                        "folder": folder,
                        "foto_numero": foto,
                        "foto_encontrada": meta.get("nome_arq"),
                        "fallback": "filesystem_only"
                    })
                
                p.update(meta)

        # Estatísticas finais
        taxa_sucesso = (success_count / len(points) * 100) if points else 0
        logger.info("Enriquecimento de metadados concluído", code="PHOTO_ENRICH_COMPLETE", data={
            "total_points": len(points),
            "matched_success": success_count,
            "matched_partial": partial_count,
            "matched_failed": failed_count,
            "not_found": missing_count,
            "taxa_sucesso_percent": round(taxa_sucesso, 1),
            "resumo": f"✓ {success_count} (sucesso) + ⚠ {partial_count} (parcial) + ✗ {failed_count} (falha) + — {missing_count} (não encontrada)"
        })
        
        return points

    # --------------------------------------------------

    @staticmethod
    def _index_photos(base_folder, recursive):
        index = {}
        logger = LogUtils(tool=ToolKey.DRONE_COORDINATES, class_name="PhotoMetadata")

        logger.info("Iniciando indexação de fotos", code="PHOTO_INDEXING_START", data={
            "base_folder": base_folder,
            "recursive": recursive
        })

        walker = os.walk(base_folder) if recursive else [
            (base_folder, [], os.listdir(base_folder))
        ]

        # Contar quantos arquivos JPG teremos para calcular percentual
        all_files = []
        for root, _, files in walker:
            for fname in files:
                if fname.lower().endswith(".jpg") and PhotoMetadata.DJI_RE.search(fname):
                    all_files.append((root, fname))
        
        logger.info(f"Fotos identificadas", code="PHOTO_FILES_FOUND", data={
            "total_jpg_files": len(all_files),
            "amostra_nomes": [f[1] for f in all_files[:5]]
        })
        
        total = len(all_files)
        if total == 0:
            logger.warning("Nenhum arquivo JPG encontrado", code="PHOTO_INDEXING_EMPTY")
            return index

        next_log = 0.05  # 5%
        exif_success = 0
        exif_failed = 0

        for i, (root, fname) in enumerate(all_files, start=1):
            m = PhotoMetadata.DJI_RE.search(fname)
            if not m:
                continue

            num = m.group(1)
            path = os.path.join(root, fname)

            try:
                st = os.stat(path)
            except Exception as e:
                logger.debug(f"Erro ao acessar arquivo", code="PHOTO_STAT_ERROR", data={
                    "arquivo": fname,
                    "caminho": path,
                    "erro": str(e)
                })
                continue

            # datas etc...
            dt = datetime.fromtimestamp(st.st_ctime)
            dates = PhotoMetadata._format_dates(dt)

            meta = {
                "nome_arq": fname,
                "tipo_arq": os.path.splitext(fname)[1].upper(),
                "tam_mb": round(st.st_size / (1024 * 1024), 2),
                **dates,
                "cam_model": None,
                "bit_depth": None,
                "larg_px": None,
                "alt_px": None,
                "res_h_dpi": None,
                "res_v_dpi": None,
                "focal_mm": None,
                "focal35mm": None,
                "iso": None,
                "abert_f": None,
            }

            # EXIF
            exif_error = None
            try:
                with Image.open(path) as img:
                    exif_raw = img._getexif() or {}
                    exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
                    meta["larg_px"], meta["alt_px"] = img.size
                    dpi = img.info.get("dpi")
                    if dpi:
                        meta["res_h_dpi"] = float(dpi[0])
                        meta["res_v_dpi"] = float(dpi[1])
                    meta["bit_depth"] = img.bits if hasattr(img, "bits") else None
                    meta["cam_model"] = exif.get("Model")
                    meta["iso"] = exif.get("ISOSpeedRatings")
                    fl = exif.get("FocalLength")
                    if isinstance(fl, tuple):
                        meta["focal_mm"] = round(fl[0] / fl[1], 2)
                    elif fl is not None:
                        meta["focal_mm"] = float(fl)
                    meta["focal35mm"] = exif.get("FocalLengthIn35mmFilm")
                    av = exif.get("MaxApertureValue") or exif.get("FNumber")
                    if isinstance(av, tuple):
                        meta["abert_f"] = round(av[0] / av[1], 2)
                    elif av is not None:
                        meta["abert_f"] = round(float(av), 2)
                    
                    exif_success += 1
                    logger.debug(f"EXIF extraído com sucesso", code="PHOTO_EXIF_SUCCESS", data={
                        "numero_sequencial": num,
                        "arquivo": fname,
                        "camera": meta.get("cam_model"),
                        "resolucao": f"{meta.get('larg_px')}x{meta.get('alt_px')}",
                        "iso": meta.get("iso"),
                        "apertura": meta.get("abert_f")
                    })
                    
            except Exception as e:
                exif_failed += 1
                exif_error = str(e)
                logger.debug(f"Falha ao extrair EXIF", code="PHOTO_EXIF_ERROR", data={
                    "numero_sequencial": num,
                    "arquivo": fname,
                    "caminho": path,
                    "erro_tipo": type(e).__name__,
                    "erro_msg": exif_error[:100]
                })

            index[num] = meta

            # LOG A CADA 5%
            percent_done = i / total
            if percent_done >= next_log:
                logger.info(f"Progresso de indexação", code="PHOTO_INDEXING_PROGRESS", data={
                    "percentual": int(percent_done*100),
                    "arquivos_processados": i,
                    "total_arquivos": total,
                    "exif_sucesso": exif_success,
                    "exif_falha": exif_failed
                })
                next_log += 0.05  # próximo 5%

        # Resumo final
        logger.info(f"Indexação concluída", code="PHOTO_INDEXING_COMPLETE", data={
            "total_fotos_indexadas": len(index),
            "exif_extraido_com_sucesso": exif_success,
            "exif_falhou": exif_failed,
            "taxa_exif_sucesso_percent": round((exif_success / max(total, 1)) * 100, 1)
        })

        return index
