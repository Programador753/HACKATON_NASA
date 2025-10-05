import { NextResponse } from 'next/server'

// estaciones simuladas para Los Angeles (lat/lng aproximados)
const LA_STATIONS = [
  { id: 'la-1', name: 'Downtown LA', lat: 34.0407, lng: -118.2468 },
  { id: 'la-2', name: 'Hollywood', lat: 34.0928, lng: -118.3287 },
  { id: 'la-3', name: 'West LA', lat: 34.0390, lng: -118.4437 },
  { id: 'la-4', name: 'South LA', lat: 33.9739, lng: -118.2487 },
  { id: 'la-5', name: 'Echo Park', lat: 34.0782, lng: -118.2606 },
  { id: 'la-6', name: 'East LA', lat: 34.0239, lng: -118.1726 },
]

function randomMetricValue(metric) {
  switch (metric) {
    case 'pm25': return +(5 + Math.random() * 50).toFixed(2)
    case 'pm10': return +(10 + Math.random() * 80).toFixed(2)
    case 'o3': return +(0.01 + Math.random() * 0.06).toFixed(3)
    case 'no2': return +(0.005 + Math.random() * 0.04).toFixed(3)
    case 'co': return +(0.1 + Math.random() * 1.5).toFixed(2)
    case 'aqi': return Math.floor(20 + Math.random() * 120)
    default: return +(5 + Math.random() * 50).toFixed(2)
  }
}

export function GET(request) {
  const url = new URL(request.url)
  const city = url.searchParams.get('city') || 'los-angeles'
  const withData = url.searchParams.get('withData') === '1'
  const metric = url.searchParams.get('metric') || 'pm25'

  // por ahora solo soportamos los-angeles en este mock
  let stations = []
  if (city.toLowerCase() === 'los-angeles' || city.toLowerCase() === 'los-angeles') {
    stations = LA_STATIONS.map(s => ({ ...s }))
  }

  if (withData) {
    const now = new Date().toISOString()
    stations = stations.map(s => ({
      ...s,
      latest: {
        timestamp: now,
        value: randomMetricValue(metric),
        metric,
      }
    }))
  }

  return NextResponse.json({ city, stations })
}
