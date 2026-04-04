import logging

# Logger general (usa app.log y consola)
logger = logging.getLogger(__name__)

# Logger especial para pasos (usa pasos.log)
logger_pasos = logging.getLogger("pasos")

# Logger especial para tareas (usa tareas.log)
logger_tareas = logging.getLogger("tareas")

# Logger especial para errores detallados (usa error.log)
logger_errors = logging.getLogger("errors")


def registrar_paso(txt: str):
    logger_pasos.info(f"Paso: {txt}")


def registrar_error(error: str):
    # En app.log se guarda el resumen (por el root logger)
    logger.error(error)
    # En error.log se guarda el detalle completo
    logger_errors.error(error, exc_info=True)


def registrar_advertencia(error: str):
    logger.warning(error)


def registrar_nuevo_proceso(proceso: str):
    logger_tareas.info(f"Tarea: {proceso} -> iniciada")


def registrar_proceso_terminado(proceso: str):
    logger_tareas.info(f"Tarea: {proceso} -> terminada")
