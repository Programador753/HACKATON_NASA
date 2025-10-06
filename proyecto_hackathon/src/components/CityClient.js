"use client"
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import GoogleMap from './GoogleMap'
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function CityClient({ slug }) {
  const [data, setData] = useState([])
  const [pred, setPred] = useState([])
  const [loading, setLoading] = useState(true)
  const [stations, setStations] = useState([])
  const [metric, setMetric] = useState('pm25')
  const [currentAQI, setCurrentAQI] = useState(null)
  const [currentValue, setCurrentValue] = useState(null)
  const [currentMetric, setCurrentMetric] = useState('')
  const [currentPollutants, setCurrentPollutants] = useState(null)
  const [dataSource, setDataSource] = useState('')
  const [warnings, setWarnings] = useState(null)
  const [cityLocation, setCityLocation] = useState(null)
  const router = useRouter()

  // Mapeo de coordenadas por ciudad
  const CITY_COORDS = {
    'los-angeles': { lat: 34.0522, lng: -118.2437 },
    'new-york': { lat: 40.7128, lng: -74.0060 },
    'chicago': { lat: 41.8781, lng: -87.6298 },
    'houston': { lat: 29.7604, lng: -95.3698 },
    'phoenix': { lat: 33.4484, lng: -112.0740 },
    'philadelphia': { lat: 39.9526, lng: -75.1652 },
    'san-antonio': { lat: 29.4241, lng: -98.4936 },
    'san-diego': { lat: 32.7157, lng: -117.1611 },
    'dallas': { lat: 32.7767, lng: -96.7970 },
    'san-francisco': { lat: 37.7749, lng: -122.4194 },
    'miami': { lat: 25.7617, lng: -80.1918 }
  }

  useEffect(() => {
    async function load() {
      setLoading(true)
      console.log(`🔄 [CityClient] Cargando datos para ciudad: ${slug}, métrica: ${metric}`)
      try {
        // Cargar estaciones con latest value
        try {
          const sres = await fetch(`/api/stations?city=${slug}&withData=1&metric=${metric}`)
          const ss = await sres.json()
          setStations(ss.stations || [])
        } catch (e) {
          console.warn('No se pudieron cargar estaciones', e)
        }

        // Predicciones desde la API Python
        const pres = await fetch(`/api/predict?city=${slug}&metric=${metric}`)
        const pp = await pres.json()
        
        console.log(`📊 [CityClient] Datos recibidos:`, {
          ciudad: pp.city,
          aqi: pp.currentAQI,
          predicciones: pp.predictions?.length,
          fuente: pp.dataSource
        })
        
        const preds = pp.predictions.map(p => ({ 
          timestamp: p.timestamp, 
          value: p.value,
          horizonte: p.horizonte,
          calidad: p.calidad,
          mensaje: p.mensaje
        }))

        setData([])
        setPred(preds)
        setCurrentAQI(pp.currentAQI)
        setCurrentValue(pp.currentValue)
        setCurrentMetric(pp.currentMetric)
        setCurrentPollutants(pp.currentPollutants)
        setDataSource(pp.dataSource || 'Desconocido')
        setWarnings(pp.warnings)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    if (slug) load()
  }, [slug, metric])

  function goBack() {
    try {
      router.back()
    } catch (e) {
      router.replace('/')
    }
  }

  const stationsForHeat = stations.map(s => ({ 
    lat: s.lat, 
    lng: s.lng, 
    weight: s.latest ? s.latest.value : 0 
  }))
  
  // Calcular centro del mapa: prioridad ciudad > estaciones > URL > Los Angeles
  const cityCoords = CITY_COORDS[slug] || { lat: 34.0522, lng: -118.2437 }
  
  const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : new URLSearchParams()
  const urlLat = urlParams.get('lat')
  const urlLng = urlParams.get('lng')
  
  const mapCenter = stations.length > 0
    ? { lat: stations[0].lat, lng: stations[0].lng } 
    : (urlLat && urlLng ? { lat: parseFloat(urlLat), lng: parseFloat(urlLng) } : cityCoords)

  // Función para obtener color según AQI
  const getAQIColor = (aqi) => {
    if (aqi <= 50) return 'bg-green-500'
    if (aqi <= 100) return 'bg-yellow-500'
    if (aqi <= 150) return 'bg-orange-500'
    if (aqi <= 200) return 'bg-red-500'
    if (aqi <= 300) return 'bg-purple-500'
    return 'bg-red-900'
  }

  const getAQILabel = (aqi) => {
    if (aqi <= 50) return 'Buena'
    if (aqi <= 100) return 'Moderada'
    if (aqi <= 150) return 'Insalubre para grupos sensibles'
    if (aqi <= 200) return 'Insalubre'
    if (aqi <= 300) return 'Muy insalubre'
    return 'Peligrosa'
  }

  console.log('🗺️ [CityClient] Centro del mapa calculado:', {
    ciudad: slug,
    mapCenter,
    estaciones: stations.length,
    coordsCiudad: cityCoords
  })

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <div className="mb-4">
        <nav className="text-sm text-gray-600">
          Inicio / Estados Unidos / <span className="font-semibold">{slug.replace(/-/g, ' ')}</span>
        </nav>
      </div>

      <div className="flex gap-6 flex-col lg:flex-row">
        {/* Mapa a la izquierda */}
        <div className="lg:w-1/2 w-full">
          <div className="bg-white p-3 rounded shadow">
            <GoogleMap 
              center={mapCenter} 
              zoom={12} 
              stations={stationsForHeat}
            />
          </div>

          {/* Información actual */}
          {currentAQI !== null && (
            <div className="bg-white p-4 rounded shadow mt-4">
              <h3 className="font-bold mb-3">📊 Calidad del Aire Actual</h3>
              <div className="flex items-center gap-4">
                <div className={`${getAQIColor(currentAQI)} text-white rounded-lg p-4 text-center min-w-[100px]`}>
                  <div className="text-3xl font-bold">{currentAQI}</div>
                  <div className="text-xs">AQI</div>
                </div>
                <div>
                  <div className="font-semibold">{getAQILabel(currentAQI)}</div>
                  {metric !== 'aqi' && currentValue !== null && currentMetric && (
                    <div className="text-sm font-medium text-blue-600 mt-1">
                      📈 {currentMetric}: {currentValue.toFixed(1)} {currentMetric.includes('PM') ? 'µg/m³' : 'ppb'}
                    </div>
                  )}
                  <div className="text-sm text-gray-600">
                    🌐 Ciudad: <strong>{slug}</strong>
                  </div>
                  <div className="text-sm text-gray-600">
                    📡 Fuente: {dataSource}
                  </div>
                  {warnings && (
                    <div className="text-xs text-yellow-600 mt-1">⚠️ {warnings}</div>
                  )}
                </div>
              </div>

              {currentPollutants && (
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-gray-500 text-xs">PM2.5</div>
                    <div className="font-semibold">{currentPollutants['PM2.5']?.toFixed(1)} µg/m³</div>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-gray-500 text-xs">PM10</div>
                    <div className="font-semibold">{currentPollutants.PM10?.toFixed(1)} µg/m³</div>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-gray-500 text-xs">O3</div>
                    <div className="font-semibold">{currentPollutants.O3?.toFixed(1)} ppb</div>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-gray-500 text-xs">NO2</div>
                    <div className="font-semibold">{currentPollutants.NO2?.toFixed(1)} ppb</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel derecho */}
        <div className="lg:w-1/2 w-full space-y-4 overflow-auto">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">
                {new Date().toLocaleDateString('es-ES', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
              <h1 className="text-2xl font-bold">
                {slug === 'los-angeles' 
                  ? 'Los Angeles (LA)' 
                  : slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                }
              </h1>
              {slug !== 'los-angeles' && (
                <p className="text-sm text-yellow-600 mt-1">
                  📍 Datos simulados - Los Angeles tiene datos reales de OpenAQ
                </p>
              )}
            </div>
            <div>
              <button 
                className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded transition"
                onClick={goBack}
              >
                ← Volver
              </button>
            </div>
          </div>

          <div className="bg-white p-3 rounded shadow">
            <div className="flex items-center gap-4 mb-3 flex-wrap">
              <label className="flex items-center gap-2 text-sm">
                Métrica:
                <select 
                  value={metric} 
                  onChange={(e) => setMetric(e.target.value)} 
                  className="ml-2 border rounded p-1"
                >
                  <option value="pm25">PM2.5</option>
                  <option value="pm10">PM10</option>
                  <option value="o3">O3</option>
                  <option value="no2">NO2</option>
                  <option value="aqi">AQI</option>
                </select>
              </label>

              <div className="text-xs text-gray-500">
                ℹ️ El tamaño del heatmap se ajusta automáticamente al zoom
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2 text-gray-500">Cargando predicciones...</p>
              </div>
            ) : (
              <div>
                <h3 className="font-bold mb-2">
                  {metric.toUpperCase()} — Predicción Próximas Horas
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={pred}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(t) => {
                        const d = new Date(t)
                        return `${d.getHours()}:00`
                      }}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(t) => new Date(t).toLocaleString('es-ES')}
                      formatter={(value, name, props) => {
                        const extra = props.payload.calidad ? ` (${props.payload.calidad})` : ''
                        return [value + extra, metric.toUpperCase()]
                      }}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#ff7300" 
                      strokeWidth={2}
                      dot={{ fill: '#ff7300', r: 4 }} 
                      name={metric.toUpperCase()} 
                    />
                  </LineChart>
                </ResponsiveContainer>

                <div className="mt-3 text-sm text-gray-600">
                  <strong>📈 Predicciones:</strong> Modelo LSTM con Attention entrenado con datos reales.
                  {pred.length > 0 && pred[0].horizonte && (
                    <div className="mt-1">
                      Horizontes: {pred.map(p => p.horizonte).join(', ')}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white p-3 rounded shadow">
            <h4 className="font-semibold mb-2">📡 Estaciones de Monitoreo</h4>
            {stations.length > 0 ? (
              <ul className="text-sm text-gray-700">
                {stations.map(s => (
                  <li key={s.id} className="mb-1">
                    {s.name} — {s.latest ? `${s.latest.value} ${metric}` : 'sin datos'}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No hay estaciones disponibles en esta área</p>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
