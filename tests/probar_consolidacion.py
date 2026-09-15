import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from consolidador import procesar_archivos  # noqa: E402

MUESTRAS = RAIZ / "muestras"
SALIDA = RAIZ / "salida" / "prueba_consolidado.xlsx"

if __name__ == "__main__":
    archivos = [p for p in MUESTRAS.glob("*.xlsx") if not p.name.startswith("~$")]
    libro, resultado = procesar_archivos(archivos)
    SALIDA.parent.mkdir(exist_ok=True)
    libro.save(SALIDA)

    print(f"Archivos procesados: {len(archivos)}")
    print(f"Salida: {SALIDA}")
    print(f"Total filas: {resultado['total_filas']}")
    print(f"Total duplicados: {resultado['total_duplicados']}")
    for a in resultado["archivos"]:
        print(f"  - {a['archivo']} -> hoja '{a['hoja']}': {a['filas']} fila(s), "
              f"duplicados: {a['duplicados_dni']}")
    print("Advertencias:" if resultado["advertencias"] else "Sin advertencias.")
    for a in resultado["advertencias"]:
        print(f"  - {a}")
