from django.shortcuts import render
from .models import Empresa   # asegúrate de importar desde tu app
import pandas as pd
from django.http import JsonResponse
from .scripts.log import *
import json
from .scripts.dian import estado, descargar_documentos
from .scripts.conecta import x, cargar_documentos,extraer_terceros,extraer_cuentas, verificar_terceros as vt, verificar_cuentas as vc, validar_porcentajes, limpiarDatos
from .scripts.comando import crear_terceros_run
import threading


def get_enlace(request, id):
    try:
        empresa = Empresa.objects.get(id=id)
        return JsonResponse({'enlace': empresa.enlace_conecta})
    except Empresa.DoesNotExist:
        return JsonResponse({'enlace': ''})

def crear_terceros(request):
    if request.method != "POST":
        return render(request, "resultado.html", {"resultado": "Método no permitido"}, status=405)

    empresa_id = request.POST.get('empresa') 
    archivo = request.FILES.get('archivo')  

    if not empresa_id:
        return render(request, "resultado.html", {"resultado": "No se recibió empresa"}, status=400)
    
    if not archivo:
        return render(request, "resultado.html", {"resultado": "No se recibió archivo"}, status=400)
    
    # Obtener enlace de la empresa
    try:
        empresa = Empresa.objects.get(id=empresa_id)
        enlace = empresa.enlace_conecta
    except Empresa.DoesNotExist:
        return render(request, "resultado.html", {"resultado": "Empresa no encontrada"}, status=404)

    # Leer archivo con pandas
    try:
        if archivo.name.endswith('.csv'):
        
            df = pd.read_csv(archivo, sep=";", encoding='latin-1')
        elif archivo.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(archivo)
        else:
            return render(request, "resultado.html", {"resultado": "Formato de archivo no soportado"}, status=400)
    except Exception as e:
        return render(request, "resultado.html", {"resultado": f"Error procesando archivo: {str(e)}"}, status=500)

    # Ejecutar proceso
    columnas_requeridas = [
        "Tipo_Documento",
        "Documento",
        "Régimen",
        "Tipo",
        "Documento_Soporte",
        "Primer_Nombre",
        "Otro_Nombre",
        "Primer_Apellido",
        "Segundo_Apellido",
        "Razón_Social",
        "Nombre_Comercial",
        "Dirección",
        "País",
        "Ciudad",
        "Teléfono",
        "Email",
    ]
    for col in columnas_requeridas:
        if not col in df.columns:
            return render(request, "resultado.html", {"resultado": f"No se encontro la columna: [{col}] en el excel"}, status=400)
    try:
        crear_terceros_run(enlace, df)
    except Exception as e:
        return render(request, "resultado.html", {"resultado": f"Error interno del server: {str(e)}"}, status=500)

    return render(request, "resultado.html", {"resultado": "Proceso ejecutado exitosamente"})


#----------------------------------Apis de produccion-----------------------------
def api_dian_descargar(request):
    if request.method == "POST":
        registrar_paso("Se inicio el proceso para descargar documentos de la DIAN")
        # Obtenemos los datos de la solicitud 
        
        token = request.POST.get("token", "").strip()
        cufes_texto = request.POST.get("cufes", "")
        cufes = [u.strip() for u in cufes_texto.splitlines() if u.strip()]
        tam = len(cufes)

        registrar_paso(f"Se solicito descargar {tam} documentos")
        # Enviamos los datos a la clase encargada
        estado.clear()
        estado.set_token(token)

        # Corremos el servicio de descargar documentos de la DIAN
        registrar_paso(f"Inciando proceso de descargar {tam} documentos")
        descargar_documentos(cufes)
        return JsonResponse({"status": "ok"}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


def api_getEstado(request):
    # Obtenemos el total de documentos descargados exitosamente
    descargados = estado.get_cant_descargados()
    # Obtenemos el total de documento que se enviaron a descargar
    total = estado.get_total()
    # Obtenemos el estado del token
    activo = estado.get_activo()

    if total == 0:
        msj = "No iniciado"
    elif descargados == 0:
        msj = "Cargando..."
    elif descargados < total:
        msj = "Descargando"
    elif activo == False:
        msj = "Esperando Token"
    elif descargados == total:
        msj = "Terminado"
        registrar_proceso_terminado(f"se descargaron los {total} documentos exitosamente")
    
    # Debug seguro
    print(f"DEBUG -> estado: {msj}, descargados: {descargados}, total: {total}")

    return JsonResponse({
        "descargados": descargados,
        "total": total,
        "estado": msj
    })

def api_cancelar_descarga():
    estado.set_stop(True)

def api_actualizar_token(request):
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        estado.set_token(token)   # tu función que guarda el token
        print("Token actualizado: ", token)
        return JsonResponse({"status": "ok", "token": token})
    return JsonResponse({"status": "error", "message": "Método no permitido"})  

#--------------------------------Apis de testeo--------------------------------------

def api_set_cant_descargados(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        cant = data.get("cant", "").strip()
        estado.cant_descargados = cant
        return JsonResponse({"status": "ok", "cant": cant}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

# Procesar formulario 
def registrar_movimientos(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    empresa_id = request.POST.get('empresa')
    archivo = request.FILES.get('archivo')
    cuentas = request.POST.get('cuentas')   
    checks = request.POST.get('checks')     
    token = request.POST.get('token')
    
    if not empresa_id:
        return JsonResponse({"error": "empresa no valida"}, status=400)
    if not archivo:
        return JsonResponse({"error": "archivo no valido"}, status=400)
    if not cuentas:
        return JsonResponse({"error": "cuentas no valida"}, status=400)
    if not checks: 
        return JsonResponse({"error": "checks no validos"}, status=400)
    if not token:
        return JsonResponse({"error": "token no valido"}, status=400)
    

    # Convertir JSON string a lista
    try:
        checks_list = json.loads(checks)
    except Exception as e:
        return JsonResponse({"error": f"Error parseando checks: {str(e)}"}, status=400)

    # Diccionario de mapeo
    mapa = {
        "Opción A": "nit",
        "Opción B": "fecha",
        "Opción C": "numero_documento"
    }

    agrupaciones_convertidas = []
    for opcion in checks_list:
        if opcion in mapa:
            agrupaciones_convertidas.append(mapa[opcion])
        else:
            print(f"Opción desconocida: {opcion}")

    print(agrupaciones_convertidas)

    # Obtener enlace de la empresa
    try:
        empresa = Empresa.objects.get(id=empresa_id)
        enlace = empresa.enlace_conecta
    except Empresa.DoesNotExist:
        enlace = None
        mensaje += " Empresa no encontrada. "

    # limpiando datos
    # Detectar extensión y leer con pandas
    if archivo.name.endswith('.csv'):
        # Forzar separador por punto y coma
        df = pd.read_csv(archivo, sep=";", encoding='latin-1')
    elif archivo.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(archivo)
    else:
        return JsonResponse({"error": "Formato no soportado"}, status=400)
    print("validadndo porcentajes")
    try: 
        archivo_limpio = limpiarDatos(df)
    except Exception as e:
        return JsonResponse({"error": f"Error limpiando el archivo: {str(e)}"}, status=500)
    
    print("se limpio el archivo")
    porcentajes_validos, errores = validar_porcentajes(archivo_limpio, cuentas)
    if not porcentajes_validos:
        return JsonResponse({
            "error": "faltan porcentajes en las bases",
            "detalles": errores
        }, status=405)

    # Ejecutar Playwright con tus parámetros
    try:
        cargar_documentos(cuentas, agrupaciones_convertidas, enlace, archivo_limpio, token)
    except Exception as e:
        return JsonResponse({"resultado": f"error en el proceso: {str(e)}"}, status=500)

    return JsonResponse({"resultado": "Proceso ejecutado correctamente."}, status=200)

hilo_terceros=None
hilo_cuentas=None

def api_verificar_documentos_conecta(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    empresa_id = request.POST.get('empresa')
    archivo = request.FILES.get('archivo')  
    token = request.POST.get('token')
    
    if not empresa_id:
        return JsonResponse({"error": "empresa no valida"}, status=400)
    if not archivo:
        return JsonResponse({"error": "archivo no valido"}, status=400)
    if not token:
        return JsonResponse({"error": "token no valido"}, status=400)
    # Obtener enlace de la empresa
    try:
        empresa = Empresa.objects.get(id=empresa_id)
        enlace = empresa.enlace_conecta
    except Empresa.DoesNotExist:
        enlace = None
        mensaje += " Empresa no encontrada. "
    # Detectar extensión y leer con pandas
    if archivo.name.endswith('.csv'):
        # Forzar separador por punto y coma
        df = pd.read_csv(archivo, sep=";", encoding='latin-1')
    elif archivo.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(archivo)
    else:
        return JsonResponse({"error": "Formato no soportado"}, status=400)
    try:
        cuentas_finales = []
        if empresa_id == x.get_id_empresa:
            cuentas_finales = list(set(extraer_cuentas(df)).difference(x.get_cuentas_verificadas()))
        if len(cuentas_finales) > 0:
            hilo_cuentas = threading.Thread(target=vc, args=(enlace, token, cuentas_finales)).start()
 
        terceros_finales = []
        if id == x.get_id_empresa:
            terceros_finales = list(set(extraer_terceros(df)).difference(x.get_terceros_verificados()))
        if len(terceros_finales) > 0:
            hilo_terceros = threading.Thread(target=vt, args=(enlace, token, terceros_finales)).start()
        
        hilo_terceros.join()
        hilo_cuentas.join()
        data = {
            "tabla1": [],
            "tabla2": []
        }

        # --- Cuentas ---
        for cuenta in x.get_cuentas_null():
            data["tabla1"].append({
                "Cuenta": cuenta,
                "Faltante": "Sí",
                "Base": ""
            })
        for cuenta in x.get_cuentas_verificadas():
            data["tabla1"].append({
                "Cuenta": cuenta,
                "Faltante": "No",
                "Base": "No"
            })
        for cuenta in x.get_cuentas_base():
            data["tabla1"].append({
                "Cuenta": cuenta,
                "Faltante": "No",
                "Base": "Sí"
            })

        # --- Terceros ---
        for tercero in x.get_terceros_null():
            data["tabla2"].append({
                "Tercero": tercero,
                "Faltante": "Sí"
            })
        for tercero in x.get_terceros_verificados():
            data["tabla2"].append({
                "Tercero": tercero,
                "Faltante": "No"
            })

        return JsonResponse(data, status=200)
    except Exception as e:
        return JsonResponse ({
        "mensaje": f"error validando: {e}", 
    }, status=500)
    
def get_x(request):
    try:
        hilo_terceros.join()
        hilo_cuentas.join()
        respuesta = x.to_dict
        return JsonResponse(respuesta, status=200)
    except Exception as e:
        return render(request, "resultado.html", {"resultado": f"error verificando los datos: {e}"}, status=500)
 


def api_extract_cuentas_and_terceros_to_csv(request):
    # Verificamos que sea un POST y que venga el archivo
    if request.method == "POST" and request.FILES.get("file"):
        try:
            # Leemos el CSV directamente desde el archivo recibido
            csv_file = request.FILES["file"]
            # Detectar extensión y leer con pandas
            if csv_file.name.endswith('.csv'):
                # Forzar separador por punto y coma
                df = pd.read_csv(csv_file, sep=";", encoding='latin-1')
            elif csv_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(csv_file)
            else:
                return JsonResponse({"error": "Formato no soportado"}, status=400)

            
            # Extraemos valores únicos de las columnas
            terceros = extraer_terceros(df)
            cuentas = extraer_cuentas(df)

            # Devolvemos ambas listas en un JSON
            return JsonResponse({
                "terceros": terceros,
                "cuentas": cuentas
            }, safe=False, status=200)

        except Exception as e:
            return JsonResponse({
                "error": f"Ocurrió un problema al procesar el archivo: {str(e)}"
            }, status=500)

    return JsonResponse({"error": "Debes enviar un archivo CSV válido"}, status=400)


from django.http import HttpResponse
import pandas as pd
from .scripts.docs_repo.services.informe_dian_services import generarInforme
from .scripts.docs_repo.services.libro_diario_conecta_services import generarInforme as gild
from .scripts.docs_repo.services.manejo_archivos_dian_services import ordenar
import os
from django.shortcuts import render
from .scripts.docs_repo.services.conta_excel.xmlToCsv import extraer_facturas
from .scripts.docs_repo.services.conta_excel.limpiar_datos import limpiar_facturas
from .scripts.docs_repo.services.conta_excel.generar_contapyme import generarContapymeRecibidos, generarContapymeEmitidos


from django.http import HttpResponse, JsonResponse

def api_generar_contapyme_excel_xml(request):
    """
    API:
        Genera archivo CONTAEXCEL para Contapyme a partir de facturas XML.
    Método:
        {POST}
    Parámetros:
        request.POST.get("ruta") -> Ruta de la carpeta con los XML
        request.POST.get("tipo") -> Emitidos o recibidos (1 o 2)
    Respuesta:
        HttpResponse con archivo CSV (facturas_contapyme.csv)
        En caso de error: JsonResponse con mensaje y código de estado
    """
    try:
        # Validación de parámetros
        tipo = request.POST.get("tipo")
        print(tipo)
        if str(tipo) not in ["emisor", "receptor"]:   # ojo: POST devuelve string
            return JsonResponse({"error": "El tipo no es valido"}, status=400)

        ruta = request.POST.get("ruta")
        if not ruta or len(ruta.strip()) == 0:
            return JsonResponse({"error": "La ruta no es válida"}, status=400)

        # Extraer y limpiar
        df = extraer_facturas(ruta)
        df_explorer = limpiar_facturas(df)

        if tipo == "recibidos":
            df_contapyme = generarContapymeRecibidos(df_explorer)
        else:
            df_contapyme = generarContapymeEmitidos(df_explorer)

        # Convertir a CSV en memoria
        csv_data = df_contapyme.to_csv(index=False, sep=";", encoding="utf-8")

        # Preparar respuesta HTTP para descarga
        response = HttpResponse(csv_data, content_type="text/csv", status=200)
        response["Content-Disposition"] = 'attachment; filename="facturas_contapyme.csv"'
        return response

    except Exception as e:
        # Captura cualquier error inesperado y devuelve JSON estructurado
        return JsonResponse(
            {"error": "Error interno al generar el archivo", "detalle": str(e)},
            status=500
        )


def api_informe_listado_dian(request):
    """
    API:
        Genera informe del listado DIAN en Excel.
    Método:
        POST
    Parámetros:
        request.FILES.get("archivo") -> Archivo listado DIAN
    Respuesta:
        HttpResponse con archivo Excel (Resumen + nombre original)
        En caso de error: JsonResponse con mensaje y código de estado
    """
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Método no permitido"}, status=405)

        archivo = request.FILES.get("archivo")
        if not archivo:
            return JsonResponse({"error": "No se recibió archivo"}, status=400)

        output = generarInforme(archivo)
        nombre_original = archivo.name

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            status=200
        )
        response["Content-Disposition"] = f'attachment; filename="Resumen {nombre_original}"'
        return response

    except Exception as e:
        return JsonResponse({"error": "Error interno al generar informe DIAN", "detalle": str(e)}, status=500)



def api_informe_libro_diario_comando(request):
    """
    API:
        Genera informe del libro diario (Comando).
    Método:
        POST
    Parámetros:
        request.FILES.get("archivo") -> Archivo listado Comando
    Respuesta:
        HttpResponse con archivo Excel (documentos_nombre.xlsx)
        En caso de error: JsonResponse con mensaje y código de estado
    """
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Método no permitido"}, status=405)

        archivo = request.FILES.get("archivo")
        if not archivo:
            return JsonResponse({"error": "No se recibió archivo"}, status=400)

        df = gild(archivo)
        nombre_base, _ = os.path.splitext(archivo.name)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            status=200
        )
        response["Content-Disposition"] = f'attachment; filename="documentos_{nombre_base}.xlsx"'

        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Hoja1", index=False)

        return response

    except Exception as e:
        return JsonResponse({"error": "Error interno al generar libro diario", "detalle": str(e)}, status=500)



def api_ordenar_facturas(request):
    """
    API:
        Ordena documentos electrónicos DIAN.
        Renombra y separa en carpetas.
    Método:
        POST
    Parámetros:
        request.FILES.get("archivo") -> Listado DIAN
        request.POST.get("ruta") -> Ruta de la carpeta con los XML
        request.POST.get("modo") -> Modo de ordenamiento
    Respuesta:
        Render de template resultado_documentos.html con el resultado
        En caso de error: JsonResponse con mensaje y código de estado
    """
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Método no permitido"}, status=405)

        archivo = request.FILES.get("archivo")
        ruta_carpeta = request.POST.get("ruta")
        modo = request.POST.get("modo")

        if not archivo:
            return JsonResponse({"error": "No se recibió archivo"}, status=400)
        if not ruta_carpeta or len(ruta_carpeta.strip()) == 0:
            return JsonResponse({"error": "La ruta no es válida"}, status=400)
        if not modo:
            return JsonResponse({"error": "El modo no es válido"}, status=400)

        resultado = ordenar(ruta_carpeta, archivo, modo)
        return render(request, "resultado_documentos.html", {"resultado": resultado})

    except Exception as e:
        return JsonResponse({"error": "Error interno al ordenar facturas", "detalle": str(e)}, status=500)

def api_generar_terceros_excel_xml():
    return

def api_generar_conecta_excel_xml():
    return
