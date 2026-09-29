import type {
  Cafeteria,
  ChatRequest,
  ChatResponse,
  ExplicacionResponse,
  ExplicarRequest,
  RecomendarRequest,
  TagsResponse,
} from '../types/cafeteria'

// Desarrollo: '/api' (Vite lo redirige a localhost:8000).
// Producción: VITE_API_URL apunta directo al backend en Railway.
const URL_BASE: string = (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '') || '/api'

export class ApiError extends Error {
  readonly status: number

  constructor(mensaje: string, status: number) {
    super(mensaje)
    this.name = 'ApiError'
    this.status = status
  }
}

async function solicitar<T>(ruta: string, init: RequestInit = {}): Promise<T> {
  let respuesta: Response
  try {
    respuesta = await fetch(`${URL_BASE}${ruta}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init.headers },
    })
  } catch (error) {
    if (esAbort(error)) throw error
    throw new ApiError('No se pudo conectar con el servidor.', 0)
  }
  if (!respuesta.ok) {
    throw new ApiError(`El servidor respondió ${respuesta.status}.`, respuesta.status)
  }
  return (await respuesta.json()) as T
}

function post<T>(ruta: string, cuerpo: object, signal?: AbortSignal): Promise<T> {
  return solicitar<T>(ruta, { method: 'POST', body: JSON.stringify(cuerpo), signal })
}

export const getCafes = (signal?: AbortSignal): Promise<Cafeteria[]> =>
  solicitar<Cafeteria[]>('/cafes', { signal })

export const getTags = (signal?: AbortSignal): Promise<TagsResponse> =>
  solicitar<TagsResponse>('/tags', { signal })

export const recomendar = (cuerpo: RecomendarRequest, signal?: AbortSignal): Promise<Cafeteria[]> =>
  post<Cafeteria[]>('/recommend', cuerpo, signal)

export const explicar = (cuerpo: ExplicarRequest, signal?: AbortSignal): Promise<ExplicacionResponse> =>
  post<ExplicacionResponse>('/explain', cuerpo, signal)

export const chatear = (cuerpo: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> =>
  post<ChatResponse>('/chat', cuerpo, signal)

/** true si el error viene de cancelar la petición con AbortController. */
export function esAbort(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export function mensajeDeError(error: unknown): string {
  return error instanceof ApiError ? error.message : 'Ocurrió un error inesperado.'
}
