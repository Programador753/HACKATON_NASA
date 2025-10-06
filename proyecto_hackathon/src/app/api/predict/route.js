import { NextResponse } from 'next/server'

// Mapeo de slugs de ciudades a endpoints de la API Python
const CITY_ENDPOINTS = {
  'los-angeles': 'los-angeles',
  'new-york': 'new-york',
  'chicago': 'chicago',
  'houston': 'houston',
  'phoenix': 'phoenix',
  'philadelphia': 'philadelphia',
  'san-antonio': 'san-antonio',
  'san-diego': 'san-diego',
  'dallas': 'dallas',
  'san-jose': 'san-jose',
  'san-francisco': 'san-francisco',
  'miami': 'miami'
}

// Mapeo de métricas del frontend a contaminantes de la API
const METRIC_MAPPING = {
  'pm25': 'PM2.5',
  'pm10': 'PM10',
  'o3': 'O3',
  'no2': 'NO2',
  'aqi': 'AQI'
}

// Función para calcular AQI basado en concentración de contaminante
function calculateAQI(pollutant, concentration) {
  // Rangos AQI estándar EPA
  const breakpoints = {
    'PM2.5': [
      { cLow: 0.0, cHigh: 12.0, iLow: 0, iHigh: 50 },
      { cLow: 12.1, cHigh: 35.4, iLow: 51, iHigh: 100 },
      { cLow: 35.5, cHigh: 55.4, iLow: 101, iHigh: 150 },
      { cLow: 55.5, cHigh: 150.4, iLow: 151, iHigh: 200 },
      { cLow: 150.5, cHigh: 250.4, iLow: 201, iHigh: 300 },
      { cLow: 250.5, cHigh: 500.4, iLow: 301, iHigh: 500 }
    ],
    'PM10': [
      { cLow: 0, cHigh: 54, iLow: 0, iHigh: 50 },
      { cLow: 55, cHigh: 154, iLow: 51, iHigh: 100 },
      { cLow: 155, cHigh: 254, iLow: 101, iHigh: 150 },
      { cLow: 255, cHigh: 354, iLow: 151, iHigh: 200 },
      { cLow: 355, cHigh: 424, iLow: 201, iHigh: 300 },
      { cLow: 425, cHigh: 604, iLow: 301, iHigh: 500 }
    ],
    'O3': [
      { cLow: 0, cHigh: 54, iLow: 0, iHigh: 50 },
      { cLow: 55, cHigh: 70, iLow: 51, iHigh: 100 },
      { cLow: 71, cHigh: 85, iLow: 101, iHigh: 150 },
      { cLow: 86, cHigh: 105, iLow: 151, iHigh: 200 },
      { cLow: 106, cHigh: 200, iLow: 201, iHigh: 300 }
    ],
    'NO2': [
      { cLow: 0, cHigh: 53, iLow: 0, iHigh: 50 },
      { cLow: 54, cHigh: 100, iLow: 51, iHigh: 100 },
      { cLow: 101, cHigh: 360, iLow: 101, iHigh: 150 },
      { cLow: 361, cHigh: 649, iLow: 151, iHigh: 200 },
      { cLow: 650, cHigh: 1249, iLow: 201, iHigh: 300 },
      { cLow: 1250, cHigh: 2049, iLow: 301, iHigh: 500 }
    ]
  }

  const ranges = breakpoints[pollutant]
  if (!ranges) return null

  // Encontrar el rango apropiado
  for (const range of ranges) {
    if (concentration >= range.cLow && concentration <= range.cHigh) {
      // Fórmula AQI: I = [(IHigh - ILow) / (CHigh - CLow)] * (C - CLow) + ILow
      const aqi = ((range.iHigh - range.iLow) / (range.cHigh - range.cLow)) * 
                  (concentration - range.cLow) + range.iLow
      return Math.round(aqi)
    }
  }

  // Si está fuera de rango, usar el límite superior
  if (concentration > ranges[ranges.length - 1].cHigh) {
    return 500
  }
  return 0
}

async function fetchPredictionsFromPythonAPI(citySlug, metric) {
  const apiUrl = process.env.NEXT_PUBLIC_AQI_API_URL || 'http://localhost:8000'
  const cityEndpoint = CITY_ENDPOINTS[citySlug] || 'los-angeles'
  
  console.log(`🌍 [API Route] Solicitando predicción para: ${citySlug} → ${cityEndpoint} (métrica: ${metric})`)
  
  try {
    const fullUrl = `${apiUrl}/predict/city/${cityEndpoint}`
    console.log(`📡 [API Route] Llamando a: ${fullUrl}`)
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // No cache para obtener siempre datos frescos
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`API Python respondió con status ${response.status}`)
    }

    const data = await response.json()
    
    console.log(`✅ [API Route] Respuesta de Python API:`, {
      ciudad: data.nombre_ubicacion,
      aqi: data.aqi_actual_estimado,
      fuente: data.fuente_datos,
      predicciones: data.predicciones?.length
    })
    
    // Transformar datos de la API Python al formato esperado por el frontend
    const metricKey = METRIC_MAPPING[metric] || 'PM2.5'
    
    const predictions = data.predicciones.map(pred => {
      // Calcular timestamp basado en horizonte
      const now = new Date()
      const hoursAhead = parseInt(pred.horizonte.replace('h', ''))
      const predictionTime = new Date(now.getTime() + hoursAhead * 60 * 60 * 1000)
      
      // Obtener valor según la métrica solicitada
      let value
      if (metric === 'aqi') {
        value = pred.aqi_predicho
      } else {
        value = pred.contaminantes[metricKey] || 0
      }
      
      return {
        timestamp: predictionTime.toISOString(),
        value: parseFloat(value.toFixed(2)),
        horizonte: pred.horizonte,
        calidad: pred.calidad,
        mensaje: pred.mensaje,
        color: pred.color,
        contaminantes: pred.contaminantes
      }
    })

    // Calcular AQI específico según la métrica seleccionada
    let currentAQI
    let currentValue
    
    if (metric === 'aqi') {
      // Si se selecciona AQI, usar el valor general
      currentAQI = data.aqi_actual_estimado
      currentValue = currentAQI
    } else {
      // Para métricas específicas, calcular AQI del contaminante
      const pollutantConcentration = data.contaminantes_actuales?.[metricKey] || 0
      currentValue = pollutantConcentration
      currentAQI = calculateAQI(metricKey, pollutantConcentration) || data.aqi_actual_estimado
    }

    return {
      predictions,
      currentAQI,
      currentValue,
      currentMetric: metricKey,
      currentPollutants: data.contaminantes_actuales,
      location: data.nombre_ubicacion,
      dataSource: data.fuente_datos,
      warnings: data.advertencias
    }
    
  } catch (error) {
    console.error('Error llamando a API Python:', error)
    // Retornar datos simulados como fallback
    return generateFallbackPredictions(metric)
  }
}

function generateFallbackPredictions(metric) {
  const out = []
  const now = new Date()
  const currentHour = now.getHours()
  
  // Encontrar la próxima hora que sea múltiplo de 3
  const nextThreeHourMark = Math.ceil((currentHour + 1) / 3) * 3
  
  const startTime = new Date()
  startTime.setHours(nextThreeHourMark % 24)
  startTime.setMinutes(0)
  startTime.setSeconds(0)
  startTime.setMilliseconds(0)
  
  if (nextThreeHourMark >= 24) {
    startTime.setDate(startTime.getDate() + 1)
  }
  
  // Generar 4 predicciones (3h, 6h, 12h, 24h simulando la API)
  const horizons = [3, 6, 12, 24]
  let t = new Date(startTime)
  
  horizons.forEach((hours, i) => {
    const predTime = new Date(now.getTime() + hours * 60 * 60 * 1000)
    out.push({ 
      timestamp: predTime.toISOString(), 
      value: +(12 + Math.sin(i / 2) * 3 + Math.random() * 4).toFixed(2),
      horizonte: `${hours}h`,
      calidad: 'Simulado',
      mensaje: 'Datos simulados (API no disponible)'
    })
  })
  
  return {
    predictions: out,
    currentAQI: 80,
    currentValue: metric === 'aqi' ? 80 : 15.5,
    currentMetric: METRIC_MAPPING[metric] || 'PM2.5',
    dataSource: 'Simulado (fallback)'
  }
}

export async function GET(request) {
  const url = new URL(request.url)
  const city = url.searchParams.get('city') || 'los-angeles'
  const metric = url.searchParams.get('metric') || 'pm25'

  const result = await fetchPredictionsFromPythonAPI(city, metric)
  
  return NextResponse.json({ 
    city, 
    metric, 
    ...result
  })
}
