# Script para reiniciar la API con el nuevo modelo
Write-Host "🔄 Reiniciando API con nuevo modelo..." -ForegroundColor Cyan

# Detener proceso de Python si está corriendo
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*run_prod*" -or $_.CommandLine -like "*run_prod*" }

if ($pythonProcesses) {
    Write-Host "⏹️ Deteniendo API anterior..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Iniciar nueva API
Write-Host "🚀 Iniciando API con modelo reentrenado..." -ForegroundColor Green
Set-Location "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"

# Ejecutar en segundo plano
Start-Process python -ArgumentList "run_prod.py" -NoNewWindow

# Esperar a que inicie
Write-Host "⏳ Esperando a que la API inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Probar la API
Write-Host "`n🧪 Probando predicción..." -ForegroundColor Cyan
try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/predict/city/los-angeles" -TimeoutSec 30
    
    Write-Host "`n✅ RESULTADOS:" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Gray
    
    foreach ($pred in $result.predicciones) {
        $horizonte = $pred.horizonte
        $aqi = [math]::Round($pred.aqi_predicho, 2)
        $calidad = $pred.calidad
        
        # Colorear según si es negativo
        if ($aqi -lt 0) {
            Write-Host "  ❌ $horizonte : AQI $aqi ($calidad) - NEGATIVO!" -ForegroundColor Red
        } else {
            Write-Host "  ✅ $horizonte : AQI $aqi ($calidad)" -ForegroundColor Green
        }
    }
    
    Write-Host "=" * 80 -ForegroundColor Gray
    Write-Host "`n🎉 Modelo funcionando correctamente!`n" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error al probar la API: $_" -ForegroundColor Red
}
