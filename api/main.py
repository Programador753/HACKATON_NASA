"""
API FastAPI para predicción de AQI usando modelo LSTM con Attention
Permite realizar predicciones de calidad del aire basadas en ubicación geográfica
"""

from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import logging

from utils.predictor import AQIPredictor
from models.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    HealthStatus,
    ModelInfo
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler('api_debug.log', mode='a', encoding='utf-8')  # File (append mode)
    ]
)

# Silenciar logs de watchfiles (auto-reload)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("="*80)
logger.info("SERVIDOR INICIANDO - Nueva sesión")
logger.info("="*80)

# Crear aplicación FastAPI
app = FastAPI(
    title="AQI Prediction API",
    description="API para predicción de índice de calidad del aire usando datos TEMPO NASA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development
        "http://localhost:3001",
        "https://tu-dominio.com",  # Tu dominio en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar predictor (se carga el modelo al iniciar la API)
predictor: Optional[AQIPredictor] = None


@app.on_event("startup")
async def startup_event():
    """Cargar modelo al iniciar la aplicación"""
    global predictor
    try:
        logger.info("🚀 Iniciando API de predicción AQI...")
        predictor = AQIPredictor()
        logger.info("✅ Modelo cargado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar el modelo: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    logger.info("👋 Cerrando API...")


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz - Verificar que la API está funcionando"""
    return {
        "message": "AQI Prediction API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Verificar el estado de salud de la API y el modelo"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    return HealthStatus(
        status="healthy",
        model_loaded=predictor.is_loaded(),
        timestamp=datetime.now()
    )


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info():
    """Obtener información sobre el modelo cargado"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    return predictor.get_model_info()


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_aqi(request: PredictionRequest):
    """
    Realizar predicción de AQI para una ubicación específica
    
    Args:
        request: Objeto con latitud, longitud y parámetros opcionales
        
    Returns:
        Predicciones de AQI para diferentes horizontes temporales (3h, 6h, 12h, 24h)
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        logger.info(f"📍 Predicción solicitada para: ({request.latitud}, {request.longitud})")
        
        # Realizar predicción
        resultado = await predictor.predict(
            latitud=request.latitud,
            longitud=request.longitud,
            location_name=request.nombre_ubicacion
        )
        
        logger.info(f"✅ Predicción completada para {request.nombre_ubicacion or 'ubicación'}")
        return resultado
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al realizar predicción: {str(e)}")


@app.get("/predict/coordinates", response_model=PredictionResponse, tags=["Prediction"])
async def predict_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)"),
    name: Optional[str] = Query(None, description="Nombre de la ubicación (opcional)")
):
    """
    Realizar predicción usando parámetros de query (GET request)
    Útil para requests simples desde el navegador
    
    Ejemplo: /predict/coordinates?lat=34.0522&lon=-118.2437&name=Los Angeles
    """
    request = PredictionRequest(
        latitud=lat,
        longitud=lon,
        nombre_ubicacion=name
    )
    return await predict_aqi(request)


@app.get("/predict/city/{city_name}", response_model=PredictionResponse, tags=["Prediction"])
async def predict_by_city(city_name: str):
    """
    Realizar predicción para ciudades predefinidas de Estados Unidos
    
    Ciudades disponibles:
    - los-angeles (Ciudad de entrenamiento del modelo)
    - new-york
    - chicago
    - houston
    - phoenix
    - philadelphia
    - san-antonio
    - san-diego
    - dallas
    - san-francisco
    """
    # Diccionario de ciudades predefinidas (solo Estados Unidos)
    cities = {
        "los-angeles": {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles, CA"},
        "new-york": {"lat": 40.7128, "lon": -74.0060, "name": "New York, NY"},
        "chicago": {"lat": 41.8781, "lon": -87.6298, "name": "Chicago, IL"},
        "houston": {"lat": 29.7604, "lon": -95.3698, "name": "Houston, TX"},
        "phoenix": {"lat": 33.4484, "lon": -112.0740, "name": "Phoenix, AZ"},
        "philadelphia": {"lat": 39.9526, "lon": -75.1652, "name": "Philadelphia, PA"},
        "san-antonio": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio, TX"},
        "san-diego": {"lat": 32.7157, "lon": -117.1611, "name": "San Diego, CA"},
        "dallas": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas, TX"},
        "san-francisco": {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco, CA"},
        "miami": {"lat": 25.7617, "lon": -80.1918, "name": "Miami, FL"},
    }
    
    city_name_lower = city_name.lower()
    if city_name_lower not in cities:
        raise HTTPException(
            status_code=404, 
            detail=f"Ciudad '{city_name}' no encontrada. Disponibles: {list(cities.keys())}"
        )
    
    city = cities[city_name_lower]
    request = PredictionRequest(
        latitud=city["lat"],
        longitud=city["lon"],
        nombre_ubicacion=city["name"]
    )
    return await predict_aqi(request)


@app.get("/cities/coverage", tags=["Cities"])
async def check_cities_coverage():
    """
    Verificar cobertura de OpenAQ para todas las ciudades predefinidas
    Útil para saber qué ciudades tienen datos reales vs estimados
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor no disponible")
    
    cities = {
        "los-angeles": {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles, CA"},
        "new-york": {"lat": 40.7128, "lon": -74.0060, "name": "New York, NY"},
        "chicago": {"lat": 41.8781, "lon": -87.6298, "name": "Chicago, IL"},
        "houston": {"lat": 29.7604, "lon": -95.3698, "name": "Houston, TX"},
        "phoenix": {"lat": 33.4484, "lon": -112.0740, "name": "Phoenix, AZ"},
        "philadelphia": {"lat": 39.9526, "lon": -75.1652, "name": "Philadelphia, PA"},
        "san-antonio": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio, TX"},
        "san-diego": {"lat": 32.7157, "lon": -117.1611, "name": "San Diego, CA"},
        "dallas": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas, TX"},
        "san-francisco": {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco, CA"},
        "miami": {"lat": 25.7617, "lon": -80.1918, "name": "Miami, FL"},
    }
    
    coverage_info = []
    
    for city_slug, city_data in cities.items():
        try:
            # Buscar estaciones cercanas
            stations = await predictor.openaq_fetcher._find_nearby_stations(
                city_data["lat"], 
                city_data["lon"], 
                radius_km=50.0
            )
            
            has_coverage = len(stations) > 0
            
            coverage_info.append({
                "slug": city_slug,
                "name": city_data["name"],
                "coordinates": {"lat": city_data["lat"], "lon": city_data["lon"]},
                "has_real_data": has_coverage,
                "stations_nearby": len(stations),
                "status": "✅ Datos reales disponibles" if has_coverage else "⚠️ Usando estimaciones"
            })
            
        except Exception as e:
            coverage_info.append({
                "slug": city_slug,
                "name": city_data["name"],
                "coordinates": {"lat": city_data["lat"], "lon": city_data["lon"]},
                "has_real_data": False,
                "stations_nearby": 0,
                "status": f"❌ Error: {str(e)[:50]}"
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_cities": len(cities),
        "cities_with_data": sum(1 for c in coverage_info if c["has_real_data"]),
        "cities": coverage_info
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )
