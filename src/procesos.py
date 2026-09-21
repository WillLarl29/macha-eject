from dataclasses import dataclass
from pathlib import Path

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


PREGRADO = Proceso(
    id="pregrado",
    titulo="MACHA",
    subtitulo="Consolidador de Excels - Pregrado",
    prefijo_salida="Consolidado-Pregrado",
    ruta_plantilla=RAIZ / "plantilla" / "Plantilla-Pregrado.xlsx",
    ruta_config=RAIZ / "config" / "alias_encabezados.json",
    ruta_catalogo=RAIZ / "config" / "nombres_hojas_conocidos.json",
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
)
