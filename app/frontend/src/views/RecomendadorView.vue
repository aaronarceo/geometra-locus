<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { esAbort, getCafes, getTags, mensajeDeError, recomendar } from '../api/client'
import BigramaChip from '../components/BigramaChip.vue'
import BuscadorCafe from '../components/BuscadorCafe.vue'
import BurbujaLLM from '../components/BurbujaLLM.vue'
import MapaLeaflet from '../components/MapaLeaflet.vue'
import MinichatLLM from '../components/MinichatLLM.vue'
import TarjetaCafe from '../components/TarjetaCafe.vue'
import type { Cafeteria, Pin, TipoPin } from '../types/cafeteria'

type ModoUI = 'A' | 'B'

const TOP_K_MODO_A = 3
const TOP_K_MODO_B = 10
const RESULTADOS_PARA_EXPLICAR = 3
const N_SUGERENCIAS = 6

const modo = ref<ModoUI>('A')
const chatAbierto = ref(false)

// Listado completo (buscador del Modo A)
const cafes = ref<Cafeteria[]>([])
const errorCafes = ref<string | null>(null)

// Modo A: por cafetería similar
const referencia = ref<Cafeteria | null>(null)
const similares = ref<Cafeteria[]>([])
const cargandoA = ref(false)
const errorA = ref<string | null>(null)

// Modo B: por características (el vocabulario lo entrega el backend en GET /tags)
const tags = ref<string[]>([])
const errorTags = ref<string | null>(null)
const activos = ref<string[]>([])
const resultadosB = ref<Cafeteria[]>([])
const cargandoB = ref(false)
const errorB = ref<string | null>(null)

// Un controlador por modo: una petición nueva cancela la anterior y evita
// que una respuesta vieja pise a la más reciente (clics rápidos en los chips).
let controladorCafes: AbortController | null = null
let controladorTags: AbortController | null = null
let controladorA: AbortController | null = null
let controladorB: AbortController | null = null

// --- Carga inicial -----------------------------------------------------------

async function cargarCafes(): Promise<void> {
  errorCafes.value = null
  controladorCafes?.abort()
  const controlador = new AbortController()
  controladorCafes = controlador
  try {
    const datos = await getCafes(controlador.signal)
    if (controlador === controladorCafes) cafes.value = datos
  } catch (error) {
    if (esAbort(error)) return
    errorCafes.value = mensajeDeError(error)
  }
}

async function cargarTags(): Promise<void> {
  errorTags.value = null
  controladorTags?.abort()
  const controlador = new AbortController()
  controladorTags = controlador
  try {
    const datos = await getTags(controlador.signal)
    if (controlador === controladorTags) tags.value = datos.tags
  } catch (error) {
    if (esAbort(error)) return
    errorTags.value = mensajeDeError(error)
  }
}

onMounted(() => {
  void cargarCafes()
  void cargarTags()
})

onBeforeUnmount(() => {
  controladorCafes?.abort()
  controladorTags?.abort()
  controladorA?.abort()
  controladorB?.abort()
})

// --- Modo A ------------------------------------------------------------------

async function cargarSimilares(): Promise<void> {
  const cafe = referencia.value
  if (!cafe) return
  controladorA?.abort()
  const controlador = new AbortController()
  controladorA = controlador
  cargandoA.value = true
  errorA.value = null
  try {
    const datos = await recomendar(
      { query: cafe.place_id, top_k: TOP_K_MODO_A, mode: 'place' },
      controlador.signal,
    )
    if (controlador === controladorA) similares.value = datos
  } catch (error) {
    if (esAbort(error)) return
    errorA.value = mensajeDeError(error)
  } finally {
    if (controlador === controladorA) cargandoA.value = false
  }
}

function seleccionarCafe(cafe: Cafeteria): void {
  referencia.value = cafe
  similares.value = []
  void cargarSimilares()
}

function limpiarSeleccion(): void {
  controladorA?.abort()
  referencia.value = null
  similares.value = []
  cargandoA.value = false
  errorA.value = null
}

// Sugerencias al azar: llenan el panel y el mapa mientras no hay una cafetería elegida.
const sugerencias = ref<Cafeteria[]>([])

function sortearSugerencias(): void {
  // Las de baja confianza (menos de 5 reseñas con texto) darían parecidos poco fiables.
  const confiables = cafes.value.filter((c) => !c.baja_confianza)
  const copia = [...(confiables.length >= N_SUGERENCIAS ? confiables : cafes.value)]
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copia[i], copia[j]] = [copia[j], copia[i]]
  }
  sugerencias.value = copia.slice(0, N_SUGERENCIAS)
}

// El listado llega después de montar la vista: se sortea una sola vez, cuando ya hay datos.
watch(
  cafes,
  (lista) => {
    if (sugerencias.value.length === 0 && lista.length > 0) sortearSugerencias()
  },
  { immediate: true },
)

function alPulsarPin(id: string): void {
  if (modo.value !== 'A' || referencia.value) return
  const cafe = sugerencias.value.find((c) => c.place_id === id)
  if (cafe) seleccionarCafe(cafe)
}

// --- Modo B ------------------------------------------------------------------

async function cargarPorCaracteristicas(): Promise<void> {
  controladorB?.abort()
  if (activos.value.length === 0) {
    resultadosB.value = []
    cargandoB.value = false
    errorB.value = null
    return
  }
  const controlador = new AbortController()
  controladorB = controlador
  cargandoB.value = true
  errorB.value = null
  try {
    const datos = await recomendar(
      { query: activos.value.join(' '), top_k: TOP_K_MODO_B, mode: 'text' },
      controlador.signal,
    )
    if (controlador === controladorB) resultadosB.value = datos
  } catch (error) {
    if (esAbort(error)) return
    errorB.value = mensajeDeError(error)
  } finally {
    if (controlador === controladorB) cargandoB.value = false
  }
}

function alternarBigrama(bigrama: string): void {
  activos.value = activos.value.includes(bigrama)
    ? activos.value.filter((b) => b !== bigrama)
    : [...activos.value, bigrama]
  void cargarPorCaracteristicas()
}

function limpiarCaracteristicas(): void {
  activos.value = []
  void cargarPorCaracteristicas()
}

// --- Mapa --------------------------------------------------------------------

function aPin(cafe: Cafeteria, tipo: TipoPin): Pin {
  return { id: cafe.place_id, lat: cafe.lat, lon: cafe.lon, nombre: cafe.nombre, tipo }
}

const pines = computed<Pin[]>(() => {
  if (modo.value === 'A') {
    if (!referencia.value) return sugerencias.value.map((c) => aPin(c, 'sugerencia'))
    return [
      aPin(referencia.value, 'principal'),
      ...similares.value.map((c) => aPin(c, 'secundario')),
    ]
  }
  return resultadosB.value.map((c) => aPin(c, 'principal'))
})

const mensajeMapaVacio = computed(() => {
  if (modo.value !== 'B') return ''
  if (activos.value.length === 0) return 'Selecciona características'
  if (!cargandoB.value && !errorB.value && resultadosB.value.length === 0) {
    return 'Ninguna cafetería cumple esa combinación'
  }
  return ''
})

// --- Minichat (solo Modo A) --------------------------------------------------

// Oculto por decisión del proyecto: el resto del código queda en su sitio y se vuelve a mostrar
// arrancando el front con VITE_CHAT=1. Hoy /explain y /chat del backend devuelven texto de muestra.
const CHAT_HABILITADO = import.meta.env.VITE_CHAT === '1'

const resultadosParaChat = computed(() =>
  similares.value.slice(0, RESULTADOS_PARA_EXPLICAR).map((c) => c.nombre),
)

// La burbuja solo aparece en el Modo A, con una cafetería elegida que ya tiene recomendaciones.
const mostrarBurbuja = computed(
  () =>
    CHAT_HABILITADO &&
    modo.value === 'A' &&
    !chatAbierto.value &&
    referencia.value !== null &&
    similares.value.length > 0,
)

// Cambiar de modo o de selección invalida la conversación en curso.
watch([modo, referencia], () => {
  chatAbierto.value = false
})
</script>

<template>
  <div class="flex flex-col bg-color1 lg:h-[calc(100vh-4rem)]">
    <!-- Zona superior: toggle + buscador (Modo A) -->
    <div class="shrink-0 border-b border-white/10 px-4 py-3 sm:px-6">
      <div class="flex flex-col gap-3 md:flex-row md:items-center">
        <div
          class="inline-flex shrink-0 self-start rounded-full bg-white/10 p-1"
          role="group"
          aria-label="Modo de recomendación"
        >
          <button
            type="button"
            :aria-pressed="modo === 'A'"
            class="rounded-full px-4 py-1.5 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-color3"
            :class="modo === 'A' ? 'bg-color2 text-white' : 'text-white/70 hover:text-white'"
            @click="modo = 'A'"
          >
            Por cafetería similar
          </button>
          <button
            type="button"
            :aria-pressed="modo === 'B'"
            class="rounded-full px-4 py-1.5 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-color3"
            :class="modo === 'B' ? 'bg-color2 text-white' : 'text-white/70 hover:text-white'"
            @click="modo = 'B'"
          >
            Por características
          </button>
        </div>

        <div v-if="modo === 'A'" class="w-full md:max-w-xl">
          <BuscadorCafe
            :cafes="cafes"
            :seleccionada="referencia"
            :deshabilitado="cafes.length === 0"
            @seleccionar="seleccionarCafe"
            @limpiar="limpiarSeleccion"
          />
          <p v-if="errorCafes" class="mt-2 text-xs text-white/70" role="alert">
            {{ errorCafes }}
            <button type="button" class="ml-1 underline hover:text-white" @click="cargarCafes">
              Reintentar
            </button>
          </p>
        </div>
      </div>
    </div>

    <!-- Mapa (60%) + panel derecho (40%). El mapa vive fuera del cambio de modo: nunca se remonta. -->
    <div class="flex min-h-0 flex-1 flex-col lg:flex-row">
      <div class="h-[45vh] w-full shrink-0 lg:h-full lg:w-3/5">
        <MapaLeaflet :pines="pines" :mensaje-vacio="mensajeMapaVacio" @seleccionar="alPulsarPin" />
      </div>

      <section
        class="relative flex h-[70vh] w-full min-w-0 flex-col border-t border-white/10 bg-color1 lg:h-auto lg:min-h-0 lg:w-2/5 lg:border-l lg:border-t-0"
        aria-label="Resultados"
      >
        <Transition name="fade" mode="out-in">
          <MinichatLLM
            v-if="chatAbierto"
            key="chat"
            modo="place"
            :seleccion="referencia?.nombre ?? ''"
            :resultados="resultadosParaChat"
            class="flex-1"
            @volver="chatAbierto = false"
          />

          <div v-else key="contenido" class="flex min-h-0 flex-1 flex-col">
            <!-- ================= Modo A ================= -->
            <template v-if="modo === 'A'">
              <div v-if="!referencia" class="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
                <div
                  class="flex items-center gap-3 rounded-2xl border-2 border-white/70 bg-gradient-to-br from-white to-color5 p-4 text-color1 shadow-tarjeta"
                >
                  <span
                    class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-color2/10 text-color2"
                  >
                    <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
                      <circle cx="11" cy="11" r="7" />
                      <path d="M20 20l-3.5-3.5" />
                    </svg>
                  </span>
                  <div>
                    <p class="font-semibold leading-tight">Busca una cafetería para comenzar</p>
                    <p class="mt-0.5 text-sm text-gray-600">
                      O elige una de estas para ver cuáles se le parecen.
                    </p>
                  </div>
                </div>

                <div v-if="sugerencias.length > 0" class="space-y-3">
                  <div class="flex items-center justify-between">
                    <p class="text-xs font-semibold uppercase tracking-wide text-white/50">
                      Para empezar
                    </p>
                    <button
                      type="button"
                      class="inline-flex items-center gap-1.5 rounded-full border border-white/15 px-3 py-1 text-xs font-medium text-white/80 transition hover:bg-white/10 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-color3"
                      @click="sortearSugerencias"
                    >
                      <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M21 12a9 9 0 0 1-15.5 6.2L3 16M3 12A9 9 0 0 1 18.5 5.8L21 8" />
                        <path d="M21 3v5h-5M3 21v-5h5" />
                      </svg>
                      Otras cafeterías
                    </button>
                  </div>
                  <TarjetaCafe
                    v-for="cafe in sugerencias"
                    :key="cafe.place_id"
                    :cafeteria="cafe"
                    seleccionable
                    @seleccionar="seleccionarCafe"
                  />
                </div>

                <template v-else-if="!errorCafes">
                  <div
                    v-for="n in 3"
                    :key="n"
                    class="h-32 animate-pulse rounded-2xl bg-white/10"
                    aria-hidden="true"
                  ></div>
                </template>
              </div>

              <div
                v-else
                class="min-h-0 flex-1 space-y-3 overflow-y-auto p-4"
                :class="{ 'pb-24': CHAT_HABILITADO }"
              >
                <TarjetaCafe :cafeteria="referencia" es-referencia />

                <template v-if="cargandoA && similares.length === 0">
                  <div
                    v-for="n in TOP_K_MODO_A"
                    :key="n"
                    class="h-32 animate-pulse rounded-2xl bg-white/10"
                    aria-hidden="true"
                  ></div>
                </template>

                <div
                  v-else-if="errorA"
                  class="rounded-2xl border border-color3 bg-color2/30 p-4 text-sm text-white"
                  role="alert"
                >
                  No se pudieron cargar las recomendaciones. {{ errorA }}
                  <button type="button" class="ml-1 font-semibold underline" @click="cargarSimilares">
                    Reintentar
                  </button>
                </div>

                <template v-else>
                  <TarjetaCafe
                    v-for="cafe in similares"
                    :key="cafe.place_id"
                    :cafeteria="cafe"
                    mostrar-score
                  />
                </template>
              </div>
            </template>

            <!-- ================= Modo B ================= -->
            <template v-else>
              <div class="shrink-0 border-b border-white/10 p-4">
                <div class="mb-3 flex items-center justify-between gap-3">
                  <p class="text-xs font-semibold uppercase tracking-wide text-white/50">
                    ¿Qué buscas en una cafetería?
                  </p>
                  <button
                    v-if="activos.length > 0"
                    type="button"
                    class="shrink-0 rounded-full border border-white/15 px-3 py-0.5 text-xs font-medium text-white/80 transition hover:bg-white/10 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-color3"
                    @click="limpiarCaracteristicas"
                  >
                    Limpiar ({{ activos.length }})
                  </button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <BigramaChip
                    v-for="bigrama in tags"
                    :key="bigrama"
                    :texto="bigrama"
                    :activo="activos.includes(bigrama)"
                    @toggle="alternarBigrama"
                  />
                </div>
                <p v-if="errorTags" class="mt-2 text-xs text-white/70" role="alert">
                  No se pudieron cargar las características. {{ errorTags }}
                  <button type="button" class="ml-1 underline hover:text-white" @click="cargarTags">
                    Reintentar
                  </button>
                </p>
              </div>

              <div
                v-if="activos.length === 0"
                class="m-4 flex flex-1 items-center justify-center rounded-2xl bg-color5 p-8 text-center text-lg font-medium text-color1"
              >
                Selecciona una o más características para ver cafeterías
              </div>

              <div v-else class="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
                <p class="text-sm text-white/60" aria-live="polite">
                  <template v-if="cargandoB">Actualizando…</template>
                  <template v-else>
                    {{ resultadosB.length }}
                    {{ resultadosB.length === 1 ? 'cafetería' : 'cafeterías' }}
                  </template>
                </p>

                <div
                  v-if="errorB"
                  class="rounded-2xl border border-color3 bg-color2/30 p-4 text-sm text-white"
                  role="alert"
                >
                  No se pudieron cargar los resultados. {{ errorB }}
                  <button
                    type="button"
                    class="ml-1 font-semibold underline"
                    @click="cargarPorCaracteristicas"
                  >
                    Reintentar
                  </button>
                </div>

                <TarjetaCafe
                  v-for="cafe in resultadosB"
                  :key="cafe.place_id"
                  :cafeteria="cafe"
                  mostrar-score
                />

                <p
                  v-if="!cargandoB && !errorB && resultadosB.length === 0"
                  class="rounded-2xl bg-color5 p-6 text-center font-medium text-color1"
                >
                  Ninguna cafetería cumple esa combinación
                </p>
              </div>
            </template>
          </div>
        </Transition>
      </section>
    </div>

    <Transition name="burbuja">
      <BurbujaLLM v-if="mostrarBurbuja" @abrir="chatAbierto = true" />
    </Transition>
  </div>
</template>
