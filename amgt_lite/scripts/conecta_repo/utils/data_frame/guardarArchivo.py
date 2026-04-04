from pathlib import Path
import os

def guardar_archivo(archivo):
    base = Path(__file__).parent
    carpeta_destino = base / "MyScripts" / "data_set"
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_destino = carpeta_destino/"dataset.csv"

    with open(ruta_destino, 'wb+') as destino:
        for chunk in archivo.chunks():
            destino.write(chunk)

    return ruta_destino