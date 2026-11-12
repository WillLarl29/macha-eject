import json

from rutas import raiz_app
from texto import normalizar

RAIZ = raiz_app()
RUTA_CONFIG = RAIZ / "config" / "alias_encabezados.json"
RUTA_CATALOGO_FORMULARIOS = RAIZ / "config" / "nombres_hojas_conocidos.json"

VARIABLES_CALCULADAS = {"FORMULARIO", "FECHA DE REGISTRO2", "FECHA", "DIA", "MES", "AÑO"}


def cargar_config(ruta=RUTA_CONFIG):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_catalogo_formularios(ruta=RUTA_CATALOGO_FORMULARIOS):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)["nombres_formulario"]


def cargar_alias_archivo(ruta=RUTA_CATALOGO_FORMULARIOS):
    """{nombre_de_evento_canonico: [nombre_de_archivo_sin_extension, ...]}.

    Permite reconocer archivos cuyo nombre no calza con el prefijo del
    catalogo (nombres_formulario) pero que el usuario ya confirmo que
    corresponden al mismo evento (ver guardar_alias_archivo)."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f).get("alias_archivo", {})


def guardar_alias_archivo(ruta, nombre_evento, nombres_archivo):
    """Agrega nombres_archivo (lista de stems de archivo, sin extension) como
    alias de nombre_evento en el catalogo, sin tocar el resto del contenido.
    Si nombre_evento no esta en nombres_formulario, tambien lo agrega ahi."""
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    datos.setdefault("nombres_formulario", [])
    if nombre_evento not in datos["nombres_formulario"]:
        datos["nombres_formulario"].append(nombre_evento)

    alias_archivo = datos.setdefault("alias_archivo", {})
    existentes = set(alias_archivo.setdefault(nombre_evento, []))
    for nombre in nombres_archivo:
        if nombre not in existentes:
            alias_archivo[nombre_evento].append(nombre)
            existentes.add(nombre)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def construir_indice_alias(config):
    """Alias normalizado -> nombre de variable de plantilla, para deteccion por texto exacto."""
    indice = {}
    for var in config["variables_plantilla"]:
        for alias in var.get("alias_conocidos", []):
            indice[normalizar(alias)] = var["variable"]
    return indice
