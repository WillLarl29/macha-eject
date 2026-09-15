from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
RUTA_PLANTILLA = RAIZ / "plantilla" / "Encabezados.xlsx"


def cargar_variables_plantilla(ruta=RUTA_PLANTILLA):
    """Lee la fila 1 de la plantilla y devuelve la lista ordenada de variables de salida."""
    wb = openpyxl.load_workbook(ruta, read_only=True)
    ws = wb.worksheets[0]
    fila = next(ws.iter_rows(min_row=1, max_row=1))
    variables = [celda.value for celda in fila if celda.value is not None]
    wb.close()
    return variables
