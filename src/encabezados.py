from texto import normalizar


def detectar_encabezados(ws, indice_alias, filas_candidatas=(1, 2)):
    """Busca en las filas candidatas cual es la fila de encabezado real.

    Se queda con la fila que reconoce mas variables (empate lo gana la primera
    fila candidata), tal como se definio: revisar fila 1 y, si no calza, fila 2.

    Devuelve (numero_fila_encabezado, {variable: indice_columna}).
    """
    mejor_fila = None
    mejor_mapeo = {}
    for num_fila in filas_candidatas:
        mapeo_fila = {}
        for celda in ws[num_fila]:
            variable = indice_alias.get(normalizar(celda.value))
            if variable is not None:
                mapeo_fila[variable] = celda.column
        if len(mapeo_fila) > len(mejor_mapeo):
            mejor_fila = num_fila
            mejor_mapeo = mapeo_fila
    return mejor_fila, mejor_mapeo
