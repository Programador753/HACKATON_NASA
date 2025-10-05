# 🌍 API de Predicción de Calidad del Aire (AQI)

API REST construida con **FastAPI** que utiliza un modelo **LSTM con Attention** para predecir el Índice de Calidad del Aire (AQI) basándose en datos de TEMPO NASA.

## 🚀 Características

- ✅ Predicciones de AQI para 4 horizontes temporales: **3h, 6h, 12h, 24h**
- ✅ Entrada por coordenadas geográficas (latitud, longitud)
- ✅ Modelo LSTM Bidireccional con mecanismo de **Attention**
- ✅ Integración con **Next.js** mediante CORS
- ✅ Documentación automática con **Swagger UI**
- ✅ Validación de datos con **Pydantic**
- ✅ Datos de TEMPO NASA (con fallback a datos simulados)

---

## 📋 Requisitos Previos

- Python 3.10+
- Modelo entrenado (`.keras` + `scaler.pkl`)
- (Opcional) Credenciales de NASA Earthdata para datos reales

---

## 🛠️ Instalación

### 1. Clonar o navegar al directorio del proyecto

```bash
cd c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Configuración mínima en `.env`:**

```env
MODEL_PATH=../modelos_guardados/LSTM_Attention_AQI_20251004_002409.keras
SCALER_PATH=../modelos_guardados/LSTM_Attention_AQI_20251004_002409_scaler.pkl
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🚀 Ejecución

### Modo desarrollo (con auto-reload)

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en: **http://localhost:8000**

---

## 📚 Documentación de la API

### Swagger UI (interactivo)
👉 **http://localhost:8000/docs**

### ReDoc
👉 **http://localhost:8000/redoc**

---

## 🔌 Endpoints Principales

### 1. **Health Check**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-10-04T00:00:00"
}
```

---

### 2. **Información del Modelo**
```http
GET /model/info
```

**Respuesta:**
```json
{
  "nombre_modelo": "LSTM_Attention_AQI",
  "version": "1.0.0",
  "arquitectura": "Bidirectional LSTM + Attention",
  "parametros_totales": 241589,
  "features_entrada": ["NO2_column_number_density", "HCHO_column_number_density", ...],
  "horizontes_prediccion": ["3h", "6h", "12h", "24h"],
  "lookback_horas": 48
}
```

---

### 3. **Predicción (POST)**
```http
POST /predict
Content-Type: application/json

{
  "latitud": 34.0522,
  "longitud": -118.2437,
  "nombre_ubicacion": "Los Angeles, CA"
}
```

**Respuesta:**
```json
{
  "ubicacion": {
    "latitud": 34.0522,
    "longitud": -118.2437
  },
  "nombre_ubicacion": "Los Angeles, CA",
  "timestamp": "2025-10-04T12:00:00",
  "predicciones": [
    {
      "horizonte": "3h",
      "aqi_predicho": 45.2,
      "calidad": "Bueno",
      "mensaje": "Calidad del aire aceptable",
      "color": "#FFFF00",
      "confianza": 0.85
    },
    {
      "horizonte": "6h",
      "aqi_predicho": 48.7,
      "calidad": "Bueno",
      "mensaje": "Calidad del aire aceptable",
      "color": "#FFFF00",
      "confianza": 0.82
    },
    ...
  ],
  "aqi_actual_estimado": 42.5,
  "datos_entrada_disponibles": true,
  "advertencias": []
}
```

---

### 4. **Predicción por GET (query params)**
```http
GET /predict/coordinates?lat=34.0522&lon=-118.2437&name=Los Angeles
```

---

### 5. **Predicción por Ciudad Predefinida**
```http
GET /predict/city/los-angeles
```

Ciudades disponibles:
- `los-angeles`
- `new-york`
- `mexico-city`
- `madrid`

---

## 🔗 Integración con Next.js

### Ejemplo de cliente en Next.js

#### 1. Crear servicio API (`lib/api.ts`)

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PredictionRequest {
  latitud: number;
  longitud: number;
  nombre_ubicacion?: string;
}

export interface HorizontePrediccion {
  horizonte: string;
  aqi_predicho: number;
  calidad: string;
  mensaje: string;
  color: string;
  confianza?: number;
}

export interface PredictionResponse {
  ubicacion: { latitud: number; longitud: number };
  nombre_ubicacion?: string;
  timestamp: string;
  predicciones: HorizontePrediccion[];
  aqi_actual_estimado?: number;
  datos_entrada_disponibles: boolean;
  advertencias?: string[];
}

export async function predictAQI(
  request: PredictionRequest
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Error en predicción: ${response.statusText}`);
  }

  return response.json();
}

export async function getModelInfo() {
  const response = await fetch(`${API_BASE_URL}/model/info`);
  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}
```

---

#### 2. Componente de Predicción (`components/AQIPrediction.tsx`)

```tsx
'use client';

import { useState } from 'react';
import { predictAQI, PredictionResponse } from '@/lib/api';

export default function AQIPrediction() {
  const [latitude, setLatitude] = useState('34.0522');
  const [longitude, setLongitude] = useState('-118.2437');
  const [locationName, setLocationName] = useState('Los Angeles');
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await predictAQI({
        latitud: parseFloat(latitude),
        longitud: parseFloat(longitude),
        nombre_ubicacion: locationName,
      });
      
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Predicción de Calidad del Aire</h1>
      
      {/* Formulario */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <input
            type="number"
            placeholder="Latitud"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            className="border rounded px-3 py-2"
          />
          <input
            type="number"
            placeholder="Longitud"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Nombre (opcional)"
            value={locationName}
            onChange={(e) => setLocationName(e.target.value)}
            className="border rounded px-3 py-2"
          />
        </div>
        
        <button
          onClick={handlePredict}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Prediciendo...' : 'Predecir AQI'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Resultados */}
      {prediction && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">
            {prediction.nombre_ubicacion || 'Ubicación'}
          </h2>
          
          {prediction.aqi_actual_estimado && (
            <p className="mb-4 text-lg">
              AQI Actual: <span className="font-bold">{prediction.aqi_actual_estimado}</span>
            </p>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {prediction.predicciones.map((pred) => (
              <div
                key={pred.horizonte}
                className="border rounded-lg p-4"
                style={{ borderColor: pred.color }}
              >
                <div className="text-sm text-gray-600 mb-1">{pred.horizonte}</div>
                <div className="text-3xl font-bold mb-2" style={{ color: pred.color }}>
                  {pred.aqi_predicho.toFixed(1)}
                </div>
                <div className="text-sm font-semibold mb-1">{pred.calidad}</div>
                <div className="text-xs text-gray-500">{pred.mensaje}</div>
                {pred.confianza && (
                  <div className="text-xs text-gray-400 mt-2">
                    Confianza: {(pred.confianza * 100).toFixed(0)}%
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {prediction.advertencias && prediction.advertencias.length > 0 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                {prediction.advertencias.join(', ')}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

#### 3. Configurar variables de entorno en Next.js (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test manual con cURL

```bash
# Health check
curl http://localhost:8000/health

# Predicción
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitud": 34.0522, "longitud": -118.2437, "nombre_ubicacion": "Los Angeles"}'
```

### Test con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "latitud": 34.0522,
        "longitud": -118.2437,
        "nombre_ubicacion": "Los Angeles, CA"
    }
)

print(response.json())
```

---

## 📁 Estructura del Proyecto

```
api/
├── main.py                 # Aplicación FastAPI principal
├── requirements.txt        # Dependencias
├── .env.example           # Ejemplo de variables de entorno
├── config/
│   ├── __init__.py
│   └── config.py          # Configuración global
├── models/
│   ├── __init__.py
│   └── schemas.py         # Modelos Pydantic
└── utils/
    ├── __init__.py
    ├── predictor.py       # Lógica de predicción
    └── data_fetcher.py    # Obtención de datos TEMPO
```

---

## 🐛 Troubleshooting

### Error: "Modelo no encontrado"
- Verificar que `MODEL_PATH` en `.env` apunta al archivo `.keras` correcto
- Verificar que el archivo existe en la ruta especificada

### Error: "CORS no permite el origen"
- Agregar tu dominio de Next.js a `ALLOWED_ORIGINS` en `.env`

### Error al instalar TensorFlow
```bash
# Intenta con una versión específica
pip install tensorflow==2.15.0

# O usa keras standalone
pip install keras==2.15.0
```

---

## 📊 Clasificación de AQI

| Rango AQI | Categoría | Color | Descripción |
|-----------|-----------|-------|-------------|
| 0-12 | Excelente | 🟢 Verde | Ideal |
| 12.1-35.4 | Bueno | 🟡 Amarillo | Aceptable |
| 35.5-55.4 | Aceptable | 🟠 Naranja | Grupos sensibles precaución |
| 55.5-150.4 | Regular | 🔴 Rojo | Efectos en salud |
| 150.5-250.4 | Malo | 🟣 Púrpura | Alerta de salud |
| 250.5-350.4 | Muy Malo | 🔴 Rojo oscuro | Emergencia |
| 350.5+ | Peligroso | ⚫ Morado oscuro | Peligroso |

---

## 📝 Licencia

Este proyecto es parte del Hackathon NASA TEMPO.

---

## 👨‍💻 Autor

Desarrollado con ❤️ para el Hackathon NASA TEMPO 2025
