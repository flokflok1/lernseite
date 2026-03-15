<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Modal from '@/presentation/components/shared/ui/Modal.vue'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  show: boolean
  anlage: Anlage | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()

const isOffer = computed(() => props.anlage?.type === 'offer')
const isApiRef = computed(() => props.anlage?.type === 'api_reference')
const offerData = computed(() => (props.anlage?.data || {}) as Record<string, unknown>)
const functions = computed(() =>
  ((props.anlage?.data as Record<string, unknown>)?.functions || []) as Array<{ name: string; description: string }>
)

// Parse raw_text into sections for offer rendering
const rawLines = computed(() => (props.anlage?.raw_text || '').split('\n').map(l => l.trim()))

const recipientLines = computed(() => {
  const lines = rawLines.value
  const start = lines.findIndex(l => l.startsWith('Systemhaus') || l.startsWith('An '))
  if (start < 0) return []
  const result: string[] = []
  for (let i = start; i < Math.min(start + 4, lines.length); i++) {
    if (lines[i] && !lines[i].includes('Angebots') && !lines[i].includes('Kunden')) result.push(lines[i])
    else break
  }
  return result
})

const priceHeaders = computed(() => {
  const line = rawLines.value.find(l => l.includes('|') && (l.includes('Pos') || l.includes('Beschreibung')))
  if (!line) return []
  return line.split('|').map(c => c.trim()).filter(Boolean)
})

const priceRows = computed(() => {
  const lines = rawLines.value
  const rows: string[][] = []
  let inTable = false
  for (const line of lines) {
    if (line.includes('|') && (line.includes('Pos') || line.includes('Beschreibung'))) {
      inTable = true
      continue
    }
    if (line.includes('---')) continue
    if (inTable && line.includes('|')) {
      const cells = line.split('|').map(c => c.trim()).filter(Boolean)
      if (cells.length >= 2) rows.push(cells)
    } else if (inTable && !line.includes('|')) {
      inTable = false
    }
  }
  return rows
})

const totalLines = computed(() => {
  return rawLines.value.filter(l =>
    (l.includes('zzgl.') || l.includes('Gesamtsumme') || l.includes('Gesamtbetrag') ||
     l.includes('Zwischensumme'))
    && !l.includes('|') && !l.includes('USt. ID')
  )
})

const bodyParagraphs = computed(() => {
  const lines = rawLines.value
  const result: string[] = []
  const skipPatterns = [
    /^TOPSICHERHEIT|^Heikvision|^ANGEBOT|^Topsicherheit|^Systemhaus|^Hans-Thoma/i,
    /^\d{5}\s/,  // PLZ lines
    /^Angebots|^Kunden|^Angebot-Nr/i,
    /\|/, // table lines
    /^zzgl|^Gesamtsumme|^Gesamtbetrag|^Zwischensumme|^\d+%\s*USt/i,
    /^Mit freundlichen|^Schubert|^Thomas|^Petra|^Karlstraße|^Gartenstraße/i,
    /^[\d+\s]*7121|^www\.|^Reutlinger|^Volksbank|^DE\s\d|^BIC|^USt\.|^Steuer/i,
    /^Geschäftsführer/i,
  ]
  // Find greeting as start, stop before table or conditions
  const greetIdx = lines.findIndex(l => l.startsWith('Sehr geehrte'))
  if (greetIdx < 0) return []

  // Find where the table/pricing starts
  const tableIdx = lines.findIndex(l => l.includes('|') && l.includes('Pos'))
  const stopIdx = tableIdx > 0 ? tableIdx : lines.findIndex(l => l.includes('freundlichen Grüßen'))

  let current = ''
  for (let i = greetIdx; i < (stopIdx > 0 ? stopIdx : lines.length); i++) {
    const line = lines[i]
    if (skipPatterns.some(p => p.test(line))) continue
    if (!line) {
      if (current) { result.push(current); current = '' }
    } else {
      current = current ? current + ' ' + line : line
    }
  }
  if (current) result.push(current)
  return result
})

const conditionLines = computed(() => {
  const lines = rawLines.value
  const result: string[] = []
  // Find lines after totals but before closing
  const totalIdx = lines.findIndex(l => l.includes('Gesamtsumme') || l.includes('Gesamtbetrag'))
  const closingIdx = lines.findIndex(l => l.includes('freundlichen Grüßen'))
  if (totalIdx < 0 || closingIdx < 0) return []

  let current = ''
  for (let i = totalIdx + 1; i < closingIdx; i++) {
    const line = lines[i]
    if (!line || line.includes('zzgl') || line.includes('USt') || line.includes('|')) continue
    if (line.length < 10) continue
    current = current ? current + ' ' + line : line
    if (lines[i + 1] === '' || i === closingIdx - 1) {
      if (current) { result.push(current); current = '' }
    }
  }
  if (current) result.push(current)
  return result
})
</script>

<template>
  <Modal :show="show" :title="anlage?.title || ''" size="lg" @close="emit('close')">
    <div v-if="anlage" class="anlage-content">

      <!-- OFFER RENDERER — realistic business letter -->
      <div v-if="isOffer" class="offer-letter">
        <!-- Company Header -->
        <div class="offer-header">
          <div class="offer-company">{{ offerData.company || '' }}</div>
          <div class="offer-type">{{ t('panel.examTrainer.anlagen.offer') }}</div>
        </div>

        <!-- Address Block -->
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

        <!-- Body paragraphs (without header/address/table/footer) -->
        <div class="offer-body-text">
          <div v-for="(para, idx) in bodyParagraphs" :key="idx" class="offer-para">
            {{ para }}
          </div>
        </div>

        <!-- Price Table -->
        <table v-if="priceRows.length" class="offer-price-table">
          <thead>
            <tr>
              <th v-for="h in priceHeaders" :key="h">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in priceRows" :key="idx">
              <td v-for="(cell, ci) in row" :key="ci" :class="{ 'text-right': ci >= 2 }">{{ cell }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Totals -->
        <div v-for="(line, idx) in totalLines" :key="'t'+idx" class="offer-total-line">
          {{ line }}
        </div>

        <!-- Conditions -->
        <div class="offer-conditions">
          <div v-for="(cond, idx) in conditionLines" :key="'c'+idx" class="offer-para">
            {{ cond }}
          </div>
        </div>

        <!-- Closing + Signer -->
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

      <!-- GENERIC / INFO DOCUMENT RENDERER -->
      <div v-else class="generic-content" v-html="renderMarkdown(anlage.raw_text)" />

    </div>
  </Modal>
</template>

<style scoped>
.anlage-content {
  color: var(--color-text);
}

/* Offer Letter Styles */
.offer-letter {
  background: #fafaf8;
  color: #1a1a1a;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 32px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 14px;
  line-height: 1.6;
}

.offer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #333;
}

.offer-company {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #1a1a1a;
}

.offer-type {
  font-size: 28px;
  font-weight: 300;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.offer-address-line {
  font-size: 11px;
  color: #888;
  text-decoration: underline;
  margin-bottom: 16px;
}

.offer-meta-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 32px;
}

.offer-recipient {
  font-size: 14px;
  line-height: 1.5;
}

.offer-numbers {
  text-align: right;
  font-size: 13px;
}

.offer-label {
  font-weight: 600;
  margin-right: 8px;
}

.offer-body-text { margin-bottom: 20px; }
.offer-para { margin-bottom: 10px; }

.offer-price-table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.offer-price-table th {
  background: #333;
  color: #fff;
  padding: 8px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
}

.offer-price-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
  font-size: 13px;
}

.text-right { text-align: right; }

.offer-total-line {
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
}

.offer-conditions { margin: 20px 0; }

.offer-closing {
  margin-top: 32px;
}

.offer-closing p { margin-bottom: 8px; }

.offer-signature {
  font-style: italic;
  font-size: 18px;
  margin-top: 16px;
  margin-bottom: 4px;
}

/* API Reference Styles */
.api-reference {
  padding: 8px;
}

.api-table {
  width: 100%;
  border-collapse: collapse;
}

.api-table th {
  background: var(--color-surface, #1a1d27);
  color: var(--color-text, #e2e4ea);
  padding: 10px 14px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 2px solid var(--color-border, #2e3348);
}

.api-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border, #2e3348);
  font-size: 13px;
  color: var(--color-text, #e2e4ea);
}

.api-name code {
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

/* Generic / Info Document */
.generic-content {
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.generic-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.generic-content :deep(th),
.generic-content :deep(td) {
  padding: 8px 12px;
  border: 1px solid var(--color-border, #2e3348);
  font-size: 13px;
}
</style>
