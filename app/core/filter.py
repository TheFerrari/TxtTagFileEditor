"""Filtrado de tags según threshold y banned tags"""

import re
from typing import List, Set

from ..models.tag_models import TagAggregate


class BannedMatchMode:
    """Modos de coincidencia para tags prohibidos"""
    EXACT = "exact"
    SUBSTRING = "substring"
    REGEX = "regex"


class TagFilter:
    """Filtra tags según threshold y banned tags"""
    
    def __init__(
        self,
        threshold: int = 5,
        banned_tags: Set[str] = None,
        match_mode: str = BannedMatchMode.EXACT
    ) -> None:
        """
        Inicializa el filtro
        
        Args:
            threshold: Conteo mínimo para mostrar tags
            banned_tags: Set de tags prohibidos
            match_mode: Modo de coincidencia (exact/substring/regex)
        """
        self.threshold = threshold
        self.banned_tags = banned_tags or set()
        self.match_mode = match_mode
        self._compiled_regexes: List[re.Pattern] = []
        self._compile_regexes()
    
    def _compile_regexes(self) -> None:
        """Compila regexes si el modo es regex"""
        if self.match_mode == BannedMatchMode.REGEX:
            self._compiled_regexes = []
            for pattern in self.banned_tags:
                try:
                    self._compiled_regexes.append(re.compile(pattern))
                except re.error:
                    # Si el regex es inválido, lo ignoramos
                    pass
    
    def set_threshold(self, threshold: int) -> None:
        """Establece el threshold mínimo"""
        self.threshold = threshold
    
    def set_banned_tags(self, banned_tags: Set[str]) -> None:
        """Establece los tags prohibidos"""
        self.banned_tags = banned_tags
        self._compile_regexes()
    
    def set_match_mode(self, match_mode: str) -> None:
        """Establece el modo de coincidencia"""
        self.match_mode = match_mode
        self._compile_regexes()
    
    def is_banned(self, namespace: str, tag: str) -> bool:
        """
        Verifica si un tag está prohibido según el modo de coincidencia
        
        Args:
            namespace: Namespace del tag
            tag: Texto del tag
            
        Returns:
            True si el tag está prohibido
        """
        if not self.banned_tags:
            return False
        
        # Formato completo: namespace:tag o solo tag para general
        if namespace == "general":
            full_tag = tag
        else:
            full_tag = f"{namespace}:{tag}"
        
        if self.match_mode == BannedMatchMode.EXACT:
            return full_tag in self.banned_tags or tag in self.banned_tags
        
        elif self.match_mode == BannedMatchMode.SUBSTRING:
            for banned in self.banned_tags:
                if banned in full_tag or banned in tag:
                    return True
            return False
        
        elif self.match_mode == BannedMatchMode.REGEX:
            for pattern in self._compiled_regexes:
                if pattern.search(full_tag) or pattern.search(tag):
                    return True
            return False
        
        return False
    
    def filter(self, aggregates: List[TagAggregate]) -> List[TagAggregate]:
        """
        Filtra agregados según threshold y banned tags
        
        Args:
            aggregates: Lista de agregados a filtrar
            
        Returns:
            Lista filtrada de agregados
        """
        filtered = []
        
        for agg in aggregates:
            # Filtrar por threshold
            if agg.count < self.threshold:
                continue
            
            # Filtrar por banned tags
            if self.is_banned(agg.namespace, agg.tag):
                continue
            
            filtered.append(agg)
        
        return filtered
