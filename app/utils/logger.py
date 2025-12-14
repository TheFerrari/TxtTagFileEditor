"""Configuración de logging para la aplicación"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


_logger: Optional[logging.Logger] = None


def setup_logger(log_dir: Path = None) -> logging.Logger:
    """
    Configura el logger de la aplicación
    
    Args:
        log_dir: Directorio para archivos de log (por defecto logs/ en el proyecto)
        
    Returns:
        Logger configurado
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    if log_dir is None:
        # Directorio del proyecto
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "tag_editor.log"
    
    # Crear logger
    logger = logging.getLogger("TagEditor")
    logger.setLevel(logging.DEBUG)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo (rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _logger = logger
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtiene un logger (configura si es necesario)
    
    Args:
        name: Nombre del logger (opcional)
        
    Returns:
        Logger
    """
    if _logger is None:
        setup_logger()
    
    if name:
        return logging.getLogger(f"TagEditor.{name}")
    return _logger or logging.getLogger("TagEditor")
