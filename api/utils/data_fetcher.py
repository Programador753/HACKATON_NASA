"""
Módulo para obtener datos de la API TEMPO NASA
Descarga y procesa datos de calidad del aire
"""

import aiohttp
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from config.config import (
    NASA_EARTHDATA_USERNAME,
    NASA_EARTHDATA_PASSWORD,
    TEMPO_API_BASE_URL,
    MODEL_FEATURES
)

logger = logging.getLogger(__name__)


class TEMPODataFetcher:
    """Clase para obtener datos de TEMPO NASA"""
    
    def __init__(self):
        """Inicializar fetcher con credenciales"""
        self.base_url = TEMPO_API_BASE_URL
        self.username = NASA_EARTHDATA_USERNAME
        self.password = NASA_EARTHDATA_PASSWORD
        self.session = None
    
    async def _create_session(self):
        """Crear sesión HTTP con autenticación"""
        if self.session is None:
            auth = aiohttp.BasicAuth(self.username, self.password) if self.username else None
            self.session = aiohttp.ClientSession(auth=auth)
    
    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()
    
    async def get_historical_data(
        self,
        latitud: float,
        longitud: float,
        horas: int = 48
    ) -> pd.DataFrame:
        """
        Obtener datos históricos de TEMPO para una ubicación
        
        Args:
            latitud: Latitud de la ubicación
            longitud: Longitud de la ubicación
            horas: Número de horas de histórico a obtener
            
        Returns:
            DataFrame con datos históricos
        """
        logger.info(f"📥 Solicitando {horas}h de datos para ({latitud}, {longitud})")
        
        try:
            await self._create_session()
            
            # Calcular rango de fechas
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=horas)
            
            # Obtener datos para cada feature
            datos_combinados = {}
            
            for feature in MODEL_FEATURES:
                try:
                    datos = await self._fetch_feature_data(
                        feature=feature,
                        latitud=latitud,
                        longitud=longitud,
                        start_time=start_time,
                        end_time=end_time
                    )
                    datos_combinados[feature] = datos
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo obtener {feature}: {e}")
                    # Usar valores por defecto si falla
                    datos_combinados[feature] = self._get_default_values(feature, horas)
            
            # Crear DataFrame
            df = pd.DataFrame(datos_combinados)
            
            # Agregar timestamps
            df['datetime'] = pd.date_range(end=end_time, periods=len(df), freq='h')
            df.set_index('datetime', inplace=True)
            
            logger.info(f"✅ Obtenidos {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error al obtener datos históricos: {e}")
            raise
    
    async def _fetch_feature_data(
        self,
        feature: str,
        latitud: float,
        longitud: float,
        start_time: datetime,
        end_time: datetime
    ) -> List[float]:
        """
        Obtener datos de un feature específico de TEMPO
        
        NOTA: Esta es una implementación placeholder.
        La API real de TEMPO requiere acceso a archivos NetCDF específicos.
        """
        logger.debug(f"Obteniendo {feature}...")
        
        # TODO: Implementar descarga real desde TEMPO
        # Por ahora, generar datos sintéticos basados en patrones reales
        
        horas = int((end_time - start_time).total_seconds() / 3600)
        
        # Patrones típicos para cada contaminante
        if "NO2" in feature:
            # NO2: Mayor en horas pico, menor en la noche
            base = np.random.uniform(1.0, 2.0, horas)
            pattern = np.sin(np.linspace(0, 4*np.pi, horas)) * 0.5
            return list(base + pattern)
        
        elif "HCHO" in feature:
            # Formaldehído: Correlacionado con temperatura
            return list(np.random.uniform(0.5, 1.5, horas))
        
        elif "aerosol" in feature:
            # Índice de aerosoles
            return list(np.random.uniform(-0.5, 1.5, horas))
        
        elif "O3" in feature:
            # Ozono: Mayor durante el día
            base = np.random.uniform(280, 320, horas)
            pattern = np.abs(np.sin(np.linspace(0, 4*np.pi, horas))) * 30
            return list(base + pattern)
        
        elif "cloud" in feature:
            # Fracción de nubes
            return list(np.random.uniform(0, 0.7, horas))
        
        elif "solar" in feature:
            # Ángulo solar cenital
            pattern = np.abs(np.sin(np.linspace(0, 4*np.pi, horas))) * 60 + 20
            return list(pattern)
        
        else:
            return list(np.random.uniform(0, 1, horas))
    
    def _get_default_values(self, feature: str, horas: int) -> List[float]:
        """Obtener valores por defecto para un feature con variación realista"""
        # Valores típicos promedio basados en datos reales de LA
        defaults = {
            "PM2.5": 12.0,   # AccuWeather: 12 µg/m³
            "PM10": 40.0,    # AccuWeather: 40 µg/m³
            "O3": 30.0,      # Típico para LA
            "NO2": 56.0,     # AccuWeather: 56 µg/m³ (contaminante principal)
            "temperatura": 20.0,
            "humedad": 60.0,
            "viento": 8.0,
            "AQI": 59.0      # AccuWeather: 59 (Mala)
        }
        
        valor_base = defaults.get(feature, 1.0)
        
        # Generar datos con patrones realistas
        if feature == "PM2.5":
            # PM2.5: Valores bajos con variación moderada
            base = np.random.uniform(8, 18, horas)
            pattern = np.sin(np.linspace(0, 4*np.pi, horas)) * 5
            return list(np.abs(base + pattern))
        
        elif feature == "PM10":
            # PM10: generalmente 1.5-2x el PM2.5
            pm25 = self._get_default_values("PM2.5", horas)
            return list(np.array(pm25) * np.random.uniform(1.5, 2.0, horas))
        
        elif feature == "O3":
            # Ozono: alto durante el día, bajo en la noche
            base = np.random.uniform(30, 70, horas)
            pattern = np.abs(np.sin(np.linspace(0, 4*np.pi, horas))) * 30
            return list(base + pattern)
        
        elif feature == "NO2":
            # NO2: picos en horas de tráfico (principal contaminante en LA)
            base = np.random.uniform(45, 65, horas)  # Rango más alto
            pattern = np.abs(np.sin(np.linspace(0, 6*np.pi, horas))) * 15
            return list(base + pattern)
        
        elif feature == "temperatura":
            # Temperatura: ciclo diario
            base = 20.0
            pattern = np.sin(np.linspace(0, 4*np.pi, horas)) * 8
            return list(base + pattern + np.random.uniform(-2, 2, horas))
        
        elif feature == "humedad":
            # Humedad: inversa a temperatura
            base = 60.0
            pattern = -np.sin(np.linspace(0, 4*np.pi, horas)) * 15
            values = base + pattern + np.random.uniform(-5, 5, horas)
            return list(np.clip(values, 20, 95))
        
        elif feature == "viento":
            # Viento: variable
            return list(np.random.uniform(3, 15, horas))
        
        elif feature == "AQI":
            # AQI: basado en NO2 principalmente (contaminante dominante)
            no2 = np.array(self._get_default_values("NO2", horas))
            # Conversión simplificada NO2 µg/m³ a AQI
            aqi = np.where(no2 <= 53, (no2 / 53) * 50, 51 + ((no2 - 54) / 46) * 49)
            return list(np.clip(aqi, 0, 200))
        
        else:
            return [valor_base] * horas
    
    async def get_latest_data(
        self,
        latitud: float,
        longitud: float
    ) -> Dict[str, float]:
        """
        Obtener datos más recientes para una ubicación
        
        Returns:
            Diccionario con valores más recientes de cada feature
        """
        df = await self.get_historical_data(latitud, longitud, horas=1)
        
        if df.empty:
            return {}
        
        return df.iloc[-1].to_dict()


# Función auxiliar para implementación real de TEMPO
async def download_tempo_netcdf(
    product: str,
    date: datetime,
    latitud: float,
    longitud: float
) -> Optional[str]:
    """
    Descargar archivo NetCDF de TEMPO
    
    Esta función requiere:
    1. Credenciales de NASA Earthdata
    2. Conocimiento de la estructura de URLs de TEMPO
    3. Herramientas para procesar NetCDF (xarray, netCDF4)
    
    Args:
        product: Producto TEMPO (ej: 'NO2', 'O3')
        date: Fecha del dato
        latitud: Latitud
        longitud: Longitud
        
    Returns:
        Ruta al archivo descargado o None si falla
    """
    # TODO: Implementar descarga real
    # Ejemplo de URL: https://asdc.larc.nasa.gov/data/TEMPO/NO2_L2/2024/001/...
    
    logger.warning("⚠️ Descarga real de TEMPO aún no implementada")
    return None


async def extract_point_from_netcdf(
    netcdf_path: str,
    latitud: float,
    longitud: float,
    variable: str
) -> Optional[float]:
    """
    Extraer valor de un punto específico de un archivo NetCDF
    
    Requiere: xarray, netCDF4
    """
    try:
        import xarray as xr
        
        # Abrir dataset
        ds = xr.open_dataset(netcdf_path)
        
        # Encontrar el punto más cercano
        punto = ds.sel(lat=latitud, lon=longitud, method='nearest')
        
        # Extraer variable
        valor = float(punto[variable].values)
        
        ds.close()
        return valor
        
    except ImportError:
        logger.error("❌ xarray no instalado. Ejecute: pip install xarray netCDF4")
        return None
    except Exception as e:
        logger.error(f"❌ Error al leer NetCDF: {e}")
        return None
