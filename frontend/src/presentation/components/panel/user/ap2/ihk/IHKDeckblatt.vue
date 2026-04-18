<script setup lang="ts">
interface Props {
  faNummer?: number | string
  semester: string
  teil: number | string
  teilLabel: string
  projektTitel: string
  zulassungshinweis?: string
}

withDefaults(defineProps<Props>(), {
  faNummer: 235,
  zulassungshinweis: 'Aufgaben nur mit Wechsel-Informationen (Prüfung FA 235)',
})
</script>

<template>
  <article class="ihk-deckblatt">
    <div class="ihk-deckblatt-top">
      <span class="ihk-deckblatt-fa">FA {{ faNummer }}</span>
      <span class="ihk-deckblatt-sem">{{ semester }}</span>
    </div>

    <div class="ihk-deckblatt-hauptblock">
      <h1 class="ihk-deckblatt-pruefung">
        Schriftliche Abschlussprüfung<br />
        Teil {{ teil }}
      </h1>
      <h2 class="ihk-deckblatt-beruf">Fachinformatiker / Fachinformatikerin</h2>
      <p class="ihk-deckblatt-fachrichtung">Fachrichtung Systemintegration</p>

      <hr class="ihk-deckblatt-trenner" />

      <h3 class="ihk-deckblatt-teilname">{{ teilLabel }}</h3>
      <p class="ihk-deckblatt-titel">
        „<em>{{ projektTitel }}</em>&ldquo;
      </p>
    </div>

    <footer class="ihk-deckblatt-footer">
      <p v-if="zulassungshinweis">{{ zulassungshinweis }}</p>
      <slot />
    </footer>
  </article>
</template>

<style scoped>
.ihk-deckblatt {
  font-family: 'Liberation Serif', 'Times New Roman', serif;
  font-size: 11pt;
  color: #000;
  background: #fff;
  max-width: 21cm;
  min-height: 90vh;
  margin: 0 auto;
  padding: 3cm 2.5cm;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  page-break-after: always;
}

.ihk-deckblatt-top {
  display: flex;
  justify-content: space-between;
  font-family: 'Liberation Sans', sans-serif;
  font-size: 10pt;
  font-weight: 600;
  padding-bottom: 1em;
  border-bottom: 1px solid #666;
}

.ihk-deckblatt-hauptblock {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  gap: 0.8em;
}

.ihk-deckblatt-pruefung {
  font-size: 18pt;
  font-weight: 700;
  margin: 0;
}

.ihk-deckblatt-beruf {
  font-size: 14pt;
  font-weight: 700;
  margin: 0.4em 0 0 0;
}

.ihk-deckblatt-fachrichtung {
  font-size: 12pt;
  margin: 0.2em 0;
}

.ihk-deckblatt-trenner {
  border: 0;
  border-top: 1px solid #666;
  width: 40%;
  margin: 1.2em auto;
}

.ihk-deckblatt-teilname {
  font-size: 13pt;
  font-weight: 700;
  margin: 0;
}

.ihk-deckblatt-titel {
  font-size: 12pt;
  font-style: normal;
  margin: 0.4em 0;
}

.ihk-deckblatt-footer {
  text-align: center;
  font-family: 'Liberation Sans', sans-serif;
  font-size: 9pt;
  padding-top: 1em;
  border-top: 1px solid #666;
  line-height: 1.5;
}

@media print {
  .ihk-deckblatt {
    box-shadow: none;
    page-break-after: always;
  }
}
</style>
