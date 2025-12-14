"""Utilidades para manejo de rutas y búsqueda de archivos"""

from pathlib import Path
from typing import List, Optional


def find_txt_files(
    directory: Path,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[Path]:
    """
    Encuentra recursivamente todos los archivos .txt en un directorio
    
    Args:
        directory: Directorio raíz para buscar
        include_patterns: Patrones de inclusión (no implementado aún)
        exclude_patterns: Patrones de exclusión (no implementado aún)
        
    Returns:
        Lista de rutas de archivos .txt encontrados
    """
    if not directory.exists() or not directory.is_dir():
        return []
    
    txt_files = []
    
    for file_path in directory.rglob("*.txt"):
        if file_path.is_file():
            txt_files.append(file_path)
    
    return sorted(txt_files)
