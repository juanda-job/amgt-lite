import pandas as pd
import unicodedata
from pathlib import Path
from tkinter import Tk, filedialog
import os
import shutil
from datetime import datetime

MESES = {
    "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
    "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
    "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
}

def to_snake(name: str) -> str:
    s = name.strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace("-", "_").replace(" ", "_").replace(".", "_").replace("/", "_")
    s = "_".join([p for p in s.lower().split("_") if p])
    return s.replace("'","")

def remove_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def normalizar_y_validar_fecha(fecha_str: str) -> str:
    try:
        partes = fecha_str.strip().split('-')
        if len(partes) != 3:
            raise ValueError("Formato incorrecto")
        dia = partes[0].zfill(2)
        mes = partes[1].zfill(2)
        anio = partes[2].zfill(4)
        fecha_normalizada = f"{dia}/{mes}/{anio}"
        datetime.strptime(fecha_normalizada, "%d/%m/%Y")
        return fecha_normalizada
    except Exception:
        return ""

def normalize_text(x):
    if pd.isna(x):
        return x
    x = str(x).strip().upper()
    x = remove_accents(x)
    x = x.lstrip('-')
    return x
import re

def limpiar_nombre(nombre: str) -> str:
    # Reemplaza caracteres inválidos por "_"
    return re.sub(r'[\\/:*?"<>|]', '_', nombre).strip()

def iniciales_tipo(tipo: str) -> str:
    """Devuelve iniciales de cada palabra hasta el primer '-'"""
    if not tipo:
        return ""
    partes = tipo.split('-')[0].split()
    return ''.join(p[0].upper() for p in partes if p)

def ordenar(ruta_carpeta, archivo, modo):
    msj = ""  # inicializamos el mensaje acumulador
    msj=""
    try:
        # Detectar tipo de archivo por nombre
        nombre = getattr(archivo, "name", str(archivo))
        if nombre.endswith(".csv"):
            df_dian = pd.read_csv(archivo, sep=";", encoding="latin1")
        elif nombre.endswith((".xlsx", ".xls")):
            df_dian = pd.read_excel(archivo, engine="openpyxl")
        else:
            raise ValueError(f"Formato no soportado: {Path(nombre).suffix}")
        
        df_dian.columns = [to_snake(c) for c in df_dian.columns]
        df_dian = df_dian.rename(columns={"cufe_cude": "cufe"})
        columnas_deseadas = ['fecha_emision', 'cufe', 'prefijo', 'folio',
                             'tipo_de_documento', 'nombre_emisor', 'nombre_receptor']
        df = df_dian[columnas_deseadas].copy()

        # Normalizar
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(normalize_text)
        df['fecha_emision'] = df['fecha_emision'].apply(normalizar_y_validar_fecha)

        # Crear subcarpetas
        pdf_dir = Path(ruta_carpeta) / "pdf"
        xml_dir = Path(ruta_carpeta) / "xml"
        comp_dir = Path(ruta_carpeta) / "comprimidos"
        pdf_dir.mkdir(exist_ok=True)
        xml_dir.mkdir(exist_ok=True)
        comp_dir.mkdir(exist_ok=True)

        # Recorrer archivos
        for archivo in os.listdir(ruta_carpeta):
            ruta_archivo = Path(ruta_carpeta) / archivo

            if ruta_archivo.is_dir():
                continue  # saltar carpetas

            nombre, ext = os.path.splitext(archivo)
            ext = ext.lower()

            # Buscar en df por cufe
            fila = df[df['cufe'] == normalize_text(nombre)]
            if fila.empty:
                continue  # no encontrado, dejarlo ahí

            fila = fila.iloc[0]
            tipo_doc = limpiar_nombre(fila['tipo_de_documento'])
            prefijo = str(fila['prefijo']) if pd.notna(fila['prefijo']) else ""
            folio = str(fila['folio']) if pd.notna(fila['folio']) else ""
            fecha = fila['fecha_emision']

            if fecha:
                partes = fecha.split('/')
                mes_anio = f"{MESES.get(partes[1].zfill(2), partes[1])} {partes[2]}"
            else:
                mes_anio = "??"

            if ext == ".pdf":
                iniciales = iniciales_tipo(tipo_doc)
                if modo == "compras":
                    nombre_persona = limpiar_nombre(fila['nombre_emisor'])
                else:
                    nombre_persona = limpiar_nombre(fila['nombre_receptor'])

                nuevo_nombre = f"{iniciales}-{nombre_persona}-{prefijo}{folio}-{mes_anio}.pdf"
                destino = pdf_dir / nuevo_nombre
                try:
                    shutil.move(str(ruta_archivo), destino)
                    msj += f"\nPDF movido y renombrado: {destino}"
                except Exception as e:
                    msj += f"\nError moviendo {archivo}: {e}"

            elif ext == ".xml":
                subdir = xml_dir / tipo_doc
                subdir.mkdir(exist_ok=True)
                destino = subdir / archivo
                try:
                    shutil.move(str(ruta_archivo), destino)
                    msj += f"\nXML movido: {destino}"
                except Exception as e:
                    msj += f"\nError moviendo {archivo}: {e}"

            elif ext in [".zip", ".rar", ".7z"]:
                subdir = comp_dir / tipo_doc
                subdir.mkdir(exist_ok=True)
                destino = subdir / archivo
                try:
                    shutil.move(str(ruta_archivo), destino)
                    msj += f"\nComprimido movido: {destino}"
                except Exception as e:
                    msj += f"\nError moviendo {archivo}: {e}"

            else:
                continue

    except Exception as e:
        msj += f"\nError general: {e}"

    return msj if msj else "No se movió ningún archivo.\nNo pudimos mover ningun archivo porque no se encontraron en el listado dian enviado "