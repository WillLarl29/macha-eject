import json
from pathlib import Path

from texto import normalizar

RAIZ = Path(__file__).resolve().parent.parent
RUTA_CONFIG = RAIZ / "config" / "alias_encabezados.json"
RUTA_CATALOGO_FORMULARIOS = RAIZ / "config" / "nombres_hojas_conocidos.json"

VARIABLES_CALCULADAS = {"FORMULARIO", "FECHA DE REGISTRO2", "FECHA", "DIA", "MES", "AÑO"}


def cargar_config(ruta=RUTA_CONFIG):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_catalogo_formularios(ruta=RUTA_CATALOGO_FORMULARIOS):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)["nombres_formulario"]


def construir_indice_alias(config):
    """Alias normalizado -> nombre de variable de plantilla, para deteccion por texto exacto."""
    indice = {}
    for var in config["variables_plantilla"]:
        for alias in var.get("alias_conocidos", []):
            indice[normalizar(alias)] = var["variable"]
    return indice
