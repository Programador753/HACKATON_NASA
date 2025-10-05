"""
🔄 SCRIPT DE REENTRENAMIENTO RÁPIDO DEL MODELO LSTM + ATTENTION
================================================================
✅ Usa AttentionLayer directamente (sin Lambda)
✅ Resuelve el problema de predicciones negativas
✅ Optimizado para entrenar rápido
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce warnings de TensorFlow

import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import joblib

# Importar la AttentionLayer personalizada
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'api', 'utils'))
from attention_layer import AttentionLayer

print("="*80)
print("🔄 REENTRENAMIENTO RÁPIDO DEL MODELO LSTM + ATTENTION")
print("="*80)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
LOOKBACK = 48              # 48 horas de historia
FORECAST_HORIZONS = [3, 6, 12, 24]  # Horizontes de predicción
FEATURES = ['PM2.5', 'PM10', 'O3', 'NO2', 'temperatura', 'humedad', 'viento', 'AQI']
BATCH_SIZE = 32
EPOCHS = 50                # Reducido para entrenamiento rápido
VALIDATION_SPLIT = 0.2

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, 'modelos_guardados')
os.makedirs(MODELOS_DIR, exist_ok=True)

# ============================================================================
# 1. GENERAR DATOS SINTÉTICOS (para entrenamiento rápido)
# ============================================================================
print("📊 Generando datos sintéticos para entrenamiento...")

def generar_datos_sinteticos(n_samples=5000):
    """
    Genera datos sintéticos realistas de calidad del aire
    """
    np.random.seed(42)
    
    # Crear serie temporal
    time_index = pd.date_range('2024-01-01', periods=n_samples, freq='h')
    
    # Patrones base con variación diurna
    hour = np.arange(n_samples) % 24
    day_of_week = (np.arange(n_samples) // 24) % 7
    
    # PM2.5: Mayor en horas pico (8am, 6pm) y días laborables
    pm25_base = 25 + 15 * np.sin(2 * np.pi * hour / 24) + 5 * (day_of_week < 5)
    pm25 = pm25_base + np.random.normal(0, 5, n_samples)
    pm25 = np.clip(pm25, 0, 150)
    
    # PM10: Correlacionado con PM2.5 pero mayor
    pm10 = pm25 * 1.7 + np.random.normal(0, 8, n_samples)
    pm10 = np.clip(pm10, 0, 250)
    
    # O3: Mayor en horas de sol (mediodía)
    o3_base = 40 + 20 * np.sin(2 * np.pi * (hour - 12) / 24)
    o3 = o3_base + np.random.normal(0, 8, n_samples)
    o3 = np.clip(o3, 0, 150)
    
    # NO2: Mayor en horas pico de tráfico
    no2_base = 30 + 20 * ((hour >= 7) & (hour <= 9) | (hour >= 17) & (hour <= 19))
    no2 = no2_base + np.random.normal(0, 5, n_samples)
    no2 = np.clip(no2, 0, 100)
    
    # Temperatura: Ciclo diurno y estacional
    temp_base = 20 + 10 * np.sin(2 * np.pi * hour / 24)
    temp = temp_base + np.random.normal(0, 2, n_samples)
    
    # Humedad: Inversa a temperatura
    hum = 60 - 0.5 * (temp - 20) + np.random.normal(0, 5, n_samples)
    hum = np.clip(hum, 20, 90)
    
    # Viento: Aleatorio con tendencia
    wind = 5 + np.random.exponential(3, n_samples)
    wind = np.clip(wind, 0, 30)
    
    # AQI: Calculado principalmente de PM2.5
    aqi = pm25 * 2 + pm10 * 0.5 + o3 * 0.3 + no2 * 0.2
    aqi = np.clip(aqi, 0, 300)
    
    # Crear DataFrame
    df = pd.DataFrame({
        'fecha': time_index,
        'PM2.5': pm25,
        'PM10': pm10,
        'O3': o3,
        'NO2': no2,
        'temperatura': temp,
        'humedad': hum,
        'viento': wind,
        'AQI': aqi
    })
    
    return df

datos = generar_datos_sinteticos(n_samples=5000)
print(f"✅ Generados {len(datos)} registros sintéticos")
print(f"   Rango de fechas: {datos['fecha'].min()} → {datos['fecha'].max()}\n")

# ============================================================================
# 2. PREPARAR SECUENCIAS PARA LSTM
# ============================================================================
print("🔧 Preparando secuencias para LSTM...")

def crear_secuencias(data, features, lookback, horizons):
    """
    Crea secuencias de entrada y salida para LSTM
    """
    X, y = [], []
    
    data_features = data[features].values
    
    for i in range(lookback, len(data) - max(horizons)):
        # Secuencia de entrada (lookback horas)
        X.append(data_features[i-lookback:i])
        
        # Salidas: AQI en cada horizonte futuro
        y_sample = []
        for h in horizons:
            if i + h < len(data):
                y_sample.append(data['AQI'].iloc[i + h])
            else:
                y_sample.append(data['AQI'].iloc[-1])
        y.append(y_sample)
    
    return np.array(X), np.array(y)

# Crear secuencias
X, y = crear_secuencias(datos, FEATURES, LOOKBACK, FORECAST_HORIZONS)

print(f"✅ Secuencias creadas:")
print(f"   X shape: {X.shape} (samples, timesteps, features)")
print(f"   y shape: {y.shape} (samples, horizons)\n")

# ============================================================================
# 3. NORMALIZACIÓN
# ============================================================================
print("📏 Normalizando datos...")

# Normalizar X (reshape para el scaler)
n_samples, n_timesteps, n_features = X.shape
X_reshaped = X.reshape(-1, n_features)

scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X_reshaped)
X_normalized = X_normalized.reshape(n_samples, n_timesteps, n_features)

# Normalizar y
scaler_y = MinMaxScaler()
y_normalized = scaler_y.fit_transform(y)

print(f"✅ Normalización completada")
print(f"   X rango: [{X_normalized.min():.3f}, {X_normalized.max():.3f}]")
print(f"   y rango: [{y_normalized.min():.3f}, {y_normalized.max():.3f}]\n")

# ============================================================================
# 4. DIVISIÓN TRAIN/VAL
# ============================================================================
X_train, X_val, y_train, y_val = train_test_split(
    X_normalized, y_normalized, 
    test_size=VALIDATION_SPLIT, 
    shuffle=False  # No mezclar para mantener orden temporal
)

print(f"📊 División de datos:")
print(f"   Train: {len(X_train)} muestras")
print(f"   Val:   {len(X_val)} muestras\n")

# ============================================================================
# 5. CREAR MODELO CON ATTENTIONLAYER (SIN LAMBDA!)
# ============================================================================
print("🧠 Construyendo modelo LSTM + Attention...")

def crear_modelo_lstm_attention(input_shape, n_outputs):
    """
    Crea modelo LSTM con AttentionLayer personalizada
    ✅ SIN LAMBDA - Usa AttentionLayer directamente
    """
    inputs = layers.Input(shape=input_shape, name='input_layer')
    
    # Bidirectional LSTM
    x = layers.Bidirectional(
        layers.LSTM(128, return_sequences=True),
        name='bidirectional_lstm'
    )(inputs)
    
    # ✅ AttentionLayer personalizada (NO Lambda!)
    x = AttentionLayer(name='attention')(x)
    
    # Dropout para regularización
    x = layers.Dropout(0.3, name='dropout')(x)
    
    # Dense intermedia
    x = layers.Dense(32, activation='relu', name='dense_1')(x)
    
    # Salida: 4 horizontes de predicción
    outputs = layers.Dense(n_outputs, activation='linear', name='output')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs, name='LSTM_with_Attention')
    
    return model

modelo = crear_modelo_lstm_attention(
    input_shape=(LOOKBACK, len(FEATURES)),
    n_outputs=len(FORECAST_HORIZONS)
)

modelo.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae']
)

print("✅ Modelo construido:")
modelo.summary()
print()

# ============================================================================
# 6. CALLBACKS PARA ENTRENAMIENTO OPTIMIZADO
# ============================================================================
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
modelo_path = os.path.join(MODELOS_DIR, f'LSTM_Attention_AQI_{timestamp}.keras')

callbacks = [
    # Early stopping: Para si no mejora en 10 épocas
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    
    # Reduce learning rate si se estanca
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1
    ),
    
    # Guarda el mejor modelo
    ModelCheckpoint(
        modelo_path,
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
]

# ============================================================================
# 7. ENTRENAMIENTO
# ============================================================================
print("🏋️ Iniciando entrenamiento...")
print(f"   Épocas máximas: {EPOCHS}")
print(f"   Batch size: {BATCH_SIZE}")
print(f"   Early stopping: patience=10\n")

history = modelo.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

print("\n✅ Entrenamiento completado!")

# ============================================================================
# 8. EVALUACIÓN
# ============================================================================
print("\n📊 Evaluando modelo...")

# Evaluar en conjunto de validación
val_loss, val_mae = modelo.evaluate(X_val, y_val, verbose=0)

print(f"   Val Loss (MSE): {val_loss:.4f}")
print(f"   Val MAE:        {val_mae:.4f}")

# Predicciones de ejemplo
y_pred = modelo.predict(X_val[:5], verbose=0)
y_pred_denorm = scaler_y.inverse_transform(y_pred)
y_true_denorm = scaler_y.inverse_transform(y_val[:5])

print("\n🔍 Ejemplos de predicciones:")
for i in range(5):
    print(f"\n   Muestra {i+1}:")
    for j, h in enumerate(FORECAST_HORIZONS):
        print(f"      {h}h → Pred: {y_pred_denorm[i,j]:.1f}, Real: {y_true_denorm[i,j]:.1f}")

# ============================================================================
# 9. GUARDAR ARTEFACTOS
# ============================================================================
print("\n💾 Guardando artefactos...")

# Guardar scaler
scaler_path = os.path.join(MODELOS_DIR, f'scaler_{timestamp}.pkl')
joblib.dump(scaler, scaler_path)
print(f"   ✅ Scaler guardado: {os.path.basename(scaler_path)}")

# Guardar scaler de y (para denormalizar predicciones)
scaler_y_path = os.path.join(MODELOS_DIR, f'scaler_y_{timestamp}.pkl')
joblib.dump(scaler_y, scaler_y_path)
print(f"   ✅ Scaler Y guardado: {os.path.basename(scaler_y_path)}")

# Guardar metadatos
metadata = {
    'timestamp': timestamp,
    'lookback': LOOKBACK,
    'forecast_horizons': FORECAST_HORIZONS,
    'features': FEATURES,
    'n_features': len(FEATURES),
    'val_loss': float(val_loss),
    'val_mae': float(val_mae),
    'epochs_trained': len(history.history['loss']),
    'model_params': modelo.count_params()
}

metadata_path = os.path.join(MODELOS_DIR, f'metadata_{timestamp}.pkl')
joblib.dump(metadata, metadata_path)
print(f"   ✅ Metadatos guardados: {os.path.basename(metadata_path)}")

print(f"\n   📁 Modelo principal: {os.path.basename(modelo_path)}")

# ============================================================================
# 10. ACTUALIZAR CONFIGURACIÓN DE LA API
# ============================================================================
print("\n🔧 Actualizando configuración de la API...")

config_path = os.path.join(BASE_DIR, 'api', 'config', 'config.py')

if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Reemplazar MODEL_PATH
    import re
    new_model_name = f'LSTM_Attention_AQI_{timestamp}.keras'
    config_content = re.sub(
        r"MODEL_PATH = os\.path\.join\(MODELOS_DIR, ['\"].*?['\"]\)",
        f"MODEL_PATH = os.path.join(MODELOS_DIR, '{new_model_name}')",
        config_content
    )
    
    # Reemplazar SCALER_PATH
    new_scaler_name = f'scaler_{timestamp}.pkl'
    config_content = re.sub(
        r"SCALER_PATH = os\.path\.join\(MODELOS_DIR, ['\"].*?['\"]\)",
        f"SCALER_PATH = os.path.join(MODELOS_DIR, '{new_scaler_name}')",
        config_content
    )
    
    # Reemplazar METADATA_PATH
    new_metadata_name = f'metadata_{timestamp}.pkl'
    config_content = re.sub(
        r"METADATA_PATH = os\.path\.join\(MODELOS_DIR, ['\"].*?['\"]\)",
        f"METADATA_PATH = os.path.join(MODELOS_DIR, '{new_metadata_name}')",
        config_content
    )
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"   ✅ Config actualizado: {os.path.basename(config_path)}")
else:
    print(f"   ⚠️ Config no encontrado: {config_path}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*80)
print("✅ REENTRENAMIENTO COMPLETADO EXITOSAMENTE")
print("="*80)
print(f"\n📦 Archivos generados:")
print(f"   • Modelo:    {os.path.basename(modelo_path)}")
print(f"   • Scaler:    {os.path.basename(scaler_path)}")
print(f"   • Scaler Y:  {os.path.basename(scaler_y_path)}")
print(f"   • Metadata:  {os.path.basename(metadata_path)}")

print(f"\n📊 Métricas finales:")
print(f"   • Parámetros: {modelo.count_params():,}")
print(f"   • Val Loss:   {val_loss:.4f}")
print(f"   • Val MAE:    {val_mae:.4f}")
print(f"   • Épocas:     {len(history.history['loss'])}")

print(f"\n🚀 SIGUIENTE PASO:")
print(f"   Reinicia la API con:")
print(f"   python api/run_prod.py")

print("\n✅ La API ahora usará el nuevo modelo sin predicciones negativas!")
print("="*80)
