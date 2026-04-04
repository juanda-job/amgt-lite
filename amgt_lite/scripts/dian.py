from playwright.sync_api import sync_playwright
import threading
import os
import time
from datetime import date
from .log import *
import tkinter as tk
from tkinter import filedialog
from playwright.sync_api import Page

class AppState:
    """
    Clase que contiene el estado de la aplicación,
    accesible de manera segura desde diferentes hilos.
    Cada instancia mantiene su propio estado.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Contadores
        self.total_documentos = 0
        self.cant_descargados = 0
        self.cant_fallidos = 0

        # Listas
        self.descargados_list = []
        self.fallidos_list = []

        # Estado del token y página
        self.activo = True
        self.token = ""

        # Bandera de stop
        self.stop = False

    # --- Métodos de contadores ---
    def set_total(self, new_total: int):
        with self._lock:
            self.total_documentos = new_total

    def get_total(self) -> int:
        with self._lock:
            return self.total_documentos

    def set_cant_descargados(self, new_descargados: int):
        with self._lock:
            self.cant_descargados = new_descargados

    def get_cant_descargados(self) -> int:
        return self.cant_descargados

    def set_cant_fallidos(self, new_fallidos: int):
        with self._lock:
            self.cant_fallidos = new_fallidos

    def get_cant_fallidos(self) -> int:
        return self.cant_fallidos

    # --- Métodos de listas ---
    def add_doc_descargado(self, cufe: str):
        with self._lock:
            self.cant_descargados += 1
            self.descargados_list.append(cufe)

    def get_docs_descargados(self) -> list:
        return self.descargados_list

    def set_docs_descargados(self, new_list: list):
        with self._lock:
            self.descargados_list = new_list

    def add_doc_fallido(self, cufe: str):
        with self._lock:
            self.cant_fallidos += 1
            self.fallidos_list.append(cufe)

    def get_docs_fallidos(self) -> list:
        return self.fallidos_list

    def set_docs_fallidos(self, new_list: list):
        with self._lock:
            self.fallidos_list = new_list

    # --- Métodos de token ---
    def set_activo(self, acti: bool):
        self.activo = acti

    def get_activo(self) -> bool:
        return self.activo

    def set_token(self, tok: str):
        self.token = tok

    def get_token(self) -> str:
        return self.token

    # --- Métodos de stop ---
    def set_stop(self, acti: bool):
        self.stop = acti

    def get_stop(self) -> bool:
        return self.stop
    
    def clear(self):
        # Contadores
        self.total_documentos = 0
        self.cant_descargados = 0
        self.cant_fallidos = 0

        # Listas
        self.descargados_list = []
        self.fallidos_list = []

        # Estado del token y página
        self.activo = True
        self.token = ""

        # Bandera de stop
        self.stop = False

estado = AppState()
def descargar_documentos(cufes):
    
    root = tk.Tk()
    root.title("Selecciona carpeta de descargas")

    ruta_seleccionada = {"valor": None}  # diccionario para capturar el valor

    def elegir_carpeta():
        ruta = filedialog.askdirectory(title="Selecciona una carpeta")
        ruta_seleccionada["valor"] = ruta   # guardar en variable externa
        root.destroy()  # cerrar ventana después de elegir

    btn = tk.Button(root, text="Elegir carpeta", command=elegir_carpeta)
    btn.pack(pady=20)

    root.mainloop()

    ruta = ruta_seleccionada["valor"]

    if not ruta:
        print("No se seleccionó carpeta")
        return

    global activo
    estado.set_total(len(cufes))
    ruta_descargas = f"{ruta}/descargas_{date.today()}"
    os.makedirs(ruta_descargas, exist_ok=True)

    k, m = divmod(len(cufes), 4)
    sublistas, inicio = [], 0
    for i in range(4):
        fin = inicio + k + (1 if i < m else 0)
        sublistas.append(cufes[inicio:fin])
        inicio = fin

    for sub in sublistas:
        if sub:   # True si la lista no está vacía
            threading.Thread(target=descargar, args=(ruta_descargas, sub)).start()

def descargar(ruta_descargas, cufes):
    """
    Docstring for descargar
    :param page: Pagina encargada de abrir los enlaces
    :type page: Page
    :param cufes: Lista de CUFES de la DIAN 
    
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)

        page_token = context.new_page()
        page_token.goto(estado.get_token())

        page = context.new_page()

        #Recorrer los cufes para descargar los documentos
        for i, cufe in enumerate(cufes, start=1):
            if(estado.get_stop()):
                browser.close()
                return
            #Indica si el documento se descargó correctamente
            exito = False
            #Indica cuantas veces se intento descargar el documento
            intentos = 0

            #intentamos tres veces descargar el documeto 
            while (intentos < 3) and (not exito):
                if(estado.get_stop()):
                    browser.close()
                    return
                try:
                    print(f"URL {i} lanzada. Intento {intentos+1}")
                    page.goto("https://www.websiteplanet.com/es/webtools/multiple-url/")
                    url_DIAN = "https://catalogo-vpfe.dian.gov.co/Document/DownloadZipFiles?trackId="
                    page.fill("#mu-list", url_DIAN+cufe)
                
                    #Si es la ultima iteracion reportar token inactivo
                    if intentos == 2:
                        estado.set_activo(False)

                    if estado.get_activo() == False:
                        # Esperar a que el token esté activo
                        print("Token inactivo, esperando...")
                        while not estado.get_activo():
                            page.wait_for_timeout(3000)
                        
                        

                    with page.expect_download() as download_info:
                        page.click("button.mu-form-button-submit")
                    download = download_info.value
                    archivo = download.suggested_filename
                    destino = os.path.join(ruta_descargas, archivo)
                    download.save_as(destino)
                    max_espera = 60
                    inicio = time.time()
                    while True:
                        if(estado.get_stop()):
                            browser.close()
                            return
                        archivos_actuales = set(os.listdir(ruta_descargas))
                        # Quitar extensión y comparar con trackIds
                        nombres_sin_ext = {os.path.splitext(a)[0] for a in archivos_actuales}

                        if cufe in nombres_sin_ext:
                            print(f"✅ Archivo {cufe} descargado correctamente")
                            estado.add_doc_descargado(cufe)
                            exito = True
                            break


                        if time.time() - inicio > max_espera:
                            print(f"⏰ Tiempo agotado en lote")
                            break

                        time.sleep(1)


                except Exception as e:
                    print("Error en descarga:", e)
                    intentos += 1
                    page_token.goto(estado.get_token())
                    time.sleep(3)

            if not exito:
                print(f"❌ No se pudo descargar la URL {i}: {cufe}")
                estado.add_doc_fallido(cufe)

    if estado.get_docs_fallidos():
        print("Descargas fallidas:")
        for f in estado.get_docs_fallidos():
            print(" -", f)
    return estado

