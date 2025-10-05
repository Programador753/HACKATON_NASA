"""
Modelos Pydantic para validación de requests y responses de la API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class CalidadAire(str, Enum):
    """Clasificación de calidad del aire según AQI"""
    EXCELENTE = "Excelente"
    BUENO = "Bueno"
    ACEPTABLE = "Aceptable"
    REGULAR = "Regular"
    MALO = "Malo"
    MUY_MALO = "Muy Malo"
    PELIGROSO = "Peligroso"


class PredictionRequest(BaseModel):
    """Modelo para solicitud de predicción"""
    latitud: float = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="Latitud de la ubicación (-90 a 90)"
    )
    longitud: float = Field(
        ..., 
        ge=-180, 
        le=180, 
        description="Longitud de la ubicación (-180 a 180)"
    )
    nombre_ubicacion: Optional[str] = Field(
        None,
        description="Nombre descriptivo de la ubicación (opcional)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitud": 34.0522,
                "longitud": -118.2437,
                "nombre_ubicacion": "Los Angeles, CA"
            }
        }


class ContaminantesData(BaseModel):
    """Datos de contaminantes individuales"""
    PM2_5: Optional[float] = Field(None, description="PM2.5 en µg/m³", alias="PM2.5")
    PM10: Optional[float] = Field(None, description="PM10 en µg/m³")
    O3: Optional[float] = Field(None, description="Ozono en µg/m³")
    NO2: Optional[float] = Field(None, description="Dióxido de nitrógeno en µg/m³")
    temperatura: Optional[float] = Field(None, description="Temperatura en °C")
    humedad: Optional[float] = Field(None, description="Humedad relativa en %")
    viento: Optional[float] = Field(None, description="Velocidad del viento en m/s")
    
    class Config:
        populate_by_name = True


class HorizontePrediccion(BaseModel):
    """Predicción para un horizonte temporal específico"""
    horizonte: str = Field(..., description="Horizonte temporal (ej: '3h', '24h')")
    aqi_predicho: float = Field(..., description="Valor de AQI predicho")
    calidad: CalidadAire = Field(..., description="Clasificación de calidad del aire")
    mensaje: str = Field(..., description="Mensaje descriptivo sobre la calidad")
    color: str = Field(..., description="Color hexadecimal asociado al nivel de calidad")
    confianza: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Nivel de confianza de la predicción (0-1)"
    )
    contaminantes: Optional[ContaminantesData] = Field(
        None,
        description="Valores predichos de contaminantes individuales"
    )


class PredictionResponse(BaseModel):
    """Modelo para respuesta de predicción"""
    ubicacion: Dict[str, float] = Field(
        ...,
        description="Coordenadas de la ubicación"
    )
    nombre_ubicacion: Optional[str] = Field(
        None,
        description="Nombre de la ubicación"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de la predicción"
    )
    predicciones: List[HorizontePrediccion] = Field(
        ...,
        description="Lista de predicciones para diferentes horizontes temporales"
    )
    aqi_actual_estimado: Optional[float] = Field(
        None,
        description="AQI actual estimado basado en datos más recientes"
    )
    contaminantes_actuales: Optional[ContaminantesData] = Field(
        None,
        description="Valores actuales de contaminantes (datos en tiempo real de OpenAQ)"
    )
    datos_entrada_disponibles: bool = Field(
        ...,
        description="Indica si se obtuvieron datos suficientes para la predicción"
    )
    fuente_datos: Optional[str] = Field(
        None,
        description="Fuente de datos usada (OpenAQ, TEMPO, simulado)"
    )
    advertencias: Optional[List[str]] = Field(
        default=[],
        description="Advertencias o notas sobre la predicción"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "ubicacion": {"latitud": 34.0522, "longitud": -118.2437},
                "nombre_ubicacion": "Los Angeles, CA",
                "timestamp": "2025-10-04T00:00:00",
                "predicciones": [
                    {
                        "horizonte": "3h",
                        "aqi_predicho": 45.2,
                        "calidad": "Bueno",
                        "mensaje": "Calidad del aire aceptable",
                        "color": "#00E400",
                        "confianza": 0.85
                    }
                ],
                "aqi_actual_estimado": 42.5,
                "datos_entrada_disponibles": True,
                "advertencias": []
            }
        }


class HealthStatus(BaseModel):
    """Estado de salud de la API"""
    status: str = Field(..., description="Estado general de la API")
    model_loaded: bool = Field(..., description="Indica si el modelo está cargado")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del health check"
    )


class ModelInfo(BaseModel):
    """Información sobre el modelo cargado"""
    nombre_modelo: str = Field(..., description="Nombre del modelo")
    version: str = Field(..., description="Versión del modelo")
    arquitectura: str = Field(..., description="Tipo de arquitectura")
    parametros_totales: int = Field(..., description="Número total de parámetros")
    features_entrada: List[str] = Field(..., description="Features que espera el modelo")
    horizontes_prediccion: List[str] = Field(..., description="Horizontes de predicción")
    lookback_horas: int = Field(..., description="Horas de histórico requeridas")
    metricas_entrenamiento: Optional[Dict[str, float]] = Field(
        None,
        description="Métricas del modelo en entrenamiento"
    )
    fecha_entrenamiento: Optional[str] = Field(
        None,
        description="Fecha de entrenamiento del modelo"
    )


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    detail: str = Field(..., description="Detalles del error")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del error"
    )
