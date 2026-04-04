from playwright.sync_api import Page
from ..exceptions import Add_line_exception
from ..exceptions import Get_infomation_exception
from ..exceptions import Fill_exception
from ..exceptions import Typing_exception
from ..exceptions import Locator_exception
from ..exceptions import Select_exception
from ..exceptions import Option_exception


# Componente raíz de la tabla de movimientos
component = "app-tabla-movimientos"
# Selector de la tabla dentro del componente
table = f"{component} table"
# Selector del cuerpo de la tabla
body = f"{table} tbody"
# Selector del encabezado de la tabla
head = f"{table} thead"
# Selector de las filas dentro del cuerpo
filas = f"{body} tr"
# Selector de las filas dentro del head
encabezados = f"{head} tr"

# Numero correspondientes a las columnas del tbody
columnas_items = {
    # Numero correspondiente a la columna para items
    "codigo": 0,
    "concepto": 1,
    "tercero": 2,
    "centro_costo": 3,
    "debito": 4,
    "credito": 5,
    "opciones": 6,
    # Numero correspondiente a la columna para resumen
    "total_debito": 1,
    "total_credito": 2,
    "diferencia": 3
}

def get_diferencia(page:Page) -> str:
    try: 
        return page.locator(filas).nth(0).locator('td').nth(columnas_items["diferencia"]).inner_text()
    except Exception as e:
        print(str(e)) 
        raise Get_infomation_exception("Error extrayendo la diferencia")

def get_total_debito(page:Page) -> str:
    try:
        return page.locator(filas).nth(0).locator('td').nth(columnas_items["total_debito"]).inner_text()
    except Exception as e:
        print(str(e)) 
        raise Get_infomation_exception("Error extrayendo el total del debito")
    
def get_total_credito(page:Page) -> str:
    try: 
        return page.locator(filas).nth(0).locator('td').nth(columnas_items["total_credito"]).inner_text()
    except Exception as e:
        print(str(e)) 
        raise Get_infomation_exception("Error extrayendo el total del credito")
    
def agregarLinea(page:Page, num_fila:int = 1, direccion:str = "arriba"):
    try: 
        page.locator(filas).nth(num_fila).locator("button.mat-mdc-menu-trigger").click()
        if direccion == "arriba":
            page.get_by_role("menuitem", name="Agregar ítem arriba").click()
        elif direccion == "abajo":
            page.get_by_role("menuitem", name="Agregar ítem abajo").click()
    except Exception as e:
        print(str(e))
        raise Add_line_exception("Error agregando una nueva fila a la tabla")

def fill_texto(page:Page, fila:int, columna: int, texto: str):
    try: 
        page.locator(filas).nth(fila).locator('td').nth(columna).locator("input").fill(texto)
    except Exception as e:
        print(str(e))
        raise Fill_exception("Error pegando el texto en el campo: "+str(columna))

def set_cuenta(page: Page, fila: int, cuenta: str):
    try:
        # Localizamos la fila y sus celdas
        fila_locator = page.locator(filas).nth(fila)
        celdas = fila_locator.locator("td")
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar la fila {fila}: {str(e)}")
    
    try:
        # Localizamos el input de la columna 'codigo'
        input_locator = celdas.nth(columnas_items["codigo"]).locator("input")
        input_locator.fill("")  # Limpia el campo
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar/limpiar el input de cuenta: {str(e)}")

    try:
        # Intentamos escribir la cuenta
        input_locator.type(cuenta, delay=100)
    except Exception as e:
        raise Typing_exception(f"No se pudo escribir la cuenta {cuenta}: {str(e)}")

    name = ""
    aux = True
    while aux:
        try:
            # Obtenemos todas las opciones visibles
            opciones = page.locator("mat-option span")
            textos = opciones.all_text_contents()
        except Exception as e:
            raise Option_exception(f"Error obteniendo opciones de cuenta: {str(e)}")

        for texto in textos:
            if texto.startswith(" " + str(cuenta) + " - "):
                aux = False
                name = texto
                break

        # Esperamos un poco antes de volver a intentar
        page.wait_for_timeout(1000)

    try:
        # Intentamos hacer clic en la opción encontrada
        page.locator("mat-option span", has_text=name).first.click()
    except Exception as e:
        raise Locator_exception(f"No se pudo seleccionar la opción {name}: {str(e)}")

def is_vacia(page: Page, fila: int, columna: int) -> bool:
    """
    Verifica si una celda de la tabla está vacía.

    Args:
        page (Page): Objeto Playwright que representa la página actual.
        fila (int): Índice de la fila dentro del cuerpo de la tabla (0-based).
        columna (int): Índice de la columna dentro de la fila (0-based).

    Returns:
        bool: True si la celda está vacía (sin texto o solo espacios), False en caso contrario.

    Raises:
        Exception: Si ocurre un error al localizar la fila o la celda.
    """
    try:
        # Localizamos la fila por índice
        fila_locator = page.locator(filas).nth(fila)
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar la fila {fila}: {str(e)}")

    try:
        # Localizamos la celda dentro de la fila
        celda_locator = fila_locator.locator("td").nth(columna)
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar la columna {columna} en la fila {fila}: {str(e)}")

    try:
        # Obtenemos el texto de la celda
        contenido = celda_locator.text_content()
    except Exception as e:
        raise Locator_exception(f"No se pudo obtener el contenido de la celda ({fila}, {columna}): {str(e)}")

    # Validamos si está vacía (None o solo espacios)
    return (contenido is None) or (contenido.strip() == "")

def set_tercero(page: Page, fila: int, nit: str):
    """
    Ingresa un tercero en la fila indicada de la tabla, buscando el NIT en las opciones desplegables.

    Args:
        page (Page): Objeto Playwright que representa la página actual.
        fila (int): Índice de la fila dentro del cuerpo de la tabla (0-based).
        nit (str): Número de identificación del tercero a ingresar.

    Raises:
        Locator_exception: Si ocurre un error al localizar fila, celdas o input.
        Typing_exception: Si ocurre un error al escribir el NIT en el campo.
        Option_exception: Si no se encuentran opciones o no coincide el NIT.
        Selection_exception: Si ocurre un error al seleccionar la opción final.
    """

    try:
        # Localizamos la fila y sus celdas
        fila_locator = page.locator(filas).nth(fila)
        celdas = fila_locator.locator("td")
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar la fila {fila}: {str(e)}")

    try:
        # Localizamos el input de la columna 'tercero'
        input_locator = celdas.nth(columnas_items["tercero"]).locator("input")
        input_locator.clear()  # Limpia el campo
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar/limpiar el input de tercero: {str(e)}")

    try:
        # Escribimos el NIT en el campo
        input_locator.type(nit, delay=100)
    except Exception as e:
        raise Typing_exception(f"No se pudo escribir el NIT {nit}: {str(e)}")

    name = ""
    aux = True
    while aux:
        try:
            # Obtenemos todas las opciones desplegadas
            opciones = page.locator("mat-option span")
            textos = opciones.all_text_contents()
        except Exception as e:
            raise Option_exception(f"Error obteniendo las opciones de terceros: {str(e)}")

        if not textos:
            raise Option_exception(f"No se encontraron opciones para el NIT {nit}")

        try:
            # Recorremos las opciones buscando coincidencia con el NIT
            for i, texto in enumerate(textos):
                datos = texto.split('-')
                print(i, texto)
                if len(datos) > 1 and datos[1].strip() == nit.strip():
                    aux = False
                    name = texto
                    break
        except Exception as e:
            raise Option_exception(f"Error procesando las opciones: {str(e)}")

        # Esperamos un poco antes de volver a intentar
        page.wait_for_timeout(1000)

    try:
        # Seleccionamos la opción encontrada
        page.locator("mat-option span", has_text=name).first.click()
    except Exception as e:
        raise Select_exception(f"No se pudo seleccionar la opción {name}: {str(e)}")
    
def set_valor(page:Page, fila:int, columna:int, base:bool, valor, porcentaje):
    print("valor:"+str(valor))
    try:
        # Localizamos la fila y sus celdas
        fila_locator = page.locator(filas).nth(fila)
        celdas = fila_locator.locator("td")
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar la fila {fila}: {str(e)}")

    try:
        # Localizamos el input de la columna 'debito'
        input_locator = celdas.nth(columna).locator("input")
        input_locator.clear()  # Limpia el campo
    except Exception as e:
        raise Locator_exception(f"No se pudo localizar/limpiar el input de tercero: {str(e)}")
    if(base):
        campo = page.locator("mat-form-field:has-text('Valor base') input")
        campo.wait_for(state="visible", timeout=5000)
        base = float(valor)/float(porcentaje)*100
        base = round(base, 2)
        campo.click()
        campo.locator("input")
        campo.fill(str(base))
        campo = page.locator("mat-form-field:has-text('Tarifa') input")
        campo.click()
        campo.wait_for(state="visible", timeout=5000)
        campo.fill(porcentaje)
        page.get_by_role("button", name="Aceptar").click()
        page.wait_for_timeout(2000)
    else:
        input_locator = celdas.nth(columna).locator("input")
        input_locator.fill(str(valor))
        input_locator.press("Enter")        





