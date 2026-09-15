# MACHA — Consolidador de Excels

Aplicación de escritorio para Windows que permite seleccionar varios archivos Excel de entrada,
normalizarlos según una plantilla de encabezados comun y generar un único Excel de salida con una
hoja por cada archivo procesado.

## Estructura del proyecto

```
MACHA/
├── ico/          Icono de la aplicacion
├── plantilla/    Plantilla de encabezados de salida
├── config/       Configuracion de mapeo de encabezados y nombres de hoja
├── src/          Codigo fuente (logica de consolidacion e interfaz grafica)
├── muestras/     Carpeta local para archivos de prueba (no se versiona)
└── tests/        Script de prueba de la logica de consolidacion
```

## Como ejecutar

```
pip install -r requirements.txt
python src/main.py
```

## Funcionalidad

- Selección de múltiples archivos Excel de entrada.
- Detección automática de encabezados y mapeo a una plantilla común.
- Descarte de registros duplicados dentro de una misma hoja.
- Generación de un único Excel consolidado, con resumen y detalle del proceso.
