import sys
from pathlib import Path


def raiz_app():
    """Carpeta base para encontrar recursos (plantilla/, config/, ico/, src/assets/).

    En desarrollo es la raiz del proyecto (padre de src/). Empaquetado con
    PyInstaller, sys._MEIPASS apunta a donde quedaron los datos incluidos con
    --add-data (tanto en modo onefile como onedir).
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent
