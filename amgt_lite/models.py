from django.db import models
from typing import List

class Empresa(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la empresa")
    nit = models.CharField(max_length=20, verbose_name="NIT")
    cedula_representante = models.CharField(max_length=20, verbose_name="Cédula del representante legal")
    nombre_representante = models.CharField(max_length=255, verbose_name="Nombre del representante legal")
    enlace_conecta = models.URLField(blank=True, null=True, verbose_name="Enlace de Conecta (si aplica)")
    correo = models.EmailField(verbose_name="Correo electrónico")

    def __str__(self):
        return f"{self.nombre} ({self.nit})"
    
class Tercero:
    def __init__(self, Tipo_Documento, Documento, Régimen, Tipo, Documento_Soporte,
                 Primer_Nombre, Otro_Nombre, Primer_Apellido, Segundo_Apellido,
                 Razón_Social, Nombre_Comercial, Dirección, País, Ciudad,
                 Teléfono, Email):
        self.Tipo_Documento = Tipo_Documento
        self.Documento = Documento
        self.Régimen = Régimen
        self.Tipo = Tipo
        self.Documento_Soporte = Documento_Soporte
        self.Primer_Nombre = Primer_Nombre
        self.Otro_Nombre = Otro_Nombre
        self.Primer_Apellido = Primer_Apellido
        self.Segundo_Apellido = Segundo_Apellido
        self.Razón_Social = Razón_Social
        self.Nombre_Comercial = Nombre_Comercial
        self.Dirección = Dirección
        self.País = País
        self.Ciudad = Ciudad
        self.Teléfono = Teléfono
        self.Email = Email

    def __repr__(self):
        return (f"Tercero({self.Documento} - {self.Primer_Nombre} {self.Primer_Apellido}, "
                f"{self.Ciudad}, {self.País})")

# Create your models here.

class LineaContable:
    def __init__(self, cuenta, detalle, tercero, centro_costo, debito, credito, porcentaje):
        self.cuenta = cuenta
        self.detalle = detalle
        self.debito = debito
        self.credito = credito
        self.tercero = tercero
        self.porcentaje = porcentaje

    def __repr__(self):
        return f"Linea({self.cuenta} | D:{self.debito} C:{self.credito} )"
    
class Doc:
    def __init__(self, fecha, numero, tipo, lineas:List[LineaContable]):
        self.fecha = fecha
        self.numero = numero
        self.tipo = tipo
        self.lineas = lineas

    def __repr__(self):
        return f"doc({self.numero} | {self.fecha})"
    

class Acuse:
    def __init__(self, cufe, numero, tercero):
        self.cufe = cufe
        self.numero = numero
        self.tercero = tercero

    def __repr__(self):
        return f"doc({self.numero})"