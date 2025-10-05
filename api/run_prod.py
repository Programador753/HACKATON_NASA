"""Script de inicio simple sin auto-reload"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando API en modo producción (sin auto-reload)...")
    print("📍 La API estará disponible en: http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    print("\n⚠️  Presiona CTRL+C para detener el servidor\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Sin reload para producción
        log_level="info"
    )
