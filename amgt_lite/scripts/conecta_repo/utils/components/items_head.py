from playwright.sync_api import Page
from ..exceptions import Date_not_equals_exception
from ..exceptions import Document_type_not_found_exception
from ..exceptions import Typing_exception
from ..exceptions import Fill_exception


def set_date(page: Page, date: str):
    """
    Llena el campo de fecha en la página y valida que el valor ingresado coincida.

    Args:
        page (Page): Objeto Playwright que representa la página actual.
        date (str): Fecha a ingresar en el campo.

    Raises:
        Date_fill_exception: Si ocurre un error al intentar llenar el campo de fecha.
        Date_not_equals_exception: Si la fecha ingresada no coincide con la fecha esperada.
    """
    # Localizamos el campo de fecha por su ID
    date_locator = page.locator('[formcontrolname="fecha"]')
    try:
        # Intentamos llenar el campo con la fecha proporcionada
        date_locator.fill(date)
    except Exception as e:
        # Excepción si falla el llenado
        print(str(e)) 
        raise Fill_exception("Error al pegar la fecha")
    else:
        # Obtenemos el valor actual del campo
        date_system = date_locator.input_value()
        # Validamos que coincida con la fecha esperada
        if not (date_system == date):
            msj = f"El sistema no está tomando la fecha: {date} | Fecha sistema: {date_system}"
            # Excepción si la fecha no coincide
            raise Date_not_equals_exception(msj)


def set_document_type(page: Page, doc_type: str):
    """
    Ingresa y selecciona un tipo de documento en el campo correspondiente.

    Args:
        page (Page): Objeto Playwright que representa la página actual.
        doc_type (str): Texto del tipo de documento a ingresar y seleccionar.

    Raises:
        Typing_document_exception: Si ocurre un error al escribir el tipo de documento en el campo.
        Document_type_not_found_exception: Si el tipo de documento no aparece en la lista desplegable.
    """
    try:
        # Localizamos el campo de tipo de documento
        doc_type_locator = page.locator('[formcontrolname="id_tipo_documento_contable"]')
        # Hacemos clic para activar el campo
        doc_type_locator.click()

        # Calculamos la mitad del texto
        half = len(doc_type) // 2
        # Dividimos el texto en dos partes
        part1, part2 = doc_type[:half], doc_type[half:]

        # Escribimos la primera parte con delay
        doc_type_locator.type(part1, delay=100)
        # Esperamos que aparezca la lista desplegable
        # Espera a que aparezca al menos un mat-option
        page.locator("mat-option span").first.wait_for(state="visible")
        # Volvemos a hacer clic para asegurar visibilidad
        doc_type_locator.click()
        # Escribimos la segunda parte del texto
        doc_type_locator.type(part2, delay=100)
    except Exception as e:
        print(str(e)) 
        # Excepción si falla la escritura en el campo
        raise Typing_exception(
            f"Error escribiendo el tipo de documento: {doc_type} en el campo especificado"
        )

    try:
        # Seleccionamos el tipo de documento de la lista desplegable
        page.locator("mat-option span", has_text=doc_type).click()
    except Exception:
        print(str(e)) 
        # Excepción si el tipo de documento no aparece en la lista
        raise Document_type_not_found_exception(
            f"Error seleccionando el tipo de documento: {doc_type}"
        )


def get_number(page: Page) -> str:
    """
    Obtiene el número ingresado en el campo.

    Args:
        page (Page): Objeto Playwright que representa la página actual.

    Returns:
        str: Valor actual del campo de número.
    """
    # Localizamos el campo por formcontrolname
    locator = page.locator('[formcontrolname="numero"]')
    # Obtenemos el valor actual del input
    value = locator.input_value()
    # Retornamos el número
    return value


def set_number(page: Page, doc_num: str):
    """
    Llena el campo de número de documento con el valor especificado,
    esperando a que el campo tenga un valor diferente de "".
    """
    try:
        locator = page.locator('input[formcontrolname="numero"]')

        # Esperar hasta que el campo tenga algún valor distinto de vacío
        max_wait = 5000  # tiempo máximo en ms
        waited = 0
        while True:
            contenido = locator.input_value()
            if contenido.strip() != "":
                break
            page.wait_for_timeout(500)
            waited += 500
            if waited >= max_wait:
                raise Fill_exception("El campo de número de documento nunca obtuvo un valor distinto de vacío.")

        # Una vez que el campo ya tiene contenido, lo llenamos con el nuevo número
        locator.click()
        locator.clear()
        locator.type(doc_num, delay=100)

    except Exception as e:
        print(str(e))
        raise Fill_exception("No se pudo pegar el número de documento")

def get_doc_type(page: Page) -> str:
    """
    Obtiene el tipo de documento ingresado.

    Args:
        page (Page): Objeto Playwright que representa la página actual.

    Returns:
        str: Valor actual del campo de tipo de documento.
    """
    # Localizamos el campo por formcontrolname
    locator = page.locator('[formcontrolname="id_tipo_documento_contable"]')
    # Obtenemos el valor actual del input
    value = locator.input_value()
    # Retornamos el tipo
    return value

def get_date(page: Page) -> str:
    """
    Obtiene la fecha ingresada en el campo.

    Args:
        page (Page): Objeto Playwright que representa la página actual.

    Returns:
        str: Valor actual del campo de fecha.
    """
    # Localizamos el campo por formcontrolname
    locator = page.locator('[formcontrolname="fecha"]')
    # Obtenemos el valor actual del input
    value = locator.input_value()
    # Retornamos la fecha
    return value