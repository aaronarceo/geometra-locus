<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { chatear, esAbort, explicar } from '../api/client'
import type { MensajeChat, ModoRecomendacion } from '../types/cafeteria'

const props = defineProps<{
  modo: ModoRecomendacion
  /** Nombre del café de referencia (Modo A) o bigramas activos (Modo B). */
  seleccion: string
  /** Nombres de las cafeterías recomendadas. */
  resultados: string[]
}>()

const emit = defineEmits<{
  volver: []
}>()

interface MensajeUI extends MensajeChat {
  id: number
  error: boolean
}

const mensajes = ref<MensajeUI[]>([])
const entrada = ref('')
const pensando = ref(false)
const explicacionFallida = ref(false)
const zonaMensajes = ref<HTMLElement | null>(null)

let contador = 0
const controlador = new AbortController()

async function bajarScroll(): Promise<void> {
  await nextTick()
  const zona = zonaMensajes.value
  if (zona) zona.scrollTop = zona.scrollHeight
}

function agregar(rol: MensajeChat['rol'], contenido: string, error = false): void {
  contador += 1
  mensajes.value.push({ id: contador, rol, contenido, error })
  void bajarScroll()
}

async function cargarExplicacion(): Promise<void> {
  explicacionFallida.value = false
  pensando.value = true
  try {
    const respuesta = await explicar(
      { modo: props.modo, seleccion: props.seleccion, resultados: props.resultados },
      controlador.signal,
    )
    agregar('asistente', respuesta.explicacion)
  } catch (error) {
    if (esAbort(error)) return
    explicacionFallida.value = true
    agregar('asistente', 'No pude conectarme con el asistente para explicar las recomendaciones.', true)
  } finally {
    pensando.value = false
  }
}

async function enviar(): Promise<void> {
  const pregunta = entrada.value.trim()
  if (!pregunta || pensando.value) return

  // El historial que se manda es la conversación previa; la pregunta va aparte.
  const historial: MensajeChat[] = mensajes.value
    .filter((m) => !m.error)
    .map(({ rol, contenido }) => ({ rol, contenido }))

  agregar('usuario', pregunta)
  entrada.value = ''
  pensando.value = true
  try {
    const respuesta = await chatear(
      {
        modo: props.modo,
        seleccion: props.seleccion,
        resultados: props.resultados,
        historial,
        pregunta,
      },
      controlador.signal,
    )
    agregar('asistente', respuesta.respuesta)
  } catch (error) {
    if (esAbort(error)) return
    agregar('asistente', 'No pude responder en este momento. Intenta de nuevo.', true)
  } finally {
    pensando.value = false
  }
}

async function reintentar(): Promise<void> {
  mensajes.value = []
  await cargarExplicacion()
}

onMounted(() => {
  void cargarExplicacion()
})

onBeforeUnmount(() => controlador.abort())
</script>

<template>
  <section class="flex h-full min-h-0 flex-col bg-color1" aria-label="Asistente Geometra">
    <header class="flex shrink-0 items-center gap-3 border-b border-white/10 px-4 py-3">
      <button
        type="button"
        class="rounded-full bg-white/10 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
        @click="emit('volver')"
      >
        ← Volver
      </button>
      <h2 class="text-base font-semibold">Asistente Geometra</h2>
    </header>

    <div
      ref="zonaMensajes"
      class="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-4"
      role="log"
      aria-live="polite"
    >
      <div
        v-for="mensaje in mensajes"
        :key="mensaje.id"
        class="flex"
        :class="mensaje.rol === 'usuario' ? 'justify-end' : 'justify-start'"
      >
        <p
          class="max-w-[85%] whitespace-pre-line rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
          :class="[
            mensaje.rol === 'usuario'
              ? 'rounded-br-sm bg-color2 text-white'
              : 'rounded-bl-sm bg-color5 text-color1',
            mensaje.error ? 'ring-2 ring-color3' : '',
          ]"
        >
          {{ mensaje.contenido }}
        </p>
      </div>

      <div v-if="pensando" class="flex justify-start" aria-label="El asistente está escribiendo">
        <span class="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-color5 px-4 py-3">
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-color1/60 [animation-delay:-0.3s]"></span>
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-color1/60 [animation-delay:-0.15s]"></span>
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-color1/60"></span>
        </span>
      </div>

      <div v-if="explicacionFallida && !pensando" class="flex justify-start">
        <button
          type="button"
          class="rounded-full border border-white/20 px-3 py-1 text-xs font-medium text-white transition hover:bg-white/10"
          @click="reintentar"
        >
          Reintentar
        </button>
      </div>
    </div>

    <form
      class="flex shrink-0 gap-2 border-t border-white/10 p-4"
      @submit.prevent="enviar"
    >
      <input
        v-model="entrada"
        type="text"
        placeholder="Pregunta sobre estos resultados"
        aria-label="Escribe tu pregunta"
        class="min-w-0 flex-1 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white placeholder:text-white/40 focus:border-color3 focus:outline-none"
      />
      <button
        type="submit"
        :disabled="pensando || !entrada.trim()"
        class="rounded-full bg-color2 px-5 py-2 text-sm font-semibold text-white transition hover:bg-color3 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-color2"
      >
        Enviar
      </button>
    </form>
  </section>
</template>
