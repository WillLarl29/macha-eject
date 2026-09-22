import os
import queue
import threading
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import estilo
from consolidador import procesar_archivos
from procesos import PREGRADO
from rutas import raiz_app

RAIZ = raiz_app()
RUTA_ICONO = RAIZ / "ico" / "macha.ico"


def _rectangulo_redondeado(canvas, x1, y1, x2, y2, radio, **kwargs):
    puntos = [
        x1 + radio, y1, x2 - radio, y1, x2, y1, x2, y1 + radio,
        x2, y2 - radio, x2, y2, x2 - radio, y2, x1 + radio, y2,
        x1, y2, x1, y2 - radio, x1, y1 + radio, x1, y1,
    ]
    return canvas.create_polygon(puntos, smooth=True, **kwargs)


class Pill(tk.Canvas):
    ALTURA = 34

    def __init__(self, master, etiqueta, color_valor=estilo.NEGRO):
        super().__init__(master, height=self.ALTURA, bg=estilo.BLANCO, highlightthickness=0)
        self.etiqueta = etiqueta
        self.color_valor = color_valor
        self.valor = "0"
        self._redibujar()

    def actualizar(self, valor):
        self.valor = valor
        self._redibujar()

    def _redibujar(self):
        self.delete("all")
        fuente_etiqueta = tkfont.Font(family=estilo.BASE, size=10)
        fuente_valor = tkfont.Font(family=estilo.DATOS_SEMIBOLD, size=10)
        texto = f"{self.etiqueta}  "
        ancho_etiqueta = fuente_etiqueta.measure(texto)
        ancho_valor = fuente_valor.measure(self.valor)
        ancho_total = ancho_etiqueta + ancho_valor + 32
        self.config(width=ancho_total)
        _rectangulo_redondeado(
            self, 1, 1, ancho_total - 1, self.ALTURA - 1, 15,
            outline=estilo.ROJO, fill=estilo.BLANCO,
        )
        self.create_text(16, self.ALTURA / 2, text=texto, anchor="w", font=fuente_etiqueta, fill=estilo.NEGRO)
        self.create_text(
            16 + ancho_etiqueta, self.ALTURA / 2, text=self.valor, anchor="w",
            font=fuente_valor, fill=self.color_valor,
        )


class FilaArchivo(tk.Frame):
    def __init__(self, master, datos):
        super().__init__(master, bg=estilo.BLANCO, highlightthickness=1, highlightbackground=estilo.ROJO)
        self.abierto = False

        cabecera = tk.Frame(self, bg=estilo.BLANCO, cursor="hand2")
        cabecera.pack(fill="x", padx=12, pady=8)

        tk.Label(
            cabecera, text=datos["archivo"], bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.DATOS, 10), anchor="w",
        ).pack(side="left")

        cantidad_dup = len(datos["duplicados_dni"])
        cantidad_prueba = len(datos.get("registros_prueba", []))
        partes_etiqueta = []
        if cantidad_dup > 0:
            partes_etiqueta.append(f"{cantidad_dup} duplicados")
        if cantidad_prueba > 0:
            partes_etiqueta.append(f"{cantidad_prueba} de prueba")
        if partes_etiqueta:
            texto_etiqueta, color_etiqueta = " · ".join(partes_etiqueta) + " removidos", estilo.ROJO
        else:
            texto_etiqueta, color_etiqueta = "0 removidos", estilo.NEGRO

        self.chevron = tk.Label(cabecera, text="⌄", bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.TITULOS_MEDIUM, 11))
        self.chevron.pack(side="right")
        tk.Label(
            cabecera, text=texto_etiqueta, bg=estilo.BLANCO, fg=color_etiqueta,
            font=(estilo.BASE_SEMIBOLD, 9),
        ).pack(side="right", padx=(0, 8))

        self.cuerpo = tk.Frame(self, bg=estilo.BLANCO)
        if cantidad_dup > 0:
            primeros = datos["duplicados_dni"][:3]
            tk.Label(
                self.cuerpo,
                text=f"DNI duplicados descartados (primeros {len(primeros)} de {cantidad_dup}):",
                bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.BASE, 9), anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 4))
            for dni in primeros:
                tk.Label(
                    self.cuerpo, text=str(dni), bg=estilo.BLANCO, fg=estilo.NEGRO,
                    font=(estilo.DATOS, 10), highlightthickness=1, highlightbackground=estilo.ROJO,
                    padx=8, pady=4, anchor="w",
                ).pack(fill="x", padx=12, pady=2)

        if cantidad_prueba > 0:
            primeros_prueba = datos["registros_prueba"][:3]
            tk.Label(
                self.cuerpo,
                text=f"Descartados por 'PRUEBA' (primeros {len(primeros_prueba)} de {cantidad_prueba}):",
                bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.BASE, 9), anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 4))
            for descripcion in primeros_prueba:
                tk.Label(
                    self.cuerpo, text=str(descripcion), bg=estilo.BLANCO, fg=estilo.NEGRO,
                    font=(estilo.DATOS, 10), highlightthickness=1, highlightbackground=estilo.ROJO,
                    padx=8, pady=4, anchor="w",
                ).pack(fill="x", padx=12, pady=2)

        if cantidad_dup == 0 and cantidad_prueba == 0:
            tk.Label(
                self.cuerpo, text="Sin registros removidos en este archivo.", bg=estilo.BLANCO,
                fg=estilo.NEGRO, font=(estilo.BASE, 9), anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 8))

        cabecera.bind("<Button-1>", self._alternar)
        for hijo in cabecera.winfo_children():
            hijo.bind("<Button-1>", self._alternar)

    def _alternar(self, _evento=None):
        self.abierto = not self.abierto
        if self.abierto:
            self.cuerpo.pack(fill="x")
            self.chevron.config(text="⌃")
        else:
            self.cuerpo.pack_forget()
            self.chevron.config(text="⌄")


class VentanaPrincipal(tk.Tk):
    def __init__(self, proceso=PREGRADO):
        super().__init__()
        estilo.registrar_fuentes()

        self.proceso = proceso
        self.ANCHO_VENTANA = 1040

        self.title(f"{proceso.titulo} - {proceso.subtitulo}")
        self.minsize(700, 200)
        self.configure(bg=estilo.BLANCO)
        if RUTA_ICONO.exists():
            self.iconbitmap(str(RUTA_ICONO))

        self.rutas_entrada = []
        self.libro_generado = None
        self.ruta_salida_generada = None
        self.fecha_generacion = None
        self.volver_seleccionado = False
        self.cola = queue.Queue()
        self._id_after_cola = None

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._construir_area_scroll()
        self._construir_widgets()
        self._actualizar_boton_generar()

        self._colocar_ventana_inicial()

    MARGEN_SUPERIOR = 70

    def _alto_maximo(self):
        return self.winfo_screenheight() - self.MARGEN_SUPERIOR - 40

    def _colocar_ventana_inicial(self):
        self.update_idletasks()
        bbox = self._canvas_principal.bbox("all")
        alto_contenido = (bbox[3] - bbox[1] + 2) if bbox else 500
        alto = min(alto_contenido, self._alto_maximo())
        x = (self.winfo_screenwidth() - self.ANCHO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{alto}+{x}+{self.MARGEN_SUPERIOR}")

    def _ajustar_alto_contenido(self, _evento=None):
        """Recalcula la altura de la ventana segun el contenido actual, sin mover
        ni cambiar el ancho (para no pelearse con un arrastre manual del usuario)."""
        self._canvas_principal.configure(scrollregion=self._canvas_principal.bbox("all"))
        bbox = self._canvas_principal.bbox("all")
        if not bbox:
            return
        alto_contenido = bbox[3] - bbox[1] + 2
        alto_maximo = self._alto_maximo()
        alto_final = min(alto_contenido, alto_maximo)

        if abs(self.winfo_height() - alto_final) > 2:
            self.geometry(f"{self.winfo_width()}x{alto_final}")

        if alto_contenido > alto_maximo:
            if not self._scrollbar.winfo_manager():
                self._scrollbar.pack(side="right", fill="y")
        else:
            if self._scrollbar.winfo_manager():
                self._scrollbar.pack_forget()
            self._canvas_principal.yview_moveto(0)

    def _construir_area_scroll(self):
        contenedor = tk.Frame(self, bg=estilo.BLANCO)
        contenedor.pack(fill="both", expand=True)

        canvas = tk.Canvas(contenedor, bg=estilo.BLANCO, highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar = scrollbar
        self._canvas_principal = canvas

        self.marco_contenido = tk.Frame(canvas, bg=estilo.BLANCO)
        ventana_id = canvas.create_window((0, 0), window=self.marco_contenido, anchor="nw")

        self.marco_contenido.bind("<Configure>", self._ajustar_alto_contenido)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(ventana_id, width=e.width))

        def _en_rueda(evento):
            if scrollbar.winfo_manager():
                canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _en_rueda)

    def _panel(self, master, texto_titulo):
        panel = tk.Frame(master, bg=estilo.BLANCO, highlightthickness=1, highlightbackground=estilo.ROJO)
        panel.pack(fill="x", pady=(0, 12))
        tk.Label(
            panel, text=texto_titulo, bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_SEMIBOLD, 11), anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 8))
        return panel

    def _boton(self, master, texto, comando, estilo_boton="secundario"):
        if estilo_boton == "primario":
            return tk.Button(
                master, text=texto, command=comando, bg=estilo.ROJO, fg=estilo.BLANCO,
                activebackground="#c81328", activeforeground=estilo.BLANCO,
                font=(estilo.TITULOS_SEMIBOLD, 11), relief="flat", bd=0, padx=14, pady=10,
                disabledforeground=estilo.BLANCO, cursor="hand2",
            )
        return tk.Button(
            master, text=texto, command=comando, bg=estilo.BLANCO, fg=estilo.NEGRO,
            activebackground=estilo.NEGRO_10, activeforeground=estilo.NEGRO,
            font=(estilo.BASE, 10), relief="flat", bd=0, padx=10, pady=6,
            highlightthickness=1, highlightbackground=estilo.NEGRO_20, cursor="hand2",
        )

    def _boton_marco_rojo(self, master, texto, comando):
        marco = tk.Frame(master, bg=estilo.ROJO)
        boton = tk.Button(
            marco, text=texto, command=comando, bg=estilo.BLANCO, fg=estilo.NEGRO,
            activebackground=estilo.NEGRO_10, activeforeground=estilo.NEGRO,
            font=(estilo.BASE, 10), relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
        )
        boton.pack(padx=2, pady=2, fill="both", expand=True)
        return marco

    def _construir_widgets(self):
        self.marco_contenido.columnconfigure(0, weight=1, uniform="columnas")
        self.marco_contenido.columnconfigure(1, weight=0)
        self.marco_contenido.columnconfigure(2, weight=1, uniform="columnas")
        self.marco_contenido.rowconfigure(0, weight=1)

        columna_izquierda = tk.Frame(self.marco_contenido, bg=estilo.BLANCO)
        columna_izquierda.grid(row=0, column=0, sticky="nsew", padx=(14, 10), pady=14)

        tk.Frame(self.marco_contenido, width=1, bg=estilo.ROJO).grid(row=0, column=1, sticky="ns", pady=14)

        columna_derecha = tk.Frame(self.marco_contenido, bg=estilo.BLANCO)
        columna_derecha.grid(row=0, column=2, sticky="nsew", padx=(10, 14), pady=14)

        encabezado = tk.Frame(columna_izquierda, bg=estilo.BLANCO)
        encabezado.pack(fill="x", pady=(0, 10))
        self._boton_marco_rojo(encabezado, "← Volver", self._volver).pack(anchor="w", pady=(0, 10))
        tk.Label(encabezado, text=self.proceso.titulo, bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.TITULOS_BOLD, 20, "bold")).pack(anchor="w")
        tk.Label(encabezado, text=self.proceso.subtitulo, bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.BASE, 11)).pack(anchor="w")

        panel_archivos = self._panel(columna_izquierda, "1. Archivos de entrada")
        fila = tk.Frame(panel_archivos, bg=estilo.BLANCO)
        fila.pack(fill="x", padx=14, pady=(0, 14))
        self.lista_archivos = tk.Listbox(
            fila, height=6, selectmode="extended", font=(estilo.DATOS, 10),
            highlightthickness=1, highlightbackground=estilo.ROJO, bd=0,
        )
        self.lista_archivos.pack(side="left", fill="both", expand=True)
        columna_botones = tk.Frame(fila, bg=estilo.BLANCO)
        columna_botones.pack(side="left", fill="y", padx=(10, 0))
        self._boton_marco_rojo(columna_botones, "Agregar...", self._agregar_archivos).pack(fill="x", pady=3)
        self._boton_marco_rojo(columna_botones, "Quitar seleccionados", self._quitar_seleccionados).pack(fill="x", pady=3)
        self._boton_marco_rojo(columna_botones, "Limpiar todo", self._limpiar_archivos).pack(fill="x", pady=3)

        self.boton_generar = self._boton(columna_izquierda, "2. Generar consolidado", self._generar, "primario")
        self.boton_generar.pack(fill="x", pady=(0, 14))

        acciones = tk.Frame(columna_izquierda, bg=estilo.BLANCO)
        acciones.pack(fill="x", pady=(0, 14))
        self.btn_guardar_abrir = self._boton(acciones, "Guardar consolidado...", self._guardar_o_abrir, "primario")
        self.btn_guardar_abrir.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.btn_guardar_abrir.config(state="disabled")
        marco_btn_ver_log = self._boton_marco_rojo(acciones, "Ver log de procesamiento", self._alternar_log)
        marco_btn_ver_log.pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.panel_resultado = tk.Frame(columna_derecha, bg=estilo.BLANCO, highlightthickness=1, highlightbackground=estilo.ROJO)
        self.panel_resultado.pack(fill="x", pady=(0, 14))

        tk.Label(
            self.panel_resultado, text="3. Resultado y Progreso", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_SEMIBOLD, 11), anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 8))

        self.marco_placeholder = tk.Frame(self.panel_resultado, bg=estilo.BLANCO)
        self.marco_placeholder.pack(fill="x")
        self.label_placeholder = tk.Label(
            self.marco_placeholder, text="Aun no se genero ningun consolidado.",
            bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.BASE, 10),
        )
        self.label_placeholder.pack(padx=14, pady=24)

        self.marco_resultado_real = tk.Frame(self.panel_resultado, bg=estilo.BLANCO)

        estado = tk.Frame(self.marco_resultado_real, bg=estilo.BLANCO)
        estado.pack(fill="x", padx=14)
        tk.Label(estado, text="✓", bg=estilo.BLANCO, fg=estilo.NEGRO, font=(estilo.TITULOS_BOLD, 13, "bold")).pack(side="left")
        tk.Label(
            estado, text=" Consolidacion finalizada", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_MEDIUM, 12),
        ).pack(side="left")

        fila_pills = tk.Frame(self.marco_resultado_real, bg=estilo.BLANCO)
        fila_pills.pack(fill="x", padx=14, pady=12)
        self.pill_filas = Pill(fila_pills, "Filas Consolidadas:")
        self.pill_filas.pack(anchor="w", pady=(0, 6))
        self.pill_duplicados = Pill(fila_pills, "Total Duplicados Removidos:", color_valor=estilo.ROJO)
        self.pill_duplicados.pack(anchor="w", pady=(0, 6))
        self.pill_prueba = Pill(fila_pills, "Total Registros de Prueba Removidos:", color_valor=estilo.ROJO)
        self.pill_prueba.pack(anchor="w")

        tk.Label(
            self.marco_resultado_real, text="Detalle por archivo", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_MEDIUM, 10), anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 6))

        self.contenedor_acordeon = tk.Frame(self.marco_resultado_real, bg=estilo.BLANCO)
        self.contenedor_acordeon.pack(fill="x", padx=14, pady=(0, 14))

        self.panel_log = tk.Frame(columna_derecha, bg=estilo.BLANCO, highlightthickness=1, highlightbackground=estilo.ROJO)
        tk.Label(
            self.panel_log, text="Log de procesamiento", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_SEMIBOLD, 11), anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 8))
        self.texto_log = tk.Text(
            self.panel_log, height=8, state="disabled", wrap="word", font=(estilo.DATOS, 9),
            bg=estilo.BLANCO, fg=estilo.NEGRO, bd=0, highlightthickness=0,
        )
        self.texto_log.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        for tipo, color in {"info": estilo.NEGRO, "advertencia": estilo.AMBAR, "error": estilo.ROJO, "exito": estilo.VERDE}.items():
            self.texto_log.tag_configure(tipo, foreground=color)

    # -- archivos de entrada --------------------------------------------

    def _agregar_archivos(self):
        rutas = filedialog.askopenfilenames(
            title="Selecciona los Excels de entrada", filetypes=[("Archivos Excel", "*.xlsx")]
        )
        for ruta in rutas:
            if ruta not in self.rutas_entrada:
                self.rutas_entrada.append(ruta)
                self.lista_archivos.insert("end", Path(ruta).name)
        self._actualizar_boton_generar()

    def _quitar_seleccionados(self):
        for indice in reversed(self.lista_archivos.curselection()):
            self.lista_archivos.delete(indice)
            del self.rutas_entrada[indice]
        self._actualizar_boton_generar()

    def _limpiar_archivos(self):
        self.lista_archivos.delete(0, "end")
        self.rutas_entrada.clear()
        self._actualizar_boton_generar()

    def _actualizar_boton_generar(self):
        self.boton_generar.config(state="normal" if self.rutas_entrada else "disabled")

    # -- procesamiento ----------------------------------------------------

    def _generar(self):
        self.boton_generar.config(state="disabled")
        self.marco_resultado_real.pack_forget()
        self.label_placeholder.config(text="Procesando...")
        self.marco_placeholder.pack(fill="x")
        self.panel_log.pack_forget()
        self.libro_generado = None
        self.ruta_salida_generada = None
        self.fecha_generacion = datetime.now()
        self.btn_guardar_abrir.config(text="Guardar consolidado...", state="disabled")
        self.texto_log.config(state="normal")
        self.texto_log.delete("1.0", "end")
        self.texto_log.config(state="disabled")

        rutas = list(self.rutas_entrada)
        hilo = threading.Thread(target=self._procesar_en_hilo, args=(rutas,), daemon=True)
        hilo.start()
        self._id_after_cola = self.after(100, self._revisar_cola)

    def _procesar_en_hilo(self, rutas):
        def on_evento(mensaje, tipo="info"):
            self.cola.put(("log", mensaje, tipo))

        try:
            libro, resultado = procesar_archivos(rutas, on_evento=on_evento, proceso=self.proceso)
            self.cola.put(("resultado", (libro, resultado), None))
        except Exception as error:
            self.cola.put(("error", str(error), None))
        finally:
            self.cola.put(("fin", None, None))

    def _revisar_cola(self):
        try:
            while True:
                tipo_evento, dato, tipo_log = self.cola.get_nowait()
                if tipo_evento == "log":
                    self._escribir_log(dato, tipo_log)
                elif tipo_evento == "resultado":
                    libro, resultado = dato
                    self._mostrar_resultado(libro, resultado)
                elif tipo_evento == "error":
                    self._escribir_log(f"Error: {dato}", "error")
                    self.label_placeholder.config(text="Ocurrio un error. Revisa el log de procesamiento.")
                    self.panel_log.pack(fill="both", expand=True, pady=(0, 14))
                elif tipo_evento == "fin":
                    self.boton_generar.config(state="normal")
        except queue.Empty:
            pass
        self._id_after_cola = self.after(100, self._revisar_cola)

    def _escribir_log(self, mensaje, tipo="info"):
        self.texto_log.config(state="normal")
        self.texto_log.insert("end", mensaje + "\n", tipo or "info")
        self.texto_log.see("end")
        self.texto_log.config(state="disabled")

    def _mostrar_resultado(self, libro, resultado):
        self.libro_generado = libro
        self.pill_filas.actualizar(f"{resultado['total_filas']:,}")
        self.pill_duplicados.actualizar(f"{resultado['total_duplicados']:,}")
        self.pill_prueba.actualizar(f"{resultado['total_prueba']:,}")

        for widget in self.contenedor_acordeon.winfo_children():
            widget.destroy()
        for archivo in resultado["archivos"]:
            FilaArchivo(self.contenedor_acordeon, archivo).pack(fill="x", pady=(0, 8))

        self.marco_placeholder.pack_forget()
        self.marco_resultado_real.pack(fill="x")
        self.btn_guardar_abrir.config(state="normal")

    def _guardar_o_abrir(self):
        if self.ruta_salida_generada:
            os.startfile(self.ruta_salida_generada)
            return

        fecha = (self.fecha_generacion or datetime.now()).strftime("%Y-%m-%d")
        nombre_inicial = f"{self.proceso.prefijo_salida}-{fecha}.xlsx"
        ruta = filedialog.asksaveasfilename(
            title="Guardar consolidado como", defaultextension=".xlsx",
            filetypes=[("Archivo Excel", "*.xlsx")], initialfile=nombre_inicial,
        )
        if not ruta:
            return
        self.libro_generado.save(ruta)
        self.ruta_salida_generada = ruta
        self.btn_guardar_abrir.config(text="Abrir Archivo Consolidado")
        self._escribir_log(f"Consolidado guardado en {ruta}", "exito")

    def _alternar_log(self):
        if self.panel_log.winfo_manager():
            self.panel_log.pack_forget()
        else:
            self.panel_log.pack(fill="both", expand=True, pady=(0, 14))

    # -- navegacion ---------------------------------------------------------

    def _cancelar_polling(self):
        """Cancela el after() pendiente de _revisar_cola antes de destruir la
        ventana: si no se cancela, puede dispararse despues de destroy() (p.ej.
        ya con otra ventana de proceso abierta) y romper con
        'invalid command name ..._revisar_cola'."""
        if self._id_after_cola is not None:
            try:
                self.after_cancel(self._id_after_cola)
            except tk.TclError:
                pass
            self._id_after_cola = None

    def _volver(self):
        self._cancelar_polling()
        self.volver_seleccionado = True
        self.destroy()

    def _cerrar(self):
        self._cancelar_polling()
        self.destroy()


def iniciar(proceso=PREGRADO):
    """Abre la ventana principal para el proceso dado y devuelve True si el
    usuario pidio volver al selector de procesos, o False si cerro la ventana."""
    app = VentanaPrincipal(proceso)
    app.mainloop()
    return app.volver_seleccionado
