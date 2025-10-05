"""
Script de ejemplo para usar el modelo LSTM con Attention entrenado
Modelo: LSTM_Attention_AQI_20251004_002409
Fecha de entrenamiento: 2025-10-04 00:24:17
"""

import numpy as np
import pickle
from keras.models import load_model

# 1. Cargar el modelo
print("Cargando modelo...")
modelo = load_model("modelos_guardados\LSTM_Attention_AQI_20251004_002409.keras")

# 2. Cargar el scaler
print("Cargando scaler...")
with open("modelos_guardados\LSTM_Attention_AQI_20251004_002409_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# 3. Preparar datos de entrada
# Los datos deben tener forma: (n_muestras, 48, 8)
# Features esperados: ['PM2.5', 'PM10', 'O3', 'NO2', 'temperatura', 'humedad', 'viento', 'AQI']

def predecir_aqi(datos_historicos):
    """
    Predice AQI para los siguientes horizontes: [3, 6, 12, 24]

    Args:
        datos_historicos: DataFrame o array con las últimas 48 horas
                         Columnas: ['PM2.5', 'PM10', 'O3', 'NO2', 'temperatura', 'humedad', 'viento', 'AQI']

    Returns:
        predicciones: Array con 4 valores (AQI a 3h, 6h, 12h, 24h)
    """
    # Normalizar datos
    datos_norm = scaler.transform(datos_historicos)

    # Reshape para el modelo (agregar dimensión batch)
    datos_input = datos_norm.reshape(1, 48, 8)

    # Realizar predicción
    prediccion = modelo.predict(datos_input, verbose=0)

    # Desnormalizar (asumiendo que AQI es la columna 0)
    # Nota: Ajustar índice según tu configuración de scaler
    prediccion_real = scaler.inverse_transform(
        np.column_stack([prediccion[0], np.zeros((4, 7))])
    )[:, 0]

    return prediccion_real

# Ejemplo de uso:
# datos = pd.DataFrame(...)  # Últimas 48 horas de datos
# predicciones = predecir_aqi(datos)
# print(f"AQI predicho a 3h: {predicciones[0]:.2f}")
# print(f"AQI predicto a 6h: {predicciones[1]:.2f}")
# print(f"AQI predicho a 12h: {predicciones[2]:.2f}")
# print(f"AQI predicho a 24h: {predicciones[3]:.2f}")
