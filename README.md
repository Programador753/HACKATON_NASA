# 🛰️ Sistema de Predicción de Calidad del Aire - NASA TEMPO + LSTM

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange.svg)
![NASA](https://img.shields.io/badge/NASA-TEMPO-red.svg)
![License](https://img.shields.io/badge/License-Educational-green.svg)

## 🌟 ¿Qué es este proyecto?

Sistema de **predicción de calidad del aire** que combina:
- 🛰️ **NASA TEMPO**: Datos satelitales de contaminación atmosférica en tiempo real
- 🧠 **LSTM (Deep Learning)**: Redes neuronales para predicción de series temporales
- 📊 **Predicciones a 3, 6, 12 y 24 horas**: Planifica tu día según la calidad del aire

### 💡 Caso de uso real:
**"¿Es mejor salir a correr ahora o en 6 horas?"**  
→ El sistema te dice cuándo el aire estará más limpio

---

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Abrir el notebook

```bash
jupyter notebook PRUEBAS.ipynb
```

### 3. Ejecutar todas las celdas

El notebook está completamente documentado y listo para ejecutar. Por defecto usa datos simulados de TEMPO.

---

## 📂 Estructura del Proyecto

```
HACKATON_NASA/
├── 📓 PRUEBAS.ipynb              # Notebook principal (¡EMPIEZA AQUÍ!)
├── 📄 README.md                  # Este archivo
├── 📄 README_TEMPO.md            # Documentación detallada
├── ⚙️ config_ejemplo.py          # Configuración del sistema
├── 🐍 prediccion_cli.py          # Script de línea de comandos
├── 📦 requirements.txt           # Dependencias de Python
└── 📁 modelos/                   # Modelos entrenados (se crea al entrenar)
```

---

## 🎯 Características Principales

### 🛰️ Integración con NASA TEMPO
- Acceso a datos satelitales de calidad del aire
- Cobertura de toda Norteamérica
- Resolución horaria
- Múltiples contaminantes: NO₂, O₃, PM2.5, PM10

### 🧠 Modelo LSTM
- Arquitectura Bidirectional LSTM profunda
- Predicción multi-horizonte (3, 6, 12, 24 horas)
- Entrenamiento con early stopping
- Métricas: MAE ~5-8 AQI a 3h, ~15-20 AQI a 24h

### 📊 Sistema Completo
- Visualizaciones interactivas
- Sistema de alertas automático
- Recomendaciones personalizadas
- Informe diario

---

## 🌍 Ubicaciones Soportadas

TEMPO cubre **Norteamérica**:

| Ciudad | Código |
|--------|--------|
| 🇲🇽 Ciudad de México | `(19.4326, -99.1332)` |
| 🇺🇸 Los Ángeles | `(34.0522, -118.2437)` |
| 🇺🇸 Nueva York | `(40.7128, -74.0060)` |
| 🇨🇦 Toronto | `(43.6532, -79.3832)` |
| 🇲🇽 Monterrey | `(25.6866, -100.3161)` |

---

## 📖 Documentación Completa

Ver **[README_TEMPO.md](README_TEMPO.md)** para:
- Guía detallada de uso
- Cómo obtener datos reales de TEMPO
- API de producción
- Despliegue en la nube
- Y mucho más...

---

## 🔧 Configuración Avanzada

### Usar datos reales de TEMPO

1. Crear cuenta en NASA Earthdata: https://urs.earthdata.nasa.gov/users/new
2. En el notebook, configurar:

```python
NASA_USERNAME = "tu_usuario"
NASA_PASSWORD = "tu_contraseña"
USAR_TEMPO_REAL = True
```

### Personalizar ubicación

```python
LATITUD = 19.4326    # Tu latitud
LONGITUD = -99.1332  # Tu longitud
NOMBRE_UBICACION = "Tu ciudad"
```

---

## 📈 Resultados

El modelo logra:
- ✅ **Alta precisión** en predicciones a corto plazo (3-6h)
- ✅ **Captura patrones** estacionales y diarios
- ✅ **Error controlado** incluso a 24 horas
- ✅ **Clasificación inteligente** de niveles de calidad del aire

### Ejemplo de predicción:

```
🔮 PREDICCIÓN DE CALIDAD DEL AIRE
==================================================
⏰ En 3 horas:
   AQI Predicho: 45.2
   Nivel: 🟢 Buena
   👍 Excelente momento para actividades al aire libre

⏰ En 6 horas:
   AQI Predicho: 78.5
   Nivel: 🟡 Moderada
   ✅ Bueno para la mayoría de actividades
```

---

## 🤝 Contribuir

Ideas de mejora:
- 🗺️ Mapas interactivos con predicciones
- 📱 App móvil con notificaciones
- 🤖 Bot de Telegram/WhatsApp
- 📊 Dashboard en tiempo real
- 🎯 Recomendaciones personalizadas por usuario

---

## 📚 Recursos

- **TEMPO Mission**: https://science.nasa.gov/mission/tempo/
- **NASA Earthdata**: https://earthdata.nasa.gov/
- **TensorFlow/Keras**: https://www.tensorflow.org/
- **Documentación completa**: [README_TEMPO.md](README_TEMPO.md)

---

## 📄 Licencia

Proyecto educativo usando datos públicos de NASA.

---

## 🙏 Agradecimientos

- **NASA TEMPO Mission** - Datos satelitales de calidad del aire
- **NASA POWER API** - Datos meteorológicos
- **TensorFlow** - Framework de deep learning

---

**🌍 ¡Prediciendo el futuro del aire que respiramos!** 🚀

Desarrollado con ❤️ para el Hackaton NASA

