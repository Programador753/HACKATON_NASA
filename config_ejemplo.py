"""
Archivo de configuración para el sistema de predicción de calidad del aire
con NASA TEMPO + LSTM

Copia este archivo a 'config.py' y personaliza tus valores
"""

# ========================================
# CONFIGURACIÓN DE DATOS
# ========================================

# Fuente de datos (elige una)
USAR_DATOS_SINTETICOS = False      # Datos generados aleatoriamente
USAR_TEMPO_SIMULADO = False         # Patrones realistas de TEMPO (SIN credenciales)
USAR_TEMPO_REAL = True            # Datos reales de TEMPO (CON credenciales)

# ========================================
# CREDENCIALES NASA EARTHDATA
# ========================================
# Obtén tus credenciales en: https://urs.earthdata.nasa.gov/users/new

NASA_USERNAME = ""  # Reemplaza con: "tu_usuario"
NASA_PASSWORD = ""  # Reemplaza con: "tu_contraseña"

# ========================================
# UBICACIÓN GEOGRÁFICA
# ========================================
# TEMPO cubre Norteamérica (México, USA, Canadá)

# Ejemplos de ciudades:
# Ciudad de México: (19.4326, -99.1332)
# Los Ángeles: (34.0522, -118.2437)
# Nueva York: (40.7128, -74.0060)
# Toronto: (43.6532, -79.3832)
# Monterrey: (25.6866, -100.3161)

LATITUD = 34.0522            # Los Ángeles, California
LONGITUD = -118.2437         # USA (dentro de cobertura TEMPO)
NOMBRE_UBICACION = "Los Angeles, CA"

# ========================================
# PERÍODO DE DATOS
# ========================================
# Formato: YYYYMMDD

FECHA_INICIO = "20240101"   # Inicio del período
FECHA_FIN = "20251001"      # Fin del período (1 año recomendado)

# ========================================
# CONFIGURACIÓN DEL MODELO
# ========================================

# Parámetros de ventana temporal
LOOKBACK_HOURS = 24         # Cuántas horas usar para predecir
FORECAST_HOURS = 24         # Cuántas horas predecir adelante

# Arquitectura LSTM
LSTM_UNITS_1 = 128          # Neuronas en primera capa
LSTM_UNITS_2 = 64           # Neuronas en segunda capa
LSTM_UNITS_3 = 32           # Neuronas en tercera capa
DROPOUT_RATE = 0.2          # Tasa de dropout

# Entrenamiento
EPOCHS = 100                # Máximo de épocas
BATCH_SIZE = 32             # Tamaño del batch
LEARNING_RATE = 0.001       # Tasa de aprendizaje inicial
VALIDATION_SPLIT = 0.2      # % de datos para validación

# Early stopping
PATIENCE = 15               # Épocas sin mejora antes de detener
MIN_DELTA = 0.001           # Mejora mínima considerada

# ========================================
# HORIZONTES DE PREDICCIÓN
# ========================================
# Horas adelante para las que generar predicciones

HORIZONTES_PREDICCION = [3, 6, 12, 24]

# ========================================
# UMBRALES DE ALERTA
# ========================================
# Valores de AQI que generan alertas

UMBRAL_BUENA = 50           # AQI ≤ 50: Buena
UMBRAL_MODERADA = 100       # AQI ≤ 100: Moderada
UMBRAL_INSALUBRE_SENSIBLES = 150   # AQI ≤ 150: Insalubre (sensibles)
UMBRAL_INSALUBRE = 200      # AQI ≤ 200: Insalubre
UMBRAL_MUY_INSALUBRE = 300  # AQI ≤ 300: Muy insalubre
# AQI > 300: Peligrosa

# ========================================
# RUTAS DE ARCHIVOS
# ========================================

DIRECTORIO_MODELOS = "modelos"
DIRECTORIO_DATOS = "datos"
DIRECTORIO_LOGS = "logs"

# Nombres de archivos
MODELO_FILENAME = "modelo_lstm_calidad_aire.h5"
SCALER_FILENAME = "scaler_calidad_aire.pkl"
FEATURES_FILENAME = "features.pkl"

# ========================================
# CONFIGURACIÓN DE API (PRODUCCIÓN)
# ========================================

# FastAPI
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "API de Predicción de Calidad del Aire"
API_VERSION = "1.0.0"

# Actualización de datos
INTERVALO_ACTUALIZACION_MINUTOS = 60  # Cada cuánto actualizar datos TEMPO

# Rate limiting
MAX_REQUESTS_POR_MINUTO = 60

# ========================================
# CONFIGURACIÓN DE VISUALIZACIONES
# ========================================

# Matplotlib
FIGURA_DPI = 100
TAMAÑO_FIGURA_DEFECTO = (16, 10)

# Colores
COLOR_PM25 = '#e74c3c'
COLOR_PM10 = '#e67e22'
COLOR_O3 = '#3498db'
COLOR_NO2 = '#9b59b6'
COLOR_AQI = '#c0392b'

# ========================================
# CONFIGURACIÓN DE LOGGING
# ========================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========================================
# VALIDACIÓN DE CONFIGURACIÓN
# ========================================

def validar_configuracion():
    """Valida que la configuración sea correcta"""
    errores = []
    
    # Validar coordenadas
    if not (-90 <= LATITUD <= 90):
        errores.append(f"Latitud inválida: {LATITUD}. Debe estar entre -90 y 90")
    
    if not (-180 <= LONGITUD <= 180):
        errores.append(f"Longitud inválida: {LONGITUD}. Debe estar entre -180 y 180")
    
    # Validar que TEMPO cubra la ubicación (Norteamérica)
    if not (15 <= LATITUD <= 55 and -140 <= LONGITUD <= -50):
        print("⚠️ ADVERTENCIA: La ubicación podría estar fuera de la cobertura de TEMPO")
        print("   TEMPO cubre Norteamérica (aprox. 15°N-55°N, 140°W-50°W)")
    
    # Validar fechas
    try:
        from datetime import datetime
        datetime.strptime(FECHA_INICIO, "%Y%m%d")
        datetime.strptime(FECHA_FIN, "%Y%m%d")
    except ValueError:
        errores.append("Formato de fecha inválido. Usar YYYYMMDD")
    
    # Validar credenciales si se usa TEMPO real
    if USAR_TEMPO_REAL and (not NASA_USERNAME or not NASA_PASSWORD):
        errores.append("TEMPO real activado pero faltan credenciales de NASA")
    
    if errores:
        print("❌ ERRORES DE CONFIGURACIÓN:")
        for error in errores:
            print(f"   - {error}")
        return False
    else:
        print("✅ Configuración válida")
        return True

if __name__ == "__main__":
    validar_configuracion()
