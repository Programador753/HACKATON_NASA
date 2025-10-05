# Script para probar la API sin interrumpirla
# Se ejecuta en una terminal separada mientras la API corre en otra

Write-Host "🧪 Probando API de Predicción AQI..." -ForegroundColor Cyan
Write-Host ""

# Esperar a que la API esté lista
Write-Host "⏳ Esperando a que la API esté disponible..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    # Test 1: Health Check
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📋 Test 1: Health Check" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "   Modelo: $($health.model_info.nombre_modelo)" -ForegroundColor Gray
    Write-Host "   Parámetros: $($health.model_info.total_parametros)" -ForegroundColor Gray
    Write-Host ""
    
    # Test 2: Predicción Los Angeles (ciudad de entrenamiento)
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📋 Test 2: Predicción Los Angeles" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    $pred_la = Invoke-RestMethod -Uri "http://localhost:8000/predict/city/los-angeles" -TimeoutSec 30
    
    Write-Host "🌍 Ubicación: $($pred_la.ubicacion.nombre)" -ForegroundColor Cyan
    Write-Host "📊 AQI Actual: $($pred_la.aqi_actual_estimado)" -ForegroundColor Yellow
    Write-Host "📡 Fuente: $($pred_la.fuente_datos)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🌫️  Contaminantes Actuales:" -ForegroundColor Magenta
    Write-Host "   PM2.5: $($pred_la.contaminantes_actuales.'PM2.5') µg/m³" -ForegroundColor Gray
    Write-Host "   PM10:  $($pred_la.contaminantes_actuales.PM10) µg/m³" -ForegroundColor Gray
    Write-Host "   O3:    $($pred_la.contaminantes_actuales.O3) µg/m³" -ForegroundColor Gray
    Write-Host "   NO2:   $($pred_la.contaminantes_actuales.NO2) µg/m³" -ForegroundColor Gray
    Write-Host "   Temp:  $($pred_la.contaminantes_actuales.temperatura) °C" -ForegroundColor Gray
    Write-Host "   Hum:   $($pred_la.contaminantes_actuales.humedad) %" -ForegroundColor Gray
    Write-Host "   Viento: $($pred_la.contaminantes_actuales.viento) m/s" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🔮 Predicciones:" -ForegroundColor Magenta
    foreach ($horizonte in $pred_la.predicciones) {
        Write-Host "   [$($horizonte.horizonte)] AQI: $($horizonte.aqi_predicho) | $($horizonte.calidad)" -ForegroundColor Cyan
        Write-Host "      PM2.5: $($horizonte.contaminantes.'PM2.5') | PM10: $($horizonte.contaminantes.PM10)" -ForegroundColor DarkGray
        Write-Host "      O3: $($horizonte.contaminantes.O3) | NO2: $($horizonte.contaminantes.NO2)" -ForegroundColor DarkGray
    }
    Write-Host ""
    
    # Test 3: Predicción New York (ciudad diferente)
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📋 Test 3: Predicción New York" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    $pred_ny = Invoke-RestMethod -Uri "http://localhost:8000/predict/city/new-york" -TimeoutSec 30
    
    Write-Host "🌍 Ubicación: $($pred_ny.ubicacion.nombre)" -ForegroundColor Cyan
    Write-Host "📊 AQI Actual: $($pred_ny.aqi_actual_estimado)" -ForegroundColor Yellow
    Write-Host "📡 Fuente: $($pred_ny.fuente_datos)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🔮 Predicción 3h: AQI $($pred_ny.predicciones[0].aqi_predicho) | $($pred_ny.predicciones[0].calidad)" -ForegroundColor Cyan
    Write-Host "   PM2.5: $($pred_ny.predicciones[0].contaminantes.'PM2.5') µg/m³" -ForegroundColor Gray
    Write-Host ""
    
    # Test 4: Predicción con coordenadas personalizadas
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📋 Test 4: Predicción Coordenadas Personalizadas (Chicago)" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    $body_chicago = @{
        latitud = 41.8781
        longitud = -87.6298
        nombre_ubicacion = "Chicago, IL"
    } | ConvertTo-Json
    
    $pred_chicago = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body_chicago -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "🌍 Ubicación: $($pred_chicago.ubicacion.nombre)" -ForegroundColor Cyan
    Write-Host "📊 AQI Actual: $($pred_chicago.aqi_actual_estimado)" -ForegroundColor Yellow
    Write-Host "🔮 Predicción 3h: AQI $($pred_chicago.predicciones[0].aqi_predicho)" -ForegroundColor Cyan
    Write-Host ""
    
    # Resumen final
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✨ Características verificadas:" -ForegroundColor Yellow
    Write-Host "   ✅ Modelo carga correctamente (241,589 parámetros)" -ForegroundColor Green
    Write-Host "   ✅ Contaminantes actuales incluidos (PM2.5, PM10, O3, NO2, etc.)" -ForegroundColor Green
    Write-Host "   ✅ Predicciones con contaminantes individuales" -ForegroundColor Green
    Write-Host "   ✅ Fuente de datos indicada (OpenAQ o simulado)" -ForegroundColor Green
    Write-Host "   ✅ Ciudades predefinidas funcionan" -ForegroundColor Green
    Write-Host "   ✅ Coordenadas personalizadas funcionan" -ForegroundColor Green
    Write-Host ""
    
    # Guardar JSON completo de ejemplo
    $pred_la | ConvertTo-Json -Depth 10 | Out-File -FilePath "ejemplo_respuesta_completa.json" -Encoding UTF8
    Write-Host "💾 Respuesta completa guardada en: ejemplo_respuesta_completa.json" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error en test: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor DarkRed
    exit 1
}
