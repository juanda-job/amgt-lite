import pandas as pd
import unicodedata
from pathlib import Path
from datetime import datetime

def remove_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def to_snake(name: str) -> str:
    s = name.strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace("-", "_").replace(" ", "_").replace(".", "_").replace("/", "_")
    s = "_".join([p for p in s.lower().split("_") if p])
    return s.replace("'","")

def normalize_text(x):
    if pd.isna(x):
        return x
    x = str(x).strip().upper()
    x = remove_accents(x)
    x = x.lstrip('-')
    return x

def normalizar_y_validar_fecha(fecha_str: str) -> str:
    try:
        partes = fecha_str.strip().split('/')
        if len(partes) != 3:
            return ""
        dia = partes[0].zfill(2)
        mes = partes[1].zfill(2)
        anio = partes[2].zfill(4)
        fecha_normalizada = f"{dia}/{mes}/{anio}"
        datetime.strptime(fecha_normalizada, "%d/%m/%Y")
        return fecha_normalizada
    except Exception:
        return ""

def generarInforme(archivo):
    """
    Procesa un archivo CSV o Excel y devuelve un DataFrame agrupado:
    - Columnas: documento, numero, fecha, tercero, credito
    - Limpieza de vacíos y normalización de fecha
    - Agrupación sumando 'credito'
    """
    try:
        # Detectar tipo de archivo por nombre
        nombre = getattr(archivo, "name", str(archivo))
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo, sep=";", encoding="latin1")
        elif nombre.endswith((".xlsx", ".xls")):
            df = pd.read_excel(archivo, engine="openpyxl")
        else:
            raise ValueError(f"Formato no soportado: {Path(nombre).suffix}")

        # Normalizar nombres de columnas
        df.columns = [to_snake(c) for c in df.columns]

        columnas_deseadas = ['documento', 'numero', 'fecha', 'tercero', 'credito']
        for col in columnas_deseadas:
            if col not in df.columns:
                raise ValueError(f"Falta columna requerida: {col}")

        df = df[columnas_deseadas]

        # Rellenar documento vacío
        df['documento'] = df['documento'].replace("", pd.NA).ffill()

        # Reemplazar vacíos en numero y tercero
        df[['numero', 'tercero']] = df[['numero', 'tercero']].replace("", pd.NA)

        # Eliminar filas donde ambas columnas estén vacías
        df = df.dropna(subset=['numero', 'tercero'], how='all')

        # Filtrar crédito distinto de 0
        df = df[df['credito'] != 0]

        # Normalizar fechas
        df['fecha'] = df['fecha'].apply(normalizar_y_validar_fecha)

        # Conversión numérica segura
        df['credito'] = pd.to_numeric(df['credito'], errors="coerce").fillna(0)

        # Agrupación
        df_grouped = (
            df.groupby(["documento", "numero", "tercero", "fecha"], as_index=False)
              .agg({"credito": "sum"})
        )

        return df_grouped

    except Exception as e:
        raise ValueError(f"Error al limpiar datos: {str(e)}")