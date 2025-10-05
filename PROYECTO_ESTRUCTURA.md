# 🌍 Sistema de Predicción de Calidad del Aire

## 📋 Estructura del Proyecto (Enfoque Paso a Paso)

### 📚 Notebooks

#### **01_TRATAMIENTO_DATOS.ipynb** ⬅️ COMENZAR AQUÍ
Este notebook cubre todo el proceso de obtención y preparación de datos:

1. **Configuración Inicial**
   - Importación de librerías
   - Definición de parámetros (ubicación, fechas)
   - Verificación de credenciales

2. **Obtención de Datos**
   - Cliente OpenAQ (estaciones terrestres)
   - Cliente TEMPO (satélite NASA)
   - Datos meteorológicos (NASA POWER)

3. **Limpieza de Datos**
   - Eliminación de duplicados
   - Manejo de valores faltantes (interpolación)
   - Detección y eliminación de outliers
   - Validación de rangos físicos

4. **Análisis Exploratorio**
   - Estadísticas descriptivas
   - Visualizaciones
   - Análisis de correlaciones
   - Identificación de patrones

5. **Exportación**
   - Guardar datos limpios
   - Preparar para modelado

#### **02_MODELADO.ipynb** (Siguiente fase)
- Preparación de secuencias temporales
- Diseño de arquitectura LSTM
- Entrenamiento del modelo
- Evaluación y validación

#### **03_PREDICCION.ipynb** (Fase final)
- Sistema de predicción en tiempo real
- Visualizaciones interactivas
- Reportes automatizados
- API de predicción

---

## 🗂️ Archivos del Proyecto

```
HACKATON_NASA/
│
├── 01_TRATAMIENTO_DATOS.ipynb    ⭐ NOTEBOOK PRINCIPAL
├── 02_MODELADO.ipynb              (Próximamente)
├── 03_PREDICCION.ipynb            (Próximamente)
│
├── TEMPO_PREDICTOR_BACKUP.ipynb   (Versión anterior - respaldo)
├── PRUEBAS.ipynb                  (Experimentos)
│
├── config_ejemplo.py              Configuración de credenciales
├── requirements.txt               Dependencias del proyecto
├── README.md                      Documentación general
├── README_TEMPO.md                Documentación NASA TEMPO
│
└── datos/                         (Se creará automáticamente)
    ├── raw/                       Datos sin procesar
    ├── processed/                 Datos limpios
    └── models/                    Modelos entrenados
```

---

## 🚀 Cómo Empezar

### 1️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar Credenciales

**Opción A: Variables de Entorno (Recomendado)**
```powershell
# NASA Earthdata
$env:NASA_USERNAME = "tu_usuario"
$env:NASA_PASSWORD = "tu_contraseña"

# OpenAQ
$env:OPENAQ_API_KEY = "tu_api_key"
```

**Opción B: Archivo de Configuración**
```python
# Copia config_ejemplo.py a config.py y completa tus credenciales
cp config_ejemplo.py config.py
```

### 3️⃣ Ejecutar Notebook
1. Abre `01_TRATAMIENTO_DATOS.ipynb`
2. Ejecuta las celdas en orden
3. Sigue las instrucciones paso a paso

---

## 📊 Fuentes de Datos

### 🛰️ NASA TEMPO
- **Tipo**: Satélite geoestacionario
- **Variables**: NO₂, calidad del aire, nubes
- **Cobertura**: Norteamérica completa
- **Resolución**: Horaria, 2-8 km
- **Registro**: https://urs.earthdata.nasa.gov/

### 📡 OpenAQ
- **Tipo**: Red de estaciones terrestres
- **Variables**: PM2.5, PM10, O₃, NO₂, CO, SO₂
- **Cobertura**: Global (>10,000 estaciones)
- **Resolución**: Minutos/horaria
- **API**: https://openaq.org/

### 🌤️ NASA POWER
- **Tipo**: Datos meteorológicos
- **Variables**: Temperatura, humedad, viento, presión
- **Cobertura**: Global
- **Resolución**: Horaria/diaria
- **Acceso**: Libre, sin registro

---

## 🎯 Objetivos del Proyecto

1. ✅ **Obtener datos de calidad del aire** de múltiples fuentes
2. ✅ **Limpiar y validar** los datos automáticamente
3. ✅ **Analizar patrones** y correlaciones
4. ⏳ **Entrenar modelo LSTM** para predicción
5. ⏳ **Crear sistema en tiempo real** de predicción
6. ⏳ **Generar reportes** automatizados

---

## 📈 Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│  1. OBTENCIÓN DE DATOS                                      │
│     • OpenAQ (estaciones)                                   │
│     • TEMPO (satélite)                                      │
│     • NASA POWER (meteorología)                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. LIMPIEZA Y VALIDACIÓN                                   │
│     • Eliminar duplicados                                   │
│     • Interpolar valores faltantes                          │
│     • Detectar outliers                                     │
│     • Validar rangos                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. ANÁLISIS EXPLORATORIO                                   │
│     • Estadísticas descriptivas                             │
│     • Visualizaciones                                       │
│     • Correlaciones                                         │
│     • Patrones temporales                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. PREPARACIÓN PARA MODELADO                               │
│     • Crear secuencias temporales                           │
│     • Normalización                                         │
│     • División train/test                                   │
│     • Exportar datos procesados                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. MODELADO (Siguiente notebook)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.11+**
- **Pandas** - Manipulación de datos
- **NumPy** - Operaciones numéricas
- **Matplotlib/Seaborn** - Visualización
- **Requests** - APIs
- **earthaccess** - NASA Earthdata
- **TensorFlow/Keras** - Deep Learning (fase de modelado)

---

## 📝 Notas Importantes

1. **Credenciales requeridas**: NASA Earthdata y OpenAQ
2. **Conexión a Internet**: Necesaria para descarga de datos
3. **Espacio en disco**: ~500 MB para datos descargados
4. **Tiempo de ejecución**: 5-15 minutos (depende de la conexión)

---

## 🤝 Contribuciones

Este proyecto es parte de un hackathon de NASA. Si tienes sugerencias o mejoras:

1. Revisa el código actual
2. Prueba los notebooks
3. Documenta tus cambios
4. Comparte tus resultados

---

## 📧 Soporte

Si tienes problemas:
1. Verifica que todas las credenciales estén configuradas
2. Asegúrate de tener conexión a Internet
3. Revisa los mensajes de error en el notebook
4. Consulta la documentación de cada API

---

## ✨ Próximos Pasos

1. ✅ **Completar `01_TRATAMIENTO_DATOS.ipynb`**
2. ⏳ Crear `02_MODELADO.ipynb`
3. ⏳ Crear `03_PREDICCION.ipynb`
4. ⏳ Optimizar el modelo
5. ⏳ Desplegar en producción

---

**¡Comienza con `01_TRATAMIENTO_DATOS.ipynb` y sigue las instrucciones paso a paso!** 🚀
