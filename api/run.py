"""Script de inicio robusto para la API"""
import uvicorn
import sys
from pathlib import Path

# Asegurarnos de que estamos en el directorio correcto
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
