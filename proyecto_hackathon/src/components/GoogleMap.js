"use client"
import { useEffect, useRef, useState } from "react"

export default function GoogleMap({ apiKey, center, zoom = 12, markerLabel, onCityClick, stations = null, heatOptions = null }) {
  const mapRef = useRef(null)
  const [error, setError] = useState(null)
  const [cities, setCities] = useState([])
  const [heatmapOn, setHeatmapOn] = useState(false)
  const markersRef = useRef([])
  const heatmapRef = useRef(null)
  const mapInstanceRef = useRef(null)

  useEffect(() => {
    const key = apiKey ?? process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

    if (!key) {
      setError('No API key found. Defina NEXT_PUBLIC_GOOGLE_MAPS_API_KEY en .env.local o pase apiKey al componente.')
      return
    }

    if (typeof window === 'undefined') return

    async function initMap() {
      if (!mapRef.current) return
      try {
        const defaultCenter = { lat: 39.8283, lng: -98.5795 } // Centro de Estados Unidos
        const mapCenter = center && center.lat && center.lng ? center : defaultCenter

        // eslint-disable-next-line no-undef
        const map = new window.google.maps.Map(mapRef.current, {
          center: mapCenter,
          zoom,
          // Desactivar el control de Street View (pegman) para quitar el personaje amarillo
          streetViewControl: false,
          // Evitar iconos clicables (lugares) que puedan abrir UI no deseada
          clickableIcons: false,
          // Mantener controles básicos; ocultar controles de tipo de mapa por simplicidad
          disableDefaultUI: false,
          zoomControl: true,
          mapTypeControl: false,
        })

        // Por seguridad, si existe un panorama de Street View asociado, ocultarlo y deshabilitar su UI
        try {
          if (map.getStreetView) {
            const sv = map.getStreetView()
            if (sv) {
              sv.setVisible(false)
              try { sv.setOptions({ disableDefaultUI: true }) } catch (e) {}
            }
          }
        } catch (e) {
          // no crítico, continuar
        }

        // No añadir marcador automático en el centro

        // Añadir listener de click en el mapa (sin geocoding - usar coordenadas directas)
        map.addListener('click', async (event) => {
          const lat = event.latLng.lat()
          const lng = event.latLng.lng()
          
          try {
            // Generar nombre de ciudad basado en coordenadas (sin usar Geocoding API)
            const cityName = `Ciudad ${lat.toFixed(2)}, ${lng.toFixed(2)}`
            const citySlug = `ciudad-${lat.toFixed(2).replace('.', '-')}-${lng.toFixed(2).replace('.', '-').replace('-', 'n')}`
            
            const simulatedCity = {
              name: cityName,
              slug: citySlug,
              lat,
              lng,
              isSimulated: true
            }
            
            // Centrar el mapa y navegar
            map.panTo({ lat, lng })
            if (map.getZoom() < 10) map.setZoom(10)
            
            if (onCityClick) {
              onCityClick(simulatedCity)
            }
          } catch (e) {
            console.warn('Error al procesar click en mapa:', e)
          }
        })

        // Cargar ciudades desde API mock
        try {
          const res = await fetch('/api/cities')
          const data = await res.json()
          setCities(data)
          // crear marcadores
          markersRef.current.forEach(m => m.setMap(null))
          markersRef.current = data.map(c => {
            // eslint-disable-next-line no-undef
            const m = new window.google.maps.Marker({ position: { lat: c.lat, lng: c.lng }, map, title: c.name })
            m.addListener('click', () => {
              try {
                // centrar el mapa en la ciudad clicada
                if (map && map.panTo) {
                  map.panTo({ lat: c.lat, lng: c.lng })
                }
                // ajustar el zoom si es pequeño
                try { if (map && map.getZoom && map.getZoom() < 10) map.setZoom(10) } catch (e) {}
              } catch (e) {}
              // llamar al callback para navegación
              onCityClick && onCityClick(c)
            })
            return m
          })
        
          // guardar referencia al mapa
          mapInstanceRef.current = map

          // Agregar listener para ajustar el heatmap al cambiar zoom
          map.addListener('zoom_changed', () => {
            if (heatmapRef.current) {
              const currentZoom = map.getZoom()
              // Calcular radio adaptativo: más zoom = radio más pequeño
              // Zoom 5 (muy alejado) → radio ~80px
              // Zoom 10 (medio) → radio ~40px
              // Zoom 15 (cerca) → radio ~20px
              // Zoom 20 (muy cerca) → radio ~10px
              const adaptiveRadius = Math.max(10, Math.min(80, 100 - (currentZoom * 4)))
              console.log(`🔍 [GoogleMap] Zoom: ${currentZoom}, Radio heatmap: ${adaptiveRadius}px`)
              heatmapRef.current.set('radius', adaptiveRadius)
            }
          })
          
        } catch (e) {
          console.warn('No se pudieron cargar ciudades', e)
        }

        setError(null)
      } catch (e) {
        setError('Error al inicializar el mapa: ' + e.message)
      }
    }

    if (window.google && window.google.maps) {
      initMap()
      return
    }

    window.initMap = initMap

  const script = document.createElement('script')
  // cargar la librería de visualización para Heatmap
  script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=visualization&callback=initMap`
    script.async = true
    script.defer = true
    script.onerror = () => setError('Error cargando el script de Google Maps. Revisa la consola y las restricciones de la clave API.')
    document.head.appendChild(script)

    return () => {
      try {
        delete window.initMap
        // limpiar marcadores
        markersRef.current.forEach(m => m.setMap(null))
        if (heatmapRef.current) heatmapRef.current.setMap(null)
      } catch (e) {}
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey])

  // Efecto para actualizar el centro del mapa cuando cambie la prop center
  useEffect(() => {
    if (!mapInstanceRef.current || !center || !center.lat || !center.lng) return
    
    console.log('🗺️ [GoogleMap] Actualizando centro del mapa a:', center)
    mapInstanceRef.current.panTo({ lat: center.lat, lng: center.lng })
    
    // Ajustar zoom si es necesario
    if (mapInstanceRef.current.getZoom() < 10) {
      mapInstanceRef.current.setZoom(12)
    }
  }, [center])

  // efecto para activar/desactivar heatmap
  useEffect(() => {
    async function toggleHeatmap() {
      if (!mapInstanceRef.current) return

      if (!heatmapOn) {
        if (heatmapRef.current) {
          heatmapRef.current.setMap(null)
          heatmapRef.current = null
        }
        return
      }

      try {
        // Si se pasan estaciones (por ejemplo en la página de ciudad), usar sus latest.value como peso
        if (stations && stations.length) {
          const weighted = stations.map(s => ({ location: new window.google.maps.LatLng(s.lat, s.lng), weight: s.weight ?? (s.latest ? s.latest.value : 0) }))
          
          // Calcular radio adaptativo basado en el zoom actual
          const currentZoom = mapInstanceRef.current.getZoom()
          let radius = (heatOptions && heatOptions.radius) ? heatOptions.radius : 30
          
          // Si no se especificó un radio fijo, usar adaptativo
          if (!heatOptions || !heatOptions.radius) {
            radius = Math.max(10, Math.min(80, 100 - (currentZoom * 4)))
          }
          
          console.log(`🌡️ [GoogleMap] Creando heatmap - Zoom: ${currentZoom}, Radio: ${radius}px, Puntos: ${weighted.length}`)
          
          heatmapRef.current = new window.google.maps.visualization.HeatmapLayer({ 
            data: weighted, 
            radius,
            maxIntensity: 100,
            dissipating: true,
            opacity: 0.6
          })
          heatmapRef.current.setMap(mapInstanceRef.current)
          return
        }

        // Fallback: usar ciudades (one-point-per-city) como antes
        let cityList = cities
        if (!cityList || cityList.length === 0) {
          const cres = await fetch('/api/cities')
          cityList = await cres.json()
          setCities(cityList)
        }
        const promises = cityList.map(async (c) => {
          try {
            const r = await fetch(`/api/data?city=${c.slug}&points=1`)
            const j = await r.json()
            const latest = j.series && j.series.length ? j.series[j.series.length - 1] : null
            const weight = latest ? latest.pm25 : 0
            return { lat: c.lat, lng: c.lng, weight }
          } catch (e) {
            return { lat: c.lat, lng: c.lng, weight: 0 }
          }
        })

        const results = await Promise.all(promises)
        const weighted = results.map(r => ({ location: new window.google.maps.LatLng(r.lat, r.lng), weight: r.weight }))
        
        // Calcular radio adaptativo basado en el zoom actual
        const currentZoom = mapInstanceRef.current.getZoom()
        let radius = (heatOptions && heatOptions.radius) ? heatOptions.radius : 30
        
        // Si no se especificó un radio fijo, usar adaptativo
        if (!heatOptions || !heatOptions.radius) {
          radius = Math.max(10, Math.min(80, 100 - (currentZoom * 4)))
        }
        
        console.log(`🌡️ [GoogleMap] Creando heatmap (ciudades) - Zoom: ${currentZoom}, Radio: ${radius}px`)
        
        heatmapRef.current = new window.google.maps.visualization.HeatmapLayer({ 
          data: weighted, 
          radius,
          maxIntensity: 50,
          dissipating: true,
          opacity: 0.6
        })
        heatmapRef.current.setMap(mapInstanceRef.current)
      } catch (e) {
        console.error('Error cargando datos para heatmap', e)
      }
    }

    toggleHeatmap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [heatmapOn, cities])

  return (
    <div>
      {error ? (
        <div className="text-yellow-300 bg-gray-800 p-3 rounded-md mb-3">{error}</div>
      ) : null}

      {/* Solo mostrar control de heatmap si hay estaciones (página de ciudad) */}
      {stations && stations.length > 0 && (
        <div className="mb-2 flex gap-2 items-center">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={heatmapOn} onChange={(e) => setHeatmapOn(e.target.checked)} /> Heatmap
          </label>
        </div>
      )}

      <div ref={mapRef} id="map" style={{ width: '100%', height: 500 }} className="rounded-md shadow-md" />
    </div>
  )
}
