<script setup lang="ts">
import { computed } from 'vue'
import type { Cafeteria, Sentimiento } from '../types/cafeteria'

const props = withDefaults(
  defineProps<{
    cafeteria: Cafeteria
    /** Marca la tarjeta como "Tu selección" (cafetería de referencia del Modo A). */
    esReferencia?: boolean
    /** Muestra el badge de similitud (solo tiene sentido en recomendaciones). */
    mostrarScore?: boolean
    /** La tarjeta se puede pulsar (o activar con Enter/Espacio) para elegir esa cafetería. */
    seleccionable?: boolean
  }>(),
  { esReferencia: false, mostrarScore: false, seleccionable: false },
)

const emit = defineEmits<{
  seleccionar: [cafeteria: Cafeteria]
}>()

function elegir(): void {
  if (props.seleccionable) emit('seleccionar', props.cafeteria)
}

const RUTA_ESTRELLA =
  'M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9 4.8 17.6l1-5.8L1.5 7.7l5.9-.9L10 1.5z'

const claseSentimiento: Record<Sentimiento, string> = {
  Positivo: 'bg-emerald-100 text-emerald-800',
  Neutro: 'bg-gray-200 text-gray-700',
  Negativo: 'bg-color3 text-white',
}

// Ancho del relleno de estrellas: rating sobre 5, en porcentaje.
const porcentajeRating = computed(() =>
  Math.min(100, Math.max(0, (props.cafeteria.rating / 5) * 100)),
)

const atributosVisibles = computed(() => props.cafeteria.atributos.slice(0, 3))

const porcentajeScore = computed(() =>
  props.cafeteria.score_similitud === undefined
    ? null
    : Math.round(props.cafeteria.score_similitud * 100),
)
</script>

<template>
  <article
    class="relative overflow-hidden rounded-2xl border-2 bg-gradient-to-br from-white to-color5 p-4 text-color1 shadow-tarjeta transition duration-200"
    :class="[
      esReferencia ? 'border-color2 ring-4 ring-color2/25' : 'border-white/70',
      seleccionable
        ? 'cursor-pointer hover:-translate-y-0.5 hover:border-color2 hover:shadow-tarjeta-hover focus-visible:border-color2 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-color2/25'
        : '',
    ]"
    :data-place-id="cafeteria.place_id"
    :role="seleccionable ? 'button' : undefined"
    :tabindex="seleccionable ? 0 : undefined"
    :aria-label="seleccionable ? `Ver cafeterías parecidas a ${cafeteria.nombre}` : undefined"
    @click="elegir"
    @keydown.enter.self.prevent="elegir"
    @keydown.space.self.prevent="elegir"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h3 class="truncate text-base font-bold leading-tight">{{ cafeteria.nombre }}</h3>
        <p class="mt-0.5 truncate text-xs text-gray-600" :title="cafeteria.direccion">
          {{ cafeteria.direccion }}
        </p>
      </div>
      <span
        v-if="esReferencia"
        class="shrink-0 rounded-full bg-color2 px-2.5 py-1 text-xs font-semibold text-white"
      >
        Tu selección
      </span>
      <span
        v-else-if="mostrarScore && porcentajeScore !== null"
        class="shrink-0 rounded-full bg-color1 px-2.5 py-1 text-[11px] font-semibold text-white"
      >
        {{ porcentajeScore }}% similar
      </span>
    </div>

    <div class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
      <div class="flex items-center gap-2">
        <span
          class="relative inline-block h-4 w-20"
          role="img"
          :aria-label="`Calificación ${cafeteria.rating.toFixed(1)} de 5`"
        >
          <span class="absolute inset-0 flex text-gray-300">
            <svg
              v-for="n in 5"
              :key="n"
              class="h-4 w-4 shrink-0"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path :d="RUTA_ESTRELLA" />
            </svg>
          </span>
          <span
            class="absolute inset-y-0 left-0 flex overflow-hidden text-amber-500"
            :style="{ width: `${porcentajeRating}%` }"
          >
            <svg
              v-for="n in 5"
              :key="n"
              class="h-4 w-4 shrink-0"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path :d="RUTA_ESTRELLA" />
            </svg>
          </span>
        </span>
        <span class="text-sm font-semibold">{{ cafeteria.rating.toFixed(1) }}</span>
      </div>

      <span
        class="rounded-full px-2.5 py-0.5 text-xs font-medium"
        :class="claseSentimiento[cafeteria.sentimiento]"
      >
        {{ cafeteria.sentimiento }}
      </span>

      <span
        v-if="cafeteria.baja_confianza"
        class="rounded-full border border-color1/30 px-2.5 py-0.5 text-xs font-medium text-color1/70"
        title="Tiene menos de 5 reseñas con texto: su parecido es menos confiable"
      >
        Pocas reseñas
      </span>
    </div>

    <ul v-if="atributosVisibles.length" class="mt-3 flex flex-wrap gap-1.5">
      <li
        v-for="atributo in atributosVisibles"
        :key="atributo"
        class="rounded-full bg-color4 px-2.5 py-0.5 text-xs font-medium text-color1"
      >
        {{ atributo }}
      </li>
    </ul>
  </article>
</template>
