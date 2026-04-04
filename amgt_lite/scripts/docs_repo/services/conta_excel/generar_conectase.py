import pandas as pd

def generarConectaseRecibidos(df: pd.DataFrame) -> pd.DataFrame:
    registros = []

    # Agrupar por documento y proveedor
    for (tipo_doc, numero_doc, nit_prov), grupo in df.groupby(["TIPO DOCUMENTO", "NUMERO DOCUMENTO", "NIT PROVEEDOR"]):
        row = grupo.iloc[0]

        # --- 1. Fila principal: débito sin impuestos ---
        registros.append({
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
            "NIT": nit_prov,
            "TIPO DOCUMENTO": tipo_doc,
            "CUENTA": "",
            "DETALLE": row["DETALLE"],
            "DEBITO": row["TOTAL SIN IMPUESTOS"],
            "CREDITO": 0.0,
            "PORCENTAJE": 0.0
        })

        # --- 2. Agrupar impuestos por tipo ---
        impuestos = (
            grupo.dropna(subset=["IMPUESTO NOMBRE", "IMPUESTO VALOR"])
                 .groupby("IMPUESTO NOMBRE")
                 .agg({"IMPUESTO VALOR": "sum", "PORCENTAJE IMPUESTO": "first"})
                 .reset_index()
        )

        for _, imp in impuestos.iterrows():
            registros.append({
                "FECHA": row["FECHA"],
                "NUMERO DOCUMENTO": numero_doc,
                "NIT": nit_prov,
                "TIPO DOCUMENTO": tipo_doc,
                "CUENTA": "",
                "DETALLE": f"IMPUESTO {imp['IMPUESTO NOMBRE']} {imp['PORCENTAJE IMPUESTO']}%",
                "DEBITO": imp["IMPUESTO VALOR"],
                "CREDITO": 0.0,
                "PORCENTAJE": imp["PORCENTAJE IMPUESTO"]
            })

        # --- 3. Fila final: crédito con impuestos ---
        registros.append({
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
            "NIT": nit_prov,
            "TIPO DOCUMENTO": tipo_doc,
            "CUENTA": "",
            "DETALLE": "TOTAL " + str(numero_doc),
            "DEBITO": 0.0,
            "CREDITO": row["TOTAL CON IMPUESTOS"],
            "PORCENTAJE": 0.0
        })

    columnas = [
        "FECHA", "NUMERO DOCUMENTO", "NIT", "TIPO DOCUMENTO", "CUENTA", "DETALLE", 
        "DEBITO", "CREDITO", "PORCENTAJE"
    ]
    df_contapyme = pd.DataFrame(registros, columns=columnas)

    # --- 4. Eliminar filas donde DEBITO y CREDITO sean ambos 0 ---
    df_contapyme = df_contapyme[~((df_contapyme["DEBITO"] == 0) & (df_contapyme["CREDITO"] == 0))]

    return df_contapyme

import pandas as pd
columnas_obligatorias = ["fecha", "nit", "tipo_documento", "cuenta", "detalle", "debito", "credito", "porcentaje"]


def generarConectaseEmitidos(df: pd.DataFrame) -> pd.DataFrame:
    registros = []

    # Agrupar por documento y proveedor
    for (tipo_doc, numero_doc, nit_prov), grupo in df.groupby(["TIPO DOCUMENTO", "NUMERO DOCUMENTO", "NIT CLIENTE"]):
        row = grupo.iloc[0]

        # --- 1. Fila principal: débito sin impuestos ---
        registros.append({
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
            "NIT": nit_prov,
            "TIPO DOCUMENTO": tipo_doc,
            "CUENTA": "",
            "DETALLE": row["DETALLE"],
            "DEBITO": row["TOTAL SIN IMPUESTOS"],
            "CREDITO": 0.0,
            "PORCENTAJE": 0.0
        })

        # --- 2. Agrupar impuestos por tipo ---
        impuestos = (
            grupo.dropna(subset=["IMPUESTO NOMBRE", "IMPUESTO VALOR"])
                 .groupby("IMPUESTO NOMBRE")
                 .agg({"IMPUESTO VALOR": "sum", "PORCENTAJE IMPUESTO": "first"})
                 .reset_index()
        )

        for _, imp in impuestos.iterrows():
            registros.append({
                "FECHA": row["FECHA"],
                "NUMERO DOCUMENTO": numero_doc,
                "NIT": nit_prov,
                "TIPO DOCUMENTO": tipo_doc,
                "CUENTA": "",
                "DETALLE": f"IMPUESTO {imp['IMPUESTO NOMBRE']} {imp['PORCENTAJE IMPUESTO']}%",
                "DEBITO": imp["IMPUESTO VALOR"],
                "CREDITO": 0.0,
                "PORCENTAJE": imp["PORCENTAJE IMPUESTO"]
            })

        # --- 3. Fila final: crédito con impuestos ---
        registros.append({
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
            "NIT": nit_prov,
            "TIPO DOCUMENTO": tipo_doc,
            "CUENTA": "",
            "DETALLE": "TOTAL " + str(numero_doc),
            "DEBITO": 0.0,
            "CREDITO": row["TOTAL CON IMPUESTOS"],
            "PORCENTAJE": 0.0
        })

    columnas = [
        "FECHA", "NUMERO DOCUMENTO", "NIT", "TIPO DOCUMENTO", "CUENTA", "DETALLE", 
        "DEBITO", "CREDITO", "PORCENTAJE"
    ]
    df_contapyme = pd.DataFrame(registros, columns=columnas)

    # --- 4. Eliminar filas donde DEBITO y CREDITO sean ambos 0 ---
    df_contapyme = df_contapyme[~((df_contapyme["DEBITO"] == 0) & (df_contapyme["CREDITO"] == 0))]

    return df_contapyme