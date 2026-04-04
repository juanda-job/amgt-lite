import pandas as pd
from collections import Counter

def generarContapymeRecibidos(df: pd.DataFrame) -> pd.DataFrame:
    registros = []

    # Agrupar por documento y proveedor
    for (tipo_doc, numero_doc, nit_prov), grupo in df.groupby(["TIPO DOCUMENTO", "NUMERO DOCUMENTO", "NIT PROVEEDOR"]):
        row = grupo.iloc[0]

        # --- Construir DETALLE concatenado y resumido ---
        detalles = grupo["DETALLE"].dropna().tolist()
        conteo = Counter(detalles)
        detalles_resumidos = [f"{d}({n})" if n > 1 else d for d, n in conteo.items()]
        detalle_final = " - ".join(detalles_resumidos)

        # --- 1. Fila principal: débito sin impuestos ---
        fila_detalle = {
            "EMPRESA":"",
            "FECHA": row["FECHA"],
            "TIPO DOCUMENTO": tipo_doc,
            "NUMERO DOCUMENTO": numero_doc,
            "CUENTA": "",
            "CENTRO DE COSTO": "",
            "DETALLE": detalle_final,
            "DEBITO": row["SUBTOTAL"],
            "CREDITO": 0.0,
            "BASE": 0.0,
            "NIT": nit_prov,
            "NOMBRE": row["NOMBRE PROVEEDOR"],
            "ESPACIO":"",
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
        }

        # --- 2. Agrupar impuestos por tipo ---
        impuestos = (
            grupo.dropna(subset=["IMPUESTO NOMBRE", "IMPUESTO VALOR"])
                 .groupby("IMPUESTO NOMBRE")
                 .agg({"IMPUESTO VALOR": "sum", "PORCENTAJE IMPUESTO": "first"})
                 .reset_index()
        )
        impuesto = 0.0
        impuestos_list = []
        for _, imp in impuestos.iterrows():
            fila_impuestos={
                "EMPRESA":"",
                "FECHA": row["FECHA"],
                "TIPO DOCUMENTO": tipo_doc,
                "NUMERO DOCUMENTO": numero_doc,
                "CUENTA": "",
                "CENTRO DE COSTO": "",
                "DETALLE": f"IMPUESTO {imp['IMPUESTO NOMBRE']} {imp['PORCENTAJE IMPUESTO']}%",
                "DEBITO": imp["IMPUESTO VALOR"],
                "CREDITO": 0.0,
                "BASE": row["TOTAL SIN IMPUESTOS"],
                "NIT": nit_prov,
                "NOMBRE": row["NOMBRE PROVEEDOR"],
                "ESPACIO":"",
                "FECHA": row["FECHA"],
                "NUMERO DOCUMENTO": numero_doc,
            }
            impuestos_list.append(fila_impuestos)
            impuesto = impuesto + imp["IMPUESTO VALOR"]
        
        dif = row["SUBTOTAL"] + impuesto - row["TOTAL CON IMPUESTOS"]
        final = row["SUBTOTAL"] - dif
        fila_detalle["DEBITO"] = round(float(final), 2)

        registros.append(fila_detalle)
        registros.extend(impuestos_list)   # <-- aquí el cambio

        # --- 3. Fila final: crédito con impuestos ---
        registros.append({
            "EMPRESA":"",
            "FECHA": row["FECHA"],
            "TIPO DOCUMENTO": tipo_doc,
            "NUMERO DOCUMENTO": numero_doc,
            "CUENTA": "",
            "CENTRO DE COSTO": "",
            "DETALLE": "TOTAL " + str(numero_doc),
            "DEBITO": 0.0,
            "CREDITO": row["TOTAL CON IMPUESTOS"],
            "BASE": 0.0,
            "NIT": nit_prov,
            "NOMBRE": row["NOMBRE PROVEEDOR"],
            "ESPACIO":"",
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
        })

    columnas = [
        "EMPRESA","FECHA", "TIPO DOCUMENTO", "NUMERO DOCUMENTO",
        "CUENTA", "CENTRO DE COSTO", "DETALLE",
        "DEBITO", "CREDITO", "BASE", "NIT", "NOMBRE","ESPACIO", "FECHA", "NUMERO DOCUMENTO"
    ]
    df_contapyme = pd.DataFrame(registros, columns=columnas)

    # --- 4. Eliminar filas donde DEBITO y CREDITO sean ambos 0 ---
    df_contapyme = df_contapyme[~((df_contapyme["DEBITO"] == 0) & (df_contapyme["CREDITO"] == 0))]

    return df_contapyme

import pandas as pd
from collections import Counter

def generarContapymeEmitidos(df: pd.DataFrame) -> pd.DataFrame:
    registros = []

    # Agrupar por documento y proveedor
    for (tipo_doc, numero_doc, nit_prov), grupo in df.groupby(["TIPO DOCUMENTO", "NUMERO DOCUMENTO", "NIT CLIENTE"]):
        row = grupo.iloc[0]

        # --- Construir DETALLE concatenado y resumido ---
        detalles = grupo["DETALLE"].dropna().tolist()
        conteo = Counter(detalles)
        detalles_resumidos = [f"{d}({n})" if n > 1 else d for d, n in conteo.items()]
        detalle_final = " - ".join(detalles_resumidos)

        # --- 1. Fila principal: débito sin impuestos ---
        fila_detalle = {
            "EMPRESA":"",
            "FECHA": row["FECHA"],
            "TIPO DOCUMENTO": tipo_doc,
            "NUMERO DOCUMENTO": numero_doc,
            "CUENTA": "",
            "CENTRO DE COSTO": "",
            "DETALLE": detalle_final,
            "DEBITO": 0.0,
            "CREDITO": row["SUBTOTAL"],
            "BASE": 0.0,
            "NIT": nit_prov,
            "NOMBRE": row["NOMBRE PROVEEDOR"],
            "ESPACIO":"",
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
        }

        # --- 2. Agrupar impuestos por tipo ---
        impuestos = (
            grupo.dropna(subset=["IMPUESTO NOMBRE", "IMPUESTO VALOR"])
                 .groupby("IMPUESTO NOMBRE")
                 .agg({"IMPUESTO VALOR": "sum", "PORCENTAJE IMPUESTO": "first"})
                 .reset_index()
        )
        impuesto = 0.0
        impuestos_list = []
        for _, imp in impuestos.iterrows():
            fila_impuestos={
                "EMPRESA":"",
                "FECHA": row["FECHA"],
                "TIPO DOCUMENTO": tipo_doc,
                "NUMERO DOCUMENTO": numero_doc,
                "CUENTA": "",
                "CENTRO DE COSTO": "",
                "DETALLE": f"IMPUESTO {imp['IMPUESTO NOMBRE']} {imp['PORCENTAJE IMPUESTO']}%",
                "DEBITO": 0.0,
                "CREDITO": imp["IMPUESTO VALOR"],
                "BASE": row["TOTAL SIN IMPUESTOS"],
                "NIT": nit_prov,
                "NOMBRE": row["NOMBRE PROVEEDOR"],
                "ESPACIO":"",
                "FECHA": row["FECHA"],
                "NUMERO DOCUMENTO": numero_doc,
            }
            impuestos_list.append(fila_impuestos)
            impuesto = impuesto + imp["IMPUESTO VALOR"]
        
        dif = row["SUBTOTAL"] + impuesto - row["TOTAL CON IMPUESTOS"]
        final = row["SUBTOTAL"] - dif
        fila_detalle["DEBITO"] = round(float(final), 2)

        registros.append(fila_detalle)
        registros.extend(impuestos_list)   # <-- aquí el cambio

        # --- 3. Fila final: crédito con impuestos ---
        registros.append({
            "EMPRESA":"",
            "FECHA": row["FECHA"],
            "TIPO DOCUMENTO": tipo_doc,
            "NUMERO DOCUMENTO": numero_doc,
            "CUENTA": "",
            "CENTRO DE COSTO": "",
            "DETALLE": "TOTAL " + str(numero_doc),
            "DEBITO": row["TOTAL CON IMPUESTOS"],
            "CREDITO": 0.0,
            "BASE": 0.0,
            "NIT": nit_prov,
            "NOMBRE": row["NOMBRE PROVEEDOR"],
            "ESPACIO":"",
            "FECHA": row["FECHA"],
            "NUMERO DOCUMENTO": numero_doc,
        })

    columnas = [
        "EMPRESA","FECHA", "TIPO DOCUMENTO", "NUMERO DOCUMENTO",
        "CUENTA", "CENTRO DE COSTO", "DETALLE",
        "DEBITO", "CREDITO", "BASE", "NIT", "NOMBRE","ESPACIO", "FECHA", "NUMERO DOCUMENTO"
    ]
    df_contapyme = pd.DataFrame(registros, columns=columnas)

    # --- 4. Eliminar filas donde DEBITO y CREDITO sean ambos 0 ---
    df_contapyme = df_contapyme[~((df_contapyme["DEBITO"] == 0) & (df_contapyme["CREDITO"] == 0))]

    return df_contapyme
