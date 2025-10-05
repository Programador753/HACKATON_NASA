"use client"
import { useState } from "react"
import GoogleMap from "../components/GoogleMap"
import Header from "../components/Header"
import SidePanel from "../components/SidePanel"
import { useRouter } from "next/navigation"

export default function Home() {
  const [panelOpen, setPanelOpen] = useState(false)
  const [panelState, setPanelState] = useState(null)
  const [panelCities, setPanelCities] = useState([])
  const router = useRouter()

  async function handleCityClick(city) {
    // Pasar coordenadas en la URL para centrar el mapa correctamente
    const url = `/ciudades/${city.slug}?lat=${city.lat}&lng=${city.lng}`
    router.push(url)
  }

  async function handleStateClick(stateAbbr) {
    setPanelState(stateAbbr)
    try {
      const res = await fetch(`/api/cities?state=${stateAbbr}`)
      const data = await res.json()
      setPanelCities(data)
      setPanelOpen(true)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header />

      <main className="max-w-6xl mx-auto p-6">
  <h1 className="text-4xl font-bold mb-2">Calidad del Aire · Estados Unidos</h1>

        <GoogleMap center={{ lat: 37.0902, lng: -95.7129 }} zoom={4} onCityClick={handleCityClick} />

        
      </main>

      <SidePanel open={panelOpen} onClose={() => setPanelOpen(false)} state={panelState} cities={panelCities} onSelectCity={handleCityClick} />
    </div>
  )
}