"""
Capa de Atención personalizada para el modelo LSTM
Compatible con TensorFlow/Keras 2.x y 3.x
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class AttentionLayer(layers.Layer):
    """
    Capa de Atención personalizada para modelos secuenciales
    Calcula pesos de atención sobre la secuencia temporal
    """
    
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        
    def build(self, input_shape):
        """
        Construir los pesos de la capa
        
        Args:
            input_shape: (batch_size, timesteps, features)
        """
        # Weight matrix para calcular attention scores
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], input_shape[-1]),
            initializer='glorot_uniform',
            trainable=True
        )
        
        # Bias
        self.b = self.add_weight(
            name='attention_bias',
            shape=(input_shape[-1],),
            initializer='zeros',
            trainable=True
        )
        
        # Vector de contexto
        self.u = self.add_weight(
            name='attention_context',
            shape=(input_shape[-1],),
            initializer='glorot_uniform',
            trainable=True
        )
        
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, inputs, mask=None):
        """
        Forward pass de la capa de atención
        
        Args:
            inputs: Tensor de entrada (batch_size, timesteps, features)
            mask: Máscara opcional
            
        Returns:
            Salida ponderada por atención (batch_size, features)
        """
        # inputs shape: (batch_size, timesteps, features)
        
        # Calcular attention scores
        # uit = tanh(W @ xt + b)
        uit = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        
        # ait = uit @ u
        ait = tf.tensordot(uit, self.u, axes=1)
        
        # Aplicar softmax para obtener pesos de atención
        a = tf.nn.softmax(ait, axis=1)
        
        # Expandir dimensión para broadcasting
        # a shape: (batch_size, timesteps) -> (batch_size, timesteps, 1)
        a = tf.expand_dims(a, -1)
        
        # Aplicar pesos de atención
        # weighted_input shape: (batch_size, timesteps, features)
        weighted_input = inputs * a
        
        # Sumar sobre el eje temporal
        # output shape: (batch_size, features)
        output = tf.reduce_sum(weighted_input, axis=1)
        
        return output
    
    def compute_output_shape(self, input_shape):
        """
        Calcular la forma de salida
        
        Args:
            input_shape: (batch_size, timesteps, features)
            
        Returns:
            (batch_size, features)
        """
        return (input_shape[0], input_shape[-1])
    
    def get_config(self):
        """Configuración para serialización"""
        config = super(AttentionLayer, self).get_config()
        return config
    
    @classmethod
    def from_config(cls, config):
        """Crear capa desde configuración"""
        return cls(**config)


# Alias para compatibilidad
Attention = AttentionLayer
