"""
Script para reconstruir el modelo sin la capa Lambda problemática
Carga los pesos y reconstruye la arquitectura
"""

import numpy as np
import pickle
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path

# Definir la capa de Atención personalizada
class AttentionLayer(layers.Layer):
    """Capa de Atención que reemplaza la Lambda problemática"""
    
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        
    def build(self, input_shape):
        # Weight matrix para calcular attention scores
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], input_shape[-1]),
            initializer='glorot_uniform',
            trainable=True
        )
        
        self.b = self.add_weight(
            name='attention_bias',
            shape=(input_shape[-1],),
            initializer='zeros',
            trainable=True
        )
        
        self.u = self.add_weight(
            name='attention_context',
            shape=(input_shape[-1],),
            initializer='glorot_uniform',
            trainable=True
        )
        
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, inputs, mask=None):
        # Calcular attention scores
        uit = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        ait = tf.tensordot(uit, self.u, axes=1)
        a = tf.nn.softmax(ait, axis=1)
        a = tf.expand_dims(a, -1)
        weighted_input = inputs * a
        output = tf.reduce_sum(weighted_input, axis=1)
        return output
    
    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])
    
    def get_config(self):
        config = super(AttentionLayer, self).get_config()
        return config


def reconstruir_modelo():
    """Reconstruir el modelo sin capas Lambda problemáticas"""
    
    print("🔧 Reconstruyendo modelo LSTM con Atención...")
    
    # Definir arquitectura manualmente (DEBE COINCIDIR con el modelo original)
    inputs = layers.Input(shape=(48, 8), name='input_layer')
    
    # Bidirectional LSTM con 128 unidades (como en el modelo original)
    x = layers.Bidirectional(
        layers.LSTM(128, return_sequences=True, name='lstm_layer'),
        name='bidirectional_lstm'
    )(inputs)
    
    # Capa de Atención personalizada (reemplaza Lambda)
    x = AttentionLayer(name='attention')(x)
    
    # Dropout
    x = layers.Dropout(0.2, name='dropout')(x)
    
    # Capa densa con 32 unidades
    x = layers.Dense(32, activation='relu', name='dense_1')(x)
    
    # Salida: 4 horizontes de predicción
    outputs = layers.Dense(4, name='output')(x)
    
    # Crear modelo
    model = keras.Model(inputs=inputs, outputs=outputs, name='LSTM_with_Attention')
    
    print("✅ Arquitectura reconstruida")
    print(f"   Parámetros totales: {model.count_params():,}")
    
    return model


def cargar_pesos_compatibles(model, weights_path):
    """
    Cargar pesos del modelo original de forma compatible
    Ignora capas que no coinciden (Lambda)
    """
    
    print(f"\n📦 Intentando cargar pesos desde: {weights_path}")
    
    try:
        # Cargar pesos directamente sin by_name para archivos .weights.h5
        model.load_weights(weights_path, skip_mismatch=True)
        print("✅ Pesos cargados exitosamente (ignorando capas incompatibles)")
        return True
    except Exception as e:
        print(f"⚠️ No se pudieron cargar pesos: {e}")
        print("   El modelo usará pesos inicializados aleatoriamente")
        return False


def guardar_modelo_reconstruido(model, output_path):
    """Guardar el modelo reconstruido"""
    
    print(f"\n💾 Guardando modelo reconstruido en: {output_path}")
    
    # Compilar modelo
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    # Guardar
    model.save(output_path)
    print("✅ Modelo guardado exitosamente")


if __name__ == "__main__":
    # Rutas - corregir path relativo
    base_dir = Path(__file__).parent.parent.parent / "modelos_guardados"
    weights_path = base_dir / "LSTM_Attention_AQI_20251004_002409.weights.h5"
    output_path = base_dir / "LSTM_Attention_AQI_RECONSTRUIDO.keras"
    
    print(f"📁 Directorio base: {base_dir}")
    print(f"📁 Archivo de pesos: {weights_path}")
    print(f"📁 Salida: {output_path}")
    print()
    
    # Verificar que el directorio existe
    if not base_dir.exists():
        print(f"❌ Error: No existe el directorio {base_dir}")
        exit(1)
    
    # Reconstruir
    model = reconstruir_modelo()
    
    # Mostrar resumen
    print("\n📊 Resumen del modelo:")
    model.summary()
    
    # Cargar pesos si existen
    if weights_path.exists():
        cargar_pesos_compatibles(model, str(weights_path))
    else:
        print(f"\n⚠️ No se encontró archivo de pesos: {weights_path}")
        print("   Usando pesos inicializados aleatoriamente")
    
    # Guardar modelo reconstruido
    guardar_modelo_reconstruido(model, str(output_path))
    
    print("\n🎉 ¡Proceso completado!")
    print(f"\n📝 Próximo paso:")
    print(f"   Actualizar config.py para usar: {output_path.name}")
