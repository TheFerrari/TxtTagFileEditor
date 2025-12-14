"""Modelos de datos para tags y archivos"""

from dataclasses import dataclass, field
from typing import List, Set
from pathlib import Path


@dataclass
class Tag:
    """Representa un tag individual con su namespace"""
    namespace: str
    tag: str
    
    def __hash__(self) -> int:
        return hash((self.namespace, self.tag))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return False
        return self.namespace == other.namespace and self.tag == other.tag


@dataclass
class TagFile:
    """Representa un archivo .txt con sus tags"""
    path: Path
    tags: List[Tag] = field(default_factory=list)
    line_endings: str = "\n"  # Detectado del archivo original
    
    def add_tag(self, tag: Tag) -> None:
        """Añade un tag al archivo"""
        self.tags.append(tag)


@dataclass
class TagAggregate:
    """Agregado de un tag con su conteo y archivos donde aparece"""
    namespace: str
    tag: str
    count: int = 0
    file_paths: Set[Path] = field(default_factory=set)
    marked_for_removal: bool = False
    
    def add_occurrence(self, file_path: Path) -> None:
        """Añade una ocurrencia del tag desde un archivo"""
        self.count += 1
        self.file_paths.add(file_path)
    
    def __hash__(self) -> int:
        return hash((self.namespace, self.tag))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TagAggregate):
            return False
        return self.namespace == other.namespace and self.tag == other.tag
