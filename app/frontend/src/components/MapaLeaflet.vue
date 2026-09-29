<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import type { Pin, TipoPin } from '../types/cafeteria'

const props = withDefaults(
  defineProps<{
    /** Pines a dibujar. Al cambiar se actualizan las marcas sin remontar el mapa. */
    pines: Pin[]
    /** Mensaje sobre el mapa mientras no hay pines (vacío: no se muestra). */
    mensajeVacio?: string
  }>(),
  { mensajeVacio: '' },
)

const emit = defineEmits<{
  /** Se pulsó el pin de la cafetería con ese `id` (place_id). */
  seleccionar: [id: string]
}>()

const CENTRO_MERIDA: L.LatLngTuple = [20.9674, -89.5926]
const ZOOM_INICIAL = 13
const ZOOM_MAXIMO_AJUSTE = 15
const DEMORA_DESTRUCCION_MS = 400

const COLOR_PIN: Record<TipoPin, string> = {
  principal: '#77181e', // color2
  secundario: '#6b7280', // gris
  sugerencia: '#282832', // color1
}

const contenedor = ref<HTMLDivElement | null>(null)

// Los objetos de Leaflet no deben ser reactivos (Vue los envolvería en proxies).
let mapa: L.Map | null = null
let capaPines: L.LayerGroup | null = null
let observador: ResizeObserver | null = null
let firmaDibujada = ''

function crearIcono(tipo: TipoPin): L.DivIcon {
  const svg =
    `<svg width="30" height="40" viewBox="0 0 30 40" xmlns="http://www.w3.org/2000/svg">` +
    `<path d="M15 39C15 39 28 24.5 28 14.5A13 13 0 0 0 2 14.5C2 24.5 15 39 15 39Z" ` +
    `fill="${COLOR_PIN[tipo]}" stroke="#ffffff" stroke-width="2"/>` +
    `<circle cx="15" cy="14.5" r="5" fill="#ffffff"/></svg>`
  return L.divIcon({
    html: svg,
    className: `pin-locus pin-${tipo}`,
    iconSize: [30, 40],
    iconAnchor: [15, 39],
    tooltipAnchor: [0, -34],
  })
}

function firma(pines: Pin[]): string {
  return pines.map((p) => `${p.id}:${p.tipo}:${p.lat}:${p.lon}`).join('|')
}

function dibujar(pines: Pin[]): void {
  if (!mapa || !capaPines) return
  const nuevaFirma = firma(pines)
  if (nuevaFirma === firmaDibujada) return
  firmaDibujada = nuevaFirma

  capaPines.clearLayers()
  for (const pin of pines) {
    L.marker([pin.lat, pin.lon], {
      icon: crearIcono(pin.tipo),
      zIndexOffset: pin.tipo === 'principal' ? 1000 : 0,
      alt: pin.nombre,
    })
      .bindTooltip(pin.nombre, { direction: 'top' })
      .on('click', () => emit('seleccionar', pin.id))
      .addTo(capaPines)
  }

  // Sin animación a propósito: Leaflet descarta setView/fitBounds pedidos mientras
  // hay una animación de zoom en curso, y aquí los pines cambian en ráfaga (primero
  // la referencia y milisegundos después las recomendaciones).
  if (pines.length === 0) {
    mapa.setView(CENTRO_MERIDA, ZOOM_INICIAL, { animate: false })
  } else {
    const limites = L.latLngBounds(pines.map((p): L.LatLngTuple => [p.lat, p.lon]))
    mapa.fitBounds(limites, { padding: [60, 60], maxZoom: ZOOM_MAXIMO_AJUSTE, animate: false })
  }
}

onMounted(() => {
  const el = contenedor.value
  if (!el) return

  mapa = L.map(el, { center: CENTRO_MERIDA, zoom: ZOOM_INICIAL })
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa)
  capaPines = L.layerGroup().addTo(mapa)

  // El panel cambia de tamaño (layout responsivo): el mapa debe recalcularse.
  observador = new ResizeObserver(() => mapa?.invalidateSize())
  observador.observe(el)

  dibujar(props.pines)
})

watch(
  () => props.pines,
  (pines) => dibujar(pines),
)

onBeforeUnmount(() => {
  observador?.disconnect()
  const mapaActual = mapa
  mapa = null
  capaPines = null
  if (!mapaActual) return
  // Leaflet cierra la animación de zoom con un temporizador de 250 ms. Si el mapa
  // se destruye antes, ese temporizador falla al leer un panel que ya no existe.
  // Se difiere remove() para que la animación termine primero.
  mapaActual.stop()
  window.setTimeout(() => mapaActual.remove(), DEMORA_DESTRUCCION_MS)
})
</script>

<template>
  <!-- isolate: contiene los z-index internos de Leaflet para que no tapen menús ni la burbuja -->
  <div class="relative isolate h-full min-h-[16rem] w-full">
    <div
      ref="contenedor"
      class="h-full w-full"
      role="region"
      aria-label="Mapa de cafeterías de Mérida"
    ></div>

    <Transition name="fade">
      <div
        v-if="pines.length === 0 && mensajeVacio"
        class="pointer-events-none absolute inset-0 z-[1000] flex items-center justify-center p-6"
      >
        <p class="rounded-full bg-color1/90 px-5 py-2 text-sm font-medium text-white shadow-lg">
          {{ mensajeVacio }}
        </p>
      </div>
    </Transition>
  </div>
</template>
