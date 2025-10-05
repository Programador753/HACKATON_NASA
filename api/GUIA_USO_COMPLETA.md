# 🎉 API de Predicción AQI - COMPLETADA Y FUNCIONANDO

## ✅ Estado Final

**Fecha**: 4 de octubre de 2025  
**Estado**: ✅ COMPLETAMENTE FUNCIONAL  
**Modelo**: LSTM + Attention (241,589 parámetros)  
**Rendimiento**: R²=0.773

---

## 🚀 Cómo Iniciar la API

### Opción 1: Terminal Simple
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
python run_prod.py
```

### Opción 2: Con limpieza de puerto
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
if (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue) {
    Get-NetTCPConnection -LocalPort 8000 | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force }
    Start-Sleep -Seconds 2
}
python run_prod.py
```

**La API estará disponible en:**
- 🌐 API: http://localhost:8000
- 📖 Documentación interactiva: http://localhost:8000/docs
- 📊 Alternativa: http://localhost:8000/redoc

---

## 🧪 Cómo Probar la API

### En otra terminal (mientras la API corre):

```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
.\test_api_manual.ps1
```

Este script probará:
1. ✅ Health Check
2. ✅ Predicción Los Angeles (ciudad de entrenamiento)
3. ✅ Predicción New York
4. ✅ Predicción con coordenadas personalizadas (Chicago)

**Resultado**: Guardará `ejemplo_respuesta_completa.json` con una respuesta de ejemplo completa.

---

## 📊 Estructura de la Respuesta

### Datos Actuales (OpenAQ o Simulados)

```json
{
  "aqi_actual_estimado": 65.3,
  "contaminantes_actuales": {
    "PM2.5": 18.5,      // Partículas finas (µg/m³)
    "PM10": 31.4,       // Partículas gruesas (µg/m³)
    "O3": 45.2,         // Ozono (µg/m³)
    "NO2": 28.7,        // Dióxido de nitrógeno (µg/m³)
    "temperatura": 22.3, // Temperatura (°C)
    "humedad": 55.0,     // Humedad relativa (%)
    "viento": 8.5        // Velocidad del viento (m/s)
  },
  "fuente_datos": "simulado"  // "OpenAQ (tiempo real)" si hay API key válida
}
```

### Predicciones Futuras (4 horizontes)

```json
{
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
    // ... 6h, 12h, 24h
  ]
}
```

---

## 🌍 Endpoints Disponibles

### 1. Health Check
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T10:37:49.730Z",
  "model_info": {
    "nombre_modelo": "5",
    "arquitectura": "Bidirectional LSTM + Attention",
    "total_parametros": 241589,
    "r2_promedio": 0.773
  }
}
```

### 2. Predicción con Ciudad Predefinida
```http
GET /predict/city/{city_id}
```

**Ciudades disponibles:**
- `los-angeles` ⭐ (Ciudad de entrenamiento)
- `new-york`
- `chicago`
- `houston`
- `phoenix`
- `philadelphia`
- `san-antonio`
- `san-diego`
- `dallas`
- `san-francisco`

**Ejemplo PowerShell:**
```powershell
Invoke-RestMethod "http://localhost:8000/predict/city/los-angeles" | ConvertTo-Json -Depth 5
```

**Ejemplo JavaScript:**
```javascript
fetch('http://localhost:8000/predict/city/los-angeles')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 3. Predicción con Coordenadas Personalizadas
```http
POST /predict
Content-Type: application/json

{
  "latitud": 41.8781,
  "longitud": -87.6298,
  "nombre_ubicacion": "Chicago, IL"
}
```

**Ejemplo PowerShell:**
```powershell
$body = @{
    latitud = 41.8781
    longitud = -87.6298
    nombre_ubicacion = "Chicago, IL"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" `
                  -Method POST `
                  -Body $body `
                  -ContentType "application/json" | 
ConvertTo-Json -Depth 5
```

**Ejemplo JavaScript/Fetch:**
```javascript
fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    latitud: 41.8781,
    longitud: -87.6298,
    nombre_ubicacion: 'Chicago, IL'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🔧 Problemas Resueltos

### ✅ Error: "dict object has no attribute 'reduce_sum'"
**Solución**: Agregadas funciones de TensorFlow a `custom_objects` al cargar el modelo.

```python
custom_objects = {
    'AttentionLayer': AttentionLayer,
    'reduce_sum': tf.reduce_sum,
    'expand_dims': tf.expand_dims,
    'tensordot': tf.tensordot,
    'tanh': tf.nn.tanh,
    'softmax': tf.nn.softmax,
}
```

### ✅ Warning: "'H' is deprecated"
**Solución**: Cambiado `freq='H'` → `freq='h'` en pandas.

### ✅ Error: Feature mismatch (6 vs 8)
**Solución**: Actualizado `data_fetcher.py` para generar las 8 features correctamente.

### ✅ Ciudad 'chicago' no encontrada
**Solución**: Agregadas 10 ciudades de Estados Unidos al diccionario.

---

## 🎯 Integración con Frontend (Next.js/React)

### Hook personalizado

```typescript
// hooks/useAQIPrediction.ts
import { useState, useEffect } from 'react';

interface ContaminantData {
  'PM2.5': number;
  PM10: number;
  O3: number;
  NO2: number;
  temperatura: number;
  humedad: number;
  viento: number;
}

interface Prediction {
  horizonte: string;
  aqi_predicho: number;
  calidad: string;
  mensaje: string;
  color: string;
  confianza: number;
  contaminantes: ContaminantData;
}

interface AQIResponse {
  aqi_actual_estimado: number;
  contaminantes_actuales: ContaminantData;
  fuente_datos: string;
  predicciones: Prediction[];
  ubicacion: {
    nombre: string;
    latitud: number;
    longitud: number;
  };
}

export const useAQIPrediction = (cityId: string) => {
  const [data, setData] = useState<AQIResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/predict/city/${cityId}`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [cityId]);

  return { data, loading, error };
};
```

### Componente de ejemplo

```tsx
// components/AQIDashboard.tsx
import { useAQIPrediction } from '@/hooks/useAQIPrediction';

export const AQIDashboard = ({ cityId = 'los-angeles' }) => {
  const { data, loading, error } = useAQIPrediction(cityId);

  if (loading) return <div>Cargando predicción...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return (
    <div className="aqi-dashboard">
      <h1>{data.ubicacion.nombre}</h1>
      
      {/* AQI Actual */}
      <div className="current-aqi">
        <h2>AQI Actual: {data.aqi_actual_estimado.toFixed(1)}</h2>
        <p>Fuente: {data.fuente_datos}</p>
      </div>

      {/* Contaminantes Actuales */}
      <div className="pollutants">
        <h3>Contaminantes Actuales</h3>
        <ul>
          <li>PM2.5: {data.contaminantes_actuales['PM2.5'].toFixed(1)} µg/m³</li>
          <li>PM10: {data.contaminantes_actuales.PM10.toFixed(1)} µg/m³</li>
          <li>O₃: {data.contaminantes_actuales.O3.toFixed(1)} µg/m³</li>
          <li>NO₂: {data.contaminantes_actuales.NO2.toFixed(1)} µg/m³</li>
          <li>Temperatura: {data.contaminantes_actuales.temperatura.toFixed(1)} °C</li>
          <li>Humedad: {data.contaminantes_actuales.humedad.toFixed(1)} %</li>
          <li>Viento: {data.contaminantes_actuales.viento.toFixed(1)} m/s</li>
        </ul>
      </div>

      {/* Predicciones */}
      <div className="predictions">
        <h3>Predicciones</h3>
        {data.predicciones.map((pred) => (
          <div 
            key={pred.horizonte} 
            className="prediction-card"
            style={{ borderLeft: `4px solid ${pred.color}` }}
          >
            <h4>{pred.horizonte}</h4>
            <p className="aqi">AQI: {pred.aqi_predicho.toFixed(1)}</p>
            <p className="quality">{pred.calidad}</p>
            <p className="message">{pred.mensaje}</p>
            <p className="confidence">Confianza: {(pred.confianza * 100).toFixed(0)}%</p>
            
            <details>
              <summary>Ver contaminantes predichos</summary>
              <ul>
                <li>PM2.5: {pred.contaminantes['PM2.5'].toFixed(1)} µg/m³</li>
                <li>PM10: {pred.contaminantes.PM10.toFixed(1)} µg/m³</li>
                <li>O₃: {pred.contaminantes.O3.toFixed(1)} µg/m³</li>
                <li>NO₂: {pred.contaminantes.NO2.toFixed(1)} µg/m³</li>
              </ul>
            </details>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 📝 Notas Importantes

### OpenAQ API Key (Opcional)

**Estado actual**: Configurada pero con datos históricos (2016-2018) en Los Angeles.

Para configurar tu API key:
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
.\configurar_openaq.ps1
```

O editar manualmente el archivo `.env`:
```env
OPENAQ_API_KEY='tu_api_key_aqui'
```

**Registro**: https://explore.openaq.org/register  
**API Key**: https://explore.openaq.org/account

### Datos Simulados

Cuando no hay datos de OpenAQ (o no hay API key), la API usa datos simulados realistas:
- **PM2.5**: 10-35 µg/m³ con patrón diurno
- **PM10**: 1.5-2x PM2.5
- **O3**: 30-70 µg/m³ con ciclo día/noche
- **NO2**: 15-35 µg/m³ con picos de tráfico
- **Temperatura**: 20±8°C ciclo diario
- **Humedad**: 60±15% inverso a temperatura
- **Viento**: 3-15 m/s variable

### CORS

La API tiene CORS habilitado para:
- `http://localhost:3000`
- `http://localhost:3001`

Para agregar más orígenes, editar `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://tu-dominio.com"  # Agregar aquí
    ],
    ...
)
```

---

## 📚 Archivos de Documentación

- 📄 `RESUMEN_FINAL.md` - Este archivo
- 📄 `README_ACTUALIZADO.md` - README completo con toda la documentación
- 📄 `OPENAQ_API_KEY_SETUP.md` - Guía para obtener API Key de OpenAQ
- 📄 `CIUDADES_USA.md` - Lista de ciudades predefinidas
- 📄 `CONFIGURACION_COMPLETADA.md` - Resumen de configuración
- 📄 `ejemplo_respuesta_completa.json` - Ejemplo de respuesta (generado por test)

---

## 🎉 Características Completadas

✅ **Predicción de AQI** con horizonte 3h, 6h, 12h, 24h  
✅ **Contaminantes individuales** en respuesta (PM2.5, PM10, O3, NO2, etc.)  
✅ **Integración OpenAQ** para datos en tiempo real  
✅ **Fallback a datos simulados** cuando no hay datos reales  
✅ **10 ciudades predefinidas** de Estados Unidos  
✅ **Coordenadas personalizadas** para cualquier ubicación  
✅ **Documentación interactiva** con Swagger UI  
✅ **CORS configurado** para desarrollo frontend  
✅ **Modelo optimizado** con 241,589 parámetros (R²=0.773)  
✅ **Capa de Atención** funcionando correctamente  
✅ **Manejo de errores** robusto  

---

## 🚀 Próximos Pasos (Opcionales)

1. **Desplegar en la nube**:
   - Railway.app (recomendado para FastAPI)
   - Render.com
   - Google Cloud Run
   - AWS Lambda + API Gateway

2. **Caché de predicciones**:
   - Redis para cachear predicciones por 1-5 minutos
   - Reducir carga de modelo

3. **Base de datos**:
   - PostgreSQL para histórico de predicciones
   - Análisis de tendencias
   - Comparativas temporales

4. **Webhooks**:
   - Notificaciones cuando AQI > umbral
   - Alertas de calidad del aire

5. **Dashboard admin**:
   - Monitoreo de uso de API
   - Estadísticas de predicciones
   - Logs centralizados

---

**🎊 La API está lista para ser integrada con tu frontend Next.js!**

Para cualquier pregunta o problema, revisa la documentación interactiva en:  
**http://localhost:8000/docs** (mientras la API está corriendo)
