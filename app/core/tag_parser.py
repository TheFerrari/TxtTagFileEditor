"""Parser para líneas de tags según el formato especificado"""

from typing import Tuple, Optional


def parse_line(line: str) -> Optional[Tuple[str, str]]:
    """
    Parsea una línea de tag según las reglas:
    - Si tiene ':', divide solo en el primer ':' (namespace:tag)
    - Si no tiene ':', namespace es "general"
    - Ignora líneas vacías
    - Recorta espacios en blanco
    
    Args:
        line: Línea de texto a parsear
        
    Returns:
        Tupla (namespace, tag) o None si la línea está vacía
    """
    line = line.strip()
    
    if not line:
        return None
    
    # Dividir solo en el primer ':'
    if ':' in line:
        parts = line.split(':', 1)
        namespace = parts[0].strip()
        tag = parts[1].strip()
        return (namespace, tag)
    else:
        # Sin ':' significa namespace "general"
        return ("general", line)


def format_tag(namespace: str, tag: str) -> str:
    """
    Formatea un tag para escribir en archivo según el estándar:
    - Tags "general" se escriben sin prefijo
    - Otros namespaces se escriben como "namespace:tag"
    
    Args:
        namespace: Namespace del tag
        tag: Texto del tag
        
    Returns:
        String formateado para escribir en archivo
    """
    if namespace == "general":
        return tag
    else:
        return f"{namespace}:{tag}"
