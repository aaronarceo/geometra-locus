<script setup lang="ts">
import { RouterLink } from 'vue-router'
import logo from '../assets/geometra-logo.webp'

interface TarjetaRol {
  ruta: string
  titulo: string
  descripcion: string
  accion: string
  icono: 'taza' | 'tienda'
}

const roles: TarjetaRol[] = [
  {
    ruta: '/recomendador',
    titulo: 'Usuario de Cafeterías',
    descripcion:
      'Descubre cafeterías similares a tus favoritas o encuentra lugares con las características que buscas.',
    accion: 'Buscar cafeterías',
    icono: 'taza',
  },
  {
    ruta: '/negocios',
    titulo: 'Dueño de Cafetería',
    descripcion:
      'Accede a análisis personalizados de tu negocio y entiende tu posición en el mercado.',
    accion: 'Conocer más',
    icono: 'tienda',
  },
]

interface Paso {
  icono: 'resenas' | 'perfil' | 'mapa'
  titulo: string
  texto: string
}

const pasos: Paso[] = [
  {
    icono: 'resenas',
    titulo: 'Leemos las reseñas',
    texto:
      'Partimos de las reseñas de Google Maps de las cafeterías de Mérida, con su calificación y su texto.',
  },
  {
    icono: 'perfil',
    titulo: 'Resumimos cada lugar',
    texto:
      'Un modelo de lenguaje multilingüe convierte cada reseña en números y promedia el resultado en un perfil por cafetería.',
  },
  {
    icono: 'mapa',
    titulo: 'Te recomendamos',
    texto:
      'Comparamos perfiles para encontrar cafeterías parecidas a tu favorita o a lo que buscas, y las ubicamos en el mapa.',
  },
]
</script>

<template>
  <div class="relative isolate overflow-hidden bg-color1">
    <!-- Fondo: difuminados de color y trama hexagonal (eco del logo) -->
    <div class="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
      <div class="absolute -top-32 left-1/2 h-[26rem] w-[44rem] -translate-x-1/2 rounded-full bg-color2/45 blur-[110px]"></div>
      <div class="absolute right-[-8rem] top-72 h-80 w-80 rounded-full bg-color3/25 blur-[100px]"></div>
      <div class="absolute left-[-6rem] top-[38rem] h-72 w-72 rounded-full bg-color4/10 blur-[90px]"></div>
      <svg
        class="absolute inset-0 h-full w-full text-white/[0.07] [mask-image:radial-gradient(ellipse_75%_50%_at_50%_0%,black,transparent)]"
      >
        <defs>
          <pattern id="trama-hex" width="56" height="100" patternUnits="userSpaceOnUse">
            <path
              d="M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100"
              fill="none"
              stroke="currentColor"
              stroke-width="1"
            />
            <path
              d="M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34"
              fill="none"
              stroke="currentColor"
              stroke-width="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#trama-hex)" />
      </svg>
    </div>

    <!-- Hero -->
    <section
      class="mx-auto grid max-w-6xl items-center gap-6 px-6 pb-5 pt-6 lg:grid-cols-[1.25fr_1fr] lg:gap-12 tall:pb-6 tall:pt-12"
    >
      <div class="text-center lg:text-left">
        <span
          class="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-medium text-white/70 backdrop-blur"
        >
          <span class="h-1.5 w-1.5 rounded-full bg-color3" aria-hidden="true"></span>
          Locus, un producto de Geometra
        </span>
        <h1
          class="mt-3 text-3xl font-extrabold leading-[1.1] tracking-tight text-white sm:text-4xl tall:mt-4 tall:xl:text-5xl"
        >
          Encuentra tu próxima cafetería favorita en Mérida
        </h1>
        <p class="mx-auto mt-3 max-w-2xl text-base leading-relaxed text-white/70 tall:mt-4 tall:text-lg lg:mx-0">
          Locus lee las reseñas de las cafeterías de la ciudad para recomendarte lugares
          parecidos a tus favoritos o con justo las características que buscas.
        </p>
      </div>

      <!-- El logo tiene trazos azul marino: sobre el fondo oscuro necesita una base clara -->
      <div class="relative mx-auto w-full max-w-xs sm:max-w-sm lg:max-w-none">
        <div
          class="pointer-events-none absolute -inset-3 rounded-[2rem] bg-color3/35 blur-2xl"
          aria-hidden="true"
        ></div>
        <div
          class="relative rounded-3xl border-2 border-white/70 bg-gradient-to-br from-white to-color5 p-4 shadow-tarjeta sm:p-5"
        >
          <img
            :src="logo"
            width="1000"
            height="444"
            alt="Geometra, geoanalítica y datos de ubicación"
            class="mx-auto h-auto w-full max-w-sm tall:max-w-md"
          />
        </div>
      </div>
    </section>

    <!-- Selección de rol -->
    <section class="mx-auto max-w-5xl px-6 pb-16 pt-1 tall:pt-4">
      <h2 class="text-center text-xl font-semibold text-white sm:text-2xl">
        ¿Qué tipo de usuario eres?
      </h2>

      <div class="mt-3 grid gap-5 md:grid-cols-2 tall:mt-6 tall:gap-6">
        <RouterLink
          v-for="rol in roles"
          :key="rol.ruta"
          :to="rol.ruta"
          class="group relative flex flex-col items-center overflow-hidden rounded-3xl border-2 border-white/70 bg-gradient-to-b from-white to-color5 p-4 text-center text-color1 shadow-tarjeta transition duration-300 hover:scale-[1.02] hover:border-color2 hover:shadow-tarjeta-hover focus-visible:scale-[1.02] focus-visible:border-color2 focus-visible:outline-none tall:p-8"
        >
          <span
            class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-color2/10 blur-2xl transition duration-300 group-hover:bg-color2/25"
            aria-hidden="true"
          ></span>

          <span
            class="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-color4 to-color5 text-color2 shadow-inner ring-4 ring-white/70 transition group-hover:from-white group-hover:to-color4 tall:h-24 tall:w-24"
          >
            <!-- Taza de café -->
            <svg
              v-if="rol.icono === 'taza'"
              class="h-8 w-8 tall:h-14 tall:w-14"
              viewBox="0 0 64 64"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M10 26h34v10a14 14 0 0 1-14 14h-6a14 14 0 0 1-14-14V26z" />
              <path d="M44 29h4a7 7 0 0 1 0 14h-5" />
              <path d="M8 56h38" />
              <path d="M20 8c-2 3 2 5 0 8M28 8c-2 3 2 5 0 8M36 8c-2 3 2 5 0 8" />
            </svg>
            <!-- Tienda -->
            <svg
              v-else
              class="h-8 w-8 tall:h-14 tall:w-14"
              viewBox="0 0 64 64"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M8 24l4-14h40l4 14" />
              <path d="M8 24c0 4 3 7 6.7 7S21.3 28 21.3 24c0 4 3 7 6.7 7s6.7-3 6.7-7c0 4 3 7 6.7 7S49.3 28 49.3 24c0 4 3 7 6.7 7" />
              <path d="M12 31v23h40V31" />
              <path d="M26 54V40h12v14" />
            </svg>
          </span>

          <h3 class="relative mt-3 text-xl font-bold tall:mt-5 tall:text-2xl">{{ rol.titulo }}</h3>
          <p class="relative mb-3 mt-2 max-w-sm text-sm leading-relaxed text-gray-700 tall:mb-4 tall:text-base">
            {{ rol.descripcion }}
          </p>
          <span
            class="relative mt-auto inline-flex items-center gap-2 rounded-full bg-color2 px-4 py-1.5 text-sm font-semibold text-white transition group-hover:bg-color3"
          >
            {{ rol.accion }}
            <svg class="h-4 w-4 transition group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </span>
        </RouterLink>
      </div>
    </section>

    <!-- Cómo funciona (debajo del primer pantallazo) -->
    <section class="mx-auto max-w-5xl px-6 pb-20">
      <div class="text-center">
        <p class="text-xs font-semibold uppercase tracking-widest text-color4">Cómo funciona</p>
        <h2 class="mt-2 text-2xl font-bold text-white sm:text-3xl">De las reseñas a tu próxima taza</h2>
      </div>

      <ol class="mt-10 grid gap-5 md:grid-cols-3">
        <li
          v-for="(paso, i) in pasos"
          :key="paso.titulo"
          class="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] p-6 shadow-panel backdrop-blur"
        >
          <span
            class="pointer-events-none absolute right-4 top-1 select-none text-6xl font-extrabold text-white/[0.05]"
            aria-hidden="true"
          >
            {{ i + 1 }}
          </span>
          <span
            class="flex h-12 w-12 items-center justify-center rounded-xl bg-color2/30 text-color4 ring-1 ring-color3/40"
          >
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <template v-if="paso.icono === 'resenas'">
                <rect x="4" y="3" width="16" height="18" rx="2.5" />
                <path d="M8 8h8M8 12h8M8 16h5" />
              </template>
              <template v-else-if="paso.icono === 'perfil'">
                <circle cx="6" cy="7" r="2" />
                <circle cx="18" cy="6" r="2" />
                <circle cx="12" cy="17" r="2" />
                <path d="M8 7.4l8-1M7 9l4 6.4M17 8l-4 7" />
              </template>
              <template v-else>
                <path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z" />
                <circle cx="12" cy="9.5" r="2.5" />
              </template>
            </svg>
          </span>
          <h3 class="mt-4 text-base font-semibold text-white">{{ paso.titulo }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-white/65">{{ paso.texto }}</p>
        </li>
      </ol>
    </section>
  </div>
</template>
