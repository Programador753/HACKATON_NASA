import { NextResponse } from 'next/server'

const cities = [
  // Los Angeles - datos reales disponibles
  { name: 'Los Angeles', slug: 'los-angeles', state: 'CA', lat: 34.0522, lng: -118.2437 },
  // Ciudades adicionales para testing - datos simulados
  { name: 'San Francisco', slug: 'san-francisco', state: 'CA', lat: 37.7749, lng: -122.4194 },
  { name: 'New York', slug: 'new-york', state: 'NY', lat: 40.7128, lng: -74.0060 },
  { name: 'Chicago', slug: 'chicago', state: 'IL', lat: 41.8781, lng: -87.6298 },
  { name: 'Miami', slug: 'miami', state: 'FL', lat: 25.7617, lng: -80.1918 }
]

export function GET(request) {
  const { searchParams } = new URL(request.url)
  const state = searchParams.get('state')
  if (state) {
    return NextResponse.json(cities.filter(c => c.state === state.toUpperCase()))
  }
  return NextResponse.json(cities)
}
