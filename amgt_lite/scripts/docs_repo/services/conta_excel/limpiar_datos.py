import pandas as pd
import unicodedata

def limpiar_facturas(df: pd.DataFrame) -> pd.DataFrame:
    # Creamos un dataset explorer para no modificar el original
    df_explore = df.copy()

    # 1. Eliminar filas donde el total a pagar sea 0
    df_explore = df_explore[df_explore["TOTAL A PAGAR"].astype(float) != 0]

    # 2. Convertir columnas categóricas (tipo object) a mayúsculas
    for col in df_explore.select_dtypes(include="object").columns:
        df_explore[col] = df_explore[col].str.upper()

    # 3. Formatear la columna FECHA en formato dd/mm/aaaa
    df_explore["FECHA"] = pd.to_datetime(df_explore["FECHA"], errors="coerce").dt.strftime("%d/%m/%Y")

    # 4. Normalizar columnas categóricas: eliminar acentos, comas y punto y coma
    def normalizar_texto(texto):
        if pd.isna(texto):
            return texto
        texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
        texto = texto.replace(",", "").replace(";", "")
        return texto

    for col in df_explore.select_dtypes(include="object").columns:
        df_explore[col] = df_explore[col].apply(normalizar_texto)

    # 5. Convertir columnas numéricas a float con 2 decimales
    num_cols = [
        "PRECIO UNITARIO", "VALOR LINEA",
        "SUBTOTAL", "TOTAL SIN IMPUESTOS", "TOTAL CON IMPUESTOS", "TOTAL A PAGAR"
    ]
    for col in num_cols:
        if col in df_explore.columns:
            df_explore[col] = pd.to_numeric(df_explore[col], errors="coerce").astype("Float64").round(2)

    if "CANTIDAD" in df_explore.columns:
        df_explore["CANTIDAD"] = pd.to_numeric(df_explore["CANTIDAD"], errors="coerce").astype("Int64")

    # 6. Limpiar la columna NUMERO DOCUMENTO: eliminar letras y dejar solo números
    if "NUMERO DOCUMENTO" in df_explore.columns:
        df_explore["NUMERO DOCUMENTO"] = df_explore["NUMERO DOCUMENTO"].str.replace(r"\D", "", regex=True)

    # 7. Reemplazar valores vacíos en IMPUESTO NOMBRE por "NINGUNO"
    if "IMPUESTO NOMBRE" in df_explore.columns:
        df_explore["IMPUESTO NOMBRE"] = df_explore["IMPUESTO NOMBRE"].fillna("NINGUNO")
        df_explore.loc[df_explore["IMPUESTO NOMBRE"].str.strip() == "", "IMPUESTO NOMBRE"] = "NINGUNO"

    # 8. Reemplazar vacíos en IMPUESTO % y IMPUESTO VALOR por 0.0
    for col in ["IMPUESTO %", "IMPUESTO VALOR"]:
        if col in df_explore.columns:
            df_explore[col] = pd.to_numeric(df_explore[col], errors="coerce").fillna(0.0).astype("Float64").round(2)

    return df_explore
