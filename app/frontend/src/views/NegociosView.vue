<script setup lang="ts">
import { RouterLink } from 'vue-router'
import marca from '../assets/geometra-marca.png'
</script>

<template>
  <div class="relative isolate overflow-hidden bg-color1">
    <!-- Fondo: difuminados de color -->
    <div class="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
      <div class="absolute -top-28 left-1/2 h-96 w-[38rem] -translate-x-1/2 rounded-full bg-color2/40 blur-[110px]"></div>
      <div class="absolute bottom-0 right-[-6rem] h-72 w-72 rounded-full bg-color3/20 blur-[100px]"></div>
    </div>

    <section class="mx-auto max-w-3xl px-6 py-14 text-center sm:py-20">
      <!-- El logo tiene trazos azul marino: sobre el fondo oscuro necesita una base clara -->
      <span
        class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border-2 border-white/70 bg-gradient-to-br from-white to-color5 shadow-tarjeta"
      >
        <img :src="marca" alt="Geometra" width="160" height="160" class="h-11 w-11 object-contain" />
      </span>

      <span
        class="mt-6 inline-flex items-center gap-2 rounded-full border border-color3 bg-color2/30 px-4 py-1.5 text-sm font-semibold uppercase tracking-wide text-white"
      >
        <span class="h-2 w-2 animate-pulse rounded-full bg-color3" aria-hidden="true"></span>
        En desarrollo
      </span>

      <h1 class="mt-6 text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl">
        Análisis inteligente para tu cafetería
      </h1>

      <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-white/70">
        Estamos construyendo herramientas para dueños de cafeterías: análisis de
        posicionamiento, benchmarking con competidores, tendencias en las reseñas de tus
        clientes e identificación de oportunidades de mercado en Mérida.
      </p>

      <div
        class="relative mt-10 overflow-hidden rounded-3xl border-2 border-white/70 bg-gradient-to-b from-white to-color5 p-8 text-color1 shadow-tarjeta"
      >
        <div class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-color2/15 blur-2xl" aria-hidden="true"></div>
        <p class="relative text-lg font-semibold">
          Contáctanos para un análisis personalizado de tu negocio
        </p>
        <a
          href="mailto:contacto@geometra.mx"
          class="relative mt-4 inline-block rounded-full bg-color2 px-6 py-2.5 font-semibold text-white shadow-md shadow-black/20 transition hover:bg-color3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
        >
          contacto@geometra.mx
        </a>
      </div>

      <RouterLink
        to="/"
        class="mt-10 inline-block rounded-full border border-white/20 px-5 py-2 text-sm font-medium text-white transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
      >
        ← Regresar
      </RouterLink>
    </section>
  </div>
</template>
