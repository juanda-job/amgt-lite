import pandas as pd
from pathlib import Path
from .....models import LineaContable, Doc

def extraer_documentos(agrupaciones: list[str], df) -> list[Doc]:
    """
    Extrae documentos agrupando dinámicamente un CSV por las columnas indicadas.

    Args:
        agrupaciones (list[str]): Lista de nombres de columnas por las que se quiere agrupar.
        df (pd.DataFrame): DataFrame con la información contable.

    Returns:
        list[Doc]: Lista de objetos Doc con sus líneas contables.
    """
    print(df.fecha)
    # Validar que df es un DataFrame
    if df is None:
        raise ValueError("El DataFrame recibido es None")

    if not hasattr(df, "columns"):
        raise TypeError(f"El objeto recibido no es un DataFrame, es de tipo {type(df)}")

    print(f"Columnas disponibles en el DataFrame: {list(df.columns)}")

    # Validar que las columnas obligatorias existen
    columnas_obligatorias = ["fecha", "nit", "tipo_documento", "cuenta", "detalle", "debito", "credito", "porcentaje"]
    for col in columnas_obligatorias:
        if col not in df.columns:
            raise KeyError(f"La columna obligatoria '{col}' no existe en el documento")

    print("✅ Validación de columnas obligatorias exitosa")

    docs = []
    try:
        # Agrupar dinámicamente
        for keys, grupo in df.groupby(agrupaciones):
            print(f"Agrupando por {agrupaciones} → clave: {keys}, tamaño grupo: {len(grupo)}")
            print(str(grupo))
            # Normalizar clave (puede ser valor único o tupla)
            if not isinstance(keys, tuple):
                keys = (keys,)

            # Construir líneas contables
            lineas = []
            for idx, fila in grupo.iterrows():
                try:
                    linea = LineaContable(
                        cuenta=fila["cuenta"],
                        detalle=fila["detalle"],
                        tercero=fila["nit"], 
                        centro_costo=fila.get("centro_costo", None),
                        debito=fila["debito"],
                        credito=fila["credito"],
                        porcentaje = fila["porcentaje"],
                    )
                    lineas.append(linea)
                except Exception as e:
                    print(f"⚠️ Error creando LineaContable en fila {idx}: {e}")
                    continue

            # Crear documento con los valores de agrupación
            try:
                doc = Doc(
                    fecha=grupo["fecha"].iloc[0],
                    numero=grupo["numero_documento"].iloc[0],
                    tipo=grupo["tipo_documento"].iloc[0],
                    lineas=lineas,
                )
                docs.append(doc)
            except Exception as e:
                print(f"⚠️ Error creando Doc para grupo {keys}: {e}")

    except Exception as e:
        print(f"❌ Error general en agrupación: {e}")
        raise

    print(f"✅ Se generaron {len(docs)} documentos")
    return docs

import pandas as pd
from pathlib import Path

def extraer_terceros(df) -> list[str]:
    # Validar que las columnas existen
    if "NIT" not in df.columns:
        raise KeyError(f"La columna nit no existe en el CSV")
    # Obtener lista única
    return df["NIT"].dropna().unique().tolist()
   
def extraer_cuentas(df) -> list[str]:
    if "CUENTA" not in df.columns:
        raise KeyError("La columna 'cuenta' no existe en el CSV")
    return df["CUENTA"].dropna().unique().tolist()


def extraer_terceros_y_cuentas(df) -> tuple[list[str], list[str]]:
    """
    Extrae listas únicas de terceros y cuentas desde el CSV limpio.

    Returns:
        tuple[list[str], list[str]]: 
            - Lista de terceros sin repetidos
            - Lista de cuentas sin repetidos
    """
    
    # Validar que las columnas existen
    for col in ["nit", "cuenta"]:
        if col not in df.columns:
            raise KeyError(f"La columna '{col}' no existe en el CSV")

    # Obtener listas únicas
    terceros = df["nit"].dropna().unique().tolist()
    cuentas = df["cuenta"].dropna().unique().tolist()

    return terceros, cuentas