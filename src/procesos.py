from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import dpa_especial as _dpa_especial
from rutas import raiz_app

RAIZ = raiz_app()


@dataclass(frozen=True)
class Proceso:
    """Describe un proceso de consolidacion (Pregrado, DPA, ...): que plantilla y
    configuracion de mapeo usa, y como se llaman en su plantilla las variables
    calculadas a partir de la fecha de registro (varian entre plantillas)."""

    id: str
    titulo: str
    subtitulo: str
    prefijo_salida: str
    ruta_plantilla: Path
    ruta_config: Path
    ruta_catalogo: Path
    campo_fecha_registro: str = "FECHA DE REGISTRO"
    variable_fecha_hora_completa: str = "FECHA DE REGISTRO2"
    variable_fecha: str = "FECHA"
    variable_dia: str = "DIA"
    variable_mes: str = "MES"
    variable_anio: str = "AÑO"
    campo_fecha_evento: str | None = None
    variable_mes_evento: str | None = None
    # Ajustes extra, por proceso, sobre una fila ya mapeada (ver dpa_especial.py).
    postprocesar: Callable | None = None
    # Estrategia alterna para nombre de hoja/FORMULARIO (por defecto: nombre de
    # archivo + catalogo, via nombre_hoja.generar_nombre_hoja).
    detectar_nombre_hoja: Callable | None = None


PREGRADO = Proceso(
    id="pregrado",
    titulo="MACHA",
    subtitulo="Consolidador de Excels - Pregrado",
    prefijo_salida="Consolidado-Pregrado",
    ruta_plantilla=RAIZ / "plantilla" / "Plantilla-PregradoV3.xlsx",
    ruta_config=RAIZ / "config" / "alias_encabezados.json",
    ruta_catalogo=RAIZ / "config" / "nombres_hojas_conocidos.json",
    campo_fecha_evento="FECHA CHARLA",
    variable_mes_evento="MES DEL EVENTO",
)

DPA = Proceso(
    id="dpa",
    titulo="MACHA",
    subtitulo="Consolidador de Excels - DPA",
    prefijo_salida="Consolidado-DPA",
    ruta_plantilla=RAIZ / "plantilla" / "Plantilla-DPA.xlsx",
    ruta_config=RAIZ / "config" / "alias_encabezados_dpa.json",
    ruta_catalogo=RAIZ / "config" / "nombres_hojas_conocidos_dpa.json",
    variable_fecha_hora_completa="FECHA EXACTA",
    # Soporta tambien los formatos BO/Joomla con 'campos extra' combinado (ver
    # plantilla/Caso_Especial.xlsx): separa ESTUDIOS SUPERIORES/MODALIDAD/
    # CARRERA DE INTERES y combina Nombre 1 + Nombre 2. Es no-op en los
    # formularios normales de DPA porque esas columnas auxiliares no existen
    # ahi. El nombre de hoja/FORMULARIO SIEMPRE sale del nombre de archivo +
    # catalogo (no de columnas como 'Nombre del Evento'/'FORMULARIO' del
    # archivo de origen, que pueden venir desactualizadas y generar hojas
    # duplicadas para el mismo evento).
    postprocesar=_dpa_especial.postprocesar,
)
