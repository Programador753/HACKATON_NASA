import { NextResponse } from 'next/server'

function generateHistoricalSeries(points, stepHours = 3) {
  const out = []
  const now = new Date()
  
  // Generar datos históricos hacia atrás desde ahora
  for (let i = points - 1; i >= 0; i--) {
    const t = new Date(now)
    t.setHours(now.getHours() - (i * stepHours))
    t.setMinutes(0)
    t.setSeconds(0)
    t.setMilliseconds(0)
    
    out.push({
      timestamp: t.toISOString(),
      pm25: +(10 + Math.sin(i / 3) * 5 + Math.random() * 3).toFixed(2),
      pm10: +(20 + Math.cos(i / 4) * 6 + Math.random() * 4).toFixed(2),
      o3: +(0.02 + Math.random() * 0.02).toFixed(3),
      no2: +(0.01 + Math.random() * 0.015).toFixed(3),
      so2: +(0.002 + Math.random() * 0.005).toFixed(3),
      co: +(0.1 + Math.random() * 0.3).toFixed(2),
      aqi: Math.floor(30 + Math.random() * 50),
      temp: +(15 + Math.random() * 15).toFixed(1),
      rh: Math.floor(40 + Math.random() * 40)
    })
  }
  return out
}

export function GET(request) {
  const url = new URL(request.url)
  const city = url.searchParams.get('city') || 'los-angeles'
  const points = parseInt(url.searchParams.get('points') || '4', 10) // Solo 4 puntos históricos cada 3h
  const step = parseInt(url.searchParams.get('step') || '3', 10) // Intervalos de 3h

  const series = generateHistoricalSeries(points, step)
  return NextResponse.json({ city, series })
}
