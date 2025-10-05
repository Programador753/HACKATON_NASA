# Script rápido para probar la API (ejecutar DESPUÉS de iniciarla)

param(
    [string]$Test = "all"
)

$baseUrl = "http://localhost:8000"

Write-Host "`n🧪 Probando API de Predicción AQI" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

function Test-Health {
    Write-Host "`n✅ Health Check..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Test-ModelInfo {
    Write-Host "`n📊 Información del Modelo..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/model/info" -Method GET
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Test-PredictGET {
    Write-Host "`n🌍 Predicción Los Angeles (GET)..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/predict/coordinates?lat=34.0522&lon=-118.2437&location_name=Los%20Angeles" -Method GET
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Test-PredictPOST {
    Write-Host "`n🏙️ Predicción New York (POST)..." -ForegroundColor Cyan
    try {
        $body = @{
            latitud = 40.7128
            longitud = -74.0060
            nombre_ubicacion = "New York, NY"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$baseUrl/predict" -Method POST -Body $body -ContentType "application/json"
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Test-PredictCity {
    Write-Host "`n🏙️ Predicción Chicago (Ciudad Predefinida)..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/predict/city/chicago" -Method GET
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

# Ejecutar pruebas según el parámetro
switch ($Test) {
    "health" { Test-Health }
    "info" { Test-ModelInfo }
    "get" { Test-PredictGET }
    "post" { Test-PredictPOST }
    "city" { Test-PredictCity }
    "all" {
        Test-Health
        Start-Sleep -Seconds 1
        Test-ModelInfo
        Start-Sleep -Seconds 1
        Test-PredictGET
        Start-Sleep -Seconds 2
        Test-PredictPOST
        Start-Sleep -Seconds 2
        Test-PredictCity
    }
    default {
        Write-Host "❌ Test desconocido: $Test" -ForegroundColor Red
        Write-Host "Opciones: health, info, get, post, city, all" -ForegroundColor Yellow
    }
}

Write-Host "`n`n✨ Pruebas completadas!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
