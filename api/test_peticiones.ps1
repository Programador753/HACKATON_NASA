# Script de prueba para la API de predicción AQI
# Ejecutar este script después de iniciar la API

Write-Host "`n🚀 Probando API de Predicción AQI" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

# Esperar a que la API esté lista
Write-Host "`n⏳ Esperando a que la API esté lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 1. Health Check
Write-Host "`n✅ 1. Probando Health Check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "Respuesta:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 2. Información del Modelo
Write-Host "`n📊 2. Obteniendo información del modelo..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/model/info" -Method GET
    Write-Host "Respuesta:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 3. Predicción usando GET con coordenadas
Write-Host "`n🌍 3. Predicción para Madrid (GET)..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict/coordinates?latitud=40.4168&longitud=-3.7038&nombre_ubicacion=Madrid" -Method GET
    Write-Host "Respuesta:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 4. Predicción usando POST
Write-Host "`n🏙️ 4. Predicción para Barcelona (POST)..." -ForegroundColor Cyan
try {
    $body = @{
        latitud = 41.3851
        longitud = 2.1734
        nombre_ubicacion = "Barcelona, España"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
    Write-Host "Respuesta:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 5. Predicción para ciudad predefinida
Write-Host "`n🗼 5. Predicción para ciudad predefinida (París)..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict/city/paris" -Method GET
    Write-Host "Respuesta:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n`n✨ Pruebas completadas!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "`n📖 Para ver la documentación interactiva, abre:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
