# 🚀 API de Predicción AQI - Guía de Inicio Rápido

## ✅ Instalación Completada

Todas las dependencias se han instalado correctamente:
- ✅ TensorFlow 2.20.0 (compatible con Python 3.12)
- ✅ FastAPI 0.118.0
- ✅ Uvicorn 0.37.0
- ✅ Pandas, NumPy, Scikit-learn
- ✅ Todas las dependencias adicionales

## 🎯 Estado del Modelo

El modelo se ha cargado exitosamente:
- **Parámetros**: 241,589
- **Arquitectura**: Bidirectional LSTM + Attention mechanism
- **Horizontes de predicción**: 3h, 6h, 12h, 24h
- **Ubicación**: `C:\Users\anton\Desktop\2ºGS\HACKATON_NASA\modelos_guardados\LSTM_Attention_AQI_20251004_002409.keras`

## 🖥️ Cómo Iniciar la API

### Opción 1: Usando el script de PowerShell
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
.\start.ps1
```

### Opción 2: Usando Python directamente
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
python run.py
```

### Opción 3: Usando uvicorn directamente
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Acceder a la Documentación Interactiva

Una vez que la API esté corriendo, abre tu navegador en:

- **Swagger UI (Recomendado)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Probar los Endpoints

### 1. Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

### 2. Información del Modelo
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/model/info" -Method GET
```

### 3. Predicción (POST)
```powershell
$body = @{
    latitud = 40.4168
    longitud = -3.7038
    nombre_ubicacion = "Madrid, España"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
```

### 4. Predicción (GET con parámetros)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/predict/coordinates?latitud=40.4168&longitud=-3.7038" -Method GET
```

### 5. Predicción para Ciudad Predefinida
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/predict/city/madrid" -Method GET
```

## 🌐 Integración con Next.js

El archivo `cliente_ejemplo.js` contiene todo el código necesario para integrar la API con Next.js:

```javascript
import { useAQIPrediction } from './cliente_ejemplo';

function MiComponente() {
  const { predict, loading, error, data } = useAQIPrediction();

  const handlePredict = async () => {
    await predict({
      latitud: 40.4168,
      longitud: -3.7038,
      nombre_ubicacion: "Madrid"
    });
  };

  return (
    <div>
      <button onClick={handlePredict} disabled={loading}>
        Predecir AQI
      </button>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
      {error && <p>Error: {error}</p>}
    </div>
  );
}
```

## 🔍 Verificación

Asegúrate de que la API esté corriendo correctamente viendo estos mensajes en la terminal:

```
INFO:     Will watch for changes in these directories: ['C:\\Users\\anton\\Desktop\\2ºGS\\HACKATON_NASA\\api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
...
2025-10-04 09:40:42,098 - main - INFO - ✅ Modelo cargado exitosamente
INFO:     Application startup complete.
```

## 📝 Notas Importantes

1. **safe_mode=False**: El modelo usa capas Lambda, por lo que se requiere `safe_mode=False` en Keras 3.x
2. **Puerto 8000**: La API corre en el puerto 8000 por defecto
3. **CORS**: Configurado para aceptar requests desde localhost:3000 y localhost:3001 (Next.js)
4. **Datos simulados**: El `TEMPODataFetcher` usa datos simulados por defecto (configurar API NASA real si es necesario)

## 🛠️ Troubleshooting

### La API se cierra sola
- Asegúrate de que no hay otro proceso usando el puerto 8000
- Ejecuta con `--reload` solo en desarrollo
- Verifica que el entorno virtual esté activado

### Error al cargar el modelo
- Verifica que el archivo `.keras` existe en la ubicación correcta
- Asegúrate de que `safe_mode=False` esté configurado en `predictor.py`

### Errores de CORS
- Verifica la configuración en `main.py` líneas 21-28
- Agrega tu frontend URL si no está en la lista

## 📞 Siguiente Paso

Abre http://localhost:8000/docs en tu navegador para interactuar con la API visualmente.
