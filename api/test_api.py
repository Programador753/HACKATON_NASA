"""
Script de prueba para verificar que la API funciona correctamente
Ejecutar: python test_api.py
"""

import requests
import json
from datetime import datetime

# URL base de la API
API_URL = "http://localhost:8000"

def print_section(title):
    """Imprimir sección con formato"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_health():
    """Test 1: Health check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API está saludable")
            print(f"   - Estado: {data['status']}")
            print(f"   - Modelo cargado: {data['model_loaded']}")
            print(f"   - Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("   ¿Está la API ejecutándose en http://localhost:8000?")
        return False

def test_model_info():
    """Test 2: Información del modelo"""
    print_section("TEST 2: Información del Modelo")
    
    try:
        response = requests.get(f"{API_URL}/model/info")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Información del modelo obtenida")
            print(f"   - Nombre: {data['nombre_modelo']}")
            print(f"   - Arquitectura: {data['arquitectura']}")
            print(f"   - Parámetros: {data['parametros_totales']:,}")
            print(f"   - Features: {len(data['features_entrada'])} features")
            print(f"   - Horizontes: {data['horizontes_prediccion']}")
            print(f"   - Lookback: {data['lookback_horas']} horas")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_prediction_post():
    """Test 3: Predicción con POST"""
    print_section("TEST 3: Predicción (POST)")
    
    payload = {
        "latitud": 34.0522,
        "longitud": -118.2437,
        "nombre_ubicacion": "Los Angeles, CA"
    }
    
    try:
        print(f"📤 Enviando request: {payload}")
        
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa")
            print(f"\n📍 Ubicación: {data['nombre_ubicacion']}")
            print(f"   Coordenadas: ({data['ubicacion']['latitud']}, {data['ubicacion']['longitud']})")
            
            if data.get('aqi_actual_estimado'):
                print(f"   AQI Actual: {data['aqi_actual_estimado']}")
            
            print(f"\n🔮 Predicciones:")
            for pred in data['predicciones']:
                print(f"   {pred['horizonte']:>4s}: AQI {pred['aqi_predicho']:>6.2f} - {pred['calidad']:<12s} {pred['color']}")
            
            if data.get('advertencias'):
                print(f"\n⚠️  Advertencias:")
                for adv in data['advertencias']:
                    print(f"   - {adv}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_prediction_get():
    """Test 4: Predicción con GET (query params)"""
    print_section("TEST 4: Predicción (GET con query params)")
    
    try:
        params = {
            "lat": 40.7128,
            "lon": -74.0060,
            "name": "New York, NY"
        }
        
        print(f"📤 Enviando request con params: {params}")
        
        response = requests.get(f"{API_URL}/predict/coordinates", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa")
            print(f"📍 {data['nombre_ubicacion']}")
            print(f"🔮 Predicciones para {len(data['predicciones'])} horizontes")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_city_prediction():
    """Test 5: Predicción por ciudad predefinida"""
    print_section("TEST 5: Predicción por Ciudad Predefinida")
    
    try:
        city = "los-angeles"
        print(f"📤 Solicitando predicción para: {city}")
        
        response = requests.get(f"{API_URL}/predict/city/{city}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa")
            print(f"📍 {data['nombre_ubicacion']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "🧪" * 40)
    print("  TEST SUITE - API de Predicción AQI")
    print("🧪" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Prediction POST", test_prediction_post),
        ("Prediction GET", test_prediction_get),
        ("City Prediction", test_city_prediction),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrumpidos por el usuario")
            break
    
    # Resumen
    print_section("RESUMEN DE TESTS")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n  Total: {total} | Pasados: {passed} | Fallidos: {failed}")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print(f"\n⚠️  {failed} test(s) fallaron")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    run_all_tests()
