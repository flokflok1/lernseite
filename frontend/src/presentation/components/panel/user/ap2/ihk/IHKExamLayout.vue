<script setup lang="ts">
interface Props {
  faNummer?: string | number
  semester?: string
  teil?: string | number
  teilLabel?: string
  page?: number
  totalPages?: number
}

withDefaults(defineProps<Props>(), {
  faNummer: 235,
  semester: '',
  teil: '',
  teilLabel: '',
  page: undefined,
  totalPages: undefined,
})
</script>

<template>
  <article class="ihk-exam-layout">
    <header class="ihk-exam-header">
      <span class="ihk-exam-fa">FA {{ faNummer }}</span>
      <span class="ihk-exam-center">
        <span class="ihk-exam-semester">{{ semester }}</span>
        <span v-if="page" class="ihk-exam-page">-{{ page }}-</span>
      </span>
      <span class="ihk-exam-teil">
        <template v-if="teilLabel">{{ teilLabel }}</template>
        <template v-else>Teil {{ teil }}</template>
        <br />
        <small>Aufgaben</small>
      </span>
    </header>

    <section class="ihk-exam-body">
      <slot />
    </section>
  </article>
</template>

<style scoped>
.ihk-exam-layout {
  font-family: 'Liberation Serif', 'Times New Roman', serif;
  font-size: 11pt;
  line-height: 1.4;
  color: #000;
  background: #fff;
  max-width: 21cm;
  margin: 0 auto;
  padding: 1.5cm 2cm;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
  min-height: 90vh;
}

.ihk-exam-header {
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

.ihk-exam-fa {
  text-align: left;
}

.ihk-exam-center {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ihk-exam-semester {
  font-weight: 600;
}

.ihk-exam-page {
  font-weight: 400;
  font-size: 9pt;
}

.ihk-exam-teil {
  text-align: right;
  line-height: 1.2;
}

.ihk-exam-teil small {
  font-size: 9pt;
  font-weight: 400;
}

.ihk-exam-body {
  font-family: 'Liberation Serif', 'Times New Roman', serif;
}

@media print {
  .ihk-exam-layout {
    box-shadow: none;
    max-width: 100%;
    margin: 0;
    padding: 1.5cm 2cm;
    page-break-inside: avoid;
  }
}
</style>
