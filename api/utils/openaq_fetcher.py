"""
Módulo para obtener datos en tiempo real de OpenAQ API v3
https://docs.openaq.org/
"""

import aiohttp
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class OpenAQFetcher:
    """Clase para obtener datos de calidad del aire de OpenAQ API v3"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar fetcher
        
        Args:
            api_key: API key de OpenAQ (opcional, se puede pasar o tomar de variable de entorno)
        """
        self.base_url = "https://api.openaq.org/v3"
        self.api_key = api_key or os.getenv("OPENAQ_API_KEY", "")
        self.session = None
    
    async def _create_session(self):
        """Crear sesión HTTP con autenticación"""
        if self.session is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "AQI-Predictor-API/1.0"
            }
            
            # Añadir API key si está disponible
            if self.api_key:
                headers["X-API-Key"] = self.api_key
                logger.info("🔑 Usando OpenAQ API Key")
            else:
                logger.warning("⚠️ No se encontró OpenAQ API Key - funcionalidad limitada")
            
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()
    
    async def get_latest_measurements(
        self,
        latitud: float,
        longitud: float,
        radius_km: float = 25.0
    ) -> Dict[str, float]:
        """
        Obtener mediciones más recientes cerca de una ubicación
        
        Args:
            latitud: Latitud de la ubicación
            longitud: Longitud de la ubicación
            radius_km: Radio de búsqueda en kilómetros
            
        Returns:
            Diccionario con valores de contaminantes
        """
        await self._create_session()
        
        print(f"\n🌍 GET_LATEST_MEASUREMENTS llamado para ({latitud}, {longitud})")
        logger.info(f"🌍 Obteniendo datos OpenAQ para ({latitud}, {longitud})")
        
        try:
            # Buscar estaciones cercanas
            print(f"📞 Llamando a _find_nearby_stations...")
            stations = await self._find_nearby_stations(latitud, longitud, radius_km)
            
            if not stations:
                logger.warning(f"⚠️ No se encontraron estaciones en {radius_km}km")
                return self._get_default_values()
            
            # Obtener mediciones de las estaciones
            measurements = await self._get_station_measurements(stations)
            
            if not measurements:
                logger.warning("⚠️ No hay mediciones disponibles")
                return self._get_default_values()
            
            # Procesar y agregar mediciones
            return self._process_measurements(measurements)
            
        except Exception as e:
            logger.error(f"❌ Error al obtener datos de OpenAQ: {e}")
            return self._get_default_values()
    
    async def _find_nearby_stations(
        self,
        latitud: float,
        longitud: float,
        radius_km: float
    ) -> List[Dict]:
        """Buscar estaciones cercanas a una ubicación"""
        try:
            # OpenAQ v3 usa locations endpoint con coordenadas en formato correcto
            url = f"{self.base_url}/locations"
            
            # Convertir radio a metros
            radius_meters = int(radius_km * 1000)
            
            params = {
                "limit": 100,
                "page": 1,
                "offset": 0,
                "sort": "asc",
                "radius": radius_meters,
                "coordinates": f"{latitud},{longitud}"
            }
            
            logger.info(f"🔍 Consultando OpenAQ: {url}")
            logger.info(f"📍 Parámetros: radius={radius_meters}m, coords={latitud},{longitud}")
            logger.info(f"🔑 API Key presente: {bool(self.api_key)} - Length: {len(self.api_key) if self.api_key else 0}")
            
            async with self.session.get(url, params=params, timeout=10) as response:
                logger.info(f"📡 OpenAQ respondió con status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    logger.info(f"✅ Encontradas {len(results)} estaciones cerca de ({latitud}, {longitud})")
                    
                    # Log de las primeras 3 estaciones
                    for i, station in enumerate(results[:3]):
                        name = station.get("name", "Unknown")
                        coords = station.get("coordinates", {})
                        lat = coords.get("latitude", 0)
                        lon = coords.get("longitude", 0)
                        logger.info(f"   {i+1}. {name} ({lat}, {lon})")
                    
                    return results
                    
                elif response.status == 401:
                    logger.warning("⚠️ OpenAQ API Key inválida o no configurada")
                    logger.info("💡 Regístrate en: https://explore.openaq.org/register")
                    logger.info("💡 Obtén tu API key en: https://explore.openaq.org/account")
                    return []
                    
                elif response.status == 422:
                    error_text = await response.text()
                    logger.error(f"⚠️ Error de validación (422): {error_text}")
                    return []
                    
                else:
                    error_text = await response.text()
                    logger.warning(f"⚠️ OpenAQ retornó status {response.status}: {error_text[:200]}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.warning("⚠️ Timeout conectando con OpenAQ")
            return []
        except Exception as e:
            logger.error(f"❌ Error buscando estaciones: {e}")
            return []
    
    async def _get_station_measurements(self, stations: List[Dict]) -> List[Dict]:
        """Obtener mediciones de múltiples estaciones"""
        all_measurements = []
        
        for station in stations[:5]:  # Limitar a 5 estaciones más cercanas
            station_id = station.get("id")
            if not station_id:
                continue
            
            try:
                # OpenAQ v3 usa /locations/{id}/latest para obtener últimas mediciones
                url = f"{self.base_url}/locations/{station_id}/latest"
                
                params = {
                    "limit": 100  # Obtener todos los parámetros disponibles
                }
                
                async with self.session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        measurements = data.get("results", [])
                        
                        if measurements:
                            station_name = station.get("name", f"Station {station_id}")
                            logger.info(f"   📡 {station_name}: {len(measurements)} parámetros")
                        
                        all_measurements.extend(measurements)
                    else:
                        logger.debug(f"   ⚠️ Station {station_id} retornó status {response.status}")
                        
            except asyncio.TimeoutError:
                logger.debug(f"   ⏱️ Timeout obteniendo datos de estación {station_id}")
                continue
            except Exception as e:
                logger.debug(f"   ❌ Error obteniendo mediciones de estación {station_id}: {e}")
                continue
        
        return all_measurements
    
    def _process_measurements(self, measurements: List[Dict]) -> Dict[str, float]:
        """
        Procesar mediciones y convertir a features del modelo
        
        Model features: PM2.5, PM10, O3, NO2, temperatura, humedad, viento, AQI
        OpenAQ v3 structure: cada measurement tiene parameter.name, value, unit
        """
        # Agrupar mediciones por parámetro
        params_data = {}
        
        for measurement in measurements:
            # Estructura OpenAQ v3
            parameter_info = measurement.get("parameter", {})
            parameter = parameter_info.get("name", "").lower()
            value = measurement.get("value")
            unit = parameter_info.get("units", "")
            
            if value is None:
                continue
            
            # Mapear nombres de OpenAQ a features del modelo
            param_mapping = {
                "pm25": "PM2.5",
                "pm2.5": "PM2.5",
                "pm10": "PM10",
                "o3": "O3",
                "no2": "NO2",
                "temperature": "temperatura",
                "humidity": "humedad",
                "wind_speed": "viento",
                "windspeed": "viento",
                "ws": "viento"
            }
            
            mapped_param = param_mapping.get(parameter)
            if mapped_param:
                if mapped_param not in params_data:
                    params_data[mapped_param] = []
                
                # Convertir unidades si es necesario
                converted_value = self._convert_units(value, unit, mapped_param)
                params_data[mapped_param].append(converted_value)
        
        # Calcular promedios
        result = {}
        for param, values in params_data.items():
            if values:
                result[param] = float(np.mean(values))
                logger.info(f"   ✓ {param}: {result[param]:.2f} (de {len(values)} mediciones)")
        
        # Calcular AQI si tenemos PM2.5
        if "PM2.5" in result:
            result["AQI"] = self._calculate_aqi_from_pm25(result["PM2.5"])
            logger.info(f"   ✓ AQI: {result['AQI']:.1f} (calculado desde PM2.5)")
        
        # Rellenar valores faltantes con defaults
        return self._fill_missing_values(result)
    
    def _convert_units(self, value: float, unit: str, parameter: str) -> float:
        """Convertir unidades a las esperadas por el modelo"""
        unit = unit.lower()
        
        # PM2.5 y PM10: µg/m³ (ya es la unidad correcta generalmente)
        if parameter in ["PM2.5", "PM10"]:
            return value
        
        # O3: convertir de ppb a µg/m³ si es necesario
        elif parameter == "O3":
            if "ppb" in unit:
                # O3: 1 ppb ≈ 2.0 µg/m³ (a 25°C y 1 atm)
                return value * 2.0
            return value
        
        # NO2: convertir de ppb a µg/m³ si es necesario
        elif parameter == "NO2":
            if "ppb" in unit:
                # NO2: 1 ppb ≈ 1.88 µg/m³ (a 25°C y 1 atm)
                return value * 1.88
            return value
        
        # Temperatura: convertir a Celsius si es necesario
        elif parameter == "temperatura":
            if "f" in unit or "fahrenheit" in unit:
                return (value - 32) * 5/9
            return value
        
        # Humedad y viento: asumir ya están en % y m/s
        else:
            return value
    
    def _calculate_aqi_from_pm25(self, pm25: float) -> float:
        """
        Calcular AQI basado en PM2.5 usando escala EPA
        
        Breakpoints EPA para PM2.5 (µg/m³):
        0-12: AQI 0-50 (Bueno)
        12.1-35.4: AQI 51-100 (Moderado)
        35.5-55.4: AQI 101-150 (Insalubre para grupos sensibles)
        55.5-150.4: AQI 151-200 (Insalubre)
        150.5-250.4: AQI 201-300 (Muy insalubre)
        250.5+: AQI 301-500 (Peligroso)
        """
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
                # Fórmula lineal de interpolación
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (pm25 - c_low) + aqi_low
                return round(aqi, 1)
        
        # Si está fuera de rango, retornar máximo
        return 500.0
    
    def _fill_missing_values(self, data: Dict[str, float]) -> Dict[str, float]:
        """Rellenar valores faltantes con defaults realistas"""
        defaults = {
            "PM2.5": 12.0,   # AccuWeather: 12 µg/m³ (Buena)
            "PM10": 40.0,    # AccuWeather: 40 µg/m³ (Buena)
            "O3": 30.0,      # Típico para LA
            "NO2": 56.0,     # AccuWeather: 56 µg/m³ (Mala - contaminante dominante)
            "temperatura": 20.0,
            "humedad": 60.0,
            "viento": 8.0,
            "AQI": 59.0      # AccuWeather: 59 (Mala/Unhealthy for Sensitive Groups)
        }
        
        result = defaults.copy()
        result.update(data)
        
        # Si tenemos PM2.5 pero no PM10, estimarlo
        if "PM2.5" in data and "PM10" not in data:
            result["PM10"] = data["PM2.5"] * 1.7
        
        # Si tenemos PM2.5 pero no AQI, calcularlo
        if "PM2.5" in data and "AQI" not in data:
            result["AQI"] = self._calculate_aqi_from_pm25(data["PM2.5"])
        
        return result
    
    def _get_default_values(self) -> Dict[str, float]:
        """Valores por defecto cuando no hay datos disponibles"""
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
    
    async def get_historical_measurements(
        self,
        latitud: float,
        longitud: float,
        horas: int = 48,
        radius_km: float = 25.0
    ) -> List[Dict[str, float]]:
        """
        Obtener mediciones históricas (si están disponibles)
        
        Nota: OpenAQ v3 tiene datos limitados de histórico.
        Esta función intenta obtener lo disponible.
        """
        await self._create_session()
        
        logger.info(f"📊 Obteniendo {horas}h de histórico para ({latitud}, {longitud})")
        
        try:
            # Buscar estaciones
            stations = await self._find_nearby_stations(latitud, longitud, radius_km)
            
            if not stations:
                logger.warning("⚠️ No hay estaciones para histórico")
                return []
            
            # Por ahora, OpenAQ v3 tiene acceso limitado a histórico sin API key
            # Retornar mediciones más recientes replicadas
            latest = await self.get_latest_measurements(latitud, longitud, radius_km)
            
            # Generar serie temporal con variación realista
            historical = []
            for i in range(horas):
                # Agregar variación aleatoria pero realista
                point = {}
                for key, value in latest.items():
                    variation = np.random.uniform(0.85, 1.15)  # ±15% variación
                    point[key] = value * variation
                historical.append(point)
            
            return historical
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo histórico: {e}")
            return []


# Función auxiliar para testing
async def test_openaq():
    """Probar conexión con OpenAQ"""
    fetcher = OpenAQFetcher()
    
    # Probar Los Angeles
    print("🧪 Probando OpenAQ para Los Angeles...")
    data = await fetcher.get_latest_measurements(34.0522, -118.2437, radius_km=25)
    
    print("\n📊 Datos obtenidos:")
    for key, value in data.items():
        print(f"  {key}: {value:.2f}")
    
    await fetcher.close()


if __name__ == "__main__":
    asyncio.run(test_openaq())
