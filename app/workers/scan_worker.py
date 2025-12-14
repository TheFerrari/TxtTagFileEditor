"""Worker para escanear archivos .txt en background"""

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QThread, Signal

from ..core.tag_parser import parse_line
from ..models.tag_models import Tag, TagFile
from ..utils.logger import get_logger
from ..utils.path_utils import find_txt_files

logger = get_logger(__name__)


class ScanWorker(QThread):
    """Worker thread para escanear archivos .txt y extraer tags"""
    
    # Señales
    progress = Signal(int, int)  # current, total
    file_processed = Signal(str, int)  # file_path (str), tag_count
    finished = Signal(object)  # {path: TagFile} - usar object para dict
    error = Signal(str)  # error_message
    
    def __init__(self, directory: Path, parent=None):
        """
        Inicializa el worker
        
        Args:
            directory: Directorio a escanear
            parent: Widget padre
        """
        super().__init__(parent)
        self.directory = directory
        self._cancelled = False
    
    def cancel(self) -> None:
        """Cancela el escaneo"""
        self._cancelled = True
    
    def run(self) -> None:
        """Ejecuta el escaneo"""
        try:
            logger.info(f"Iniciando escaneo de directorio: {self.directory}")
            
            # Encontrar todos los archivos .txt
            txt_files = find_txt_files(self.directory)
            
            if not txt_files:
                logger.warning("No se encontraron archivos .txt")
                self.finished.emit({})
                return
            
            total_files = len(txt_files)
            logger.info(f"Encontrados {total_files} archivos .txt")
            
            files_data: Dict[Path, TagFile] = {}
            
            for idx, file_path in enumerate(txt_files):
                if self._cancelled:
                    logger.info("Escaneo cancelado por el usuario")
                    break
                
                try:
                    tag_file = self._process_file(file_path)
                    if tag_file:
                        files_data[file_path] = tag_file
                        self.file_processed.emit(str(file_path), len(tag_file.tags))
                
                except Exception as e:
                    logger.error(f"Error procesando {file_path}: {e}")
                    self.error.emit(f"Error en {file_path.name}: {str(e)}")
                
                self.progress.emit(idx + 1, total_files)
            
            logger.info(f"Escaneo completado: {len(files_data)} archivos procesados")
            self.finished.emit(files_data)
        
        except Exception as e:
            logger.error(f"Error en escaneo: {e}", exc_info=True)
            self.error.emit(f"Error fatal: {str(e)}")
            self.finished.emit({})
    
    def _process_file(self, file_path: Path) -> Optional[TagFile]:
        """
        Procesa un archivo .txt y extrae sus tags
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            TagFile con los tags encontrados o None si hay error
        """
        try:
            # Detectar line endings
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                content = f.read()
            
            # Detectar line endings
            if '\r\n' in content:
                line_ending = '\r\n'
            elif '\r' in content:
                line_ending = '\r'
            else:
                line_ending = '\n'
            
            lines = content.splitlines()
            tags: List[Tag] = []
            
            for line in lines:
                parsed = parse_line(line)
                if parsed:
                    namespace, tag = parsed
                    tags.append(Tag(namespace=namespace, tag=tag))
            
            tag_file = TagFile(path=file_path, tags=tags, line_endings=line_ending)
            logger.debug(f"Procesado {file_path}: {len(tags)} tags")
            
            return tag_file
        
        except UnicodeDecodeError:
            # Intentar con Latin-1 como fallback
            logger.warning(f"Error de codificación UTF-8 en {file_path}, intentando Latin-1")
            try:
                with open(file_path, 'r', encoding='latin-1', newline='') as f:
                    content = f.read()
                
                if '\r\n' in content:
                    line_ending = '\r\n'
                elif '\r' in content:
                    line_ending = '\r'
                else:
                    line_ending = '\n'
                
                lines = content.splitlines()
                tags: List[Tag] = []
                
                for line in lines:
                    parsed = parse_line(line)
                    if parsed:
                        namespace, tag = parsed
                        tags.append(Tag(namespace=namespace, tag=tag))
                
                tag_file = TagFile(path=file_path, tags=tags, line_endings=line_ending)
                logger.debug(f"Procesado {file_path} (Latin-1): {len(tags)} tags")
                
                return tag_file
            
            except Exception as e:
                logger.error(f"Error procesando {file_path} con Latin-1: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            raise
