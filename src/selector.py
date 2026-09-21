import tkinter as tk

import estilo
from rutas import raiz_app

RAIZ = raiz_app()
RUTA_ICONO = RAIZ / "ico" / "macha.ico"


class VentanaSelector(tk.Tk):
    ANCHO_VENTANA = 420
    MARGEN_SUPERIOR = 70

    def __init__(self):
        super().__init__()
        estilo.registrar_fuentes()

        self.title("MACHA - Selecciona un proceso")
        self.resizable(False, False)
        self.configure(bg=estilo.BLANCO)
        if RUTA_ICONO.exists():
            self.iconbitmap(str(RUTA_ICONO))

        self.proceso_elegido = None

        self._construir_widgets()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        alto = self.winfo_reqheight()
        x = (self.winfo_screenwidth() - self.ANCHO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{alto}+{x}+{self.MARGEN_SUPERIOR}")

    def _construir_widgets(self):
        panel = tk.Frame(self, bg=estilo.BLANCO, highlightthickness=1, highlightbackground=estilo.ROJO)
        panel.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            panel, text="MACHA", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.TITULOS_BOLD, 20, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 0))
        tk.Label(
            panel, text="Selecciona un proceso para continuar", bg=estilo.BLANCO, fg=estilo.NEGRO,
            font=(estilo.BASE, 11),
        ).pack(anchor="w", padx=16, pady=(0, 16))

        botones = tk.Frame(panel, bg=estilo.BLANCO)
        botones.pack(fill="x", padx=16, pady=(0, 16))
        botones.columnconfigure(0, weight=1, uniform="opciones")
        botones.columnconfigure(1, weight=1, uniform="opciones")

        self._boton_primario(botones, "Pregrado", self._elegir_pregrado).grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._boton_marco_rojo(botones, "DPA", self._elegir_dpa).grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _boton_primario(self, master, texto, comando):
        return tk.Button(
            master, text=texto, command=comando, bg=estilo.ROJO, fg=estilo.BLANCO,
            activebackground="#c81328", activeforeground=estilo.BLANCO,
            font=(estilo.TITULOS_SEMIBOLD, 12), relief="flat", bd=0, padx=14, pady=18,
            cursor="hand2",
        )

    def _boton_marco_rojo(self, master, texto, comando):
        marco = tk.Frame(master, bg=estilo.ROJO)
        boton = tk.Button(
            marco, text=texto, command=comando, bg=estilo.BLANCO, fg=estilo.NEGRO,
            activebackground=estilo.NEGRO_10, activeforeground=estilo.NEGRO,
            font=(estilo.TITULOS_SEMIBOLD, 12), relief="flat", bd=0, padx=14, pady=16,
            cursor="hand2",
        )
        boton.pack(padx=2, pady=2, fill="both", expand=True)
        return marco

    def _elegir_pregrado(self):
        self.proceso_elegido = "pregrado"
        self.destroy()

    def _elegir_dpa(self):
        self.proceso_elegido = "dpa"
        self.destroy()


def elegir_proceso():
    """Muestra la ventana de seleccion de proceso y devuelve el proceso elegido.

    Devuelve "pregrado" o "dpa" segun lo elegido, o None si se cerro la
    ventana sin elegir.
    """
    ventana = VentanaSelector()
    ventana.mainloop()
    return ventana.proceso_elegido
