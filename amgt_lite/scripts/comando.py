#------------------------------  Importaciones  --------------------------------------------
from playwright.sync_api import sync_playwright, Page, expect
import pandas as pd
import os
import sys
sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import unicodedata
from pandas import DataFrame
from ..models import Tercero
from ..scripts.navegador import login

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
    # Recompone el texto para conservar tildes en vocales
    x = unicodedata.normalize('NFC', x)
    x = x.lstrip('-')  # elimina guiones al inicio
    return x.replace("Ü","U")

resultado = {
    "cant_correctos" : "cant_correctos",
    "cant_fallidos" : "cant_fallidos",
    "cant_total" : "cant_total"
}

def crearTercero(page:Page,df: DataFrame):
    page.locator('#ul_0 >> #li_23').click()
    page.locator('#ul_0 >> #li_23 >> #ul_23 >> a:has-text("Proveedor")').click()
    page.wait_for_selector('#bCrear', state='visible')
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in obj_cols:
        df[col] = df[col].apply(normalize_text)
    for index, row in df.iterrows():            
        boton_crear = page.locator("#bCrear")
        boton_crear.wait_for(state="visible")
        boton_crear.click()
        tercero = Tercero(
            row['Tipo_Documento'],
            row['Documento'],
            row['Régimen'],
            row['Tipo'],
            row['Documento_Soporte'],
            row['Primer_Nombre'],
            row['Otro_Nombre'],
            row['Primer_Apellido'],
            row['Segundo_Apellido'],
            row['Razón_Social'],
            row['Nombre_Comercial'],
            row['Dirección'],
            row['País'],
            row['Ciudad'],
            row['Teléfono'],
            row['Email']
        )
        page.wait_for_selector('#idTipoDocumento', state='visible')
        page.select_option("#idTipoDocumento", value=str(tercero.Tipo_Documento))
        page.locator("#documento").fill(str(int(float(tercero.Documento))))
        page.locator("#telefono").clear()
        page.locator("#telefono").click()
        if not str(tercero.Teléfono) == "0":
            page.locator("#telefono").fill(str(int(float(tercero.Teléfono))))
        page.wait_for_selector('#lab_digitoVerificacion', state='visible')
        page.select_option("#idRegimen", value=str(tercero.Régimen))
        page.select_option("#idNaturalezaProveedor", value=str(tercero.Tipo))
        page.select_option("#documentoSoporte", value=str(tercero.Documento_Soporte).lower())
        if(str(tercero.Tipo)=="PERSONA NATURAL Y ASIMILADAS" or str(tercero.Tipo)=="2"):
            page.locator("#primerNombre").clear()
            page.locator("#otroNombre").clear()
            page.locator("#primerApellido").clear()
            page.locator("#segundoApellido").clear()
            page.locator("#primerNombre").fill(str(tercero.Primer_Nombre))
            page.locator("#otroNombre").fill(str(tercero.Otro_Nombre))
            page.locator("#primerApellido").fill(str(tercero.Primer_Apellido))
            page.locator("#segundoApellido").fill(str(tercero.Segundo_Apellido))
            page.locator("#nombreComercial").clear()
            page.locator("#nombreComercial").fill(str(tercero.Primer_Nombre)+" "+str(tercero.Otro_Nombre)+" "+str(tercero.Primer_Apellido)+" "+str(tercero.Segundo_Apellido))
        else:
            page.locator("#razonSocial").clear()
            page.locator("#razonSocial").fill(str(tercero.Razón_Social))
            page.locator("#nombreComercial").clear()
            page.locator("#nombreComercial").fill(str(tercero.Nombre_Comercial))
        page.locator("#direccion").clear()
        page.locator("#direccion").fill(str(tercero.Dirección))
        page.locator("#idPais_Search").click()
        page.locator("#idPais_Search").clear()
        page.locator("#idPais_Search").type(str(tercero.País), delay=100)
        page.locator("label.campoListado", has_text=str(tercero.País)).click()
        page.locator("#idCiudad_Search").click()
        page.locator("#idCiudad_Search").clear()
        page.locator("#idCiudad_Search").type(str(tercero.Ciudad+" "), delay=100)
        page.locator("label.campoListado", has_text=str(tercero.Ciudad+" ")).click()

        page.locator("#email").clear()
        page.locator("#email").fill(str(tercero.Email))
        page.locator("#bCerrar").click()

        
        i=True
        while(i):
            try:
                titulo = page.locator("#swal2-title")
                titulo.wait_for(state="visible")
                # Extrae el texto
                texto = titulo.text_content()
                # Valida si contiene "Éxito"
                if texto and "Éxito" in texto:
                    i= False
                else:
                    print("[INFO] El texto no indica éxito:", texto)
                    page.wait_for_timeout(10000)
            except Exception as e:
                page.wait_for_timeout(10000)
            
        # Localiza el botón
        boton_ok = page.locator("button.swal2-confirm.swal2-styled")

        # Espera a que esté visible
        boton_ok.wait_for(state="visible")

        # Haz clic
        boton_ok.click()        
    return   

#-------------------------------------------  Run  -----------------------------------
def crear_terceros_run(enlace,df):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page,enlace,"DRAMIREZ",'41946592')
        crearTercero(page,df)
        browser.close()


def validarExcel():
    return