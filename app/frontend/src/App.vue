<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import BotonContacto from './components/BotonContacto.vue'
import marca from './assets/geometra-marca.png'

const route = useRoute()
const mostrarFooter = computed(() => !route.meta.ocultarFooter)

const enlaces = [
  { ruta: '/recomendador', texto: 'Recomendador' },
  { ruta: '/negocios', texto: 'Para negocios' },
]
</script>

<template>
  <div class="flex min-h-screen flex-col bg-color1 text-white">
    <header class="sticky top-0 z-40 h-16 shrink-0 border-b border-white/10 bg-color1/90 shadow-lg shadow-black/20 backdrop-blur">
      <nav class="flex h-full items-center gap-4 px-4 sm:px-6" aria-label="Principal">
        <RouterLink to="/" class="flex items-center gap-3 rounded-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-color3">
          <!-- El logo tiene trazos azul marino: sobre el fondo oscuro necesita una base clara -->
          <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-white to-color5 shadow-md shadow-black/40 ring-1 ring-white/40">
            <img :src="marca" alt="" width="160" height="160" class="h-8 w-8 object-contain" />
          </span>
          <span class="text-lg font-semibold tracking-tight">
            Geometra <span class="mx-1 text-white/30">|</span> <span class="text-color4">Locus</span>
          </span>
        </RouterLink>

        <div class="ml-auto flex items-center gap-1 sm:gap-2">
          <RouterLink
            v-for="enlace in enlaces"
            :key="enlace.ruta"
            :to="enlace.ruta"
            class="hidden rounded-full px-3 py-1.5 text-sm font-medium text-white/70 transition hover:bg-white/10 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-color3 sm:inline-block"
            active-class="!bg-white/10 !text-white"
          >
            {{ enlace.texto }}
          </RouterLink>
          <BotonContacto />
        </div>
      </nav>
    </header>

    <main class="min-h-0 flex-1">
      <RouterView />
    </main>

    <footer v-if="mostrarFooter" class="shrink-0 border-t border-white/10 bg-color1">
      <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-sm text-gray-400 sm:flex-row">
        <p>© 2026 Geometra. Todos los derechos reservados.</p>
        <a
          href="mailto:contacto@geometra.mx"
          class="rounded-md text-gray-300 transition hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-color3"
        >
          contacto@geometra.mx
        </a>
      </div>
    </footer>
  </div>
</template>
