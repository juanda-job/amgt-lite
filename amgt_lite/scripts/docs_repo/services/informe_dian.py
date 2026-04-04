import pandas as pd
import unicodedata
from pathlib import Path
from tkinter import Tk, filedialog
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

def remove_accents(text: str) -> str:
    """Elimina acentos y diacriticos de una cadena."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def normalize_text(x):
    """Normaliza un texto para analisis o comparacion."""
    if pd.isna(x):
        return x
    x = str(x).strip().upper()
    x = remove_accents(x)
    x = x.lstrip('-')
    return x

def generarInforme():
    """
    Permite al usuario seleccionar un archivo (CSV o Excel) y exporta un nuevo Excel con dos hojas:
    1. Hoja 'datos' con los datos originales.
    2. Hoja 'resumen' agrupada por Tipo de documento y Grupo, sumando IVA y Total.
       Se agrega la columna 'Antes de IVA' = Total - IVA.
       Los grupos se separan con 3 filas en blanco y se aplica borde a las celdas.
    """
    salida = ""
    try:
        Tk().withdraw()
        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo de entrada",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Archivos CSV", "*.csv")]
        )
        if not ruta:
            salida ="No se selecciono ningun archivo."
            print(salida)
            return salida

        # Cargar archivo segun extension
        if ruta.endswith(".csv"):
            df = pd.read_csv(ruta, sep=";", encoding="latin1")
        elif ruta.endswith((".xlsx", ".xls")):
            df = pd.read_excel(ruta, engine="openpyxl")
        else:
            raise ValueError(f"Formato no soportado: {Path(ruta).suffix}")

        # Conversion numerica segura
        for col in ["IVA", "Total"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Crear resumen agrupado si existen las columnas clave
        if {"Tipo de documento", "Grupo"}.issubset(df.columns):
            resumen = (
                df.groupby(["Tipo de documento", "Grupo"], as_index=False)[["IVA", "Total"]]
                  .sum()
            )
            # Calcular columna Antes de IVA
            resumen["Antes de IVA"] = resumen["Total"] - resumen["IVA"]

            # Reordenar columnas
            resumen = resumen[["Tipo de documento", "Grupo", "Antes de IVA", "IVA", "Total"]]

            # Ordenar por grupo
            resumen = resumen.sort_values(by="Grupo")

            # Construir bloques con separacion de grupos
            bloques = []
            for grupo, datos in resumen.groupby("Grupo"):
                # Encabezados
                encabezados = pd.DataFrame([["Tipo de documento", "Grupo", "Antes de IVA", "IVA", "Total"]],
                                           columns=resumen.columns)
                bloques.append(encabezados)
                bloques.append(datos)
                # 3 filas vacias
                bloques.append(pd.DataFrame([["", "", "", "", ""]] * 3, columns=resumen.columns))
            resumen_final = pd.concat(bloques, ignore_index=True)
        else:
            resumen_final = pd.DataFrame()

        # Seleccionar nombre y ubicacion del archivo final
        salida_excel = filedialog.asksaveasfilename(
            title="Guardar archivo final",
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if not salida_excel:
            salida = "No se selecciono nombre para el archivo final."
            print(salida)
            return salida

        # Exportar a Excel con dos hojas
        with pd.ExcelWriter(salida_excel, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="datos", index=False)
            resumen_final.to_excel(writer, sheet_name="resumen", index=False, header=False)

        # Aplicar bordes
        wb = load_workbook(salida_excel)
        ws = wb["resumen"]

        thin_border = Border(left=Side(style="thin"),
                             right=Side(style="thin"),
                             top=Side(style="thin"),
                             bottom=Side(style="thin"))

        for row in ws.iter_rows():
            for cell in row:
                if cell.value not in (None, ""):
                    cell.border = thin_border

        wb.save(salida_excel)

        salida = (f"Archivo generado: {salida_excel}")
        print(salida)

    except Exception as e:
        salida = f"Error al limpiar datos: {str(e)}"
        print(salida)
    return salida

