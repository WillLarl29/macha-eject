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


def construir_fila_salida(valores_fila, mapeo, variables_plantilla, nombre_hoja):
    """Arma una fila de salida en el orden de variables_plantilla.

    valores_fila: {indice_columna: valor_crudo} de una fila del archivo de entrada.
    mapeo: {variable_plantilla: indice_columna} detectado en el encabezado.
    """
    col_fecha_registro = mapeo.get("FECHA DE REGISTRO")
    crudo_fecha_registro = valores_fila.get(col_fecha_registro) if col_fecha_registro else None
    fecha_dt = parsear_fecha(crudo_fecha_registro)

    fila_salida = []
    for variable in variables_plantilla:
        if variable == "FORMULARIO":
            valor = nombre_hoja
        elif variable == "FECHA DE REGISTRO2":
            valor = crudo_fecha_registro
        elif variable == "FECHA":
            valor = fecha_dt.date() if fecha_dt else None
        elif variable == "DIA":
            valor = fecha_dt.day if fecha_dt else None
        elif variable == "MES":
            valor = fecha_dt.month if fecha_dt else None
        elif variable == "AÑO":
            valor = fecha_dt.year if fecha_dt else None
        else:
            col = mapeo.get(variable)
            valor = valores_fila.get(col) if col else None
        fila_salida.append(valor)
    return fila_salida
