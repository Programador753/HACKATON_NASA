# 🌍 API Predicción AQI con OpenAQ - Actualizado

## 🆕 Nuevas Características

### ✨ Integración con OpenAQ API v3
La API ahora obtiene **datos en tiempo real** de calidad del aire usando la API pública de OpenAQ:

- **Datos reales** de estaciones de monitoreo cercanas
- **Búsqueda automática** de estaciones en un radio de 25km
- **Fallback inteligente** a datos simulados si no hay estaciones disponibles
- **Conversión de unidades** automática (ppb a µg/m³, etc.)

### 📊 Valores de Contaminantes Individuales
Ahora cada predicción incluye:

- **PM2.5**: Partículas finas (µg/m³)
- **PM10**: Partículas gruesas (µg/m³)  
- **O3**: Ozono troposférico (µg/m³)
- **NO2**: Dióxido de nitrógeno (µg/m³)
- **Temperatura**: °C
- **Humedad**: % relativo
- **Viento**: velocidad en m/s

### 🎯 Predicciones Mejoradas
Cada horizonte de predicción (3h, 6h, 12h, 24h) incluye:
- **AQI predicho** con clasificación EPA
- **Valores estimados** de cada contaminante
- **Confianza** de la predicción

## 📡 Estructura de Respuesta

```json
{
  "ubicacion": {
    "latitud": 34.0522,
    "longitud": -118.2437
  },
  "nombre_ubicacion": "Los Angeles, CA",
  "timestamp": "2025-10-04T12:00:00",
  "fuente_datos": "OpenAQ (tiempo real)",
  
  "aqi_actual_estimado": 65.3,
  "contaminantes_actuales": {
    "PM2.5": 18.5,
    "PM10": 31.4,
    "O3": 45.2,
    "NO2": 28.7,
    "temperatura": 22.3,
    "humedad": 55.0,
    "viento": 8.5
  },
  
  "predicciones": [
    {
      "horizonte": "3h",
      "aqi_predicho": 68.5,
      "calidad": "Aceptable",
      "mensaje": "Calidad del aire aceptable...",
      "color": "#FFFF00",
      "confianza": 0.85,
      "contaminantes": {
        "PM2.5": 19.8,
        "PM10": 33.7,
        "O3": 47.1,
        "NO2": 29.9,
        "temperatura": 23.1,
        "humedad": 52.0,
        "viento": 9.2
      }
    },
    {
      "horizonte": "6h",
      "aqi_predicho": 72.1,
      "calidad": "Aceptable",
      ...
    }
  ],
  
  "datos_entrada_disponibles": true,
  "advertencias": []
}
```

## 🚀 Cambios Corregidos

### ✅ 1. Arreglado: Error de Features (6 vs 8)
**Problema anterior**: `X has 6 features, but MinMaxScaler is expecting 8 features`

**Solución**: Actualizado `data_fetcher.py` para generar correctamente las 8 features:
- PM2.5, PM10, O3, NO2, temperatura, humedad, viento, AQI

### ✅ 2. Arreglado: Ciudades Predefinidas
**Problema anterior**: `Ciudad 'chicago' no encontrada`

**Solución**: Actualizado diccionario en `main.py` con 10 ciudades de Estados Unidos:
```python
cities = {
    "los-angeles": {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles, CA"},
    "new-york": {"lat": 40.7128, "lon": -74.0060, "name": "New York, NY"},
    "chicago": {"lat": 41.8781, "lon": -87.6298, "name": "Chicago, IL"},
    "houston": {"lat": 29.7604, "lon": -95.3698, "name": "Houston, TX"},
    "phoenix": {"lat": 33.4484, "lon": -112.0740, "name": "Phoenix, AZ"},
    "philadelphia": {"lat": 39.9526, "lon": -75.1652, "name": "Philadelphia, PA"},
    "san-antonio": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio, TX"},
    "san-diego": {"lat": 32.7157, "lon": -117.1611, "name": "San Diego, CA"},
    "dallas": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas, TX"},
    "san-francisco": {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco, CA"}
}
```

## 🧪 Cómo Probar

### 1. Iniciar la API
```powershell
# Opción 1: Script de inicio
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\iniciar_api.ps1"

# Opción 2: Modo producción
python "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\run_prod.py"

# Opción 3: Desarrollo con auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Ejecutar Pruebas
```powershell
# Todas las pruebas
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test all

# Pruebas individuales
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test get    # Los Angeles
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test post   # New York
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test city   # Chicago
```

### 3. Probar OpenAQ Directamente
```powershell
# Probar el fetcher de OpenAQ
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\utils"
python openaq_fetcher.py
```

### 4. Documentación Interactiva
Abre en tu navegador: http://localhost:8000/docs

## 📋 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info básica de la API |
| `/health` | GET | Estado de salud |
| `/model/info` | GET | Info del modelo ML |
| `/predict` | POST | Predicción por coordenadas (JSON) |
| `/predict/coordinates` | GET | Predicción por coordenadas (query params) |
| `/predict/city/{city}` | GET | Predicción para ciudad predefinida |

## 🌐 Ejemplos de Uso

### Ejemplo 1: Obtener datos reales de Los Angeles
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/los-angeles" | ConvertTo-Json -Depth 5
```

### Ejemplo 2: Predicción para New York con datos en tiempo real
```powershell
$body = @{
    latitud = 40.7128
    longitud = -74.0060
    nombre_ubicacion = "New York, NY"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 5
```

### Ejemplo 3: Desde Next.js/React
```javascript
const obtenerPrediccion = async () => {
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
  
  console.log('AQI Actual:', data.aqi_actual_estimado);
  console.log('Fuente:', data.fuente_datos);
  console.log('Contaminantes:', data.contaminantes_actuales);
  
  data.predicciones.forEach(pred => {
    console.log(`${pred.horizonte}: AQI=${pred.aqi_predicho}, PM2.5=${pred.contaminantes.PM2_5}`);
  });
};
```

## 🔍 Fuentes de Datos

### OpenAQ API v3
- **URL**: https://api.openaq.org/v3
- **Documentación**: https://docs.openaq.org/
- **Cobertura**: +15,000 estaciones mundiales
- **Actualización**: Tiempo real (varía por estación)
- **Gratis**: Sí, sin API key necesaria para uso básico

### Datos de Entrenamiento
- **Modelo**: LSTM con Attention (241,589 parámetros)
- **Entrenado en**: Los Angeles, CA
- **Features**: 8 (PM2.5, PM10, O3, NO2, temperatura, humedad, viento, AQI)
- **Horizontes**: 3h, 6h, 12h, 24h
- **Performance**: R² = 0.773, MAE = 0.0948

## 📁 Archivos Actualizados

```
api/
├── main.py                      ✅ Ciudades USA actualizadas
├── requirements.txt             ✅ aiohttp incluido
├── utils/
│   ├── data_fetcher.py         ✅ Generación de 8 features correcta
│   ├── openaq_fetcher.py       🆕 Integración OpenAQ v3
│   └── predictor.py            ✅ Contaminantes y OpenAQ integrados
├── models/
│   └── schemas.py              ✅ ContaminantesData añadido
└── probar_api.ps1              ✅ Tests con ciudades USA
```

## 🎯 Próximos Pasos

1. **Probar la API**: Ejecutar `probar_api.ps1 -Test all`
2. **Verificar OpenAQ**: Comprobar si hay estaciones cerca de tus ubicaciones
3. **Integrar en Frontend**: Usar los datos de contaminantes para visualizaciones
4. **Optimizar**: Ajustar radio de búsqueda (25km default) según necesites
5. **Cachear**: Implementar caché para reducir llamadas a OpenAQ

## 🐛 Troubleshooting

### OpenAQ no retorna datos
- Verifica conectividad: `curl https://api.openaq.org/v3/locations?limit=1`
- Aumenta el radio de búsqueda en `predictor.py`
- La API caerá a datos simulados automáticamente

### Error de features
- Verifica que `MODEL_FEATURES` en `config.py` tenga 8 elementos
- Confirma que `data_fetcher.py` genera todas las features

### Ciudad no encontrada
- Usa nombres en minúsculas con guiones: `los-angeles`, `new-york`
- Verifica lista completa en `/docs` endpoint

## 📞 Soporte

Para más información, consulta:
- 📖 Swagger UI: http://localhost:8000/docs
- 📘 ReDoc: http://localhost:8000/redoc
- 📄 `CIUDADES_USA.md`: Lista completa de ciudades
- 📄 `COMO_PROBAR.md`: Guía de testing

---

**Última actualización**: 4 de octubre de 2025  
**Versión**: 2.0.0 (con OpenAQ + Contaminantes)
