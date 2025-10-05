"""
Configuración de la aplicación
Variables de entorno y constantes
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configuración del modelo
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(BASE_DIR / "modelos_guardados" / "LSTM_Attention_AQI_20251004_111121.keras")
)

SCALER_PATH = os.getenv(
    "SCALER_PATH",
    str(BASE_DIR / "modelos_guardados" / "scaler_20251004_111121.pkl")
)

METADATA_PATH = os.getenv(
    "METADATA_PATH",
    str(BASE_DIR / "modelos_guardados" / "metadata_20251004_111121.pkl")
)

# Configuración de la API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# Configuración de CORS
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

# Configuración de datos TEMPO NASA
NASA_EARTHDATA_USERNAME = os.getenv("NASA_EARTHDATA_USERNAME", "")
NASA_EARTHDATA_PASSWORD = os.getenv("NASA_EARTHDATA_PASSWORD", "")

# OpenAQ API Configuration
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")
OPENAQ_BASE_URL = "https://api.openaq.org/v3"

# URLs de la API de NASA TEMPO
TEMPO_API_BASE_URL = "https://asdc.larc.nasa.gov/data/TEMPO/"

# Parámetros del modelo
LOOKBACK_HOURS = 48  # Horas de histórico necesarias
FORECAST_HORIZONS = [3, 6, 12, 24]  # Horizontes de predicción en horas

# Features que espera el modelo (deben coincidir con el entrenamiento)
# IMPORTANTE: Estas son las features reales con las que se entrenó el modelo
MODEL_FEATURES = [
    "PM2.5",
    "PM10",
    "O3",
    "NO2",
    "temperatura",
    "humedad",
    "viento",
    "AQI"
]

# Clasificación de calidad del aire (AQI)
AQI_CATEGORIES = {
    "Excelente": {"range": (0, 12), "color": "#00E400", "mensaje": "Calidad del aire ideal"},
    "Bueno": {"range": (12.1, 35.4), "color": "#FFFF00", "mensaje": "Calidad del aire aceptable"},
    "Aceptable": {"range": (35.5, 55.4), "color": "#FF7E00", "mensaje": "Grupos sensibles deben limitar actividades prolongadas"},
    "Regular": {"range": (55.5, 150.4), "color": "#FF0000", "mensaje": "Todos pueden experimentar efectos en la salud"},
    "Malo": {"range": (150.5, 250.4), "color": "#99004C", "mensaje": "Alerta de salud: todos pueden experimentar efectos graves"},
    "Muy Malo": {"range": (250.5, 350.4), "color": "#7E0023", "mensaje": "Alerta de salud de emergencia"},
    "Peligroso": {"range": (350.5, float('inf')), "color": "#4C0026", "mensaje": "Advertencia de salud de condiciones de emergencia"}
}

# Cache settings
CACHE_PREDICTIONS = os.getenv("CACHE_PREDICTIONS", "False").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutos

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Límites de rate limiting (requests por minuto)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
