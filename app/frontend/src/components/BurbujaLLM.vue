<script setup lang="ts">
const emit = defineEmits<{
  abrir: []
}>()
</script>

<template>
  <button
    type="button"
    class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-color2 px-5 py-3 text-sm font-semibold text-white shadow-xl shadow-black/40 transition hover:-translate-y-0.5 hover:bg-color3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
    @click="emit('abrir')"
  >
    <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />
    </svg>
    ¿Por qué estas recomendaciones?
  </button>
</template>
