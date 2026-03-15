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
</script>

<template>
  <Modal :show="show" :title="anlage?.title || ''" size="lg" @close="emit('close')">
    <div v-if="anlage" class="anlage-content">

      <!-- OFFER RENDERER — render raw_text as realistic document -->
      <div v-if="isOffer" class="offer-letter">
        <div class="offer-body" v-html="renderMarkdown(anlage.raw_text)" />
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

.offer-body {
  margin-bottom: 24px;
}

.offer-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.offer-body :deep(th) {
  background: #333;
  color: #fff;
  padding: 8px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
}

.offer-body :deep(td) {
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
  font-size: 13px;
}

.offer-body :deep(tr:last-child td) {
  font-weight: 600;
}

.offer-signer {
  margin-top: 32px;
  padding-top: 8px;
}

.offer-signature {
  font-style: italic;
  font-size: 16px;
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
