# MACHA — Consolidador de Excels

Herramienta (ejecutable .exe) que permite elegir varios Excels de entrada, normaliza cada uno
segun la plantilla de encabezados (`plantilla/Encabezados.xlsx`) y genera un unico Excel de
salida con una hoja por cada archivo de entrada consolidado y normalizado.

## Organizacion de carpetas

```
MACHA/
├── ico/                        Icono del ejecutable (existente)
│   └── macha.ico
├── plantilla/                  Plantilla de encabezados de salida (existente)
│   └── Encabezados.xlsx        21 variables (fila 1) que debe tener toda hoja de salida
├── src/                        Codigo fuente de la aplicacion (Fase 2 en adelante)
├── config/
│   └── alias_encabezados.json  Mapeo encabezado-origen -> variable-plantilla (se completa
│                                revisando archivos reales, nunca por inferencia)
├── muestras/                   Excels de entrada de ejemplo para definir los mapeos (no se
│                                empaqueta en el .exe final)
├── salida/                     Carpeta por defecto para el Excel consolidado generado
├── tests/                      Pruebas con los archivos de muestras/
├── build/, dist/                Generados por PyInstaller (no se versionan)
├── requirements.txt
└── macha.spec                  Spec de PyInstaller (se crea en la Fase 4)
```

## Decisiones ya confirmadas

- El usuario elige los archivos de entrada mediante un dialogo de seleccion al ejecutar el .exe
  (no hay carpeta fija de entrada).
- Cada variable de la plantilla puede estar ubicada en distinta columna segun el archivo de
  origen: se debe revisar la fila 1 y, si no aparece ahi, la fila 2, para ubicar cada variable
  por su encabezado (no por posicion fija).
- Cada Excel de entrada aporta una sola hoja al consolidado (se toma su hoja activa/primera
  hoja); el nombre de esa hoja se deriva del nombre del archivo.

## Mapeo definido hasta ahora

**Mapeo general de la plataforma ExitoESAN** (16 columnas fijas: Fecha de Registro, Nombre,
Apellido Paterno, Apellido Materno, DNI, Celular, Correo Electrónico, Información de Cookie,
Acepta Trámite de Datos, Acepta Publicidad, Carrera, Modalidad, Año que cursa, Participante,
Edad, Acepta Participación), confirmado con el archivo real "Comunícate con UE - ExitoESAN" y
verificado contra una captura comparativa de otros 4 formularios (OPEN DAY, Carreras Comunicate,
BECA BCP, Beca Huellas): todos comparten el mismo vocabulario de encabezados, solo que cada
formulario usa un subconjunto (las columnas que no le aplican quedan sin encabezado). Registrado
en `config/alias_encabezados.json`:

- Directo por encabezado: PARTICIPANTE, NOMBRE, AP. PATERNO, APE. MATERNO, DNI, CORREO,
  CELULAR, AÑO CURSANDO, MODALIDAD DE ADMISIÓN, CARRERA DE INTERÉS, ACEPTA PUBLICIDAD,
  FECHA DE REGISTRO.
- ACEPTA POLÍTICAS ← columna "Acepta Trámite de Datos" (la columna "Acepta Participación" de
  este archivo no se usa, no tiene destino en la plantilla).
- PROCEDENCIA ← columna "Información de Cookie" (datos de campaña de origen).
- FORMULARIO: no viene en el archivo; se llena con el nombre de la hoja/formulario, igual para
  todas las filas de esa hoja.
- FECHA DE REGISTRO2 = igual a FECHA DE REGISTRO (fecha y hora completas). FECHA = solo la
  parte de fecha (sin hora). DIA, MES, AÑO = partes numéricas extraídas de esa misma fecha.
- CONSULTAS: ningun formulario visto hasta ahora trae esa columna; queda vacía.
- Columna "Edad" del archivo: se descarta cuando no se usa (sin variable equivalente en la
  plantilla).
- **Regla general**: si el encabezado de una variable no aparece en un archivo de entrada, esa
  variable queda vacía para toda esa hoja (aplica a cualquiera de las 21 variables).
- **Deteccion a prueba de errores**: la columna de cada variable NO es fija entre archivos, asi
  que la deteccion debe hacerse por texto de encabezado (normalizado: sin tildes, sin
  mayus/minus, sin espacios sobrantes) exigiendo coincidencia EXACTA contra `alias_conocidos`,
  nunca coincidencia parcial, para no asignar una variable equivocada.

## Regla de nombre de hoja (definida)

- El nombre de hoja es el nombre de formulario **tal cual aparece** en
  `config/nombres_hojas_conocidos.json` (sin recortar sufijos como "- ExitoESAN"/"- UESAN"), que
  se identifica buscando cual de esos 23 nombres es el inicio del nombre de archivo (el resto del
  nombre de archivo es la fecha/hora del export, se descarta).
- Si el nombre resultante supera 31 caracteres o tiene alguno de los caracteres invalidos de
  Excel (`: \ / ? * [ ]`), se trunca a 31 y se sanean esos caracteres. Implementado en
  `src/nombre_hoja.py`.
- **Formulario no catalogado (confirmado)**: si el nombre de archivo no coincide con ningun
  formulario de `config/nombres_hojas_conocidos.json`, igual se procesa: `src/nombre_hoja.py`
  recorta la fecha/hora final del nombre de archivo para armar el nombre de hoja, y
  `consolidador.py` lo reporta como advertencia (no detiene el proceso).
- **DNI duplicado dentro de una misma hoja (confirmado)**: si dos o mas filas de la MISMA hoja
  tienen el mismo DNI, se conserva solo la primera y se descartan las siguientes, reportando una
  advertencia con la cantidad descartada. El mismo DNI en hojas distintas (formularios distintos)
  no se considera duplicado. Filas sin DNI nunca se consideran duplicadas entre si. Implementado
  en `consolidador.procesar_archivos`.

## Pendiente de definir (no se infiere, se consulta antes de implementar)

- **Formularios que no sigan el esquema ExitoESAN de 16 columnas**: si aparece un archivo con
  encabezados distintos a los ya conocidos, se revisa aparte antes de asumir nada.

## Plan de implementacion

1. **Fase 0 — Base del proyecto** (hecho): estructura de carpetas, `requirements.txt`,
   `config/alias_encabezados.json` con las 21 variables de la plantilla listas para mapear.
2. **Fase 1 — Definicion de mapeo** (hecho): mapeo general ExitoESAN definido y registrado en
   `config/alias_encabezados.json`; regla de nombre de hoja definida (ver seccion arriba).
3. **Fase 2 — Deteccion y normalizacion** (hecho, probado con el archivo real de `muestras/`):
   codigo en `src/` — `texto.py` (normalizacion de encabezados), `plantilla.py` (lee las 21
   variables de `plantilla/Encabezados.xlsx`), `config_mapeo.py` (carga los JSON de `config/`),
   `encabezados.py` (detecta fila y columnas de encabezado por texto), `mapeo.py` (arma cada fila
   de salida, incluye los campos calculados de fecha), `nombre_hoja.py` (nombre de hoja) y
   `consolidador.py` (orquesta todo y genera el libro de salida). Script de prueba:
   `tests/probar_consolidacion.py`.
4. **Fase 3 — GUI** (hecho): `src/gui.py` define `VentanaPrincipal` con el sistema de diseno
   pedido (rojo `#f01830` / negro `#040404` / blanco, tipografias libres Inter, Raleway y Space
   Grotesk registradas solo para el proceso via `estilo.registrar_fuentes()`, sin instalarlas en
   el sistema — ver `src/estilo.py` y `src/assets/fonts/`). Flujo: 1) agregar archivos de
   entrada, 2) Generar consolidado (procesa en memoria, sin pedir destino todavia), 3) panel de
   Resultado y Progreso con pills (filas consolidadas / duplicados removidos) y un acordeon por
   archivo con los primeros 3 DNI descartados por duplicado. El boton final dice "Guardar
   consolidado..." (abre el dialogo de guardado recien ahi y escribe el archivo) y una vez
   guardado cambia a "Abrir Archivo Consolidado"; "Ver Log de Procesamiento" muestra el avance
   tecnico crudo. Todo el contenido va dentro de un area con scroll. El procesamiento corre en un
   hilo aparte para no congelar la ventana. `src/main.py` solo llama a `gui.iniciar()`. Se
   ejecuta con `python src/main.py`.
   - Se probo primero con pywebview (vista HTML/CSS local) para lograr el diseno con mayor
     fidelidad, pero se descarto: el SDK de WebView2 que trae pywebview es incompatible con el
     WebView2 Runtime instalado en la maquina de prueba (falla con errores COM al iniciar). Se
     opto por tkinter, ya validado como estable en este equipo.
5. **Fase 4 — Empaquetado como .exe** (siguiente): `macha.spec` de PyInstaller con el icono
   `ico/macha.ico` y los recursos (`plantilla/`, `config/`) empaquetados; generar y probar el
   ejecutable de forma independiente (sin Python instalado).
6. **Fase 5 — Pruebas y ajustes**: probar con mas archivos reales y casos limite (encabezados no
   reconocibles, nombre de hoja duplicado, formularios no catalogados, etc.).

## Como continuar

Fases 1, 2 y 3 completas. Siguiente: Fase 4 (empaquetado como .exe con PyInstaller).
