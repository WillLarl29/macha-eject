import re
from pathlib import Path

CARACTERES_INVALIDOS = r"[:\\/\?\*\[\]]"
PATRON_FECHA_HORA = re.compile(r"\s+\d{4}-\d{2}-\d{2}\s+\d{4,6}\s*$")
LARGO_MAXIMO = 31


def sanear(nombre):
    nombre = re.sub(CARACTERES_INVALIDOS, "-", nombre)
    return nombre.strip()[:LARGO_MAXIMO].strip()


def generar_nombre_hoja(nombre_archivo, catalogo_formularios, alias_archivo=None):
    """Determina el nombre de hoja a partir del nombre de archivo de entrada.

    alias_archivo: {nombre_evento: [stem_de_archivo, ...]}, opcional. Si el
    stem del archivo (sin extension) calza EXACTO con alguno, se usa ese
    evento directamente (esto es lo que confirma el usuario manualmente desde
    la interfaz para archivos cuyo nombre no sigue el patron del catalogo;
    ver config_mapeo.guardar_alias_archivo).

    Devuelve (nombre_hoja, reconocido) donde reconocido indica si el nombre de
    formulario vino del catalogo o de un alias de archivo confirmado, o de un
    recorte heuristico (nombre de formulario no catalogado todavia).
    """
    stem = Path(nombre_archivo).stem

    if alias_archivo:
        for evento, nombres in alias_archivo.items():
            if stem in nombres:
                return sanear(evento), True

    for formulario in sorted(catalogo_formularios, key=len, reverse=True):
        if stem == formulario or stem.startswith(formulario + " "):
            return sanear(formulario), True

    heuristico = PATRON_FECHA_HORA.sub("", stem).strip()
    return sanear(heuristico or stem), False
