<script setup lang="ts">
interface Teilaufgabe {
  nummer: string
  frage: string
  punkte: number
}

interface Props {
  nummer: number | string
  titel: string
  gesamtPunkte: number
  teilaufgaben?: Teilaufgabe[]
}

withDefaults(defineProps<Props>(), {
  teilaufgaben: () => [],
})
</script>

<template>
  <section class="ihk-aufgabe">
    <header class="ihk-aufgabe-header">
      <span class="ihk-aufgabe-title">
        <strong>Aufgabe {{ nummer }}</strong>&nbsp;&nbsp;{{ titel }}
      </span>
      <span class="ihk-aufgabe-punkte">Punkte {{ gesamtPunkte }}</span>
    </header>

    <div v-if="$slots.default" class="ihk-aufgabe-intro">
      <slot />
    </div>

    <div
      v-for="ta in teilaufgaben"
      :key="ta.nummer"
      class="ihk-teilaufgabe"
      :class="'ihk-teilaufgabe-level-' + ta.nummer.split('.').length"
    >
      <span class="ihk-teilaufgabe-num">{{ ta.nummer }}</span>
      <div class="ihk-teilaufgabe-frage">{{ ta.frage }}</div>
      <span class="ihk-teilaufgabe-punkte">{{ ta.punkte }}</span>
    </div>
  </section>
</template>

<style scoped>
.ihk-aufgabe {
  margin: 1.6em 0;
  page-break-inside: avoid;
}

.ihk-aufgabe-header {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: baseline;
  padding-bottom: 0.4em;
  border-bottom: 1px solid #666;
  margin-bottom: 0.6em;
}

.ihk-aufgabe-title {
  font-size: 12pt;
}

.ihk-aufgabe-title strong {
  font-weight: 700;
}

.ihk-aufgabe-punkte {
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
  white-space: nowrap;
}

.ihk-aufgabe-intro {
  margin: 0.4em 0 0.8em 0;
  text-align: justify;
}

.ihk-teilaufgabe {
  display: grid;
  grid-template-columns: 40px 1fr 50px;
  gap: 0.6em;
  align-items: start;
  margin: 0.6em 0;
}

.ihk-teilaufgabe-level-3 {
  padding-left: 2em;
}

.ihk-teilaufgabe-num {
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
  text-align: right;
  padding-top: 1px;
}

.ihk-teilaufgabe-frage {
  text-align: justify;
  line-height: 1.45;
}

.ihk-teilaufgabe-punkte {
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
  text-align: right;
  padding-top: 1px;
}

@media print {
  .ihk-aufgabe { page-break-inside: avoid; }
}
</style>
