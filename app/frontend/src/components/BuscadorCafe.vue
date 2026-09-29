<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Cafeteria } from '../types/cafeteria'

const props = defineProps<{
  cafes: Cafeteria[]
  seleccionada: Cafeteria | null
  deshabilitado?: boolean
}>()

const emit = defineEmits<{
  seleccionar: [cafe: Cafeteria]
  limpiar: []
}>()

const ID_LISTA = 'buscador-cafe-lista'

const texto = ref('')
const abierto = ref(false)
const indiceActivo = ref(0)

/** Minúsculas y sin acentos, para que "cafe" encuentre "Café". */
function normalizar(valor: string): string {
  return valor
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim()
}

const colador = new Intl.Collator('es')

/** Los nombres que no empiezan con letra ni dígito (".", "¡Ay...", "\"TROPICAL\"...") van al final. */
function empiezaConSimbolo(nombre: string): boolean {
  return !/^[\p{L}\p{N}]/u.test(nombre)
}

/** Clave de orden alfabético: sin los símbolos del inicio, para que `¡Ay!` quede junto a las "A". */
function claveAlfabetica(nombre: string): string {
  return nombre.replace(/^[^\p{L}\p{N}]+/u, '')
}

function compararNombres(a: Cafeteria, b: Cafeteria): number {
  return (
    Number(empiezaConSimbolo(a.nombre)) - Number(empiezaConSimbolo(b.nombre)) ||
    colador.compare(claveAlfabetica(a.nombre), claveAlfabetica(b.nombre))
  )
}

const sugerencias = computed<Cafeteria[]>(() => {
  const consulta = normalizar(texto.value)
  const filtradas = props.cafes.filter(
    (c) =>
      consulta === '' ||
      normalizar(c.nombre).includes(consulta) ||
      normalizar(c.direccion).includes(consulta),
  )
  return [...filtradas].sort(compararNombres)
})

// Si cambia la selección desde fuera, el input refleja el nombre elegido.
watch(
  () => props.seleccionada,
  (cafe) => {
    texto.value = cafe?.nombre ?? ''
  },
  { immediate: true },
)

watch(sugerencias, () => {
  indiceActivo.value = 0
})

function abrir(): void {
  if (!props.deshabilitado) abierto.value = true
}

function elegir(cafe: Cafeteria): void {
  texto.value = cafe.nombre
  abierto.value = false
  emit('seleccionar', cafe)
}

function alEscribir(): void {
  abierto.value = true
}

function alSalir(): void {
  abierto.value = false
  // Si no eligió nada nuevo, se restaura el nombre de la selección vigente.
  texto.value = props.seleccionada?.nombre ?? ''
}

function limpiar(): void {
  texto.value = ''
  abierto.value = false
  emit('limpiar')
}

function alTeclear(evento: KeyboardEvent): void {
  const total = sugerencias.value.length
  if (evento.key === 'ArrowDown') {
    evento.preventDefault()
    abierto.value = true
    if (total > 0) indiceActivo.value = (indiceActivo.value + 1) % total
  } else if (evento.key === 'ArrowUp') {
    evento.preventDefault()
    abierto.value = true
    if (total > 0) indiceActivo.value = (indiceActivo.value - 1 + total) % total
  } else if (evento.key === 'Enter') {
    const cafe = sugerencias.value[indiceActivo.value]
    if (abierto.value && cafe) {
      evento.preventDefault()
      elegir(cafe)
    }
  } else if (evento.key === 'Escape') {
    abierto.value = false
  }
}

const idActivo = computed(() =>
  abierto.value && sugerencias.value[indiceActivo.value]
    ? `${ID_LISTA}-${indiceActivo.value}`
    : undefined,
)
</script>

<template>
  <div class="relative w-full">
    <div class="relative">
      <svg
        class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="M20 20l-3.5-3.5" />
      </svg>
      <input
        v-model="texto"
        type="text"
        role="combobox"
        autocomplete="off"
        placeholder="Busca una cafetería que te haya gustado"
        aria-label="Buscar cafetería"
        aria-autocomplete="list"
        :aria-expanded="abierto"
        :aria-controls="ID_LISTA"
        :aria-activedescendant="idActivo"
        :disabled="deshabilitado"
        class="w-full rounded-full border border-white/10 bg-white/10 py-2 pl-10 pr-10 text-sm text-white placeholder:text-white/40 focus:border-color3 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        @focus="abrir"
        @input="alEscribir"
        @blur="alSalir"
        @keydown="alTeclear"
      />
      <button
        v-if="seleccionada"
        type="button"
        class="absolute right-2 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-white/60 transition hover:bg-white/10 hover:text-white"
        aria-label="Quitar selección"
        @mousedown.prevent
        @click="limpiar"
      >
        <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
    </div>

    <ul
      v-show="abierto"
      :id="ID_LISTA"
      role="listbox"
      class="absolute left-0 right-0 top-full z-50 mt-2 max-h-72 overflow-y-auto rounded-2xl border border-white/10 bg-color5 py-1 shadow-2xl"
    >
      <li
        v-for="(cafe, i) in sugerencias"
        :id="`${ID_LISTA}-${i}`"
        :key="cafe.place_id"
        role="option"
        :aria-selected="i === indiceActivo"
        class="flex cursor-pointer items-center justify-between gap-3 px-4 py-2 text-color1"
        :class="i === indiceActivo ? 'bg-color4' : ''"
        @mousedown.prevent
        @mouseenter="indiceActivo = i"
        @click="elegir(cafe)"
      >
        <span class="min-w-0">
          <span class="block truncate text-sm font-semibold">{{ cafe.nombre }}</span>
          <span class="block truncate text-xs text-gray-600">{{ cafe.direccion }}</span>
        </span>
        <span class="shrink-0 text-xs font-semibold text-gray-600">★ {{ cafe.rating.toFixed(1) }}</span>
      </li>
      <li v-if="sugerencias.length === 0" class="px-4 py-3 text-sm text-gray-600" role="presentation">
        Sin coincidencias
      </li>
    </ul>
  </div>
</template>
