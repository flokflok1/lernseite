<script setup lang="ts">
interface Props {
  nummer: number | string
  titel: string
  zuAufgabe?: string
  faNummer?: number | string
  semester?: string
  teil?: number | string
  page?: number
}

withDefaults(defineProps<Props>(), {
  zuAufgabe: '',
  faNummer: 235,
  semester: '',
  teil: '',
  page: undefined,
})
</script>

<template>
  <article class="ihk-anlage">
    <header class="ihk-anlage-header">
      <span>FA {{ faNummer }}</span>
      <span class="ihk-anlage-center">
        {{ semester }}
        <span v-if="page" class="ihk-anlage-page">-{{ page }}-</span>
      </span>
      <span>
        Teil {{ teil }}<br />
        <small>Aufgaben</small>
      </span>
    </header>

    <div class="ihk-anlage-title">
      <span><strong>Anlage {{ nummer }}</strong>&nbsp;&nbsp;{{ titel }}</span>
      <span v-if="zuAufgabe" class="ihk-anlage-ref-target">
        zu Aufgabe {{ zuAufgabe }}
      </span>
    </div>

    <div class="ihk-anlage-content">
      <slot />
    </div>
  </article>
</template>

<style scoped>
.ihk-anlage {
  font-family: 'Liberation Serif', 'Times New Roman', serif;
  font-size: 11pt;
  color: #000;
  background: #fff;
  max-width: 21cm;
  margin: 2em auto;
  padding: 1.5cm 2cm;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
  min-height: 70vh;
  page-break-before: always;
}

.ihk-anlage-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: start;
  padding-bottom: 0.6cm;
  border-bottom: 1px solid #666;
  margin-bottom: 0.8cm;
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
}

.ihk-anlage-header > :nth-child(1) { text-align: left; }
.ihk-anlage-center { text-align: center; display: flex; flex-direction: column; }
.ihk-anlage-header > :nth-child(3) { text-align: right; line-height: 1.2; }
.ihk-anlage-header small { font-size: 9pt; font-weight: 400; }

.ihk-anlage-page {
  font-weight: 400;
  font-size: 9pt;
}

.ihk-anlage-title {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1em;
  font-size: 12pt;
  margin-bottom: 1.2em;
  padding-bottom: 0.4em;
  border-bottom: 1px solid #666;
}

.ihk-anlage-ref-target {
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
}

.ihk-anlage-content {
  min-height: 50vh;
}

@media print {
  .ihk-anlage { box-shadow: none; page-break-before: always; }
}
</style>
