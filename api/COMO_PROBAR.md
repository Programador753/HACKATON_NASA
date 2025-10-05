# 📋 RESUMEN: Cómo Probar la API

## ✅ Estado Actual

La API está **funcionando** en el puerto 8000. Ya se han realizado pruebas exitosas de:
- ✅ Health check
- ✅ Model info

## ⚠️ Problema Actual

El modelo fue entrenado con estas 8 features:
1. PM2.5
2. PM10
3. O3
4. NO2
5. temperatura
6. humedad
7. viento
8. AQI

Los archivos de configuración ya han sido actualizados para usar estas features correctas.

## 🔄 Pasos para Aplicar los Cambios

### 1. Detener la API actual
Presiona `CTRL+C` en la terminal donde está corriendo la API

### 2. Reiniciar la API
Ejecuta uno de estos comandos:

```powershell
# Opción 1: Script dedicado
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\iniciar_api.ps1"

# Opción 2: Manualmente
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api"
python run_prod.py
```

### 3. Probar los Endpoints

Una vez que la API esté corriendo (espera ~15-20 segundos para que cargue):

```powershell
# Probar TODOS los endpoints
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test all

# O probarlos individualmente:
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test health
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test info
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test get
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test post
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test city
```

## 🌐 Usar la Interfaz Web Interactiva

La forma MÁS FÁCIL de probar la API es usando la documentación interactiva:

1. Inicia la API
2. Abre tu navegador en: **http://localhost:8000/docs**
3. Verás una interfaz gráfica donde puedes:
   - Ver todos los endpoints disponibles
   - Probar cada endpoint con botones "Try it out"
   - Ver las respuestas en tiempo real
   - Ver los esquemas de datos

## 📝 Ejemplos de Peticiones Manuales

### Health Check (GET)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

### Info del Modelo (GET)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/model/info"
```

### Predicción con GET
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/coordinates?lat=40.4168&lon=-3.7038&location_name=Madrid"
```

### Predicción con POST
```powershell
$body = @{
    latitud = 41.3851
    longitud = 2.1734
    nombre_ubicacion = "Barcelona"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
```

### Predicción para Ciudad Predefinida
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/city/paris"
```

## 🎯 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado de la API |
| `/model/info` | GET | Información del modelo |
| `/predict` | POST | Predicción (JSON body) |
| `/predict/coordinates` | GET | Predicción (query params) |
| `/predict/city/{name}` | GET | Ciudades predefinidas |
| `/docs` | GET | Documentación interactiva |
| `/redoc` | GET | Documentación alternativa |

## 🔍 Verificar que Todo Funciona

Ejecuta:
```powershell
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test all
```

Deberías ver respuestas exitosas con predicciones de AQI para diferentes horizontes temporales (3h, 6h, 12h, 24h).

## 📞 Archivos de Ayuda Creados

- `iniciar_api.ps1` - Inicia la API en una nueva ventana
- `probar_api.ps1` - Script de pruebas automáticas
- `GUIA_INICIO.md` - Guía completa de inicio
- `run_prod.py` - Script de inicio en modo producción
- `test_peticiones.ps1` - Otro script de pruebas

## ✨ Próximo Paso

**AHORA MISMO**: Detén la API actual (CTRL+C) y reiníciala para aplicar los cambios de configuración.
