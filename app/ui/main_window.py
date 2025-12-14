"""Ventana principal de la aplicación"""

from pathlib import Path
from typing import Dict, List, Set, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QSpinBox, QTextEdit, QLabel, QTabWidget, QGroupBox,
    QComboBox, QProgressBar, QStatusBar, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal

from ..core.aggregator import TagAggregator
from ..core.filter import TagFilter, BannedMatchMode
from ..models.tag_models import TagFile, TagAggregate
from ..workers.scan_worker import ScanWorker
from ..workers.apply_worker import ApplyWorker
from ..utils.logger import setup_logger, get_logger
from ..utils.backup import create_backup
from .namespace_tab import NamespaceTab

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tag File Editor - Revisión y Limpieza de Tags")
        self.setMinimumSize(1200, 800)
        
        # Configurar logger
        setup_logger()
        
        # Estado de la aplicación
        self.directory: Optional[Path] = None
        self.files_data: Dict[Path, TagFile] = {}
        self.aggregator = TagAggregator()
        self.filter = TagFilter(threshold=5)
        self.namespace_tabs: Dict[str, NamespaceTab] = {}
        
        # Workers
        self.scan_worker: Optional[ScanWorker] = None
        self.apply_worker: Optional[ApplyWorker] = None
        
        self._setup_ui()
        logger.info("Aplicación iniciada")
    
    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo (controles)
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho (tabs de namespaces)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 900])
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def _create_left_panel(self) -> QWidget:
        """Crea el panel izquierdo con controles"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Selección de directorio
        dir_group = QGroupBox("Directorio")
        dir_layout = QVBoxLayout()
        
        self.dir_label = QLabel("No seleccionado")
        self.dir_label.setWordWrap(True)
        dir_layout.addWidget(self.dir_label)
        
        self.select_dir_btn = QPushButton("Seleccionar Directorio")
        self.select_dir_btn.clicked.connect(self._on_select_directory)
        dir_layout.addWidget(self.select_dir_btn)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Configuración de filtros
        filter_group = QGroupBox("Filtros")
        filter_layout = QVBoxLayout()
        
        # Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMinimum(1)
        self.threshold_spin.setMaximum(10000)
        self.threshold_spin.setValue(5)
        self.threshold_spin.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.threshold_spin)
        filter_layout.addLayout(threshold_layout)
        
        # Banned tags
        filter_layout.addWidget(QLabel("Tags Prohibidos:"))
        self.banned_tags_edit = QTextEdit()
        self.banned_tags_edit.setMaximumHeight(150)
        self.banned_tags_edit.setPlaceholderText(
            "Un tag por línea\nEjemplo:\nwitch hat\nartist:test"
        )
        self.banned_tags_edit.textChanged.connect(self._on_banned_tags_changed)
        filter_layout.addWidget(self.banned_tags_edit)
        
        # Modo de coincidencia
        match_layout = QHBoxLayout()
        match_layout.addWidget(QLabel("Modo:"))
        self.match_mode_combo = QComboBox()
        self.match_mode_combo.addItems([
            BannedMatchMode.EXACT,
            BannedMatchMode.SUBSTRING,
            BannedMatchMode.REGEX
        ])
        self.match_mode_combo.currentTextChanged.connect(self._on_match_mode_changed)
        match_layout.addWidget(self.match_mode_combo)
        filter_layout.addLayout(match_layout)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Acciones
        actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        self.scan_btn = QPushButton("Escanear / Recargar")
        self.scan_btn.clicked.connect(self._on_scan)
        self.scan_btn.setEnabled(False)
        actions_layout.addWidget(self.scan_btn)
        
        self.dry_run_btn = QPushButton("Dry-run (Vista Previa)")
        self.dry_run_btn.clicked.connect(self._on_dry_run)
        self.dry_run_btn.setEnabled(False)
        actions_layout.addWidget(self.dry_run_btn)
        
        self.apply_btn = QPushButton("Aplicar Cambios")
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        actions_layout.addWidget(self.apply_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Crea el panel derecho con tabs de namespaces"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.namespace_tabs_widget = QTabWidget()
        layout.addWidget(self.namespace_tabs_widget)
        
        return panel
    
    def _on_select_directory(self) -> None:
        """Maneja la selección de directorio"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Directorio",
            str(Path.home())
        )
        
        if directory:
            self.directory = Path(directory)
            self.dir_label.setText(str(self.directory))
            self.scan_btn.setEnabled(True)
            self.status_bar.showMessage(f"Directorio seleccionado: {self.directory}")
            logger.info(f"Directorio seleccionado: {self.directory}")
    
    def _on_threshold_changed(self, value: int) -> None:
        """Maneja cambios en el threshold"""
        self.filter.set_threshold(value)
        if self.files_data:
            self._refresh_tags_display()
        logger.debug(f"Threshold cambiado a {value}")
    
    def _on_banned_tags_changed(self) -> None:
        """Maneja cambios en los tags prohibidos"""
        text = self.banned_tags_edit.toPlainText()
        banned_set = {
            line.strip()
            for line in text.split('\n')
            if line.strip()
        }
        self.filter.set_banned_tags(banned_set)
        if self.files_data:
            self._refresh_tags_display()
        logger.debug(f"Tags prohibidos actualizados: {len(banned_set)} tags")
    
    def _on_match_mode_changed(self, mode: str) -> None:
        """Maneja cambios en el modo de coincidencia"""
        self.filter.set_match_mode(mode)
        if self.files_data:
            self._refresh_tags_display()
        logger.debug(f"Modo de coincidencia cambiado a {mode}")
    
    def _on_scan(self) -> None:
        """Inicia el escaneo de archivos"""
        if not self.directory:
            QMessageBox.warning(self, "Error", "Por favor seleccione un directorio")
            return
        
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, "Error", "Ya hay un escaneo en progreso")
            return
        
        # Limpiar datos anteriores
        self.files_data.clear()
        self.aggregator.clear()
        self.namespace_tabs.clear()
        self.namespace_tabs_widget.clear()
        
        # Deshabilitar botones
        self.scan_btn.setEnabled(False)
        self.dry_run_btn.setEnabled(False)
        self.apply_btn.setEnabled(False)
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Escaneando archivos...")
        
        # Crear y ejecutar worker
        self.scan_worker = ScanWorker(self.directory)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.file_processed.connect(self._on_file_processed)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.error.connect(self._on_scan_error)
        self.scan_worker.start()
        
        logger.info("Iniciando escaneo...")
    
    def _on_scan_progress(self, current: int, total: int) -> None:
        """Actualiza el progreso del escaneo"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Escaneando: {current}/{total} archivos")
    
    def _on_file_processed(self, file_path: str, tag_count: int) -> None:
        """Maneja un archivo procesado"""
        pass  # Puede usarse para logging adicional
    
    def _on_scan_finished(self, files_data: object) -> None:
        """Maneja la finalización del escaneo"""
        # Convertir object a Dict[Path, TagFile]
        if not isinstance(files_data, dict):
            logger.error(f"Tipo inesperado recibido: {type(files_data)}")
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Error: datos inválidos recibidos")
            self.scan_btn.setEnabled(True)
            return
        
        self.files_data = files_data  # type: Dict[Path, TagFile]
        
        if not files_data:
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("No se encontraron archivos .txt")
            self.scan_btn.setEnabled(True)
            QMessageBox.information(self, "Información", "No se encontraron archivos .txt")
            return
        
        # Agregar archivos al agregador
        for file_path, tag_file in files_data.items():
            self.aggregator.add_file(file_path, tag_file.tags)
        
        # Refrescar display
        self._refresh_tags_display()
        
        # Ocultar progreso
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(
            f"Escaneo completado: {len(files_data)} archivos, "
            f"{sum(len(tf.tags) for tf in files_data.values())} tags totales"
        )
        
        # Habilitar botones
        self.scan_btn.setEnabled(True)
        self.dry_run_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        
        logger.info(f"Escaneo completado: {len(files_data)} archivos")
    
    def _on_scan_error(self, error_message: str) -> None:
        """Maneja errores del escaneo"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Error: {error_message}")
        self.scan_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Error durante el escaneo:\n{error_message}")
        logger.error(f"Error en escaneo: {error_message}")
    
    def _refresh_tags_display(self) -> None:
        """Refresca la visualización de tags"""
        # Obtener agregados
        all_aggregates = self.aggregator.get_aggregates()
        
        # Filtrar
        filtered_aggregates = self.filter.filter(all_aggregates)
        
        # Agrupar por namespace
        namespace_groups: Dict[str, List[TagAggregate]] = {}
        for agg in filtered_aggregates:
            if agg.namespace not in namespace_groups:
                namespace_groups[agg.namespace] = []
            namespace_groups[agg.namespace].append(agg)
        
        # Actualizar tabs
        current_tabs = set(self.namespace_tabs.keys())
        new_tabs = set(namespace_groups.keys())
        
        # Remover tabs que ya no existen
        for namespace in current_tabs - new_tabs:
            tab = self.namespace_tabs.pop(namespace)
            idx = self.namespace_tabs_widget.indexOf(tab)
            if idx >= 0:
                self.namespace_tabs_widget.removeTab(idx)
        
        # Añadir/actualizar tabs
        for namespace, aggregates in namespace_groups.items():
            if namespace not in self.namespace_tabs:
                tab = NamespaceTab(namespace, self)
                self.namespace_tabs[namespace] = tab
                # Ordenar nombres de tabs: general primero, luego alfabético
                if namespace == "general":
                    self.namespace_tabs_widget.insertTab(0, tab, namespace)
                else:
                    self.namespace_tabs_widget.addTab(tab, namespace)
            
            self.namespace_tabs[namespace].set_aggregates(aggregates)
        
        # Actualizar estado
        total_tags = len(filtered_aggregates)
        total_namespaces = len(namespace_groups)
        self.status_bar.showMessage(
            f"{total_tags} tags mostrados en {total_namespaces} namespaces "
            f"(threshold={self.filter.threshold})"
        )
    
    def _on_dry_run(self) -> None:
        """Ejecuta un dry-run para mostrar vista previa"""
        if not self.files_data:
            QMessageBox.warning(self, "Error", "Primero debe escanear archivos")
            return
        
        # Obtener tags marcados para remover
        tags_to_remove: Set[tuple[str, str]] = set()
        
        for tab in self.namespace_tabs.values():
            marked = tab.get_marked_tags()
            tags_to_remove.update(marked)
        
        # También incluir banned tags
        for agg in self.aggregator.get_aggregates():
            if self.filter.is_banned(agg.namespace, agg.tag):
                tags_to_remove.add((agg.namespace, agg.tag))
        
        if not tags_to_remove:
            QMessageBox.information(
                self,
                "Dry-run",
                "No hay tags marcados para remover"
            )
            return
        
        # Calcular estadísticas
        files_to_modify = set()
        total_tags_to_remove = 0
        
        for file_path, tag_file in self.files_data.items():
            file_tags_to_remove = sum(
                1 for tag in tag_file.tags
                if (tag.namespace, tag.tag) in tags_to_remove
            )
            if file_tags_to_remove > 0:
                files_to_modify.add(file_path)
                total_tags_to_remove += file_tags_to_remove
        
        # Mostrar resumen
        message = (
            f"Vista Previa (Dry-run):\n\n"
            f"Tags a remover: {len(tags_to_remove)}\n"
            f"Archivos a modificar: {len(files_to_modify)}\n"
            f"Total de tags removidos: {total_tags_to_remove}\n\n"
            f"¿Desea proceder con la aplicación?"
        )
        
        reply = QMessageBox.question(
            self,
            "Dry-run",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._on_apply()
    
    def _on_apply(self) -> None:
        """Aplica los cambios a los archivos"""
        if not self.files_data:
            QMessageBox.warning(self, "Error", "Primero debe escanear archivos")
            return
        
        # Obtener tags marcados para remover
        tags_to_remove: Set[tuple[str, str]] = set()
        
        for tab in self.namespace_tabs.values():
            marked = tab.get_marked_tags()
            tags_to_remove.update(marked)
        
        # También incluir banned tags
        for agg in self.aggregator.get_aggregates():
            if self.filter.is_banned(agg.namespace, agg.tag):
                tags_to_remove.add((agg.namespace, agg.tag))
        
        if not tags_to_remove:
            QMessageBox.information(
                self,
                "Aplicar",
                "No hay tags marcados para remover"
            )
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self,
            "Confirmar Aplicación",
            (
                f"Se removerán {len(tags_to_remove)} tags.\n"
                f"Se crearán backups antes de modificar archivos.\n\n"
                f"¿Desea continuar?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Calcular archivos a modificar
        files_to_modify = []
        for file_path, tag_file in self.files_data.items():
            has_tags_to_remove = any(
                (tag.namespace, tag.tag) in tags_to_remove
                for tag in tag_file.tags
            )
            if has_tags_to_remove:
                files_to_modify.append(file_path)
        
        if not files_to_modify:
            QMessageBox.information(
                self,
                "Aplicar",
                "No hay archivos que modificar"
            )
            return
        
        # Crear backup
        try:
            backup_dir = create_backup(files_to_modify, self.directory)
            QMessageBox.information(
                self,
                "Backup Creado",
                f"Backup creado en:\n{backup_dir}"
            )
        except Exception as e:
            reply = QMessageBox.critical(
                self,
                "Error de Backup",
                f"Error al crear backup:\n{str(e)}\n\n¿Desea continuar de todas formas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Deshabilitar botones
        self.apply_btn.setEnabled(False)
        self.dry_run_btn.setEnabled(False)
        self.scan_btn.setEnabled(False)
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Aplicando cambios...")
        
        # Crear y ejecutar worker
        self.apply_worker = ApplyWorker(self.files_data, tags_to_remove)
        self.apply_worker.progress.connect(self._on_apply_progress)
        self.apply_worker.file_processed.connect(self._on_file_processed_apply)
        self.apply_worker.finished.connect(self._on_apply_finished)
        self.apply_worker.error.connect(self._on_apply_error)
        self.apply_worker.start()
        
        logger.info(f"Aplicando cambios: {len(tags_to_remove)} tags a remover")
    
    def _on_apply_progress(self, current: int, total: int) -> None:
        """Actualiza el progreso de la aplicación"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Aplicando: {current}/{total} archivos")
    
    def _on_file_processed_apply(self, file_path: str, modified: bool) -> None:
        """Maneja un archivo procesado durante la aplicación"""
        pass
    
    def _on_apply_finished(self, files_modified: int, tags_removed: int) -> None:
        """Maneja la finalización de la aplicación"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(
            f"Aplicación completada: {files_modified} archivos modificados, "
            f"{tags_removed} tags removidos"
        )
        
        # Habilitar botones
        self.scan_btn.setEnabled(True)
        self.dry_run_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Aplicación Completada",
            (
                f"Cambios aplicados exitosamente:\n\n"
                f"Archivos modificados: {files_modified}\n"
                f"Tags removidos: {tags_removed}"
            )
        )
        
        logger.info(
            f"Aplicación completada: {files_modified} archivos, "
            f"{tags_removed} tags removidos"
        )
        
        # Recargar para reflejar cambios
        self._on_scan()
    
    def _on_apply_error(self, error_message: str) -> None:
        """Maneja errores de la aplicación"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Error: {error_message}")
        self.scan_btn.setEnabled(True)
        self.dry_run_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Error durante la aplicación:\n{error_message}")
        logger.error(f"Error en aplicación: {error_message}")
