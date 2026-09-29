// Interfaces del contrato con el backend (ver app/CLAUDE.md)

export type Sentimiento = 'Positivo' | 'Neutro' | 'Negativo'

/** "place": el query es un place_id. "text": el query son los tags elegidos, unidos por espacios. */
export type ModoRecomendacion = 'place' | 'text'

export interface Cafeteria {
  place_id: string
  nombre: string
  /** Calle y colonia, sin código postal: distingue sucursales del mismo nombre. */
  direccion: string
  colonia?: string | null // aún no hay colonias en los datos
  lat: number
  lon: number
  rating: number
  sentimiento: Sentimiento
  atributos: string[]
  /** Menos de 5 reseñas con texto: su similitud es menos confiable. */
  baja_confianza?: boolean
  n_resenas_texto?: number
  score_similitud?: number // solo en resultados de /recommend
}

export interface TagsResponse {
  tags: string[]
}

export interface RecomendacionResponse {
  referencia?: Cafeteria // solo en mode: "place"
  cafeterias: Cafeteria[]
}

export interface ExplicacionResponse {
  explicacion: string
}

// --- Requests ---------------------------------------------------------------

export interface RecomendarRequest {
  query: string
  top_k: number
  mode: ModoRecomendacion
}

export interface ExplicarRequest {
  modo: ModoRecomendacion
  seleccion: string
  resultados: string[]
}

// --- Chat (POST /chat, ampliación del contrato) -----------------------------

export interface MensajeChat {
  rol: 'usuario' | 'asistente'
  contenido: string
}

export interface ChatRequest extends ExplicarRequest {
  historial: MensajeChat[]
  pregunta: string
}

export interface ChatResponse {
  respuesta: string
}

// --- Mapa -------------------------------------------------------------------

/**
 * "principal" se dibuja en color2 (rojo); "secundario" en gris; "sugerencia" en color1 (oscuro):
 * cafeterías al azar que se muestran mientras no hay selección y se pueden elegir con un clic.
 */
export type TipoPin = 'principal' | 'secundario' | 'sugerencia'

export interface Pin {
  id: string
  lat: number
  lon: number
  nombre: string
  tipo: TipoPin
}
