<script setup lang="ts">
interface Props {
  firma: string
  beschreibung: string
  label?: string
}

withDefaults(defineProps<Props>(), {
  label: 'Projektbeschreibung',
})
</script>

<template>
  <div class="ihk-projekt">
    <p class="ihk-projekt-label"><strong>{{ label }}:</strong></p>
    <p class="ihk-projekt-text">
      Die Firma „<em>{{ firma }}</em>&ldquo; {{ beschreibung }}
    </p>
    <div v-if="$slots.default" class="ihk-projekt-extra">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.ihk-projekt {
  margin: 1.2em 0 1.6em 0;
  page-break-inside: avoid;
}

.ihk-projekt-label {
  margin-bottom: 0.3em;
  font-size: 11pt;
}

.ihk-projekt-text {
  text-align: justify;
  line-height: 1.5;
  margin: 0 0 0.6em 0;
}

.ihk-projekt-extra {
  margin-top: 0.4em;
  text-align: justify;
}

@media print {
  .ihk-projekt { page-break-inside: avoid; }
}
</style>
