import re

VARIABLE_CAMPOS_EXTRA = "CAMPOS EXTRA"
VARIABLE_NOMBRE_2 = "NOMBRE 2"

PATRON_LINEA_CAMPO_EXTRA = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.*)$")

ETIQUETAS_CAMPOS_EXTRA = {
    "ESTUDIOS_REALIZADOS": "ESTUDIOS SUPERIORES",
    "MODALIDAD": "MODALIDAD",
    "CARRERA": "CARRERA DE INTERÉS",
}


def parsear_campos_extra(texto):
    """Parsea el valor crudo de la columna 'campos extra' (una linea por
    'etiqueta: valor', ej. 'estudios_realizados: Universitarios Completos') en
    un dict {etiqueta_en_mayusculas: valor}."""
    resultado = {}
    if not texto:
        return resultado
    for linea in str(texto).splitlines():
        coincidencia = PATRON_LINEA_CAMPO_EXTRA.match(linea)
        if not coincidencia:
            continue
        etiqueta = coincidencia.group(1).strip().upper()
        valor = coincidencia.group(2).strip()
        if valor:
            resultado[etiqueta] = valor
    return resultado


def postprocesar(valores_fila, mapeo, fila_salida, variables_plantilla):
    """Ajustes especificos de DPA_Especial sobre una fila ya mapeada:

    - Combina NOMBRE 1 (ya mapeado como NOMBRE) + NOMBRE 2, cuando este ultimo
      viene en columna aparte (formato BO).
    - Si ESTUDIOS SUPERIORES / MODALIDAD / CARRERA DE INTERES no vinieron en
      columnas propias, las completa separando el texto de 'campos extra'
      (tambien formato BO). Si ya vinieron en columnas propias (formato
      Joomla), no las toca.
    """
    indice = {variable: i for i, variable in enumerate(variables_plantilla)}

    if "NOMBRE" in indice:
        col_nombre2 = mapeo.get(VARIABLE_NOMBRE_2)
        if col_nombre2 is not None:
            nombre2 = valores_fila.get(col_nombre2)
            if nombre2 is not None and str(nombre2).strip():
                i_nombre = indice["NOMBRE"]
                base = fila_salida[i_nombre]
                base_txt = str(base).strip() if base else ""
                fila_salida[i_nombre] = (base_txt + " " + str(nombre2).strip()).strip()

    col_campos_extra = mapeo.get(VARIABLE_CAMPOS_EXTRA)
    if col_campos_extra is not None:
        valores_extra = parsear_campos_extra(valores_fila.get(col_campos_extra))
        for etiqueta, variable in ETIQUETAS_CAMPOS_EXTRA.items():
            if variable not in indice or etiqueta not in valores_extra:
                continue
            i_variable = indice[variable]
            if fila_salida[i_variable] in (None, ""):
                fila_salida[i_variable] = valores_extra[etiqueta]

    return fila_salida
