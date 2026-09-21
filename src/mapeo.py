from datetime import datetime

FORMATOS_FECHA_CONOCIDOS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]


def parsear_fecha(valor):
    """Convierte el valor crudo de 'Fecha de Registro' a datetime, o None si no se puede."""
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        for formato in FORMATOS_FECHA_CONOCIDOS:
            try:
                return datetime.strptime(valor.strip(), formato)
            except ValueError:
                continue
    return None


def construir_fila_salida(
    valores_fila, mapeo, variables_plantilla, nombre_hoja,
    campo_fecha_registro="FECHA DE REGISTRO",
    variable_fecha_hora_completa="FECHA DE REGISTRO2",
    variable_fecha="FECHA",
    variable_dia="DIA",
    variable_mes="MES",
    variable_anio="AÑO",
):
    """Arma una fila de salida en el orden de variables_plantilla.

    valores_fila: {indice_columna: valor_crudo} de una fila del archivo de entrada.
    mapeo: {variable_plantilla: indice_columna} detectado en el encabezado.
    campo_fecha_registro: nombre de la variable auxiliar (no necesariamente una
    columna de la plantilla) que identifica la columna de fecha/hora de origen.
    Las variable_* indican en que columna de la plantilla va cada dato derivado
    de esa fecha, ya que su nombre difiere entre plantillas (ej. Pregrado usa
    "FECHA DE REGISTRO2" y DPA usa "FECHA EXACTA" para la fecha/hora completa).
    """
    col_fecha_registro = mapeo.get(campo_fecha_registro)
    crudo_fecha_registro = valores_fila.get(col_fecha_registro) if col_fecha_registro else None
    fecha_dt = parsear_fecha(crudo_fecha_registro)

    fila_salida = []
    for variable in variables_plantilla:
        if variable == "FORMULARIO":
            valor = nombre_hoja
        elif variable == variable_fecha_hora_completa:
            valor = crudo_fecha_registro
        elif variable == variable_fecha:
            valor = fecha_dt.date() if fecha_dt else None
        elif variable == variable_dia:
            valor = fecha_dt.day if fecha_dt else None
        elif variable == variable_mes:
            valor = fecha_dt.month if fecha_dt else None
        elif variable == variable_anio:
            valor = fecha_dt.year if fecha_dt else None
        else:
            col = mapeo.get(variable)
            valor = valores_fila.get(col) if col else None
        fila_salida.append(valor)
    return fila_salida
