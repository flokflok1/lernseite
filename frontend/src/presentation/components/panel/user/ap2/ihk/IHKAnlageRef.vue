<script setup lang="ts">
interface Props {
  number: number | string
  title?: string
}

defineProps<Props>()

const emit = defineEmits<{
  open: [nummer: string | number]
}>()

function handleClick() {
  emit('open', (arguments as any).length ? arguments[0] : null)
}
</script>

<template>
  <button
    type="button"
    class="ihk-anlage-ref"
    :aria-label="`Anlage ${number} öffnen`"
    @click="emit('open', number)"
  >
    Anlage {{ number }}<span v-if="title"> ({{ title }})</span>
  </button>
</template>

<style scoped>
.ihk-anlage-ref {
  display: inline;
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  font: inherit;
  color: #000;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-underline-offset: 2px;
  cursor: pointer;
  white-space: nowrap;
}

.ihk-anlage-ref:hover,
.ihk-anlage-ref:focus-visible {
  text-decoration-style: solid;
  outline: 1px dashed #666;
  outline-offset: 2px;
}

@media print {
  .ihk-anlage-ref {
    text-decoration: none;
    cursor: default;
  }
}
</style>
