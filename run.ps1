# Script para PowerShell: activar entorno virtual y correr servidor Django

# Ruta del entorno virtual (ajusta si está en otra carpeta)
$envPath = "A:\AMGT LITE\amgt-lite\.venv\Scripts\Activate.ps1"

# Activar entorno virtual
if (Test-Path $envPath) {
    & $envPath
    Write-Host "Entorno virtual activado."
} else {
    Write-Host "No se encontró el entorno virtual en '$envPath'."
    exit
}

# Verificar si Django está instalado
$djangoCheck = python -m django --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "Django está instalado. Versión: $djangoCheck"
} else {
    Write-Host "Django no está instalado en este entorno."
    exit
}

# Ejecutar servidor de desarrollo
Write-Host "Iniciando servidor Django en http://127.0.0.1:8000/"
python "A:\AMGT LITE\amgt-lite\manage.py" runserver