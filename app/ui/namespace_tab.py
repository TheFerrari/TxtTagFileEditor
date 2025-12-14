"""Widget de pestaña para mostrar tags de un namespace"""

from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QHeaderView
)
from PySide6.QtCore import Qt

from ..models.tag_models import TagAggregate
from .tag_table_model import TagTableModel


class NamespaceTab(QWidget):
    """Widget de pestaña para un namespace específico"""
    
    def __init__(self, namespace: str, parent=None):
        """
        Inicializa la pestaña
        
        Args:
            namespace: Nombre del namespace
            parent: Widget padre
        """
        super().__init__(parent)
        self.namespace = namespace
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Campo de búsqueda
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Buscar tags...")
        self.search_field.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_field)
        
        # Tabla de tags
        self.table_view = QTableView()
        self.model = TagTableModel(self)
        self.table_view.setModel(self.model)
        
        # Configurar columnas
        self.table_view.setColumnWidth(0, 30)  # Checkbox
        self.table_view.setColumnWidth(1, 400)  # Tag
        self.table_view.setColumnWidth(2, 80)  # Count
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        
        # Habilitar ordenamiento
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(1, Qt.SortOrder.DescendingOrder)  # Ordenar por count desc
        
        layout.addWidget(self.table_view)
    
    def _on_search_changed(self, text: str) -> None:
        """Maneja cambios en el campo de búsqueda"""
        self.model.filter_by_text(text)
    
    def set_aggregates(self, aggregates: List[TagAggregate]) -> None:
        """
        Establece los agregados a mostrar
        
        Args:
            aggregates: Lista de agregados del namespace
        """
        self.model.set_aggregates(aggregates)
    
    def get_marked_tags(self) -> List[tuple[str, str]]:
        """
        Obtiene los tags marcados para remover
        
        Returns:
            Lista de tuplas (namespace, tag)
        """
        return self.model.get_marked_tags()
