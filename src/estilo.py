import ctypes
from pathlib import Path

CARPETA_FUENTES = Path(__file__).resolve().parent / "assets" / "fonts"
FR_PRIVATE = 0x10

ROJO = "#f01830"
NEGRO = "#040404"
BLANCO = "#ffffff"
NEGRO_10 = "#e6e6e6"
NEGRO_15 = "#d9d9d9"
NEGRO_20 = "#cdcdcd"
AMBAR = "#a86400"
VERDE = "#146c2e"

# Nombres de familia reales que Windows expone luego de registrar cada .ttf
# (verificado con tkinter.font.families() tras registrar los archivos).
TITULOS_MEDIUM = "Inter Medium"
TITULOS_SEMIBOLD = "Inter SemiBold"
TITULOS_BOLD = "Inter"
BASE = "Raleway"
BASE_SEMIBOLD = "Raleway SemiBold"
DATOS = "Space Grotesk Medium"
DATOS_SEMIBOLD = "Space Grotesk SemiBold"
DATOS_BOLD = "Space Grotesk"


def registrar_fuentes():
    """Registra los .ttf de assets/fonts solo para este proceso (sin instalarlos)."""
    if not CARPETA_FUENTES.exists():
        return False
    gdi32 = ctypes.windll.gdi32
    ok = True
    for archivo in CARPETA_FUENTES.glob("*.ttf"):
        resultado = gdi32.AddFontResourceExW(str(archivo), FR_PRIVATE, 0)
        ok = ok and resultado > 0
    return ok
