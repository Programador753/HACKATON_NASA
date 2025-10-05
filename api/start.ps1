# Script de inicio rápido para la API
# Ejecutar: .\start.ps1

Write-Host "🚀 Iniciando API de Predicción AQI..." -ForegroundColor Green

# Verificar si existe el entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Activar entorno virtual
Write-Host "🔌 Activando entorno virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Verificar si existe .env
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creando archivo .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Por favor, edita el archivo .env con tus configuraciones" -ForegroundColor Red
    notepad .env
}

# Instalar dependencias si es necesario
Write-Host "📥 Verificando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Verificar que existe el modelo
$modelPath = "../modelos_guardados"
if (-not (Test-Path $modelPath)) {
    Write-Host "❌ Error: No se encuentra la carpeta de modelos guardados" -ForegroundColor Red
    Write-Host "   Asegúrate de haber ejecutado el notebook y exportado el modelo" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Todo listo! Iniciando servidor..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 API disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentación en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python main.py
