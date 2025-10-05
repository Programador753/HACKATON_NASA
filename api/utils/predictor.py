"""
Módulo de predicción AQI usando modelo LSTM con Attention
Carga el modelo, scaler y realiza predicciones
"""

import numpy as np
import pandas as pd
import pickle
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    from keras.models import load_model
except ImportError:
    from tensorflow.keras.models import load_model

from config.config import (
    MODEL_PATH,
    SCALER_PATH,
    METADATA_PATH,
    LOOKBACK_HOURS,
    FORECAST_HORIZONS,
    MODEL_FEATURES,
    AQI_CATEGORIES,
    OPENAQ_API_KEY
)
from utils.data_fetcher import TEMPODataFetcher
from utils.openaq_fetcher import OpenAQFetcher
from utils.attention_layer import AttentionLayer
from models.schemas import (
    PredictionResponse,
    HorizontePrediccion,
    CalidadAire,
    ModelInfo,
    ContaminantesData
)

logger = logging.getLogger(__name__)


class AQIPredictor:
    """Clase para realizar predicciones de AQI usando el modelo entrenado"""
    
    def __init__(self):
        """Inicializar el predictor cargando modelo y scaler"""
        self.model = None
        self.scaler = None
        self.scaler_y = None  # Scaler específico para predicciones
        self.metadata = None
        self.data_fetcher = TEMPODataFetcher()
        self.openaq_fetcher = OpenAQFetcher(api_key=OPENAQ_API_KEY)
        
        self._load_model()
        self._load_scaler()
        self._load_metadata()
    
    def _load_model(self):
        """Cargar el modelo de Keras"""
        try:
            logger.info(f"📦 Cargando modelo desde: {MODEL_PATH}")
            
            if not Path(MODEL_PATH).exists():
                raise FileNotFoundError(f"Modelo no encontrado en: {MODEL_PATH}")
            
            # Importar tensorflow para funciones de backend
            import tensorflow as tf
            import tensorflow.keras.backend as K
            
            # Función para la capa Lambda de atención
            def attention_lambda(x):
                """Función personalizada para la capa Lambda de atención"""
                return tf.reduce_sum(x, axis=1)
            
            # Definir custom objects para capas personalizadas y funciones Lambda
            custom_objects = {
                'AttentionLayer': AttentionLayer,
                'Attention': AttentionLayer,
                # Funciones de TensorFlow para capas Lambda
                'reduce_sum': tf.reduce_sum,
                'expand_dims': tf.expand_dims,
                'tensordot': tf.tensordot,
                'tanh': tf.nn.tanh,
                'softmax': tf.nn.softmax,
                # Backend functions
                'sum': K.sum,
                'mean': K.mean,
                # Función lambda personalizada
                '<lambda>': attention_lambda,
                'attention_lambda': attention_lambda,
            }
            
            # Cargar modelo SIN compilar para evitar problemas con Lambda
            self.model = load_model(
                MODEL_PATH,
                custom_objects=custom_objects,
                compile=False,  # No compilar para evitar problemas con capas personalizadas
                safe_mode=False
            )
            
            # Compilar manualmente con configuración simple
            self.model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            logger.info(f"✅ Modelo cargado: {self.model.count_params():,} parámetros")
            
        except Exception as e:
            logger.error(f"❌ Error al cargar modelo: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _load_scaler(self):
        """Cargar el scaler para normalización"""
        try:
            logger.info(f"📦 Cargando scaler desde: {SCALER_PATH}")
            
            if not Path(SCALER_PATH).exists():
                raise FileNotFoundError(f"Scaler no encontrado en: {SCALER_PATH}")
            
            # Usar joblib en lugar de pickle (más robusto para sklearn objects)
            self.scaler = joblib.load(SCALER_PATH)
            
            logger.info("✅ Scaler cargado correctamente")
            
            # Intentar cargar scaler_y (para predicciones)
            scaler_y_path = SCALER_PATH.replace('scaler_', 'scaler_y_')
            if Path(scaler_y_path).exists():
                self.scaler_y = joblib.load(scaler_y_path)
                logger.info("✅ Scaler Y cargado correctamente")
            else:
                logger.warning("⚠️ Scaler Y no encontrado, usando scaler principal")
                self.scaler_y = None
            
        except Exception as e:
            logger.error(f"❌ Error al cargar scaler: {e}")
            raise
    
    def _load_metadata(self):
        """Cargar metadatos del modelo"""
        try:
            if Path(METADATA_PATH).exists():
                # Intentar cargar como pickle (joblib) primero
                try:
                    self.metadata = joblib.load(METADATA_PATH)
                    logger.info("✅ Metadatos cargados (joblib)")
                except:
                    # Si falla, intentar como JSON
                    with open(METADATA_PATH, 'r') as f:
                        self.metadata = json.load(f)
                    logger.info("✅ Metadatos cargados (JSON)")
            else:
                logger.warning("⚠️ Archivo de metadatos no encontrado")
                self.metadata = {}
        except Exception as e:
            logger.warning(f"⚠️ Error al cargar metadatos: {e}")
            self.metadata = {}
    
    def is_loaded(self) -> bool:
        """Verificar si el modelo y scaler están cargados"""
        return self.model is not None and self.scaler is not None
    
    def get_model_info(self) -> ModelInfo:
        """Obtener información del modelo"""
        return ModelInfo(
            nombre_modelo=self.metadata.get("nombre_experimento", "LSTM_Attention_AQI"),
            version="1.0.0",
            arquitectura="Bidirectional LSTM + Attention",
            parametros_totales=self.model.count_params() if self.model else 0,
            features_entrada=MODEL_FEATURES,
            horizontes_prediccion=[f"{h}h" for h in FORECAST_HORIZONS],
            lookback_horas=LOOKBACK_HOURS,
            metricas_entrenamiento=self.metadata.get("metricas", None),
            fecha_entrenamiento=self.metadata.get("fecha_entrenamiento", None)
        )
    
    def clasificar_aqi(self, aqi_value: float) -> Tuple[CalidadAire, str, str]:
        """
        Clasificar el valor de AQI según categorías EPA
        
        Returns:
            Tuple[CalidadAire, mensaje, color]
        """
        for categoria, info in AQI_CATEGORIES.items():
            min_val, max_val = info["range"]
            if min_val <= aqi_value <= max_val:
                return (
                    CalidadAire(categoria),
                    info["mensaje"],
                    info["color"]
                )
        
        # Por defecto si está fuera de rango
        return (
            CalidadAire.PELIGROSO,
            "Valor fuera de rango esperado",
            "#4C0026"
        )
    
    async def predict(
        self,
        latitud: float,
        longitud: float,
        location_name: Optional[str] = None
    ) -> PredictionResponse:
        """
        Realizar predicción de AQI para una ubicación
        
        Args:
            latitud: Latitud de la ubicación
            longitud: Longitud de la ubicación
            location_name: Nombre de la ubicación (opcional)
            
        Returns:
            PredictionResponse con las predicciones
        """
        advertencias = []
        fuente_datos = "simulado"
        
        # 1. Intentar obtener datos en tiempo real de OpenAQ con búsqueda progresiva
        print(f"\n{'='*60}")
        print(f"🌍 INICIANDO BÚSQUEDA OPENAQ para ({latitud}, {longitud})")
        print(f"{'='*60}\n")
        logger.info(f"🌍 Obteniendo datos en tiempo real de OpenAQ para ({latitud}, {longitud})")
        
        datos_actuales = None
        # OpenAQ v3 solo acepta radio máximo de 25km
        radios_busqueda = [25.0]  # Radio en km
        
        try:
            for radio in radios_busqueda:
                print(f"🔍 Buscando estaciones OpenAQ en radio de {radio}km...")
                logger.info(f"🔍 Buscando estaciones OpenAQ en radio de {radio}km...")
                
                datos_temp = await self.openaq_fetcher.get_latest_measurements(
                    latitud=latitud,
                    longitud=longitud,
                    radius_km=radio
                )
                
                print(f"📊 Datos recibidos de OpenAQ: {datos_temp}")
                logger.info(f"📊 Datos OpenAQ completos: {datos_temp}")
                
                # Verificar si encontramos datos reales
                # OpenAQ puede devolver cualquier valor, incluso si coincide con nuestros defaults
                # Lo importante es que venga de una estación real
                if datos_temp and any(key in datos_temp for key in ["PM2.5", "NO2", "O3", "PM10"]):
                    logger.info(f"✅ Datos reales obtenidos de OpenAQ en radio {radio}km")
                    print(f"✅ USANDO DATOS REALES DE OPENAQ: PM2.5={datos_temp.get('PM2.5')}, NO2={datos_temp.get('NO2')}, O3={datos_temp.get('O3')}")
                    datos_actuales = datos_temp
                    fuente_datos = f"OpenAQ (tiempo real, {radio}km)"
                    break
                else:
                    logger.warning(f"⚠️ OpenAQ no retornó contaminantes en {radio}km")
            
            if not datos_actuales:
                logger.warning("⚠️ OpenAQ no retornó datos reales en ningún radio, usando datos estimados")
                advertencias.append(f"No hay estaciones OpenAQ cercanas (buscado hasta {radios_busqueda[-1]}km)")
                datos_actuales = self._get_default_current_data()
                fuente_datos = "Datos estimados (sin cobertura OpenAQ)"
            else:
                print(f"✅ USANDO DATOS REALES DE OPENAQ")
                logger.info(f"✅ Usando datos reales de OpenAQ: {fuente_datos}")
                
        except Exception as e:
            logger.error(f"❌ Error al obtener datos de OpenAQ: {e}")
            advertencias.append(f"Error OpenAQ: {str(e)[:100]}")
            datos_actuales = self._get_default_current_data()
            fuente_datos = "Datos estimados (error de conexión)"
        
        # 2. Obtener datos históricos de TEMPO o simulados
        logger.info(f"📊 Obteniendo datos históricos para predicción...")
        
        try:
            datos_historicos = await self.data_fetcher.get_historical_data(
                latitud=latitud,
                longitud=longitud,
                horas=LOOKBACK_HOURS
            )
        except Exception as e:
            logger.error(f"❌ Error al obtener datos históricos: {e}")
            advertencias.append(f"Usando datos simulados para histórico: {str(e)[:100]}")
            datos_historicos = self._generar_datos_simulados()
        
        # 3. Verificar que tenemos suficientes datos
        if len(datos_historicos) < LOOKBACK_HOURS:
            advertencias.append(
                f"Solo se obtuvieron {len(datos_historicos)} horas de {LOOKBACK_HOURS} requeridas"
            )
        
        # 4. Preparar datos para el modelo
        X = self._preparar_datos(datos_historicos)
        
        # 5. Realizar predicción
        logger.info("🔮 Realizando predicción...")
        predicciones_raw = self.model.predict(X, verbose=0)
        
        # 6. Desnormalizar predicciones
        predicciones_aqi = self._desnormalizar_predicciones(predicciones_raw[0])
        
        # 7. Crear predicciones con contaminantes
        predicciones_lista = []
        for i, horizonte in enumerate(FORECAST_HORIZONS):
            aqi_pred = float(predicciones_aqi[i])
            calidad, mensaje, color = self.clasificar_aqi(aqi_pred)
            
            # Estimar contaminantes futuros basados en AQI predicho
            contaminantes_futuros = self._estimar_contaminantes_desde_aqi(aqi_pred, datos_actuales)
            
            predicciones_lista.append(
                HorizontePrediccion(
                    horizonte=f"{horizonte}h",
                    aqi_predicho=round(aqi_pred, 2),
                    calidad=calidad,
                    mensaje=mensaje,
                    color=color,
                    confianza=0.85,  # Placeholder - podría calcularse con ensembles
                    contaminantes=contaminantes_futuros
                )
            )
        
        # 8. Calcular AQI actual desde contaminantes reales
        # Si tenemos PM2.5 de OpenAQ, calcular AQI real
        if "PM2.5" in datos_actuales and datos_actuales["PM2.5"] is not None:
            aqi_actual = self._calcular_aqi_desde_pm25(datos_actuales["PM2.5"])
            logger.info(f"✅ AQI calculado desde PM2.5: {aqi_actual:.1f} (PM2.5={datos_actuales['PM2.5']:.1f} µg/m³)")
        else:
            # Fallback: estimar desde datos históricos
            aqi_actual = self._estimar_aqi_actual(datos_historicos)
            logger.warning(f"⚠️ AQI estimado desde históricos: {aqi_actual:.1f}")
        
        # 9. Crear objeto de contaminantes actuales
        contaminantes_actuales = ContaminantesData(
            **{
                "PM2.5": datos_actuales.get("PM2.5"),
                "PM10": datos_actuales.get("PM10"),
                "O3": datos_actuales.get("O3"),
                "NO2": datos_actuales.get("NO2"),
                "temperatura": datos_actuales.get("temperatura"),
                "humedad": datos_actuales.get("humedad"),
                "viento": datos_actuales.get("viento")
            }
        )
        
        return PredictionResponse(
            ubicacion={"latitud": latitud, "longitud": longitud},
            nombre_ubicacion=location_name,
            timestamp=datetime.now(),
            predicciones=predicciones_lista,
            aqi_actual_estimado=aqi_actual,
            contaminantes_actuales=contaminantes_actuales,
            datos_entrada_disponibles=len(datos_historicos) >= LOOKBACK_HOURS,
            fuente_datos=fuente_datos,
            advertencias=advertencias if advertencias else None
        )
    
    def _preparar_datos(self, df: pd.DataFrame) -> np.ndarray:
        """
        Preparar datos para el modelo (normalizar y reshape)
        
        Args:
            df: DataFrame con features
            
        Returns:
            Array con shape (1, LOOKBACK_HOURS, n_features)
        """
        # Asegurar que tenemos todas las features
        features_disponibles = [col for col in MODEL_FEATURES if col in df.columns]
        
        if len(features_disponibles) < len(MODEL_FEATURES):
            logger.warning(
                f"⚠️ Solo {len(features_disponibles)}/{len(MODEL_FEATURES)} features disponibles"
            )
        
        # Seleccionar features
        datos = df[features_disponibles].values
        
        # Si faltan horas, rellenar con la media
        if len(datos) < LOOKBACK_HOURS:
            padding = np.tile(datos.mean(axis=0), (LOOKBACK_HOURS - len(datos), 1))
            datos = np.vstack([padding, datos])
        elif len(datos) > LOOKBACK_HOURS:
            datos = datos[-LOOKBACK_HOURS:]
        
        # Normalizar
        datos_norm = self.scaler.transform(datos)
        
        # Reshape para el modelo: (1, timesteps, features)
        return datos_norm.reshape(1, LOOKBACK_HOURS, len(features_disponibles))
    
    def _desnormalizar_predicciones(self, predicciones_norm: np.ndarray) -> np.ndarray:
        """
        Desnormalizar las predicciones del modelo
        
        Args:
            predicciones_norm: Predicciones normalizadas
            
        Returns:
            Predicciones en escala original
        """
        # Si tenemos scaler_y específico, usarlo (modelo nuevo)
        if self.scaler_y is not None:
            # Asegurar que sea 2D: (n_samples, n_features)
            if predicciones_norm.ndim == 1:
                predicciones_norm = predicciones_norm.reshape(1, -1)
            
            predicciones_denorm = self.scaler_y.inverse_transform(predicciones_norm)
            # Aplicar post-procesamiento: convertir negativos a 0
            predicciones_denorm = np.maximum(predicciones_denorm, 0)
            return predicciones_denorm.flatten()
        
        # Método antiguo (modelo reconstruido)
        n_features = len(MODEL_FEATURES)
        predicciones_full = np.zeros((len(predicciones_norm), n_features))
        predicciones_full[:, 0] = predicciones_norm
        
        predicciones_denorm = self.scaler.inverse_transform(predicciones_full)
        
        # Aplicar post-procesamiento: convertir negativos a 0
        result = np.maximum(predicciones_denorm[:, 0], 0)
        
        return result
        predicciones_full[:, 0] = predicciones_norm
        
        predicciones_denorm = self.scaler.inverse_transform(predicciones_full)
        
        # Aplicar post-procesamiento: convertir negativos a 0
        result = np.maximum(predicciones_denorm[:, 0], 0)
        
        return result
    
    def _estimar_aqi_actual(self, df: pd.DataFrame) -> Optional[float]:
        """Estimar AQI actual a partir del DataFrame histórico"""
        if df.empty:
            return None
        
        # Si hay columna AQI, usar el último valor
        if 'AQI' in df.columns:
            return float(df['AQI'].iloc[-1])
        
        # Calcular AQI de cada contaminante y tomar el máximo
        aqi_values = []
        
        # AQI desde PM2.5
        if 'PM2.5' in df.columns:
            pm25 = float(df['PM2.5'].iloc[-1])
            aqi_pm25 = self._calculate_aqi_from_pm25(pm25)
            aqi_values.append(aqi_pm25)
        
        # AQI desde PM10
        if 'PM10' in df.columns:
            pm10 = float(df['PM10'].iloc[-1])
            aqi_pm10 = self._calculate_aqi_from_pm10(pm10)
            aqi_values.append(aqi_pm10)
        
        # AQI desde O3
        if 'O3' in df.columns:
            o3 = float(df['O3'].iloc[-1])
            aqi_o3 = self._calculate_aqi_from_o3(o3)
            aqi_values.append(aqi_o3)
        
        # AQI desde NO2
        if 'NO2' in df.columns:
            no2 = float(df['NO2'].iloc[-1])
            aqi_no2 = self._calculate_aqi_from_no2(no2)
            aqi_values.append(aqi_no2)
        
        # Retornar el AQI máximo (el peor contaminante define el AQI total)
        if aqi_values:
            return max(aqi_values)
        
        return None
    
    def _calculate_aqi_from_pm25(self, pm25: float) -> float:
        """Calcular AQI basado en PM2.5 usando escala EPA"""
        breakpoints = [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ]
        
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= pm25 <= c_high:
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (pm25 - c_low) + aqi_low
                return round(aqi, 1)
        
        return 500.0
    
    def _calculate_aqi_from_pm10(self, pm10: float) -> float:
        """Calcular AQI basado en PM10 usando escala EPA"""
        breakpoints = [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 604, 301, 500)
        ]
        
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= pm10 <= c_high:
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (pm10 - c_low) + aqi_low
                return round(aqi, 1)
        
        return 500.0
    
    def _calculate_aqi_from_o3(self, o3: float) -> float:
        """Calcular AQI basado en O3 (ppb) usando escala EPA"""
        breakpoints = [
            (0, 54, 0, 50),
            (55, 70, 51, 100),
            (71, 85, 101, 150),
            (86, 105, 151, 200),
            (106, 200, 201, 300)
        ]
        
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= o3 <= c_high:
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (o3 - c_low) + aqi_low
                return round(aqi, 1)
        
        return 300.0
    
    def _calculate_aqi_from_no2(self, no2: float) -> float:
        """Calcular AQI basado en NO2 (ppb) usando escala EPA"""
        breakpoints = [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 2049, 301, 500)
        ]
        
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= no2 <= c_high:
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (no2 - c_low) + aqi_low
                return round(aqi, 1)
        
        return 500.0
    
    def _estimar_contaminantes_desde_aqi(
        self, 
        aqi: float, 
        datos_actuales: Dict[str, float]
    ) -> ContaminantesData:
        """
        Estimar valores de contaminantes basados en AQI predicho
        
        Args:
            aqi: Valor de AQI predicho
            datos_actuales: Datos actuales para referencia
            
        Returns:
            ContaminantesData con valores estimados
        """
        # Estimar PM2.5 desde AQI (inverso de la fórmula EPA)
        if aqi <= 50:
            pm25 = (aqi / 50) * 12.0
        elif aqi <= 100:
            pm25 = ((aqi - 51) / 49) * (35.4 - 12.1) + 12.1
        elif aqi <= 150:
            pm25 = ((aqi - 101) / 49) * (55.4 - 35.5) + 35.5
        elif aqi <= 200:
            pm25 = ((aqi - 151) / 49) * (150.4 - 55.5) + 55.5
        else:
            pm25 = ((aqi - 201) / 99) * (250.4 - 150.5) + 150.5
        
        # Estimar otros contaminantes basados en relaciones típicas
        pm10 = pm25 * 1.7  # PM10 típicamente 1.5-2x PM2.5
        
        # Ajustar O3 y NO2 basados en cambio de AQI
        aqi_actual = datos_actuales.get("AQI", 59.0)
        factor_cambio = aqi / max(aqi_actual, 1.0)
        
        o3 = datos_actuales.get("O3", 30.0) * factor_cambio
        no2 = datos_actuales.get("NO2", 56.0) * factor_cambio
        
        # Variables meteorológicas se mantienen relativamente estables
        temperatura = datos_actuales.get("temperatura", 20.0) + np.random.uniform(-2, 2)
        humedad = datos_actuales.get("humedad", 60.0) + np.random.uniform(-5, 5)
        viento = datos_actuales.get("viento", 8.0) * np.random.uniform(0.9, 1.1)
        
        return ContaminantesData(
            **{
                "PM2.5": round(pm25, 2),
                "PM10": round(pm10, 2),
                "O3": round(o3, 2),
                "NO2": round(no2, 2),
                "temperatura": round(temperatura, 1),
                "humedad": round(min(max(humedad, 0), 100), 1),
                "viento": round(max(viento, 0), 1)
            }
        )
    
    def _calcular_aqi_desde_pm25(self, pm25: float) -> float:
        """
        Calcular AQI usando la fórmula EPA para PM2.5
        
        Args:
            pm25: Concentración de PM2.5 en µg/m³
            
        Returns:
            Valor de AQI
        """
        # Breakpoints EPA para PM2.5 (24 horas)
        # https://www.airnow.gov/aqi/aqi-calculator-concentration/
        if pm25 <= 12.0:
            return (50 / 12.0) * pm25
        elif pm25 <= 35.4:
            return ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
        elif pm25 <= 55.4:
            return ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
        elif pm25 <= 150.4:
            return ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5) + 151
        elif pm25 <= 250.4:
            return ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5) + 201
        else:
            return ((500 - 301) / (500.4 - 250.5)) * (pm25 - 250.5) + 301
    
    def _get_default_current_data(self) -> Dict[str, float]:
        """Obtener datos por defecto cuando OpenAQ no está disponible"""
        return {
            "PM2.5": 12.0,   # AccuWeather: 12 µg/m³ (Buena)
            "PM10": 40.0,    # AccuWeather: 40 µg/m³ (Buena)
            "O3": 30.0,      # Típico para LA
            "NO2": 56.0,     # AccuWeather: 56 µg/m³ (Mala - contaminante dominante)
            "temperatura": 20.0,
            "humedad": 60.0,
            "viento": 8.0,
            "AQI": 59.0      # AccuWeather: 59 (Mala/Unhealthy for Sensitive Groups)
        }
    
    def _generar_datos_simulados(self) -> pd.DataFrame:
        """Generar datos simulados para demo cuando no hay datos reales"""
        logger.warning("⚠️ Generando datos simulados para demostración")
        
        fechas = pd.date_range(
            end=datetime.now(),
            periods=LOOKBACK_HOURS,
            freq='H'
        )
        
        # Generar datos sintéticos con patrones realistas
        np.random.seed(42)
        datos = {
            'datetime': fechas,
            'NO2_column_number_density': np.random.uniform(0.5, 2.5, LOOKBACK_HOURS),
            'HCHO_column_number_density': np.random.uniform(0.3, 1.8, LOOKBACK_HOURS),
            'aerosol_index_354_388': np.random.uniform(-1, 2, LOOKBACK_HOURS),
            'O3_column_number_density': np.random.uniform(250, 350, LOOKBACK_HOURS),
            'cloud_fraction': np.random.uniform(0, 0.8, LOOKBACK_HOURS),
            'solar_zenith_angle': np.random.uniform(20, 80, LOOKBACK_HOURS)
        }
        
        df = pd.DataFrame(datos)
        df.set_index('datetime', inplace=True)
        
        return df
