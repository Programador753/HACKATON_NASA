"use client"
import Link from "next/link"

export default function Header() {
  return (
    <header className="w-full bg-white text-black shadow-sm">
      <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="/nasa.jpg" alt="NASA logo" onError={(e)=>{e.currentTarget.onerror=null; e.currentTarget.src='/nasa-banner.jpg'}} className="h-14 md:h-16 lg:h-20 w-auto object-contain" />
          <div className="text-left">
            {/* Aumentado tamaño: 2xl en móvil, 4xl en md y 5xl en lg */}
            <div className="text-2xl md:text-3xl lg:text-4xl font-bold text-black">Do You Breathe This?</div>
          </div>
        </div>

        {/* Nav vacío - eliminamos enlaces según solicitud del usuario */}
      </div>
    </header>
  )
}
