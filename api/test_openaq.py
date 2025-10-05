"""
Script de prueba para verificar datos de OpenAQ
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio api al path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from utils.openaq_fetcher import OpenAQFetcher

async def test_openaq():
    """Probar obtención de datos de OpenAQ"""
    fetcher = OpenAQFetcher()
    
    print("🧪 PRUEBA DE OPENAQ API")
    print("=" * 60)
    
    # Los Angeles
    lat, lon = 34.0522, -118.2437
    
    print(f"\n📍 Ubicación: Los Angeles ({lat}, {lon})")
    print("\n⏳ Obteniendo datos...")
    
    datos = await fetcher.get_latest_measurements(lat, lon, radius_km=25.0)
    
    print("\n📊 DATOS RECIBIDOS:")
    print("-" * 60)
    for key, value in datos.items():
        print(f"   {key:15s}: {value}")
    
    print("\n" + "=" * 60)
    
    # Verificar si son datos reales o por defecto
    if datos.get("PM2.5") == 12.0 and datos.get("NO2") == 56.0:
        print("⚠️  DATOS POR DEFECTO (OpenAQ no tiene datos completos)")
    else:
        print("✅ DATOS REALES DE OPENAQ")
    
    await fetcher.close()

if __name__ == "__main__":
    asyncio.run(test_openaq())
