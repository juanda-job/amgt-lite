from ...log import *

class Fill_exception(Exception):
    """
    Excepción personalizada para errores al llenar el campo de numero.

    Se utiliza cuando:
    - El método `fill` de Playwright falla durante la operación.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Date_not_equals_exception(Exception):
    """
    Excepción personalizada para discrepancias en la fecha.

    Se utiliza cuando:
    - La fecha ingresada en el campo no coincide con la solicitada por el usuario.
    - Existe una diferencia entre la fecha del sistema y la esperada.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Document_type_not_found_exception(Exception):
    """
    Excepción personalizada para errores relacionados con el tipo de documento.

    Se utiliza cuando:
    - El campo de tipo de documento no existe en la página.
    - No se encuentra el valor esperado para el tipo de documento.
    - El tipo de documento no existe
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Typing_exception(Exception):
    """
    Excepción personalizada para errores al escribir en el campo de documento.

    Se utiliza cuando:
    - El método `type` de Playwright falla al ingresar texto.
    - El valor escrito no se refleja correctamente en el campo.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Not_is_my_page_exception(Exception):
    """
    Excepción personalizada para errores de contexto de página.

    Se utiliza cuando:
    - La página actual no corresponde a la esperada en el flujo de automatización.
    - Se detecta un cambio inesperado de URL o estructura.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Num_load_exception(Exception):
    """
    Excepción personalizada para errores en la carga de números o datos.

    Se utiliza cuando:
    - El número esperado no se carga correctamente en la página.
    - El valor numérico no coincide con lo solicitado.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Add_line_exception(Exception):
    """
    Excepción personalizada para errores al agregar una fila.

    Se utiliza cuando:
    - La fila no se inserta correctamente en la página.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Get_infomation_exception(Exception):
    """
    Excepción personalizada para errores al agregar una fila.

    Se utiliza cuando:
    - La fila no se inserta correctamente en la página.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Locator_exception(Exception):
    """
    Excepción personalizada para errores al obtener objetos.

    Se utiliza cuando:
    - no se encuentra el objeto en la pagina.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Option_exception(Exception):
    """
    Excepción personalizada para errores al obtener objetos.

    Se utiliza cuando:
    - no se encuentra el objeto en la pagina.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)

class Select_exception(Exception):
    """
    Excepción personalizada para errores al obtener objetos.

    Se utiliza cuando:
    - no se encuentra el objeto en la pagina.
    """
    def __init__(self, mensaje):
        registrar_error(mensaje)
        super().__init__(mensaje)












