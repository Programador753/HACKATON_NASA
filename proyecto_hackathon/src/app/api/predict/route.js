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

    return {
      predictions,
      currentAQI: data.aqi_actual_estimado,
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
