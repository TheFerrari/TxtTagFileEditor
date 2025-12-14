"""Punto de entrada principal de la aplicación"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.utils.logger import setup_logger, get_logger


def main():
    """Función principal"""
    # Configurar logging
    setup_logger()
    logger = get_logger(__name__)
    
    logger.info("Iniciando aplicación Tag File Editor")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Tag File Editor")
    app.setOrganizationName("TagEditor")
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar loop de eventos
    exit_code = app.exec()
    
    logger.info(f"Aplicación finalizada con código {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
