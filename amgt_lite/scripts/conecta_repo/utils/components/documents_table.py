from playwright.sync_api import Page

def consultar(page: Page,  cadena:str):
    page.locator('input[placeholder="Buscar"]').clear()
    page.locator('input[placeholder="Buscar"]').type(f"{cadena}", delay=100)
    page.wait_for_timeout(3000)

    # Verifica si aparece el mensaje "No se encontraron movimientos"
    mensaje = page.locator("tbody tr td").first.text_content()
    if mensaje and "No se encontraron" in mensaje:
        return False

    # Localiza todas las filas dentro del tbody
    return page.locator("tbody tr")

def filtrar_fecha(page: Page, dia:str, mes:str, anio:str, nombre:str = "FECHA", dia_final:str=0, mes_final:str=0, anio_final:str=0):
    #seleccionar filtro
    page = seleccionarfiltroColumna(page,nombre)

    # Simular pulsación de flecha izquierda (dos veces)
    page.keyboard.press("ArrowLeft")
    page.keyboard.press("ArrowLeft")

    # Escribir la fecha
    fecha_inicio = "/".join([dia, mes, anio])
    fecha.type(fecha_inicio)

    # Fecha inicial (primer input dentro del th de la segunda columna)
    fecha = page.locator("table thead tr").locator("th").nth(1).locator("div div input").nth(1)

    # Dar foco al input
    fecha.click()

    # Simular pulsación de flecha izquierda (dos veces)
    page.keyboard.press("ArrowLeft")
    page.keyboard.press("ArrowLeft")

    #Validamos la fecha final 
    if dia_final == 0:
        dia_final = dia
    if mes_final == 0:
        mes_final = mes
    if anio_final == 0:
        anio_final == anio

    #configuramos la fecha final
    fecha_final = "/".join([dia_final, mes_final, anio_final])

    # Escribir la fecha
    fecha.type(fecha_final)

    # Simular la tecla Escape 
    page.keyboard.press("Escape")
    page.wait_for_timeout(2000)
    page.locator("button.refresh-boton").click()
    # Verifica si aparece el mensaje "No se encontraron movimientos"
    #mensaje = page.locator("tbody tr td").first.text_content()
    #if mensaje and "No se encontraron movimientos" in mensaje:
        #return False
    page.wait_for_timeout(2000)
    page.locator("button.refresh-boton").click()

    return page

def filtrar_evento(page:Page, tipo_evento:str = "ACUSE RECIBO", nombre:str = "TIPO EVENTO"):
    # Seleccionar boton filtro
    page = seleccionarfiltroColumna(page,nombre)

    # Seleccionar el evento
    page.wait_for_selector("text=Todos", state="visible", timeout=10000)
    page.click("text=Todos")
    page.wait_for_selector(f"text={tipo_evento}", timeout=5000)
    page.click(f"text={tipo_evento}")

    # Devolver la pagina filtrada
    return page

def seleccionarfiltroColumna(page:Page, nombre: str):
    # Obtener el filtro
    filtro = page.locator("table thead tr").locator(f"th:has-text('{nombre}')").locator("div div input").nth(0)
    # Dar foco al input
    filtro.click()
    return page
import re
from playwright.sync_api import Locator

def ExtraerValorFila(fila, columna: int) -> str:
    """
    Compara un valor con el contenido de una fila en una columna específica.

    Args:
        valor (str): El valor que se desea comparar.
        fila (list): La fila de datos donde se realizará la comparación.
        columna (int): El índice de la columna dentro de la fila a verificar.

    Returns:
        bool: True si el valor coincide con el contenido de la columna, False en caso contrario.
    """

    # Selecciona la tercera celda (índice 2 porque empieza en 0)
    celda = fila.locator("td").nth(columna)

    # Obtén el texto de esa celda
    texto = celda.inner_text()

    return texto

