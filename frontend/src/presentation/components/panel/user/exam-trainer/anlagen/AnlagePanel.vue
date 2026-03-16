<script setup lang="ts">
import { ref, computed, watch, onUnmounted, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import { useAnlageRenderer } from './useAnlageRenderer'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  anlage: Anlage
  examId?: string
  x: number
  y: number
  width: number
  height: number
  zIndex: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  focus: []
}>()

const { t } = useI18n()

// --- Position & size (internal, synced from props) ---
const pos = ref({ x: props.x, y: props.y })
const size = ref({ w: props.width, h: props.height })
const isDragging = ref(false)
const isResizing = ref(false)

watch(() => [props.x, props.y], ([x, y]) => {
  if (!isDragging.value) pos.value = { x, y }
})

watch(() => [props.width, props.height], ([w, h]) => {
  if (!isResizing.value) size.value = { w, h }
})

const panelStyle = computed(() => ({
  left: `${pos.value.x}px`,
  top: `${pos.value.y}px`,
  width: `${size.value.w}px`,
  height: `${size.value.h}px`,
  zIndex: props.zIndex,
}))

// --- Drag ---
let dragOffset = { x: 0, y: 0 }

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  dragOffset = { x: e.clientX - pos.value.x, y: e.clientY - pos.value.y }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  emit('focus')
}

const onDrag = (e: MouseEvent) => {
  pos.value = {
    x: Math.max(0, Math.min(window.innerWidth - 100, e.clientX - dragOffset.x)),
    y: Math.max(0, Math.min(window.innerHeight - 40, e.clientY - dragOffset.y)),
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// --- Resize ---
let resizeStart = { x: 0, y: 0, w: 0, h: 0 }

const startResize = (e: MouseEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isResizing.value = true
  resizeStart = { x: e.clientX, y: e.clientY, w: size.value.w, h: size.value.h }
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  emit('focus')
}

const onResize = (e: MouseEvent) => {
  size.value = {
    w: Math.max(380, resizeStart.w + (e.clientX - resizeStart.x)),
    h: Math.max(260, resizeStart.h + (e.clientY - resizeStart.y)),
  }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
})

// --- Popout to new browser window ---
const popout = () => {
  if (!props.examId) return
  const url = `/exam-trainer/anlage/${props.examId}/${props.anlage.number}`
  window.open(url, `anlage-${props.anlage.number}`, 'width=860,height=700,menubar=no,toolbar=no')
}

// --- Anlage rendering (shared composable) ---
const anlageRef = toRef(props, 'anlage')
const {
  isOffer, isApiRef, offerData, functions,
  recipientLines, priceHeaders, priceRows, totalLines,
  bodyParagraphs, conditionLines,
} = useAnlageRenderer(anlageRef)
</script>

<template>
  <Teleport to="body">
    <div
      class="anlage-panel"
      :style="panelStyle"
      @mousedown="emit('focus')"
    >
      <!-- Header (drag handle) -->
      <div class="anlage-panel-header" @mousedown.prevent="startDrag">
        <span class="anlage-panel-title">
          {{ t('panel.examTrainer.anlagen.anlageNr', { number: anlage.number }) }}
          — {{ anlage.title }}
        </span>
        <button
          v-if="examId"
          class="anlage-panel-action"
          :title="t('panel.examTrainer.anlagen.popout')"
          @mousedown.stop
          @click="popout"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </button>
        <button
          class="anlage-panel-close"
          aria-label="Close"
          @mousedown.stop
          @click="emit('close')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="anlage-panel-body">
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

      <!-- Resize handle -->
      <div class="anlage-panel-resize" @mousedown="startResize" />
    </div>
  </Teleport>
</template>

<style scoped>
.anlage-panel {
  position: fixed;
  display: flex;
  flex-direction: column;
  background: var(--color-surface, #1e2030);
  border: 1px solid var(--color-border, #2e3348);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.anlage-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
  background: var(--color-surface-elevated, #252840);
  border-bottom: 1px solid var(--color-border, #2e3348);
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
}

.anlage-panel-header:active { cursor: grabbing; }

.anlage-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text, #e2e4ea);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.anlage-panel-action,
.anlage-panel-close {
  flex-shrink: 0;
  padding: 4px;
  border-radius: 4px;
  color: var(--color-text-secondary, #9094a6);
  transition: all 0.15s;
}

.anlage-panel-action:hover,
.anlage-panel-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text, #e2e4ea);
}

.anlage-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.anlage-panel-resize {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 50%, var(--color-text-secondary, #9094a6) 50%);
  opacity: 0.3;
  border-radius: 0 0 10px 0;
  transition: opacity 0.15s;
}

.anlage-panel-resize:hover { opacity: 0.6; }

/* --- Offer Letter: Paper-on-desk effect (Dark Mode Fix) --- */
.offer-letter {
  background: #fafaf8;
  color: #1a1a1a;
  border-radius: 4px;
  padding: 32px 36px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #c8c8c4;
}

.offer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #333;
}

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
.offer-price-table th {
  background: #333; color: #fff; padding: 8px 12px;
  text-align: left; font-size: 12px; font-weight: 600;
}
.offer-price-table td { padding: 8px 12px; border-bottom: 1px solid #ddd; font-size: 13px; }
.text-right { text-align: right; }

.offer-total-line { text-align: right; font-size: 14px; font-weight: 600; padding: 4px 12px; }
.offer-conditions { margin: 20px 0; }
.offer-closing { margin-top: 32px; }
.offer-closing p { margin-bottom: 8px; }
.offer-signature { font-style: italic; font-size: 18px; margin-top: 16px; margin-bottom: 4px; }

/* --- API Reference --- */
.api-reference { padding: 8px; }
.api-table { width: 100%; border-collapse: collapse; }
.api-table th {
  background: var(--color-surface, #1a1d27); color: var(--color-text, #e2e4ea);
  padding: 10px 14px; text-align: left; font-size: 13px; font-weight: 600;
  border-bottom: 2px solid var(--color-border, #2e3348);
}
.api-table td {
  padding: 10px 14px; border-bottom: 1px solid var(--color-border, #2e3348);
  font-size: 13px; color: var(--color-text, #e2e4ea);
}
.api-name code {
  font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 13px;
  color: #60a5fa; background: rgba(96, 165, 250, 0.1);
  padding: 2px 6px; border-radius: 4px; white-space: nowrap;
}

/* --- Generic / Info Document --- */
.generic-content { font-size: 14px; line-height: 1.7; white-space: pre-wrap; }
.generic-content :deep(table) { width: 100%; border-collapse: collapse; margin: 12px 0; }
.generic-content :deep(th),
.generic-content :deep(td) {
  padding: 8px 12px; border: 1px solid var(--color-border, #2e3348); font-size: 13px;
}
</style>
