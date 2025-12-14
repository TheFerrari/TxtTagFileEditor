"""Worker para aplicar cambios a archivos en background"""

from pathlib import Path
from typing import Dict, Set, Tuple, List

from PySide6.QtCore import QThread, Signal

from ..core.tag_parser import format_tag
from ..models.tag_models import Tag, TagFile
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ApplyWorker(QThread):
    """Worker thread para aplicar cambios (remover tags) a archivos"""
    
    # Señales
    progress = Signal(int, int)  # current, total
    file_processed = Signal(str, bool)  # file_path (str), modified
    finished = Signal(int, int)  # files_modified, tags_removed
    error = Signal(str)  # error_message
    
    def __init__(
        self,
        files_data: Dict[Path, TagFile],
        tags_to_remove: Set[tuple[str, str]],  # Set de (namespace, tag)
        parent=None
    ):
        """
        Inicializa el worker
        
        Args:
            files_data: Diccionario de archivos con sus tags
            tags_to_remove: Set de tuplas (namespace, tag) a remover
            parent: Widget padre
        """
        super().__init__(parent)
        self.files_data = files_data
        self.tags_to_remove = tags_to_remove
        self._cancelled = False
    
    def cancel(self) -> None:
        """Cancela la aplicación"""
        self._cancelled = True
    
    def run(self) -> None:
        """Ejecuta la aplicación de cambios"""
        try:
            logger.info(f"Aplicando cambios a {len(self.files_data)} archivos")
            logger.info(f"Tags a remover: {len(self.tags_to_remove)}")
            
            files_modified = 0
            total_tags_removed = 0
            total_files = len(self.files_data)
            
            for idx, (file_path, tag_file) in enumerate(self.files_data.items()):
                if self._cancelled:
                    logger.info("Aplicación cancelada por el usuario")
                    break
                
                try:
                    modified, tags_removed = self._process_file(file_path, tag_file)
                    
                    if modified:
                        files_modified += 1
                        total_tags_removed += tags_removed
                    
                    self.file_processed.emit(str(file_path), modified)
                
                except Exception as e:
                    logger.error(f"Error procesando {file_path}: {e}")
                    self.error.emit(f"Error en {file_path.name}: {str(e)}")
                
                self.progress.emit(idx + 1, total_files)
            
            logger.info(
                f"Aplicación completada: {files_modified} archivos modificados, "
                f"{total_tags_removed} tags removidos"
            )
            self.finished.emit(files_modified, total_tags_removed)
        
        except Exception as e:
            logger.error(f"Error en aplicación: {e}", exc_info=True)
            self.error.emit(f"Error fatal: {str(e)}")
            self.finished.emit(0, 0)
    
    def _process_file(
        self,
        file_path: Path,
        tag_file: TagFile
    ) -> Tuple[bool, int]:
        """
        Procesa un archivo y remueve los tags especificados
        
        Args:
            file_path: Ruta del archivo
            tag_file: TagFile con los tags originales
            
        Returns:
            Tupla (modified, tags_removed)
        """
        # Filtrar tags a mantener
        tags_to_keep: List[Tag] = []
        tags_removed = 0
        
        for tag in tag_file.tags:
            key = (tag.namespace, tag.tag)
            if key not in self.tags_to_remove:
                tags_to_keep.append(tag)
            else:
                tags_removed += 1
        
        # Si no hay cambios, no escribir
        if tags_removed == 0:
            return False, 0
        
        # Escribir archivo con tags restantes
        # Mantener orden original (solo remover los seleccionados)
        # Remover duplicados manteniendo orden
        seen = set()
        unique_tags = []
        for tag in tags_to_keep:
            key = (tag.namespace, tag.tag)
            if key not in seen:
                seen.add(key)
                unique_tags.append(tag)
        
        # Formatear líneas
        lines = []
        for tag in unique_tags:
            formatted = format_tag(tag.namespace, tag.tag)
            lines.append(formatted)
        
        # Escribir archivo
        content = tag_file.line_endings.join(lines)
        if lines:  # Si hay líneas, añadir line ending al final
            content += tag_file.line_endings
        
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            logger.debug(
                f"Archivo modificado {file_path}: {tags_removed} tags removidos, "
                f"{len(unique_tags)} tags restantes"
            )
            
            return True, tags_removed
        
        except Exception as e:
            logger.error(f"Error escribiendo {file_path}: {e}")
            raise
