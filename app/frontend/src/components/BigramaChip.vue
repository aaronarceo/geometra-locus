<script setup lang="ts">
const props = defineProps<{
  texto: string
  activo: boolean
}>()

const emit = defineEmits<{
  toggle: [texto: string]
}>()
</script>

<template>
  <button
    type="button"
    :aria-pressed="props.activo"
    class="rounded-full px-4 py-1.5 text-sm font-medium transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-color3"
    :class="
      props.activo
        ? 'bg-color2 text-white hover:bg-color3'
        : 'bg-color5 text-color1 hover:bg-color4'
    "
    @click="emit('toggle', props.texto)"
  >
    {{ props.texto }}
  </button>
</template>
