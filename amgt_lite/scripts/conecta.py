from .conecta_repo.services.documentos_services import *
from .conecta_repo.services.page_services import *
from .conecta_repo.utils.data_frame.extraerData import *
from .conecta_repo.utils.data_frame.limparDatos import limpiarDatos
import json

import threading
from typing import List

class XConecta:
    def __init__(self):
        self.data = {
            'id_empresa': "",
            'terceros_null': [],
            'terceros_verificados': [],
            'cuentas_null': [],
            'cuentas_verificadas': [],
            'cuentas_base': [],
            'bandera_cuentas': False,
            'bandera_terceros': False
        }
        self._lock = threading.Lock()

    # --- Getters ---
    def get_id_empresa(self) -> str:
        with self._lock:
            return self.data['id_empresa']

    def get_terceros_null(self) -> List[str]:
        with self._lock:
            return self.data['terceros_null']

    def get_terceros_verificados(self) -> List[str]:
        with self._lock:
            return self.data['terceros_verificados']

    def get_cuentas_null(self) -> List[str]:
        with self._lock:
            return self.data['cuentas_null']

    def get_cuentas_verificadas(self) -> List[str]:
        with self._lock:
            return self.data['cuentas_verificadas']

    def get_cuentas_base(self) -> List[str]:
        with self._lock:
            return self.data['cuentas_base']

    def get_bandera_cuentas(self) -> bool:
        with self._lock:
            return self.data['bandera_cuentas']
        
    def get_bandera_terceros(self) -> bool:
        with self._lock:
            return self.data['bandera_terceros']

    # --- Setters ---
    def set_id_empresa(self, value: str):
        with self._lock:
            self.data['id_empresa'] = value

    def set_terceros_null(self, value: List[str]):
        with self._lock:
            self.data['terceros_null'] = value

    def set_terceros_verificados(self, value: List[str]):
        with self._lock:
            self.data['terceros_verificados'] = value

    def set_cuentas_null(self, value: List[str]):
        with self._lock:
            self.data['cuentas_null'] = value

    def set_cuentas_verificadas(self, value: List[str]):
        with self._lock:
            self.data['cuentas_verificadas'] = value

    def set_cuentas_base(self, value: List[str]):
        with self._lock:
            self.data['cuentas_base'] = value

    def set_bandera_cuentas(self, value: bool):
        with self._lock:
            self.data['bandera_cuentas'] = value

    def set_bandera_terceros(self, value: bool):
        with self._lock:
            self.data['bandera_terceros'] = value

    # --- Exportar todo el diccionario ---
    def to_dict(self) -> dict:
        """Devuelve una copia segura del diccionario completo"""
        with self._lock:
            return dict(self.data)

x = XConecta()


def verificar_terceros(enlace, token, terceros):
    try: 
        with sync_playwright() as p:
            browser, context, page = new_context(p)
            page = go_to_conecta(login(page, enlace, "DRAMIREZ", '41946592'), context, token)
            print("iniciando verificacion")
            terceros_verificados, terceros_null = verificar_terceros_services(page, terceros) 

            # Actualizamos la variable x
            x.set_terceros_verificados(terceros_verificados)
            x.set_terceros_null(terceros_null)
            x.set_bandera_terceros(True)

    except Exception as e:
        x.set_bandera_terceros(False)
        # Propagamos el error hacia arriba
        raise e

        

def verificar_cuentas(enlace, token, cuentas):

    try:
        with sync_playwright() as p:
            browser, context, page = new_context(p)
            page = go_to_conecta(login(page, enlace, "DRAMIREZ", '41946592'), context, token)
            print("iniciando verificacion")
            cuentas_verificadas, cuentas_null, cuentas_base= verificar_cuentas_services(page, cuentas) 

            # Actualizamos la variable x
            x.set_cuentas_verificadas(cuentas_verificadas)
            x.set_cuentas_null(cuentas_null)
            x.set_cuentas_base(cuentas_base)
            x.set_bandera_cuentas(True)

    except Exception as e:
        x.set_bandera_cuentas(False)
        raise e

    
def cargar_documentos(cuentas_bases, agrupaciones, enlace:str, df, token):
    print(token)
    try:
        with sync_playwright() as p:
            browser, context, page = new_context(p)
            page = go_to_conecta(login(page,enlace,"DRAMIREZ",'41946592'), context, token)
            print("login exitoso")
            docs = extraer_documentos(agrupaciones,df)
            for doc in docs:
                page.goto(token)
                #filtrar_tipo_documento(page, str(doc.tipo))
                filas = consultar(page, f"{doc.numero} {doc.lineas[0].tercero}")

                if not filas:  # si consultar devolvió False
                    existe = False
                else:
                    existe = False
                    cant = filas.count()
                    for i in range(cant):
                        isNumber =ExtraerValorFila(filas.nth(i), 0) == str(doc.numero)
                        isTercero = compararNitFila(doc.lineas[0].tercero, ExtraerValorFila(filas.nth(i), 3))
                        isTipo = ExtraerValorFila(filas.nth(i), 2) == str(doc.tipo).split(" ", 1)[1]
                        print(isNumber)
                        print(isTercero)
                        print(isTipo)
                        if isNumber and isTercero and isTipo:
                            existe = True
                            break
                if not existe:
                    page.get_by_role("button", name="Nuevo").click()
                    cargar_documento(page,doc,cuentas_bases)
                else:
                    print(f"El documento {doc.numero} ya se encuentra en la base de datos")
            browser.close()
    except Exception as e:
        print(e)

            

def validar_porcentajes(df: pd.DataFrame, cuentas_str: str):
    """
    Filtra el DataFrame por columnas relevantes y valida porcentajes.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'numero_documento', 'cuenta', 'porcentaje'.
        cuentas (list): Lista de cuentas a verificar.

    Returns:
        tuple: (True, []) si todas las filas cumplen la condición.
            (False, lista) si alguna fila tiene porcentaje vacío o cero.
            La lista contiene strings en formato "numero_documento-cuenta".
    """
    try:
        cuentas = json.loads(cuentas_str)  # ahora sí es lista
    except Exception:
        cuentas = [cuentas_str]  # fallback: si no es JSON, lo metemos en lista
    # Filtrar solo las columnas necesarias
    df_filtrado = df[['numero_documento', 'cuenta', 'porcentaje']]

    # Filtrar filas que coincidan con alguna cuenta de la lista
    df_filtrado = df_filtrado[df_filtrado['cuenta'].isin(cuentas)]

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
