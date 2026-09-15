import re
import unicodedata


def normalizar(valor):
    """Texto listo para comparar encabezados: sin tildes, en mayusculas, espacios colapsados."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.upper()
    texto = re.sub(r"\s+", " ", texto)
    return texto
