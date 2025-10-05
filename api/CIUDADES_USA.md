# 🇺🇸 API de Predicción AQI - Ciudades de Estados Unidos

## ⚠️ IMPORTANTE: Ubicaciones Geográficas

El modelo fue entrenado con datos de **Los Angeles, California**. Para obtener las mejores predicciones, usa ubicaciones dentro de **Estados Unidos**.

## 🏙️ Ciudades Predefinidas Disponibles

Todas las ciudades predefinidas están en Estados Unidos:

| Ciudad | Endpoint | Coordenadas |
|--------|----------|-------------|
| **Los Angeles, CA** ⭐ | `/predict/city/los-angeles` | 34.0522, -118.2437 |
| New York, NY | `/predict/city/new-york` | 40.7128, -74.0060 |
| Chicago, IL | `/predict/city/chicago` | 41.8781, -87.6298 |
| Houston, TX | `/predict/city/houston` | 29.7604, -95.3698 |
| Phoenix, AZ | `/predict/city/phoenix` | 33.4484, -112.0740 |
| Philadelphia, PA | `/predict/city/philadelphia` | 39.9526, -75.1652 |
| San Antonio, TX | `/predict/city/san-antonio` | 29.4241, -98.4936 |
| San Diego, CA | `/predict/city/san-diego` | 32.7157, -117.1611 |
| Dallas, TX | `/predict/city/dallas` | 32.7767, -96.7970 |
| San Francisco, CA | `/predict/city/san-francisco` | 37.7749, -122.4194 |

⭐ = Ciudad usada durante el entrenamiento del modelo

## 📝 Ejemplos Actualizados

### 1. Predicción para Los Angeles (Ciudad de Entrenamiento)
```powershell
# GET
Invoke-RestMethod -Uri "http://localhost:8000/predict/coordinates?lat=34.0522&lon=-118.2437&location_name=Los%20Angeles"

# POST
$body = @{
    latitud = 34.0522
    longitud = -118.2437
    nombre_ubicacion = "Los Angeles, CA"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"

# Ciudad predefinida
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/los-angeles"
```

### 2. Predicción para New York
```powershell
# GET
Invoke-RestMethod -Uri "http://localhost:8000/predict/coordinates?lat=40.7128&lon=-74.0060&location_name=New%20York"

# POST
$body = @{
    latitud = 40.7128
    longitud = -74.0060
    nombre_ubicacion = "New York, NY"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"

# Ciudad predefinida
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/new-york"
```

### 3. Predicción para Chicago
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/chicago"
```

### 4. Predicción para San Francisco
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/san-francisco"
```

## 🧪 Probar Todas las Ciudades

```powershell
# Probar todas las ciudades predefinidas
$cities = @("los-angeles", "new-york", "chicago", "houston", "phoenix", "philadelphia", "san-antonio", "san-diego", "dallas", "san-francisco")

foreach ($city in $cities) {
    Write-Host "`nProbando $city..." -ForegroundColor Cyan
    Invoke-RestMethod -Uri "http://localhost:8000/predict/city/$city" | ConvertTo-Json -Depth 3
    Start-Sleep -Seconds 1
}
```

## 🌐 Usar desde Next.js (Frontend)

```javascript
// Predicción para Los Angeles
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    latitud: 34.0522,
    longitud: -118.2437,
    nombre_ubicacion: 'Los Angeles, CA'
  })
});

const data = await response.json();
console.log(data);

// O usar ciudad predefinida
const response2 = await fetch('http://localhost:8000/predict/city/new-york');
const data2 = await response2.json();
```

## 📊 Datos de Entrenamiento

El modelo fue entrenado con:
- **Ubicación**: Los Angeles, CA (34.0522, -118.2437)
- **Features**: PM2.5, PM10, O3, NO2, temperatura, humedad, viento, AQI
- **Período**: Datos históricos de calidad del aire
- **Horizontes de predicción**: 3h, 6h, 12h, 24h

## ⚡ Script de Prueba Rápido

```powershell
# Ejecutar pruebas con ubicaciones de Estados Unidos
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test all
```

Este script ahora usa:
- **Los Angeles** para prueba GET
- **New York** para prueba POST  
- **Chicago** para ciudad predefinida

## 🎯 Mejores Prácticas

1. **Usa Los Angeles** para las pruebas iniciales (ciudad de entrenamiento)
2. **Otras ciudades de EE.UU.** también funcionarán bien
3. **Evita** ubicaciones fuera de Estados Unidos (el modelo no tiene datos de esas regiones)
4. Los datos son **simulados** actualmente - para producción necesitarías integrar con la API real de TEMPO NASA

## 🔄 Reiniciar la API

Si acabas de hacer cambios, reinicia la API:

```powershell
# Detener: CTRL+C
# Iniciar:
python "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\run_prod.py"
```

Luego abre: http://localhost:8000/docs para probar visualmente.
