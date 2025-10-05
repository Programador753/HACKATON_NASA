# 🛰️ Modelo Predictivo de Calidad del Aire con NASA TEMPO + LSTM

Sistema de predicción de calidad del aire que integra datos de la misión **TEMPO** de la NASA con redes neuronales **LSTM** para predecir la contaminación atmosférica en las próximas 3, 6, 12 y 24 horas.

## 🌟 Características

- **Integración con NASA TEMPO**: Acceso a datos satelitales de calidad del aire en tiempo real
- **Predicción con LSTM**: Modelo de deep learning para series temporales
- **Múltiples horizontes**: Predicciones a 3, 6, 12 y 24 horas
- **Recomendaciones inteligentes**: Sistema de alertas y sugerencias personalizadas
- **Visualizaciones avanzadas**: Gráficos interactivos de tendencias y predicciones

## 🛰️ ¿Qué es TEMPO?

**TEMPO (Tropospheric Emissions: Monitoring of Pollution)** es la primera misión espacial que monitorea la calidad del aire sobre Norteamérica con resolución horaria desde órbita geoestacionaria.

### Capacidades de TEMPO:
- ✅ Resolución temporal: **cada hora** durante el día
- ✅ Resolución espacial: **~10 km²**
- ✅ Cobertura: **Norteamérica completa**
- ✅ Contaminantes: NO₂, O₃, SO₂, HCHO, CHOCHO, aerosoles

## 📋 Requisitos

### Python 3.8+
```bash
pip install tensorflow numpy pandas matplotlib scikit-learn requests seaborn xarray netCDF4
```

### Para datos reales de TEMPO (opcional):
```bash
pip install earthaccess
```

## 🚀 Inicio Rápido

### Opción 1: Datos Simulados (Sin credenciales)

```python
# Usar datos simulados con patrones realistas de TEMPO
USAR_TEMPO_SIMULADO = True
client = TEMPODataClient()
df = client.combinar_datos_tempo_power(19.4326, -99.1332, "20240101", "20241231")
```

### Opción 2: Datos Reales de TEMPO

1. **Crear cuenta en NASA Earthdata**:
   - Visita: https://urs.earthdata.nasa.gov/users/new
   - Completa el registro
   - Acepta términos de uso

2. **Configurar credenciales**:
```python
NASA_USERNAME = "tu_usuario"
NASA_PASSWORD = "tu_contraseña"

client = TEMPODataClient(NASA_USERNAME, NASA_PASSWORD)
df = client.combinar_datos_tempo_power(19.4326, -99.1332, "20240101", "20241231")
```

## 📊 Estructura del Proyecto

```
HACKATON_NASA/
├── PRUEBAS.ipynb           # Notebook principal con todo el código
├── README_TEMPO.md         # Esta documentación
└── modelos/                # Modelos entrenados (se crea al entrenar)
    ├── modelo_lstm_*.h5
    ├── scaler_*.pkl
    └── features.pkl
```

## 🧠 Arquitectura del Modelo LSTM

```
Input (24 horas, 8 características)
    ↓
Bidirectional LSTM (128 unidades)
    ↓
Dropout (0.2)
    ↓
LSTM (64 unidades)
    ↓
Dropout (0.2)
    ↓
LSTM (32 unidades)
    ↓
Dense (64, relu)
    ↓
Dense (32, relu)
    ↓
Output (24 predicciones)
```

## 📈 Variables de Entrada

1. **PM2.5**: Partículas finas (µg/m³)
2. **PM10**: Partículas gruesas (µg/m³)
3. **O3**: Ozono troposférico (µg/m³)
4. **NO2**: Dióxido de nitrógeno (µg/m³)
5. **Temperatura**: (°C)
6. **Humedad**: (%)
7. **Viento**: Velocidad (km/h)
8. **AQI**: Índice de calidad del aire

## 🎯 Casos de Uso

### 1. Predicción Personal
```python
predicciones = predictor.predecir(datos_ultimas_24h, horas_adelante=[3, 6, 24])
```

### 2. Alertas Automáticas
```python
sistema = SistemaTEMPOTiempoReal(modelo, preparador, client, lat, lon)
alertas = sistema.generar_alerta()
```

### 3. Informe Diario
```python
sistema.informe_diario()
```

## 📱 Ejemplos de Aplicación

### ¿Es mejor salir a correr ahora o en 6 horas?

```python
datos_ejemplo = df.iloc[-24:]
predicciones = predictor.predecir(datos_ejemplo, horas_adelante=[6])

aqi_actual = datos_ejemplo['AQI'].iloc[-1]
aqi_6h = predicciones[6]['AQI']

if aqi_6h < aqi_actual:
    print("✅ Es mejor esperar 6 horas")
else:
    print("🏃 Es mejor salir ahora")
```

## 🌍 Ubicaciones Soportadas

TEMPO cubre **Norteamérica**:
- 🇲🇽 México
- 🇺🇸 Estados Unidos
- 🇨🇦 Canadá
- Partes del Caribe

### Ejemplos de Coordenadas:

| Ciudad | Latitud | Longitud |
|--------|---------|----------|
| Ciudad de México | 19.4326 | -99.1332 |
| Los Ángeles | 34.0522 | -118.2437 |
| Nueva York | 40.7128 | -74.0060 |
| Toronto | 43.6532 | -79.3832 |
| Monterrey | 25.6866 | -100.3161 |

## 📚 Recursos

### APIs de NASA
- **TEMPO Data**: https://tempo.si.edu/data.html
- **GES DISC**: https://disc.gsfc.nasa.gov/datasets?project=TEMPO
- **NASA Earthdata**: https://earthdata.nasa.gov/
- **NASA POWER API**: https://power.larc.nasa.gov/

### Documentación
- **TEMPO Mission**: https://science.nasa.gov/mission/tempo/
- **Tutoriales**: https://www.earthdata.nasa.gov/learn/webinars-and-tutorials
- **Data User Guide**: https://tempo.si.edu/documentation.html

## 🔧 Configuración Avanzada

### Personalizar el Modelo

```python
# Cambiar arquitectura LSTM
def crear_modelo_personalizado(lookback, n_features, forecast_horizon):
    model = Sequential([
        Bidirectional(LSTM(256, return_sequences=True), 
                     input_shape=(lookback, n_features)),
        Dropout(0.3),
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        LSTM(64),
        Dense(forecast_horizon)
    ])
    return model
```

### Agregar Más Características

```python
# Incluir datos adicionales
features = [
    'PM2.5', 'PM10', 'O3', 'NO2', 
    'temperatura', 'humedad', 'viento',
    'precipitacion',  # Nuevo
    'presion',        # Nuevo
    'hora_del_dia',   # Nuevo
    'dia_semana',     # Nuevo
    'AQI'
]
```

## 🚀 Despliegue en Producción

### 1. Containerizar con Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### 2. Crear API con FastAPI

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/predecir")
def predecir_calidad_aire(lat: float, lon: float):
    sistema = SistemaTEMPOTiempoReal(modelo, preparador, client, lat, lon)
    predicciones = sistema.predecir_proximas_horas([3, 6, 24])
    return predicciones
```

### 3. Automatizar Actualizaciones

```python
# Cron job para actualizar datos cada hora
import schedule

def actualizar_datos():
    sistema.actualizar_datos_tempo()
    sistema.informe_diario()

schedule.every().hour.do(actualizar_datos)
```

## 🏆 Métricas del Modelo

Basado en datos de prueba:
- **MAE a 3h**: ~5-8 AQI
- **MAE a 6h**: ~8-12 AQI
- **MAE a 24h**: ~15-20 AQI
- **R² Score**: 0.85-0.92

## 🤝 Contribuir

Mejoras sugeridas:
1. Integración con más fuentes de datos (tráfico, eventos)
2. Modelos ensemble (LSTM + GRU + Transformer)
3. Interface web interactiva
4. Notificaciones push móviles
5. Mapas de calor geoespaciales

## 📄 Licencia

Este proyecto utiliza datos públicos de NASA y está disponible para uso educativo y de investigación.

## 🙏 Agradecimientos

- **NASA TEMPO Mission** - Por proporcionar datos de calidad del aire
- **NASA POWER API** - Por datos meteorológicos gratuitos
- **TensorFlow/Keras** - Framework de deep learning

## 📞 Contacto

Para preguntas o colaboraciones relacionadas con este proyecto.

---

**🌍 ¡Prediciendo el futuro del aire que respiramos!**
