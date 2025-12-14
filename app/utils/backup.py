"""Utilidades para crear backups de archivos"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from .logger import get_logger

logger = get_logger(__name__)


def create_backup(files: List[Path], base_directory: Path) -> Path:
    """
    Crea un backup con timestamp de los archivos especificados
    
    Args:
        files: Lista de archivos a respaldar
        base_directory: Directorio base donde crear el backup
        
    Returns:
        Ruta del directorio de backup creado
    """
    if not files:
        raise ValueError("No hay archivos para respaldar")
    
    # Crear nombre de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_directory / f"backup_{timestamp}"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creando backup en: {backup_dir}")
    
    # Copiar cada archivo manteniendo estructura relativa
    for file_path in files:
        try:
            # Calcular ruta relativa desde el directorio base
            try:
                rel_path = file_path.relative_to(base_directory)
            except ValueError:
                # Si el archivo no está dentro del directorio base, usar solo el nombre
                rel_path = Path(file_path.name)
            
            backup_file_path = backup_dir / rel_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_file_path)
            logger.debug(f"Respaldado: {file_path} -> {backup_file_path}")
        
        except Exception as e:
            logger.error(f"Error al respaldar {file_path}: {e}")
            raise
    
    logger.info(f"Backup completado: {len(files)} archivos respaldados")
    return backup_dir
