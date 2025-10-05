# 🔑 Cómo Obtener y Configurar tu OpenAQ API Key

## ¿Por qué necesitas una API Key?

OpenAQ API v3 requiere autenticación para acceder a datos en tiempo real de calidad del aire de más de 15,000 estaciones mundiales. Sin API key, la aplicación usará datos simulados.

## 📝 Paso 1: Registrarse en OpenAQ

1. Visita: **https://explore.openaq.org/register**
2. Completa el formulario de registro:
   - Nombre
   - Email
   - Contraseña
   - Acepta los términos de servicio
3. Verifica tu email (revisa spam/correo no deseado)

## 🔐 Paso 2: Obtener tu API Key

1. Inicia sesión en: **https://explore.openaq.org/login**
2. Ve a tu perfil: **https://explore.openaq.org/account**
3. En la sección "API Keys", haz clic en **"Generate New Key"**
4. Copia la API key generada (⚠️ solo se muestra una vez)

## ⚙️ Paso 3: Configurar la API Key

### Método 1: Archivo .env (Recomendado)

1. Abre el archivo `.env` en la carpeta `api/`:
   ```
   c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\.env
   ```

2. Busca la línea:
   ```env
   OPENAQ_API_KEY=''
   ```

3. Pega tu API key entre las comillas:
   ```env
   OPENAQ_API_KEY='tu-api-key-aqui-1234567890abcdef'
   ```

4. Guarda el archivo

### Método 2: Variable de Entorno del Sistema

En PowerShell:
```powershell
$env:OPENAQ_API_KEY="tu-api-key-aqui-1234567890abcdef"
```

En CMD:
```cmd
set OPENAQ_API_KEY=tu-api-key-aqui-1234567890abcdef
```

⚠️ Nota: Este método es temporal y se pierde al cerrar la terminal.

## ✅ Paso 4: Verificar la Configuración

### Opción A: Probar el Fetcher Directamente
```powershell
cd "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\utils"
python openaq_fetcher.py
```

**Salida esperada CON API key:**
```
🧪 Probando OpenAQ para Los Angeles...
🔑 Usando OpenAQ API Key
✅ Encontradas X estaciones

📊 Datos obtenidos:
  PM2.5: 18.50
  PM10: 31.40
  O3: 45.20
  NO2: 28.70
  temperatura: 22.30
  humedad: 55.00
  viento: 8.50
  AQI: 65.30
```

**Salida esperada SIN API key:**
```
🧪 Probando OpenAQ para Los Angeles...
⚠️ No se encontró OpenAQ API Key - funcionalidad limitada
⚠️ OpenAQ API Key inválida o no configurada
💡 Regístrate en: https://explore.openaq.org/register

📊 Datos obtenidos:
  PM2.5: 25.00  ← Valores por defecto simulados
  PM10: 40.00
  ...
```

### Opción B: Probar la API Completa
```powershell
# 1. Iniciar la API
python "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\run_prod.py"

# 2. En otra terminal, ejecutar pruebas
& "c:\Users\anton\Desktop\2ºGS\HACKATON_NASA\api\probar_api.ps1" -Test all
```

Revisa el campo `fuente_datos` en la respuesta:
- **"OpenAQ (tiempo real)"** ✅ = API key funciona
- **"simulado"** ⚠️ = Usando datos simulados

## 🌍 Cobertura de OpenAQ

### Países con Mejor Cobertura:
- 🇺🇸 **Estados Unidos**: +1,000 estaciones
- 🇪🇺 **Unión Europea**: +2,000 estaciones
- 🇮🇳 **India**: +500 estaciones
- 🇨🇳 **China**: +400 estaciones
- 🇲🇽 **México**: +50 estaciones

### Ciudades del Modelo con Estaciones OpenAQ:
| Ciudad | Estaciones | Cobertura |
|--------|-----------|-----------|
| Los Angeles | ✅ Alta | +30 estaciones |
| New York | ✅ Alta | +20 estaciones |
| Chicago | ✅ Media | +15 estaciones |
| Houston | ✅ Media | +10 estaciones |
| Phoenix | ✅ Baja | +5 estaciones |
| San Diego | ✅ Media | +8 estaciones |

## 🔧 Troubleshooting

### Problema: "401 Unauthorized"
**Causa**: API key inválida o no configurada

**Solución**:
1. Verifica que copiaste la key completa (sin espacios)
2. Asegúrate de que está entre comillas en el .env
3. Reinicia la API después de configurar la key

### Problema: "No se encontraron estaciones"
**Causa**: No hay estaciones OpenAQ en el área

**Solución**:
1. La API automáticamente usará datos simulados
2. Verifica cobertura en: https://explore.openaq.org/map
3. Aumenta el radio de búsqueda (default: 25km)

### Problema: "Timeout"
**Causa**: Problemas de conectividad

**Solución**:
1. Verifica tu conexión a internet
2. La API tiene timeout de 5 segundos
3. Usará datos simulados como fallback

## 📊 Datos Disponibles por Parámetro

OpenAQ proporciona (cuando están disponibles):

| Parámetro | Unidad | Descripción |
|-----------|--------|-------------|
| pm25 | µg/m³ | Partículas finas |
| pm10 | µg/m³ | Partículas gruesas |
| o3 | µg/m³ o ppb | Ozono troposférico |
| no2 | µg/m³ o ppb | Dióxido de nitrógeno |
| so2 | µg/m³ o ppb | Dióxido de azufre |
| co | mg/m³ o ppm | Monóxido de carbono |
| temperature | °C | Temperatura |
| humidity | % | Humedad relativa |
| wind_speed | m/s | Velocidad del viento |

La API convierte automáticamente las unidades al formato esperado por el modelo.

## 💰 Límites y Costos

### Plan Gratuito:
- ✅ **10,000 requests/mes**
- ✅ Acceso a datos en tiempo real
- ✅ Acceso a históricos limitados
- ✅ Sin tarjeta de crédito requerida

### Plan Pro (Futuro):
- 📈 100,000+ requests/mes
- 📊 Acceso completo a históricos
- 🚀 Prioridad en respuestas
- 💼 Para uso comercial

## 🔒 Seguridad

### ⚠️ NO COMPARTAS TU API KEY:
- ❌ No la subas a GitHub
- ❌ No la pongas en código público
- ❌ No la compartas en screenshots
- ✅ Mantenla en el archivo .env (ya está en .gitignore)

### Si comprometes tu API key:
1. Ve a https://explore.openaq.org/account
2. Revoca la key comprometida
3. Genera una nueva
4. Actualiza tu .env

## 📚 Recursos Adicionales

- **Documentación OpenAQ**: https://docs.openaq.org/
- **Explorador de Datos**: https://explore.openaq.org/
- **API Reference**: https://docs.openaq.org/reference/
- **Status de la API**: https://status.openaq.org/

## 🎯 Próximos Pasos

Una vez configurada la API key:

1. ✅ Reinicia la API de predicción
2. ✅ Ejecuta las pruebas para verificar datos reales
3. ✅ Revisa el dashboard en http://localhost:8000/docs
4. ✅ Integra con tu frontend Next.js
5. ✅ Monitorea el uso en tu panel de OpenAQ

---

**¿Necesitas ayuda?**  
Consulta la documentación completa en `README_ACTUALIZADO.md`
