from django.shortcuts import render
from .models import Empresa
def home(request):
    return render(request, "base.html")

def formulario_acceso_terceros(request):
    empresas = Empresa.objects.all()
    return render(request, "formulario_acceso_terceros.html", {'empresas': empresas})

def form_ordenar(request):
    return render(request, "form_ordenar.html")

def form_libro_diario(request):
    return render(request, "form_libro_diario.html")

def form_informe_dian(request):
    return render(request, "form_informe_dian.html")

def form_descargas(request):
    return render(request, "form_descargas.html")

def form_contaexcel(request):
    return render(request, "form_contaexcel.html")

def form_carga_documentos(request):
    empresas = Empresa.objects.all()
    return render(request, "form_carga_documentos.html", {'empresas': empresas})

def en_desarrollo(request):
    return render(request, "en_desarrollo.html")

def carga_descargas(request):
    return render(request, "carga_descargas.html")

def view_progreso_descarga(request):
    return render(request, "carga_descargas.html")