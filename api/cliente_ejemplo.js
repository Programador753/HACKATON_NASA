/**
 * Cliente JavaScript para conectar con la API de predicción AQI
 * Usa desde Next.js, React, o cualquier aplicación JavaScript
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Verificar el estado de salud de la API
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error en health check:', error);
    throw error;
  }
}

/**
 * Obtener información sobre el modelo
 */
export async function getModelInfo() {
  try {
    const response = await fetch(`${API_BASE_URL}/model/info`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo info del modelo:', error);
    throw error;
  }
}

/**
 * Realizar predicción de AQI por coordenadas (POST)
 * 
 * @param {number} latitud - Latitud (-90 a 90)
 * @param {number} longitud - Longitud (-180 a 180)
 * @param {string} nombreUbicacion - Nombre opcional de la ubicación
 * @returns {Promise<Object>} Objeto con las predicciones
 */
export async function predictAQI(latitud, longitud, nombreUbicacion = null) {
  try {
    const requestBody = {
      latitud,
      longitud,
    };
    
    if (nombreUbicacion) {
      requestBody.nombre_ubicacion = nombreUbicacion;
    }
    
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error en predicción:', error);
    throw error;
  }
}

/**
 * Realizar predicción usando query parameters (GET)
 * Útil para requests simples o desde el navegador
 * 
 * @param {number} lat - Latitud
 * @param {number} lon - Longitud
 * @param {string} name - Nombre opcional
 */
export async function predictByCoordinates(lat, lon, name = null) {
  try {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
    });
    
    if (name) {
      params.append('name', name);
    }
    
    const url = `${API_BASE_URL}/predict/coordinates?${params.toString()}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error en predicción por coordenadas:', error);
    throw error;
  }
}

/**
 * Obtener predicción para una ciudad predefinida
 * 
 * @param {string} cityName - Nombre de la ciudad (los-angeles, new-york, etc.)
 */
export async function predictByCity(cityName) {
  try {
    const response = await fetch(`${API_BASE_URL}/predict/city/${cityName}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error en predicción por ciudad:', error);
    throw error;
  }
}

/**
 * Obtener clasificación de calidad del aire según AQI
 * 
 * @param {number} aqi - Valor de AQI
 * @returns {Object} Objeto con categoría, color y mensaje
 */
export function getAQIClassification(aqi) {
  if (aqi <= 12) {
    return {
      categoria: 'Excelente',
      color: '#00E400',
      mensaje: 'Calidad del aire ideal',
    };
  } else if (aqi <= 35.4) {
    return {
      categoria: 'Bueno',
      color: '#FFFF00',
      mensaje: 'Calidad del aire aceptable',
    };
  } else if (aqi <= 55.4) {
    return {
      categoria: 'Aceptable',
      color: '#FF7E00',
      mensaje: 'Grupos sensibles deben limitar actividades prolongadas',
    };
  } else if (aqi <= 150.4) {
    return {
      categoria: 'Regular',
      color: '#FF0000',
      mensaje: 'Todos pueden experimentar efectos en la salud',
    };
  } else if (aqi <= 250.4) {
    return {
      categoria: 'Malo',
      color: '#99004C',
      mensaje: 'Alerta de salud: todos pueden experimentar efectos graves',
    };
  } else if (aqi <= 350.4) {
    return {
      categoria: 'Muy Malo',
      color: '#7E0023',
      mensaje: 'Alerta de salud de emergencia',
    };
  } else {
    return {
      categoria: 'Peligroso',
      color: '#4C0026',
      mensaje: 'Advertencia de salud de condiciones de emergencia',
    };
  }
}

/**
 * Hook de React para usar en componentes funcionales
 * Ejemplo de uso:
 * 
 * const { prediction, loading, error, predict } = useAQIPrediction();
 * 
 * <button onClick={() => predict(lat, lon)}>Predecir</button>
 */
export function useAQIPrediction() {
  const [prediction, setPrediction] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const predict = async (latitud, longitud, nombreUbicacion = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await predictAQI(latitud, longitud, nombreUbicacion);
      setPrediction(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { prediction, loading, error, predict };
}

// Exportar constantes útiles
export const CIUDADES_DISPONIBLES = [
  { id: 'los-angeles', nombre: 'Los Angeles, CA', lat: 34.0522, lon: -118.2437 },
  { id: 'new-york', nombre: 'New York, NY', lat: 40.7128, lon: -74.0060 },
  { id: 'mexico-city', nombre: 'Ciudad de México', lat: 19.4326, lon: -99.1332 },
  { id: 'madrid', nombre: 'Madrid, España', lat: 40.4168, lon: -3.7038 },
];

export const HORIZONTES = ['3h', '6h', '12h', '24h'];
