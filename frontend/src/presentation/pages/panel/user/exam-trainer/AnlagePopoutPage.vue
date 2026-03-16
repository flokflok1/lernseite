<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import { useAnlageRenderer } from '@/presentation/components/panel/user/exam-trainer/anlagen/useAnlageRenderer'
import { trainerGetAnlagen } from '@/infrastructure/api/clients/panel/user/exams'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

const props = defineProps<{
  examId: string
  anlageNumber: string
}>()

const { t } = useI18n()
const anlage = ref<Anlage | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const anlagen = await trainerGetAnlagen(props.examId)
    anlage.value = anlagen.find(a => a.number === parseInt(props.anlageNumber)) || null
    if (!anlage.value) error.value = `Anlage ${props.anlageNumber} not found`
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
  // Set window title
  if (anlage.value) {
    document.title = `${t('panel.examTrainer.anlagen.anlageNr', { number: anlage.value.number })} — ${anlage.value.title}`
  }
})

const {
  isOffer, isApiRef, offerData, functions,
  recipientLines, priceHeaders, priceRows, totalLines,
  bodyParagraphs, conditionLines,
} = useAnlageRenderer(anlage)
</script>

<template>
  <div class="popout-page">
    <div v-if="loading" class="popout-loading">Loading...</div>
    <div v-else-if="error" class="popout-error">{{ error }}</div>
    <template v-else-if="anlage">
      <!-- OFFER RENDERER -->
      <div v-if="isOffer" class="offer-letter">
        <div class="offer-header">
          <div class="offer-company">{{ offerData.company || '' }}</div>
          <div class="offer-type">{{ t('panel.examTrainer.anlagen.offer') }}</div>
        </div>
        <div class="offer-meta-row">
          <div class="offer-recipient">
            <div class="offer-address-line">{{ offerData.company }}</div>
            <div v-for="line in recipientLines" :key="line">{{ line }}</div>
          </div>
          <div class="offer-numbers">
            <div v-if="offerData.document_number">
              <span class="offer-label">{{ t('panel.examTrainer.anlagen.offerNr') }}</span>
              {{ offerData.document_number }}
            </div>
            <div v-if="offerData.customer_number">
              <span class="offer-label">{{ t('panel.examTrainer.anlagen.customerNr') }}</span>
              {{ offerData.customer_number }}
            </div>
          </div>
        </div>
        <div class="offer-body-text">
          <div v-for="(para, idx) in bodyParagraphs" :key="idx" class="offer-para">{{ para }}</div>
        </div>
        <table v-if="priceRows.length" class="offer-price-table">
          <thead><tr><th v-for="h in priceHeaders" :key="h">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, idx) in priceRows" :key="idx">
              <td v-for="(cell, ci) in row" :key="ci" :class="{ 'text-right': ci >= 2 }">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
        <div v-for="(line, idx) in totalLines" :key="'t'+idx" class="offer-total-line">{{ line }}</div>
        <div class="offer-conditions">
          <div v-for="(cond, idx) in conditionLines" :key="'c'+idx" class="offer-para">{{ cond }}</div>
        </div>
        <div v-if="offerData.signer" class="offer-closing">
          <p>Mit freundlichen Grüßen</p>
          <div class="offer-signature">{{ offerData.signer }}</div>
        </div>
      </div>

      <!-- API REFERENCE -->
      <div v-else-if="isApiRef" class="api-reference">
        <h2>{{ anlage.title }}</h2>
        <table class="api-table">
          <thead><tr>
            <th>{{ t('panel.examTrainer.anlagen.function') }}</th>
            <th>{{ t('panel.examTrainer.anlagen.description') }}</th>
          </tr></thead>
          <tbody>
            <tr v-for="fn in functions" :key="fn.name">
              <td class="api-name"><code>{{ fn.name }}</code></td>
              <td>{{ fn.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- GENERIC -->
      <div v-else class="generic-content" v-html="renderMarkdown(anlage.raw_text)" />
    </template>
  </div>
</template>

<style scoped>
.popout-page {
  min-height: 100vh;
  background: #f5f5f3;
  padding: 32px;
}

.popout-loading, .popout-error {
  text-align: center; padding: 48px; font-size: 16px; color: #666;
}

/* Offer styles — same as AnlagePanel but full-page */
.offer-letter {
  max-width: 800px; margin: 0 auto;
  background: #fafaf8; color: #1a1a1a;
  border-radius: 4px; padding: 48px 56px;
  font-family: 'Georgia', 'Times New Roman', serif; font-size: 15px; line-height: 1.65;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.04);
  border: 1px solid #d0d0d0;
}
.offer-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; padding-bottom: 18px; border-bottom: 2px solid #333; }
.offer-company { font-size: 24px; font-weight: 700; letter-spacing: 0.02em; }
.offer-type { font-size: 30px; font-weight: 300; color: #666; text-transform: uppercase; letter-spacing: 0.1em; }
.offer-address-line { font-size: 11px; color: #888; text-decoration: underline; margin-bottom: 16px; }
.offer-meta-row { display: flex; justify-content: space-between; margin-bottom: 32px; }
.offer-recipient { font-size: 15px; line-height: 1.5; }
.offer-numbers { text-align: right; font-size: 14px; }
.offer-label { font-weight: 600; margin-right: 8px; }
.offer-body-text { margin-bottom: 24px; }
.offer-para { margin-bottom: 12px; }
.offer-price-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
.offer-price-table th { background: #333; color: #fff; padding: 10px 14px; text-align: left; font-size: 13px; font-weight: 600; }
.offer-price-table td { padding: 10px 14px; border-bottom: 1px solid #ddd; font-size: 14px; }
.text-right { text-align: right; }
.offer-total-line { text-align: right; font-size: 15px; font-weight: 600; padding: 4px 14px; }
.offer-conditions { margin: 24px 0; }
.offer-closing { margin-top: 36px; }
.offer-closing p { margin-bottom: 8px; }
.offer-signature { font-style: italic; font-size: 20px; margin-top: 16px; }

/* API Reference */
.api-reference { max-width: 800px; margin: 0 auto; }
.api-reference h2 { font-size: 20px; margin-bottom: 16px; }
.api-table { width: 100%; border-collapse: collapse; }
.api-table th { background: #f0f0f0; padding: 10px 14px; text-align: left; font-size: 14px; border-bottom: 2px solid #ddd; }
.api-table td { padding: 10px 14px; border-bottom: 1px solid #eee; font-size: 14px; }
.api-name code { font-family: 'Fira Code', monospace; color: #2563eb; background: #f0f4ff; padding: 2px 6px; border-radius: 4px; }

/* Generic */
.generic-content { max-width: 800px; margin: 0 auto; font-size: 15px; line-height: 1.7; }
</style>
