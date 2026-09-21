from gui import iniciar
from procesos import DPA, PREGRADO
from selector import elegir_proceso

PROCESOS = {"pregrado": PREGRADO, "dpa": DPA}

if __name__ == "__main__":
    while True:
        eleccion = elegir_proceso()
        proceso = PROCESOS.get(eleccion)
        if proceso is None:
            break
        if not iniciar(proceso):
            break
