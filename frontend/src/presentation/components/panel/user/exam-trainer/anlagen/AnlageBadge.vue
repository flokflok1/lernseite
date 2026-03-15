<script setup lang="ts">
interface Props {
  number: number
  title: string
}

defineProps<Props>()

const emit = defineEmits<{
  click: [number: number]
}>()
</script>

<template>
  <button
    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
           border border-amber-500/40 bg-amber-500/10 text-amber-400
           hover:bg-amber-500/20 hover:border-amber-500/60 transition-all cursor-pointer"
    :title="title"
    @click="emit('click', number)"
  >
    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
    </svg>
    Anlage {{ number }}
  </button>
</template>
