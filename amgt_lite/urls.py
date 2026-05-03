from django.urls import path
from . import views
from . import controllers
from django.contrib import admin

urlpatterns = [
    path('', views.home, name="home"),
    path('amgt/admin/', admin.site.urls),
    path('amgt/comando/terceros/form/', views.formulario_acceso_terceros, name="formulario_acceso_terceros"),
    path('form-ordenar/', views.form_ordenar, name="form_ordenar"),
    path('form-libro-diario/', views.form_libro_diario, name="form_libro_diario"),
    path('form-informe-dian/', views.form_informe_dian, name="form_informe_dian"),
    path('amgt/dian/descargas/form/', views.form_descargas, name="form_descargas"),
    path('form-carga-documentos/', views.form_carga_documentos, name="form_carga_documentos"),
    path('en-desarrollo/', views.en_desarrollo, name="en_desarrollo"),
    path('carga-descargas/', views.carga_descargas, name="carga_descargas"),
    path('amgt/docs/generar-contaexcel/form', views.form_contaexcel, name='form_generar_contaexcel'),
    path('amgt/conecta/documentos/run/', controllers.registrar_movimientos, name='cargar_documentos'),
    path('amgt/conecta/documentos/validar/',controllers.api_verificar_documentos_conecta, name='validar_documentos'),
    path('amgt/dian/descargas/run/', controllers.api_dian_descargar, name="dian_descargar_run"),
    path('amgt/comando/terceros/run/', controllers.crear_terceros, name="cargar_terceros"),
    #@GET - Api para traer el enlace de la empresa
    path('amgt/ajax/enlace-conecta/<int:id>/', controllers.get_enlace, name='get_enlace'),
    path('amgt/dian/descargas/set/token/', controllers.api_actualizar_token, name='api_actualizar_token_dian'),
    path('amgt/dian/descargas/get/estado/', controllers.api_getEstado, name="get_estado_descargas"),
    # Documentos
    #@POST - Generar informe del listado de la dian
    path('amgt/dian/generar-informe/run/', controllers.api_informe_listado_dian, name='api_informe_listado_dian'),
    path('amgt/dian/descargas/set/stop/', controllers.api_cancelar_descarga, name="cancelar_descargas_dian"),
    #@POST - Generar informe del libro diario conecta
    path('amgt/comando/generar-informe/run/', controllers.api_informe_libro_diario_comando, name='api_informe_libro_diario_comando'),

    #@POST - Ordenar archivos DIAN
    path('amgt/local/ordenar_documentos/run/', controllers.api_ordenar_facturas, name='api_ordenar_documentos'),

    #@POST - Crear excel contapyme
    path('amgt/contapyme/xml-to-csv/documentos/run',controllers.api_generar_contapyme_excel_xml, name='api_contapyme_xml_to_csv_documentos'),

    #@POST - Crear excel terceros contapyme
    #path('amgt/contapyme/xml-to-csv/terceros/run',controllers.api_generar_terceros_excel_xml, name='api_contapyme_xml_to_csv_terceros'),

    #@POST - Crear excel conecta
    #path('amgt/conecta/xml-to-csv/documentos/run',controllers.api_generar_conecta_excel_xml, name='api_conecta_xml_to_csv_documentos'),

    #@POST - Extraer informacion de facturas personalidas 
    #path('',controllers.api_extraer_info_fras, name='api_extraer_info_fras'),

    #@GET - Cuentas del archivo excel
    #path('', controllers.get_cuentas, name='get_cuentas'),


]
