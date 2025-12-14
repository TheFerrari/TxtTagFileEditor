"""Modelo de tabla para mostrar tags con checkboxes"""

from typing import List

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

from ..models.tag_models import TagAggregate


class TagTableModel(QAbstractTableModel):
    """Modelo de tabla para mostrar TagAggregate con checkboxes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._aggregates: List[TagAggregate] = []
        self._filtered_aggregates: List[TagAggregate] = []
        self._sort_column = 1  # Columna de count por defecto
        self._sort_order = Qt.SortOrder.DescendingOrder
    
    def set_aggregates(self, aggregates: List[TagAggregate]) -> None:
        """Establece los agregados a mostrar"""
        self.beginResetModel()
        self._aggregates = aggregates
        self._apply_filter_and_sort()
        self.endResetModel()
    
    def _apply_filter_and_sort(self) -> None:
        """Aplica filtro y ordenamiento"""
        self._filtered_aggregates = self._aggregates.copy()
        self._sort_data()
    
    def _sort_data(self) -> None:
        """Ordena los datos según la columna y orden actuales"""
        if self._sort_column == 0:  # Tag name
            reverse = self._sort_order == Qt.SortOrder.DescendingOrder
            self._filtered_aggregates.sort(
                key=lambda x: x.tag.lower(),
                reverse=reverse
            )
        elif self._sort_column == 1:  # Count
            reverse = self._sort_order == Qt.SortOrder.DescendingOrder
            self._filtered_aggregates.sort(
                key=lambda x: x.count,
                reverse=reverse
            )
    
    def filter_by_text(self, text: str) -> None:
        """
        Filtra tags por texto de búsqueda
        
        Args:
            text: Texto a buscar (case-insensitive)
        """
        if not text:
            self._filtered_aggregates = self._aggregates.copy()
        else:
            text_lower = text.lower()
            self._filtered_aggregates = [
                agg for agg in self._aggregates
                if text_lower in agg.tag.lower() or text_lower in agg.namespace.lower()
            ]
        
        self._sort_data()
        self.layoutChanged.emit()
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna el número de filas"""
        return len(self._filtered_aggregates)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna el número de columnas"""
        return 3  # Checkbox, Tag, Count
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Retorna los datos para el índice dado"""
        if not index.isValid() or index.row() >= len(self._filtered_aggregates):
            return None
        
        agg = self._filtered_aggregates[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 1:  # Tag
                if agg.namespace == "general":
                    return agg.tag
                else:
                    return f"{agg.namespace}:{agg.tag}"
            elif col == 2:  # Count
                return str(agg.count)
        
        elif role == Qt.ItemDataRole.CheckStateRole and col == 0:
            return Qt.CheckState.Checked if agg.marked_for_removal else Qt.CheckState.Unchecked
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col == 2:  # Count
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        return None
    
    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Establece los datos para el índice dado"""
        if not index.isValid() or index.row() >= len(self._filtered_aggregates):
            return False
        
        if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            agg = self._filtered_aggregates[index.row()]
            agg.marked_for_removal = (value == Qt.CheckState.Checked)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            return True
        
        return False
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Retorna los datos del encabezado"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "Tag", "Count"]
            if section < len(headers):
                return headers[section]
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Retorna las banderas del ítem"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        if index.column() == 0:  # Checkbox
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        
        return flags
    
    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Ordena la tabla por la columna especificada"""
        self._sort_column = column
        self._sort_order = order
        self._sort_data()
        self.layoutChanged.emit()
    
    def get_marked_tags(self) -> List[tuple[str, str]]:
        """
        Obtiene las tuplas (namespace, tag) de los tags marcados para remover
        
        Returns:
            Lista de tuplas (namespace, tag)
        """
        return [
            (agg.namespace, agg.tag)
            for agg in self._aggregates
            if agg.marked_for_removal
        ]
    
    def get_all_aggregates(self) -> List[TagAggregate]:
        """Obtiene todos los agregados (filtrados)"""
        return self._filtered_aggregates.copy()
