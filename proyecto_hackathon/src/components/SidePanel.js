"use client"
import { useState } from "react"

export default function SidePanel({ open, onClose, state, cities, onSelectCity }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-40 flex">
      <div className="w-80 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-xl p-4 overflow-auto">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold">{state ? `Ciudades en ${state}` : 'Ciudades'}</h3>
          <button onClick={onClose} className="text-sm text-gray-500">Cerrar</button>
        </div>

        <ul className="space-y-2">
          {cities && cities.length ? (
            cities.map((c) => (
              <li key={c.slug} className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer" onClick={() => onSelectCity(c)}>
                <div className="font-medium">{c.name}</div>
                <div className="text-xs text-gray-500">{c.state}</div>
              </li>
            ))
          ) : (
            <li className="text-sm text-gray-500">No hay ciudades</li>
          )}
        </ul>
      </div>

      <div className="flex-1" onClick={onClose} />
    </div>
  )
}
