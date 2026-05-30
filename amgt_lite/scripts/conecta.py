from .conecta_repo.services.documentos_services import *
from .conecta_repo.services.page_services import *
from .conecta_repo.utils.data_frame.extraerData import *
from .conecta_repo.utils.data_frame.limparDatos import limpiarDatos
import json

import threading
from typing import List


import threading
from typing import List

    
def cargar_documentos(agrupaciones, enlace:str, df, token):
    print(token)
    try:
        with sync_playwright() as p:
            browser, context, page = new_context(p)
            page2, page = go_to_conecta(login(page,enlace,"DRAMIREZ",'41946592'), context, token)
            print("login exitoso")
            docs = extraer_documentos(agrupaciones,df)
            for doc in docs:
                page.goto(token)
                filas = consultar(page, f"{doc.numero} {doc.lineas[0].tercero}")
                existe = False
                if filas:
                    cant = filas.count()
                    for i in range(cant):
                        isNumber = ExtraerValorFila(filas.nth(i), 0) == str(doc.numero)
                        isTercero = compararNitFila(doc.lineas[0].tercero, ExtraerValorFila(filas.nth(i), 3))
                        isTipo = ExtraerValorFila(filas.nth(i), 2) == str(doc.tipo).split(" ", 1)[1]
                        if isNumber and isTercero and isTipo:
                            existe = True
                            break
                if not existe:
                    page.get_by_role("button", name="Nuevo").click()
                    cargar_documento(page, doc, x)   # <--- pásale x
                else:
                    print(f"El documento {doc.numero} ya se encuentra en la base de datos")
            browser.close()
            return x.to_dict()
    except Exception as e:
        print(e)
        return x.to_dict()

            

def validar_porcentajes(df: pd.DataFrame):
    """
    Filtra el DataFrame por columnas relevantes y valida porcentajes.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'numero_documento', 'cuenta', 'porcentaje'.

    Returns:
        tuple: (True, []) si todas las filas cumplen la condición.
            (False, lista) si alguna fila tiene porcentaje vacío o cero.
            La lista contiene strings en formato "numero_documento-cuenta".
    """
    # Filtrar solo las columnas necesarias
    df_filtrado = df[['numero_documento', 'cuenta', 'porcentaje']]

    # Normalizar porcentaje: convertir "" a NaN y luego a numérico
    df_filtrado['porcentaje'] = df_filtrado['porcentaje'].replace("", None)
    df_filtrado['porcentaje'] = pd.to_numeric(df_filtrado['porcentaje'], errors='coerce')

    # Detectar filas inválidas (NaN o 0)
    invalidas = df_filtrado[(df_filtrado['porcentaje'].isna()) | (df_filtrado['porcentaje'] == 0)]

    if invalidas.empty:
        return True, []
    else:
        # Construir lista "numero_documento-cuenta"
        errores = [f"{row['numero_documento']}-{row['cuenta']}" for _, row in invalidas.iterrows()]
        return False, errores
    
def compararNitFila(nit_doc:str, tercero:str ) -> bool:
    # Divide el texto por " - " y toma la segunda parte (el número)
    partes = tercero.split(" - ")
    if len(partes) > 1:
        nit_en_fila = partes[1].strip()
        return nit_en_fila == str(nit_doc).strip()
    return False
