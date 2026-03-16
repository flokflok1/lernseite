<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import { useAnlageRenderer } from './useAnlageRenderer'
import type { LsxPanel } from '@/application/stores/modules/workspace/panel.types'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  window: LsxPanel
}

const props = defineProps<Props>()
const { t } = useI18n()

// Extract Anlage data from window payload
const anlage = computed(() => (props.window.payload?.anlage as Anlage) || null)
const examId = computed(() => (props.window.payload?.examId as string) || '')

const {
  isOffer, isApiRef, offerData, functions,
  recipientLines, priceHeaders, priceRows, totalLines,
  bodyParagraphs, conditionLines,
} = useAnlageRenderer(anlage)

const popout = () => {
  if (!examId.value || !anlage.value) return
  const url = `/exam-trainer/anlage/${examId.value}/${anlage.value.number}`
  window.open(url, `anlage-${anlage.value.number}`, 'width=860,height=700,menubar=no,toolbar=no')
}
</script>

<template>
  <div v-if="anlage" class="anlage-content">
    <!-- Popout link -->
    <div v-if="examId" class="flex justify-end mb-2">
      <button
        class="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors flex items-center gap-1"
        @click="popout"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M7 1h4v4M11 1L6 6M5 1H2a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1V7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ t('panel.examTrainer.anlagen.popout') }}
      </button>
    </div>

    <!-- OFFER RENDERER — paper document -->
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
        <thead>
          <tr><th v-for="h in priceHeaders" :key="h">{{ h }}</th></tr>
        </thead>
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

    <!-- API REFERENCE RENDERER -->
    <div v-else-if="isApiRef" class="api-reference">
      <table class="api-table">
        <thead>
          <tr>
            <th>{{ t('panel.examTrainer.anlagen.function') }}</th>
            <th>{{ t('panel.examTrainer.anlagen.description') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="fn in functions" :key="fn.name">
            <td class="api-name"><code>{{ fn.name }}</code></td>
            <td>{{ fn.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- GENERIC / INFO DOCUMENT -->
    <div v-else class="generic-content" v-html="renderMarkdown(anlage.raw_text)" />
  </div>
</template>

<style scoped>
.anlage-content { padding: 16px; }

/* Offer Letter: Paper-on-desk effect */
.offer-letter {
  background: #fafaf8; color: #1a1a1a; border-radius: 4px;
  padding: 32px 36px; font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 14px; line-height: 1.6;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #c8c8c4;
}
.offer-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid #333; }
.offer-company { font-size: 22px; font-weight: 700; letter-spacing: 0.02em; color: #1a1a1a; }
.offer-type { font-size: 28px; font-weight: 300; color: #666; text-transform: uppercase; letter-spacing: 0.1em; }
.offer-address-line { font-size: 11px; color: #888; text-decoration: underline; margin-bottom: 16px; }
.offer-meta-row { display: flex; justify-content: space-between; margin-bottom: 32px; }
.offer-recipient { font-size: 14px; line-height: 1.5; }
.offer-numbers { text-align: right; font-size: 13px; }
.offer-label { font-weight: 600; margin-right: 8px; }
.offer-body-text { margin-bottom: 20px; }
.offer-para { margin-bottom: 10px; }
.offer-price-table { width: 100%; border-collapse: collapse; margin: 16px 0; }
.offer-price-table th { background: #333; color: #fff; padding: 8px 12px; text-align: left; font-size: 12px; font-weight: 600; }
.offer-price-table td { padding: 8px 12px; border-bottom: 1px solid #ddd; font-size: 13px; }
.text-right { text-align: right; }
.offer-total-line { text-align: right; font-size: 14px; font-weight: 600; padding: 4px 12px; }
.offer-conditions { margin: 20px 0; }
.offer-closing { margin-top: 32px; }
.offer-closing p { margin-bottom: 8px; }
.offer-signature { font-style: italic; font-size: 18px; margin-top: 16px; margin-bottom: 4px; }

/* API Reference */
.api-reference { padding: 8px; }
.api-table { width: 100%; border-collapse: collapse; }
.api-table th { background: var(--color-surface, #1a1d27); color: var(--color-text, #e2e4ea); padding: 10px 14px; text-align: left; font-size: 13px; font-weight: 600; border-bottom: 2px solid var(--color-border, #2e3348); }
.api-table td { padding: 10px 14px; border-bottom: 1px solid var(--color-border, #2e3348); font-size: 13px; color: var(--color-text, #e2e4ea); }
.api-name code { font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 13px; color: #60a5fa; background: rgba(96,165,250,0.1); padding: 2px 6px; border-radius: 4px; white-space: nowrap; }

/* Generic */
.generic-content { font-size: 14px; line-height: 1.7; white-space: pre-wrap; }
.generic-content :deep(table) { width: 100%; border-collapse: collapse; margin: 12px 0; }
.generic-content :deep(th), .generic-content :deep(td) { padding: 8px 12px; border: 1px solid var(--color-border, #2e3348); font-size: 13px; }
</style>
