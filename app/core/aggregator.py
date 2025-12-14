"""Agregación de tags desde múltiples archivos"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from ..models.tag_models import Tag, TagFile, TagAggregate
from .tag_parser import parse_line


class TagAggregator:
    """Agrega tags de múltiples archivos y mantiene conteos"""
    
    def __init__(self) -> None:
        self._aggregates: Dict[Tuple[str, str], TagAggregate] = {}
        self._files: Dict[Path, TagFile] = {}
    
    def add_file(self, file_path: Path, tags: List[Tag]) -> None:
        """
        Añade un archivo con sus tags al agregador
        
        Args:
            file_path: Ruta del archivo
            tags: Lista de tags encontrados en el archivo
        """
        tag_file = TagFile(path=file_path, tags=tags)
        self._files[file_path] = tag_file
        
        # Agregar cada tag
        for tag in tags:
            key = (tag.namespace, tag.tag)
            
            if key not in self._aggregates:
                self._aggregates[key] = TagAggregate(
                    namespace=tag.namespace,
                    tag=tag.tag
                )
            
            self._aggregates[key].add_occurrence(file_path)
    
    def get_aggregates(self) -> List[TagAggregate]:
        """
        Obtiene todos los agregados de tags
        
        Returns:
            Lista de TagAggregate ordenada por namespace y luego por tag
        """
        return sorted(
            self._aggregates.values(),
            key=lambda x: (x.namespace, x.tag)
        )
    
    def get_aggregates_by_namespace(self) -> Dict[str, List[TagAggregate]]:
        """
        Obtiene agregados agrupados por namespace
        
        Returns:
            Diccionario {namespace: [TagAggregate, ...]}
        """
        result: Dict[str, List[TagAggregate]] = defaultdict(list)
        
        for agg in self._aggregates.values():
            result[agg.namespace].append(agg)
        
        # Ordenar cada lista por tag
        for namespace in result:
            result[namespace].sort(key=lambda x: x.tag)
        
        return dict(result)
    
    def get_files(self) -> Dict[Path, TagFile]:
        """
        Obtiene todos los archivos procesados
        
        Returns:
            Diccionario {path: TagFile}
        """
        return self._files.copy()
    
    def clear(self) -> None:
        """Limpia todos los datos agregados"""
        self._aggregates.clear()
        self._files.clear()
    
    def get_file_paths_for_tag(self, namespace: str, tag: str) -> List[Path]:
        """
        Obtiene las rutas de archivos que contienen un tag específico
        
        Args:
            namespace: Namespace del tag
            tag: Texto del tag
            
        Returns:
            Lista de rutas de archivos
        """
        key = (namespace, tag)
        if key in self._aggregates:
            return sorted(list(self._aggregates[key].file_paths))
        return []
