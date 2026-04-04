from ....models import *
from ..utils.components.documents_table import *
from ..utils.components.documents_head import *
from ..utils.components.items_head import *
from ..utils.components.items_table import *
from ..utils.exceptions import *
from typing import List
from playwright.async_api import Page
from playwright.sync_api import sync_playwright, Page

def verificar_terceros_services(page, terceros):
    print(terceros)
    page.get_by_role("button", name="Nuevo").click()
    terceros_null = []
    terceros_verificados = []
    for tercero in terceros:
        if not verificar_terceros(page, tercero):
            terceros_null.append(tercero)
        else:
            terceros_verificados.append(tercero)           
 
    if len(terceros_null) > 0:
        print("hay terceros no encontrados")
        print("no se encontraron los siguientes terceros:")
        print(terceros_null)
    
    return terceros_verificados, terceros_null 


def verificar_cuentas_services(page, cuentas):
    print(cuentas)
    page.get_by_role("button", name="Nuevo").click()
    cuentas_null = []
    cuentas_verificadas = []
    cuentas_base = []

    for cuenta in cuentas:
        if not verificar_cuentas(page, cuenta):
            cuentas_null.append(cuenta)
        else:
            try:
                set_valor(page, 1, columnas_items["debito"], True, 500, 19)
                cuentas_base.append(cuenta)
                cuentas_verificadas.append(cuenta)
            except:
                try:
                    set_valor(page, 1, columnas_items["credito"], True, 500, 19)
                    cuentas_base.append(cuenta)
                    cuentas_verificadas.append(cuenta)
                except:
                    cuentas_verificadas.append(cuenta)
    if len(cuentas_null) > 0:
        print("hay cuentas no encontrados")
        print("no se encontraron las siguientes cuentas:")
        print(cuentas_null)
    
    return cuentas, cuentas_null, cuentas_base




def cargar_documento(page:Page, doc: Doc, cuentas_bases:List[str]):
    try: 
        print("Vamos a cargar documentos")
        # Agregar el encabezado
        set_date(page,str(doc.fecha))
        print(str(doc))
        set_document_type(page, str(doc.tipo))
        set_number(page, str(doc.numero))

        # Agregamos las lineas
        for linea in doc.lineas:
            set_cuenta(page, 1,linea.cuenta)
            fill_texto(page, 1, columnas_items["concepto"],linea.detalle)
            set_tercero(page, 1, linea.tercero)
            print(float(linea.debito))
            if float(linea.debito) == 0.0:
                set_valor(page, 1, columnas_items["credito"],str(linea.cuenta) in cuentas_bases, linea.credito, linea.porcentaje)
            else:
                set_valor(page, 1, columnas_items["debito"],str(linea.cuenta) in cuentas_bases, linea.debito, linea.porcentaje)
            
            agregarLinea(page)
            while(is_vacia(page,1,0)):
                page.wait_for_timeout(1000)
        dif = get_diferencia(page)
        if str(dif) == "0.00" or str(dif) == "$0.00":
            guardarRegistro(page,doc.numero)
            return 1
        else:
            guardarRegistro(page,doc.numero)
            print(f"El documento {doc.tipo} se encuentra descuadrdo")
            return 2
    except Exception as e:
        print(str(e)+"/nEste error ocurrio en el documento "+ doc.numero)
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