# Tag File Editor

Aplicación PySide6 para revisión y limpieza masiva de tags en archivos .txt.

## Descripción

Esta herramienta permite escanear recursivamente directorios con archivos .txt que contienen tags, agruparlos por namespace, filtrarlos según frecuencia y tags prohibidos, y aplicar limpieza masiva removiendo tags seleccionados.

## Formato de Tags

Cada archivo .txt contiene un tag por línea en uno de estos formatos:

- **Tags generales** (sin namespace):
  ```
  watersports
  witch hat
  ```

- **Tags con namespace** (namespace:tag):
  ```
  artist:alacarte
  character:enit (alacarte)
  species:domestic cat
  meta:2018
  meta:1 1
  ```

### Reglas de Parsing

- Se divide solo en el primer `:` (ej: `character:enit (alacarte)` → namespace=`character`, tag=`enit (alacarte)`)
- Si no hay `:`, el namespace es `"general"`
- Se ignoran líneas vacías y se recorta whitespace
- Se preserva el texto original del tag (espacios permitidos)

## Instalación

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar la aplicación

```bash
python -m app.main
```

O desde el directorio del proyecto:

```bash
python app/main.py
```

### Funcionalidades

1. **Seleccionar Directorio**: Elige un directorio que contenga archivos .txt con tags
2. **Escanear**: Escanea recursivamente todos los archivos .txt y agrega tags
3. **Filtros**:
   - **Threshold**: Muestra solo tags que aparecen al menos N veces (default: 5)
   - **Tags Prohibidos**: Lista de tags a excluir (uno por línea)
   - **Modo de Coincidencia**: Exacto, Substring o Regex
4. **Visualización**: Tags agrupados por namespace en pestañas, con checkboxes para marcar remoción
5. **Búsqueda**: Campo de búsqueda en cada pestaña de namespace
6. **Ordenamiento**: Click en encabezados de columna para ordenar por tag o count
7. **Dry-run**: Vista previa de cambios sin aplicar
8. **Aplicar**: Crea backup y aplica cambios removiendo tags marcados

### Flujo de Trabajo

1. Seleccionar directorio con archivos .txt
2. Click en "Escanear / Recargar"
3. Ajustar threshold y tags prohibidos según necesidad
4. Revisar tags en las pestañas de namespaces
5. Marcar tags para remover usando checkboxes
6. Opcional: Click en "Dry-run" para ver vista previa
7. Click en "Aplicar Cambios" para crear backup y aplicar cambios

## Características

- ✅ Escaneo recursivo de archivos .txt
- ✅ Agregación de tags por namespace con conteos
- ✅ Filtrado por threshold (frecuencia mínima)
- ✅ Filtrado por tags prohibidos (exacto, substring, regex)
- ✅ Interfaz con pestañas por namespace
- ✅ Búsqueda y ordenamiento de tags
- ✅ Vista previa (dry-run) antes de aplicar
- ✅ Backup automático antes de modificar archivos
- ✅ Workers en background para no bloquear UI
- ✅ Logging completo a archivo y consola
- ✅ Manejo robusto de errores y codificaciones

## Estructura del Proyecto

```
app/
├── __init__.py
├── main.py                 # Punto de entrada
├── models/                 # Modelos de datos
│   ├── __init__.py
│   └── tag_models.py
├── core/                   # Lógica de negocio
│   ├── __init__.py
│   ├── tag_parser.py      # Parser de líneas de tags
│   ├── aggregator.py       # Agregación de tags
│   └── filter.py          # Filtrado de tags
├── ui/                     # Interfaz de usuario
│   ├── __init__.py
│   ├── main_window.py     # Ventana principal
│   ├── namespace_tab.py   # Widget de pestaña
│   └── tag_table_model.py # Modelo de tabla
├── workers/                # Workers en background
│   ├── __init__.py
│   ├── scan_worker.py     # Worker de escaneo
│   └── apply_worker.py    # Worker de aplicación
└── utils/                  # Utilidades
    ├── __init__.py
    ├── logger.py          # Configuración de logging
    ├── backup.py          # Utilidades de backup
    └── path_utils.py      # Utilidades de rutas
```

## Logs y Backups

- **Logs**: Se guardan en `logs/tag_editor.log` (rotating, max 10MB, 5 backups)
- **Backups**: Se crean en el directorio seleccionado como `backup_YYYYMMDD_HHMMSS/`

## Notas

- Los archivos se reescriben en UTF-8
- Se preservan los line endings originales (`\n`, `\r\n`, `\r`)
- Se remueven duplicados al aplicar cambios (manteniendo orden)
- Si un archivo no puede leerse en UTF-8, se intenta con Latin-1

## Requisitos

- Python 3.8+
- PySide6 6.6.0+

## Licencia

Este proyecto es de código abierto.
