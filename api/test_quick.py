"""Script rápido para probar la API"""
import requests
import time

# Esperar un momento para que la API esté lista
time.sleep(2)

try:
    # Probar endpoint de health
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Health check: {response.status_code}")
    print(response.json())
    
    # Probar endpoint de info del modelo
    response = requests.get("http://localhost:8000/model/info")
    print(f"\n✅ Model info: {response.status_code}")
    print(response.json())
    
except Exception as e:
    print(f"❌ Error: {e}")
