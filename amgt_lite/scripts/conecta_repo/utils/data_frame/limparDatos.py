import pandas as pd
import os
import unicodedata

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
    x = ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn')
    x = x.lstrip('-')  # ← elimina guiones al inicio
    return x

def normalizar_y_validar_cuenta(cuenta):
    try:
        return str(int(float(cuenta)))
    except (ValueError, TypeError):
        return ''  # o puedes usar np.nan si prefieres marcarlo como nulo


def normalizar_y_validar_numero(numero: str) -> str:
    try:
        # Convierte a float y luego a int para eliminar decimales como .0
        numero_entero = int(float(numero))
        print(numero_entero)
        return str(numero_entero)
    except (ValueError, TypeError):
        # Si no se puede convertir, elimina todo lo que no sea dígito
        return str(''.join(n for n in str(numero) if n.isdigit())).replace(".0","")

from datetime import datetime
import re
import pandas as pd

def normalizar_y_validar_porcentaje(porcentaje) -> str:
    """
    Normaliza el valor de porcentaje:
    - Convierte "" o None en 0
    - Convierte valores no numéricos en 0
    - Deja solo números (descarta letras, símbolos)
    - Retorna como string
    """
    try:
        # Si es None o cadena vacía
        if porcentaje is None or str(porcentaje).strip() == "":
            return "0"

        # Extraer solo dígitos y punto decimal
        limpio = re.sub(r"[^0-9.]", "", str(porcentaje))

        # Convertir a número seguro
        valor = pd.to_numeric(limpio, errors="coerce")

        if pd.isna(valor):
            return "0"

        return str(valor)
    except Exception:
        return "0"

def normalizar_nit(nit) -> str:
    try:
        # Convierte a entero si es float, luego a string
        return str(int(float(nit)))
    except (ValueError, TypeError):
        # Si no se puede convertir, extrae solo los dígitos
        return ''.join(c for c in str(nit) if c.isdigit())
    
def normalizar_y_validar_fecha(fecha_str) -> str:
    try:
        # Caso 1: si ya es datetime o Timestamp
        if isinstance(fecha_str, (datetime, pd.Timestamp)):
            return fecha_str.strftime("%d/%m/%Y")

        # Caso 2: si es string
        partes = fecha_str.replace("00:00:00","").replace("-","/").replace("\\","/").strip().split("/")
        if len(partes) != 3:
            raise ValueError("Formato incorrecto")
        if(len(partes[2])==4):
            dia = partes[0].zfill(2)
            mes = partes[1].zfill(2)
            anio = partes[2].zfill(4)
        elif (len(partes[0])==4):
            dia = partes[2].zfill(2)
            mes = partes[1].zfill(2)
            anio = partes[0].zfill(4)
        fecha_normalizada = f"{dia}/{mes}/{anio}"

        # Validación real
        datetime.strptime(fecha_normalizada, "%d/%m/%Y")

        return fecha_normalizada
    except Exception as e:
        print(e)
        return ""  # o None si prefieres

from pathlib import Path


def limpiarDatos(df):
    try:
        df.columns = [to_snake(c) for c in df.columns]
        #print(df.columns.tolist())
        print(df.columns.tolist())
        columnas_deseadas = ['fecha', 'numero_documento', 'detalle', "tipo_documento", 'nit', 'cuenta', 'debito', 'credito', 'porcentaje' ]
        df = df[columnas_deseadas]
        #print(df.columns.tolist())
        #print(df[['debito','credito']].head(20))
        df.loc[:, 'debito'] = pd.to_numeric(df['debito'], errors='coerce').fillna(0)
        df.loc[:, 'credito'] = pd.to_numeric(df['credito'], errors='coerce').fillna(0)
        #print(df[['debito','credito']].head(20))
        df = df[~((df['debito'] == 0) & (df['credito'] == 0))]
        #print(df[['debito','credito']].head(20))
        #print(df.columns.tolist())
        #print(df.head())
        #print(df.isna().sum())
        # Solo eliminar columnas vacías que no estén en las deseadas
        df = df.dropna(axis=1, how='all').reindex(columns=columnas_deseadas, fill_value=0)
        
        #print(df.columns.tolist())
        df = df.loc[:, ~df.columns.duplicated()]
        #print(df.columns.tolist())
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        #print(df.columns.tolist())
        #print(df[['debito','credito']].head(20))
        print(df.columns.tolist())
        for col in obj_cols:
            df[col] = df[col].apply(normalize_text)
        print(df.fecha)
        df['fecha'] = df['fecha'].apply(normalizar_y_validar_fecha)
        print(df.fecha)
        df['numero_documento'] = df['numero_documento'].apply(normalizar_y_validar_numero)
        df['porcentaje'] = df['porcentaje'].apply(normalizar_y_validar_porcentaje)
        df['cuenta'] = df['cuenta'].apply(normalizar_y_validar_cuenta)
        df["nit"] = df["nit"].apply(normalizar_nit)
        return df

    except Exception as e:
        print(str(e))
        raise RuntimeError(f"Error al limpiar datos: {str(e)}")  # ← esto lo captura tu vista




def limpiarDatosDocs(archivo):
    try:
        
        df.columns = [to_snake(c) for c in df.columns]
        columnas_deseadas = ['fecha', 'numero', 'tipo']
        df = df[columnas_deseadas]
        df = df.dropna(axis=1, how='all')
        #print(df.columns.tolist())
        df = df.T.drop_duplicates().T
        #print(df.columns.tolist())
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        #print(df.columns.tolist())
        #print(df[['debito','credito']].head(20))
        for col in obj_cols:
            df[col] = df[col].apply(normalize_text)

        df['fecha'] = df['fecha'].apply(normalizar_y_validar_fecha)
        #df['numero'] = df['numero'].apply(normalizar_y_validar_numero_documento)
        return df

    except Exception as e:
        print(str(e))
        raise RuntimeError(f"Error al limpiar datos: {str(e)}")  # ← esto lo captura tu vista











