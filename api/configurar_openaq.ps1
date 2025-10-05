# Script para configurar OpenAQ API Key
# Uso: .\configurar_openaq.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey
)

Write-Host "`n🔑 Configurador de OpenAQ API Key" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Ruta al archivo .env
$envPath = Join-Path $PSScriptRoot ".env"

# Verificar que existe el archivo .env
if (-not (Test-Path $envPath)) {
    Write-Host "`n❌ Error: No se encontró el archivo .env en:" -ForegroundColor Red
    Write-Host "   $envPath" -ForegroundColor Yellow
    exit 1
}

# Si no se pasó API key como parámetro, pedirla
if (-not $ApiKey) {
    Write-Host "`n📝 Instrucciones para obtener tu API Key:" -ForegroundColor Yellow
    Write-Host "   1. Regístrate en: https://explore.openaq.org/register" -ForegroundColor White
    Write-Host "   2. Inicia sesión en: https://explore.openaq.org/login" -ForegroundColor White
    Write-Host "   3. Ve a tu perfil: https://explore.openaq.org/account" -ForegroundColor White
    Write-Host "   4. Genera una nueva API Key" -ForegroundColor White
    Write-Host ""
    
    $ApiKey = Read-Host "Ingresa tu OpenAQ API Key (o presiona Enter para usar datos simulados)"
    
    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        Write-Host "`n⚠️ No se configuró API Key. La aplicación usará datos simulados." -ForegroundColor Yellow
        exit 0
    }
}

# Leer el contenido actual del .env
$envContent = Get-Content $envPath -Raw

# Verificar si ya existe la configuración de OPENAQ_API_KEY
if ($envContent -match "OPENAQ_API_KEY=") {
    Write-Host "`n📝 Actualizando API Key existente..." -ForegroundColor Yellow
    
    # Reemplazar la línea existente
    $envContent = $envContent -replace "OPENAQ_API_KEY='.*'", "OPENAQ_API_KEY='$ApiKey'"
    $envContent = $envContent -replace 'OPENAQ_API_KEY=""', "OPENAQ_API_KEY='$ApiKey'"
    $envContent = $envContent -replace "OPENAQ_API_KEY=''", "OPENAQ_API_KEY='$ApiKey'"
    
} else {
    Write-Host "`n📝 Añadiendo configuración de OpenAQ..." -ForegroundColor Yellow
    
    # Añadir al final del archivo
    if (-not $envContent.EndsWith("`n")) {
        $envContent += "`n"
    }
    $envContent += "`n# OpenAQ API Key`n"
    $envContent += "OPENAQ_API_KEY='$ApiKey'`n"
}

# Guardar el archivo
Set-Content -Path $envPath -Value $envContent -NoNewline

Write-Host "`n✅ API Key configurada exitosamente!" -ForegroundColor Green
Write-Host "`n📄 Archivo actualizado: $envPath" -ForegroundColor Cyan

# Mostrar un preview (ocultando parte de la key)
$maskedKey = if ($ApiKey.Length -gt 8) {
    $ApiKey.Substring(0, 4) + "*" * ($ApiKey.Length - 8) + $ApiKey.Substring($ApiKey.Length - 4)
} else {
    "*" * $ApiKey.Length
}

Write-Host "`n🔐 API Key configurada: $maskedKey" -ForegroundColor Yellow

# Instrucciones siguientes
Write-Host "`n📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Reiniciar la API si está corriendo" -ForegroundColor White
Write-Host "   2. Ejecutar: python run_prod.py" -ForegroundColor White
Write-Host "   3. Probar con: .\probar_api.ps1 -Test all" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Para probar solo OpenAQ:" -ForegroundColor Cyan
Write-Host "   cd utils" -ForegroundColor White
Write-Host "   python openaq_fetcher.py" -ForegroundColor White
Write-Host ""

# Preguntar si quiere probar ahora
$test = Read-Host "¿Quieres probar la conexión con OpenAQ ahora? (s/n)"

if ($test -eq "s" -or $test -eq "S") {
    Write-Host "`n🧪 Probando conexión con OpenAQ..." -ForegroundColor Cyan
    
    Push-Location (Join-Path $PSScriptRoot "utils")
    
    # Establecer la variable de entorno para esta sesión
    $env:OPENAQ_API_KEY = $ApiKey
    
    python openaq_fetcher.py
    
    Pop-Location
    
    Write-Host "`n✨ Prueba completada!" -ForegroundColor Green
}

Write-Host "`n🎯 Configuración finalizada." -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
