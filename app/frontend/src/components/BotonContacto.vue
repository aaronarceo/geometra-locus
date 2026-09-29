<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const CORREO = 'contacto@geometra.mx'
const ID_PANEL = 'panel-contacto'

const abierto = ref(false)
const copiado = ref(false)
const raiz = ref<HTMLElement | null>(null)
let temporizador: number | undefined

function cerrar(): void {
  abierto.value = false
}

function alPulsarFuera(evento: MouseEvent): void {
  if (abierto.value && raiz.value && !raiz.value.contains(evento.target as Node)) cerrar()
}

function alTeclear(evento: KeyboardEvent): void {
  if (evento.key === 'Escape' && abierto.value) {
    cerrar()
    raiz.value?.querySelector<HTMLButtonElement>('button')?.focus()
  }
}

async function copiar(): Promise<void> {
  try {
    await navigator.clipboard.writeText(CORREO)
    copiado.value = true
    window.clearTimeout(temporizador)
    temporizador = window.setTimeout(() => (copiado.value = false), 2000)
  } catch {
    // Sin permiso de portapapeles el correo sigue visible y con enlace mailto.
  }
}

onMounted(() => {
  document.addEventListener('mousedown', alPulsarFuera)
  document.addEventListener('keydown', alTeclear)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', alPulsarFuera)
  document.removeEventListener('keydown', alTeclear)
  window.clearTimeout(temporizador)
})
</script>

<template>
  <div ref="raiz" class="relative">
    <button
      type="button"
      class="inline-flex items-center gap-2 rounded-full bg-color2 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-black/30 ring-1 ring-white/10 transition hover:bg-color3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
      :aria-expanded="abierto"
      :aria-controls="ID_PANEL"
      @click="abierto = !abierto"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="3" y="5" width="18" height="14" rx="2.5" />
        <path d="M3.5 7l8.5 6 8.5-6" />
      </svg>
      Contáctanos
    </button>

    <Transition name="fade">
      <div
        v-if="abierto"
        :id="ID_PANEL"
        role="dialog"
        aria-label="Contacto"
        class="absolute right-0 top-full z-50 mt-3 w-[min(20rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border-2 border-white/70 bg-gradient-to-b from-white to-color5 p-5 text-color1 shadow-tarjeta"
      >
        <div class="pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full bg-color2/20 blur-2xl" aria-hidden="true"></div>
        <p class="relative text-base font-bold">Contáctanos</p>
        <p class="relative mt-1 text-sm leading-relaxed text-gray-700">
          Cuéntanos qué necesitas o pide un análisis personalizado de tu negocio.
        </p>

        <a
          :href="`mailto:${CORREO}?subject=Contacto%20desde%20Locus`"
          class="relative mt-4 flex items-center justify-center gap-2 rounded-full bg-color2 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-color3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
        >
          {{ CORREO }}
        </a>
        <button
          type="button"
          class="relative mt-2 w-full rounded-full border border-color1/20 px-4 py-2 text-sm font-medium text-color1 transition hover:bg-color4/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
          @click="copiar"
        >
          <span aria-live="polite">{{ copiado ? 'Correo copiado' : 'Copiar correo' }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>
