import re
from pathlib import Path

CARACTERES_INVALIDOS = r"[:\\/\?\*\[\]]"
PATRON_FECHA_HORA = re.compile(r"\s+\d{4}-\d{2}-\d{2}\s+\d{4,6}\s*$")
LARGO_MAXIMO = 31


def _sanear(nombre):
    nombre = re.sub(CARACTERES_INVALIDOS, "-", nombre)
    return nombre.strip()[:LARGO_MAXIMO].strip()


def generar_nombre_hoja(nombre_archivo, catalogo_formularios):
    """Determina el nombre de hoja a partir del nombre de archivo de entrada.

    Devuelve (nombre_hoja, reconocido) donde reconocido indica si el nombre de
    formulario vino del catalogo (config/nombres_hojas_conocidos.json) o de un
    recorte heuristico (nombre de formulario no catalogado todavia).
    """
    stem = Path(nombre_archivo).stem

    for formulario in sorted(catalogo_formularios, key=len, reverse=True):
        if stem == formulario or stem.startswith(formulario + " "):
            return _sanear(formulario), True

    heuristico = PATRON_FECHA_HORA.sub("", stem).strip()
    return _sanear(heuristico or stem), False
