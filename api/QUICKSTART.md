# 🚀 GUÍA DE INICIO RÁPIDO

## ⚡ Instalación en 3 pasos

### 1️⃣ Instalar dependencias

```powershell
cd c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2️⃣ Configurar variables de entorno

```powershell
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env (opcional - funciona con valores por defecto)
notepad .env
```

### 3️⃣ Iniciar el servidor

```powershell
# Opción 1: Usar el script de inicio
.\start.ps1

# Opción 2: Ejecutar directamente
python main.py
```

✅ **Listo!** La API estará disponible en: http://localhost:8000

---

## 📖 Ver documentación interactiva

Abre en tu navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Probar la API

### Opción 1: Con el script de test

```powershell
python test_api.py
```

### Opción 2: Con cURL

```powershell
# Health check
curl http://localhost:8000/health

# Predicción
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{\"latitud\": 34.0522, \"longitud\": -118.2437, \"nombre_ubicacion\": \"Los Angeles\"}'
```

### Opción 3: Desde el navegador

```
http://localhost:8000/predict/coordinates?lat=34.0522&lon=-118.2437&name=Los%20Angeles
```

---

## 🔗 Conectar con Next.js

### 1. Copiar el cliente JavaScript

```bash
cp cliente_ejemplo.js ../tu-proyecto-nextjs/lib/api-client.js
```

### 2. Configurar variables de entorno en Next.js

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Usar en tu componente

```jsx
import { predictAQI } from '@/lib/api-client';

// En tu componente
const resultado = await predictAQI(34.0522, -118.2437, 'Los Angeles');
console.log(resultado);
```

---

## 📊 Endpoints disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado de la API |
| GET | `/model/info` | Info del modelo |
| POST | `/predict` | Predicción (JSON) |
| GET | `/predict/coordinates` | Predicción (query params) |
| GET | `/predict/city/{name}` | Ciudades predefinidas |

---

## 🐛 Solución de problemas

### Error: "Modelo no encontrado"

```powershell
# Verificar que existe el modelo
dir ..\modelos_guardados\*.keras
```

Si no existe, ejecuta el notebook `TEMPO.ipynb` y exporta el modelo.

### Error: "Module not found"

```powershell
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Puerto 8000 ocupado

Edita `main.py` y cambia:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Cambiar puerto
```

---

## 📚 Documentación completa

Lee el archivo `README.md` para información detallada sobre:
- Arquitectura de la API
- Ejemplos de integración con Next.js
- Clasificación de AQI
- Configuración avanzada

---

## 🎯 Próximos pasos

1. ✅ Iniciar la API
2. ✅ Probar con test_api.py
3. ✅ Conectar desde Next.js
4. 📊 Crear tu interfaz de visualización
5. 🚀 Desplegar en producción

---

**¡Listo para usar!** 🎉

Si tienes problemas, revisa los logs en la consola o consulta el README.md
