import threading

from ....models import *
from ..utils.components.documents_table import *
from ..utils.components.documents_head import *
from ..utils.components.items_head import *
from ..utils.components.items_table import *
from ..utils.exceptions import *
from typing import List
from playwright.async_api import Page
from playwright.sync_api import sync_playwright, Page
class XConecta:
    def __init__(self):
        self.data = {
            'terceros_error': [],
            'cuentas_error': [],
            'documentos_faltantes': [],
            'documentos_cargados': [],
            'documentos_descuadrados': [],
        }
        self._lock = threading.Lock()

    # --- Getters ---
    def get_terceros_error(self) -> List[str]:
        with self._lock:
            return self.data['terceros_error']

    def get_cuentas_error(self) -> List[str]:
        with self._lock:
            return self.data['cuentas_error']

    def get_documentos_faltantes(self) -> List[str]:
        with self._lock:
            return self.data['documentos_faltantes']

    def get_documentos_cargados(self) -> List[str]:
        with self._lock:
            return self.data['documentos_cargados']

    def get_documentos_descuadrados(self) -> List[str]:
        with self._lock:
            return self.data['documentos_descuadrados']

    # --- Setters ---
    def set_terceros_error(self, value: List[str]):
        with self._lock:
            self.data['terceros_error'] = value

    def set_cuentas_error(self, value: List[str]):
        with self._lock:
            self.data['cuentas_error'] = value

    def set_documentos_faltantes(self, value: List[str]):
        with self._lock:
            self.data['documentos_faltantes'] = value

    def set_documentos_cargados(self, value: List[str]):
        with self._lock:
            self.data['documentos_cargados'] = value

    def set_documentos_descuadrados(self, value: List[str]):
        with self._lock:
            self.data['documentos_descuadrados'] = value

    # --- Métodos para agregar evitando duplicados ---
    def add_terceros_error(self, value: List[str]):
        with self._lock:
            self.data['terceros_error'].extend(v for v in value if v not in self.data['terceros_error'])

    def add_cuentas_error(self, value: List[str]):
        with self._lock:
            self.data['cuentas_error'].extend(v for v in value if v not in self.data['cuentas_error'])

    def add_documentos_faltantes(self, value: List[str]):
        with self._lock:
            self.data['documentos_faltantes'].extend(v for v in value if v not in self.data['documentos_faltantes'])

    def add_documentos_cargados(self, value: List[str]):
        with self._lock:
            self.data['documentos_cargados'].extend(v for v in value if v not in self.data['documentos_cargados'])

    def add_documentos_descuadrados(self, value: List[str]):
        with self._lock:
            self.data['documentos_descuadrados'].extend(v for v in value if v not in self.data['documentos_descuadrados'])

    # --- Exportar todo el diccionario ---
    def to_dict(self) -> dict:
        with self._lock:
            return dict(self.data)

    def reset(self):
        with self._lock:
            self.data = {
                'terceros_error': [],
                'cuentas_error': [],
                'documentos_faltantes': [],
                'documentos_cargados': [],
                'documentos_descuadrados': [],
            }
x = XConecta()

def crear_registro_error(componente, error, detalles=None):
    return {
        "componente": componente,
        "error": error,
        "detalles": detalles
    }

def cargar_documento(page:Page, doc: Doc, x: XConecta):
    try: 
        print("Vamos a cargar documentos")
        set_date(page,str(doc.fecha))
        set_document_type(page, str(doc.tipo))
        set_number(page, str(doc.numero))

        for linea in doc.lineas:
            try:
                verificar_cuentas(page, str(linea.cuenta))
            except:
                x.add_cuentas_error(crear_registro_error(
                    f"{linea.cuenta}",
                    f"La cuenta {linea.cuenta} del documento {doc.numero} no existe en la base de datos"
                ))
                return 0
            try:
                verificar_terceros(page, str(linea.tercero))
            except:
                x.add_terceros_error(crear_registro_error(
                    f"{linea.tercero}",
                    f"El tercero {linea.tercero} del documento {doc.numero} no existe en la base de datos"
                ))
                return 0
            set_cuenta(page, 1,linea.cuenta)
            fill_texto(page, 1, columnas_items["concepto"],linea.detalle)
            set_tercero(page, 1, linea.tercero)
            print(float(linea.debito))
            try:
                if float(linea.debito) == 0.0:
                    set_valor(page, 1, columnas_items["credito"],verificar_cuentas(page, str(linea.cuenta)), linea.credito, linea.porcentaje)
                else:
                    set_valor(page, 1, columnas_items["debito"],verificar_cuentas(page, str(linea.cuenta)), linea.debito, linea.porcentaje)
            except:
                x.add_documentos_faltantes(crear_registro_error(f"{linea.cuenta}",f"La cuenta {linea.cuenta} del documento {doc.numero} no existe en la base de datos"))
                return 0
            agregarLinea(page)
            while(is_vacia(page,1,0)):
                page.wait_for_timeout(1000)
        dif = get_diferencia(page)
        if str(dif) == "0.00" or str(dif) == "$0.00":
            guardarRegistro(page,doc.numero)
            return 1
        else:
            x.add_documentos_descuadrados(crear_registro_error(f"{doc.numero}", f"El documento {doc.numero} se encuentra descuadrado"))
            guardarRegistro(page,doc.numero)
            print(f"El documento {doc.tipo} se encuentra descuadrdo")
            return 2
    except Exception as e:
        x.add_documentos_faltantes(crear_registro_error(f"{doc.numero}", f"Error al cargar el documento {doc.numero}: {str(e)}"))
        return 0
    

def guardarRegistro(page:Page, num:str):
    try:
        page.get_by_role("button", name="Guardar").click()
        print(f"Documento {num} guardado exitosamente")
    except Exception as e:
        print(f"Error al guardar la factura {num} desde el boton")
    return

def verificar_terceros(page:Page, nit:str):
    try:
        set_tercero(page,1,nit)
        return True
    except:
        return False
    
def verificar_cuentas(page:Page, cuenta:str):
    try:
        set_cuenta(page,1,cuenta)
        return True
    except:
        return False