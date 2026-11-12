from pathlib import Path

import openpyxl

from config_mapeo import (
    cargar_alias_archivo,
    cargar_catalogo_formularios,
    cargar_config,
    construir_indice_alias,
    guardar_alias_archivo,
)
from encabezados import detectar_encabezados
from mapeo import construir_fila_salida
from nombre_hoja import generar_nombre_hoja, sanear
from plantilla import cargar_variables_plantilla
from procesos import PREGRADO
from texto import normalizar


NOMBRE_HOJA_GENERAL = "Consolidado General"


def listar_eventos_conocidos(proceso):
    """Lista de nombres de evento conocidos (catalogo) para el proceso, o
    lista vacia si el proceso no agrupa archivos (ver Proceso.agrupar_archivos)."""
    if not proceso.agrupar_archivos:
        return []
    return list(cargar_catalogo_formularios(proceso.ruta_catalogo))


def sugerir_nombre_evento(ruta, proceso):
    """Abre el archivo y sugiere a que evento/hoja pertenece, para mostrarlo en
    la interfaz ANTES de generar el consolidado (ver 'Grupo' en gui.py).

    Devuelve (nombre_sugerido, reconocido). Si el archivo no tiene encabezados
    reconocidos, devuelve (nombre_de_archivo_sin_extension, False) para que la
    interfaz igual tenga algo que mostrar/editar.
    """
    ruta = Path(ruta)
    indice_alias = construir_indice_alias(cargar_config(proceso.ruta_config))
    catalogo_formularios = cargar_catalogo_formularios(proceso.ruta_catalogo)
    alias_archivo = cargar_alias_archivo(proceso.ruta_catalogo) if proceso.agrupar_archivos else {}

    try:
        wb = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
        _, mapeo = detectar_encabezados(wb.active, indice_alias)
        wb.close()
    except Exception:
        mapeo = {}

    if not mapeo:
        return ruta.stem, False

    return generar_nombre_hoja(ruta.name, catalogo_formularios, alias_archivo)


def confirmar_grupos_archivo(proceso, grupos_confirmados):
    """Guarda en el catalogo del proceso las asociaciones archivo->evento que
    el usuario confirmo desde la interfaz, para que la proxima vez se
    reconozcan solas (ver config_mapeo.guardar_alias_archivo).

    grupos_confirmados: {nombre_evento: [nombre_de_archivo_sin_extension, ...]}
    """
    if not proceso.agrupar_archivos or not grupos_confirmados:
        return
    for nombre_evento, nombres_archivo in grupos_confirmados.items():
        guardar_alias_archivo(proceso.ruta_catalogo, nombre_evento, nombres_archivo)

CAMPOS_REVISION_PRUEBA = ["NOMBRE", "AP. PATERNO", "APE. MATERNO", "DNI", "CORREO"]


def _indices_revision_prueba(variables_plantilla):
    return [
        (campo, variables_plantilla.index(campo))
        for campo in CAMPOS_REVISION_PRUEBA
        if campo in variables_plantilla
    ]


def _detectar_prueba(fila_salida, indices_prueba):
    """Devuelve una descripcion 'CAMPO: valor' del primer campo donde aparece
    la palabra PRUEBA (con o sin numeros pegados, ej. PRUEBA24), o None si no
    se encontro en ninguno de los campos revisados."""
    for campo, indice in indices_prueba:
        valor = fila_salida[indice]
        if valor is not None and "PRUEBA" in normalizar(valor):
            return f"{campo}: {valor}"
    return None


def _nombre_unico(nombre, usados):
    if nombre not in usados:
        usados.add(nombre)
        return nombre
    n = 2
    while True:
        candidato = f"{nombre[:28]} ({n})"
        if candidato not in usados:
            usados.add(candidato)
            return candidato
        n += 1


def procesar_archivos(rutas_entrada, on_evento=None, proceso=PREGRADO, grupos_por_archivo=None):
    """Consolida los excels de rutas_entrada en un libro en memoria (no lo guarda).

    proceso: descriptor (ver procesos.py) que indica que plantilla y
    configuracion de mapeo usar (Pregrado, DPA, ...).

    grupos_por_archivo: {str(ruta): nombre_de_evento}, opcional. Permite forzar
    a que un archivo pertenezca a un evento especifico (elegido por el usuario
    en la interfaz) en vez de calcularlo por nombre de archivo + catalogo.
    Solo tiene efecto si proceso.agrupar_archivos es True (DPA); se ignora en
    caso contrario.

    on_evento(mensaje, tipo), si se pasa, se llama en tiempo real con el avance
    (tipo: "info", "advertencia" o "exito").

    Devuelve (libro_salida, resultado) donde libro_salida es el Workbook de
    openpyxl (para guardarlo despues con libro_salida.save(ruta) una vez el
    usuario elija donde) y resultado es un dict:
      {
        "total_filas": int,
        "total_duplicados": int,
        "total_prueba": int,
        "advertencias": [str, ...],
        "archivos": [
          {"archivo": str, "hoja": str, "filas": int, "duplicados_dni": [str, ...],
           "registros_prueba": [str, ...]},
          ...
        ],
      }
    """

    def emitir(mensaje, tipo="info"):
        if on_evento:
            on_evento(mensaje, tipo)

    variables_plantilla = cargar_variables_plantilla(proceso.ruta_plantilla)
    indice_alias = construir_indice_alias(cargar_config(proceso.ruta_config))
    catalogo_formularios = cargar_catalogo_formularios(proceso.ruta_catalogo)
    alias_archivo = cargar_alias_archivo(proceso.ruta_catalogo) if proceso.agrupar_archivos else {}
    indice_dni = variables_plantilla.index("DNI")
    indices_prueba = _indices_revision_prueba(variables_plantilla)

    wb_salida = openpyxl.Workbook()
    wb_salida.remove(wb_salida.active)
    advertencias = []
    archivos_resultado = []
    filas_generales = []
    total_filas = 0
    total_duplicados = 0
    total_prueba = 0

    # --- Paso 1: abrir cada archivo y resolver a que evento/hoja pertenece,
    # sin crear todavia las hojas de salida (eso se hace agrupando en el paso 2). ---
    archivos_abiertos = []
    for ruta in rutas_entrada:
        ruta_str = str(ruta)
        ruta = Path(ruta)
        emitir(f"Leyendo {ruta.name}...")
        wb_entrada = openpyxl.load_workbook(ruta, data_only=True)
        ws = wb_entrada.active

        fila_encabezado, mapeo = detectar_encabezados(ws, indice_alias)
        if not mapeo:
            mensaje = f"{ruta.name}: no se reconocio ningun encabezado, se omitio."
            advertencias.append(mensaje)
            emitir(mensaje, "advertencia")
            wb_entrada.close()
            continue

        if grupos_por_archivo and ruta_str in grupos_por_archivo:
            nombre_evento = grupos_por_archivo[ruta_str]
        else:
            nombre_evento, reconocido = generar_nombre_hoja(ruta.name, catalogo_formularios, alias_archivo)
            if not reconocido:
                mensaje = f"{ruta.name}: nombre de formulario no catalogado, se uso '{nombre_evento}'."
                advertencias.append(mensaje)
                emitir(mensaje, "advertencia")

        archivos_abiertos.append(
            {
                "ruta": ruta,
                "wb_entrada": wb_entrada,
                "ws": ws,
                "fila_encabezado": fila_encabezado,
                "mapeo": mapeo,
                "nombre_evento": nombre_evento,
            }
        )

    # --- Paso 2: agrupar por evento (si el proceso lo permite) y crear una
    # sola hoja de salida por grupo, con deteccion de DNI duplicado
    # compartida entre todos los archivos del mismo grupo. ---
    nombres_usados = set()
    if proceso.agrupar_archivos:
        grupos = {}
        for info in archivos_abiertos:
            grupos.setdefault(info["nombre_evento"], []).append(info)
    else:
        # Comportamiento clasico (Pregrado): cada archivo es su propia hoja,
        # con nombres forzados a ser unicos aunque calcen con el mismo evento.
        grupos = {}
        for info in archivos_abiertos:
            nombre_unico = _nombre_unico(info["nombre_evento"], nombres_usados)
            grupos[nombre_unico] = [info]

    nombres_hoja_usados = {NOMBRE_HOJA_GENERAL}
    for nombre_grupo, infos in grupos.items():
        nombre_hoja = _nombre_unico(sanear(nombre_grupo), nombres_hoja_usados)
        ws_salida = wb_salida.create_sheet(title=nombre_hoja)
        ws_salida.append(variables_plantilla)

        dnis_vistos = set()
        duplicados_grupo = 0
        filas_grupo = 0

        for info in infos:
            ruta, ws = info["ruta"], info["ws"]
            fila_encabezado, mapeo = info["fila_encabezado"], info["mapeo"]
            emitir(f"Procesando {ruta.name} -> hoja '{nombre_hoja}'...")

            dnis_duplicados = []
            registros_prueba = []
            filas_agregadas = 0
            for fila in ws.iter_rows(min_row=fila_encabezado + 1):
                if all(celda.value is None for celda in fila):
                    continue
                valores_fila = {celda.column: celda.value for celda in fila}
                fila_salida = construir_fila_salida(
                    valores_fila, mapeo, variables_plantilla, nombre_hoja,
                    campo_fecha_registro=proceso.campo_fecha_registro,
                    variable_fecha_hora_completa=proceso.variable_fecha_hora_completa,
                    variable_fecha=proceso.variable_fecha,
                    variable_dia=proceso.variable_dia,
                    variable_mes=proceso.variable_mes,
                    variable_anio=proceso.variable_anio,
                    campo_fecha_evento=proceso.campo_fecha_evento,
                    variable_mes_evento=proceso.variable_mes_evento,
                )
                if proceso.postprocesar:
                    fila_salida = proceso.postprocesar(valores_fila, mapeo, fila_salida, variables_plantilla)

                deteccion_prueba = _detectar_prueba(fila_salida, indices_prueba)
                if deteccion_prueba is not None:
                    registros_prueba.append(deteccion_prueba)
                    continue

                dni = fila_salida[indice_dni]
                if dni is not None and str(dni).strip() != "":
                    clave_dni = str(dni).strip()
                    if clave_dni in dnis_vistos:
                        dnis_duplicados.append(clave_dni)
                        continue
                    dnis_vistos.add(clave_dni)

                ws_salida.append(fila_salida)
                filas_generales.append(fila_salida)
                filas_agregadas += 1

            if registros_prueba:
                mensaje = (
                    f"{ruta.name}: se descartaron {len(registros_prueba)} fila(s) por "
                    "contener 'PRUEBA' en nombre, apellidos, DNI o correo."
                )
                advertencias.append(mensaje)
                emitir(mensaje, "advertencia")

            if dnis_duplicados:
                mensaje = (
                    f"{ruta.name}: se descartaron {len(dnis_duplicados)} fila(s) con DNI "
                    f"ya visto en la hoja '{nombre_hoja}' (puede venir de este mismo archivo "
                    "o de otro archivo fusionado en el mismo evento)."
                )
                advertencias.append(mensaje)
                emitir(mensaje, "advertencia")

            emitir(f"-> {ruta.name}: {filas_agregadas} fila(s) agregadas a '{nombre_hoja}'.")
            archivos_resultado.append(
                {
                    "archivo": ruta.name,
                    "hoja": nombre_hoja,
                    "filas": filas_agregadas,
                    "duplicados_dni": dnis_duplicados,
                    "registros_prueba": registros_prueba,
                }
            )
            total_filas += filas_agregadas
            total_duplicados += len(dnis_duplicados)
            total_prueba += len(registros_prueba)
            duplicados_grupo += len(dnis_duplicados)
            filas_grupo += filas_agregadas
            info["wb_entrada"].close()

        if len(infos) > 1:
            emitir(
                f"-> hoja '{nombre_hoja}': {len(infos)} archivo(s) fusionados, "
                f"{filas_grupo} fila(s) en total ({duplicados_grupo} duplicado(s) entre ellos)."
            )

    ws_general = wb_salida.create_sheet(title=NOMBRE_HOJA_GENERAL, index=0)
    ws_general.append(variables_plantilla)
    for fila_salida in filas_generales:
        ws_general.append(fila_salida)
    emitir(f"-> hoja '{NOMBRE_HOJA_GENERAL}': {len(filas_generales)} fila(s) agregadas.")

    emitir("Consolidado generado en memoria. Elige donde guardarlo.", "exito")

    resultado = {
        "total_filas": total_filas,
        "total_duplicados": total_duplicados,
        "total_prueba": total_prueba,
        "advertencias": advertencias,
        "archivos": archivos_resultado,
    }
    return wb_salida, resultado
