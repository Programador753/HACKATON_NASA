# Script para iniciar la API en una nueva ventana de terminal
# Esto evita que se cierre automáticamente

Write-Host "🚀 Abriendo API en una nueva ventana de terminal..." -ForegroundColor Green

$apiPath = "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
$scriptPath = Join-Path $apiPath "run_prod.py"

# Abrir nueva ventana de PowerShell que ejecute la API
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$apiPath' ; python run_prod.py"
)

Write-Host "✅ API iniciada en nueva ventana" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Esperando 20 segundos para que cargue el modelo..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "🌐 Abriendo documentación interactiva..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/docs"

Write-Host ""
Write-Host "✨ ¡Listo! Puedes:" -ForegroundColor Green
Write-Host "   1. Usar la interfaz web en: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   2. Hacer peticiones con PowerShell (ver ejemplos abajo)" -ForegroundColor White
Write-Host ""
Write-Host "📝 Ejemplos de peticiones desde PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Health Check" -ForegroundColor Gray
Write-Host 'Invoke-RestMethod -Uri "http://localhost:8000/health"' -ForegroundColor White
Write-Host ""
Write-Host "# Info del Modelo" -ForegroundColor Gray
Write-Host 'Invoke-RestMethod -Uri "http://localhost:8000/model/info"' -ForegroundColor White
Write-Host ""
Write-Host "# Predicción (GET)" -ForegroundColor Gray
Write-Host 'Invoke-RestMethod -Uri "http://localhost:8000/predict/coordinates?latitud=40.4168&longitud=-3.7038"' -ForegroundColor White
Write-Host ""
Write-Host "# Predicción (POST)" -ForegroundColor Gray
Write-Host '$body = @{ latitud = 40.4168; longitud = -3.7038; nombre_ubicacion = "Madrid" } | ConvertTo-Json' -ForegroundColor White
Write-Host 'Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"' -ForegroundColor White
Write-Host ""
