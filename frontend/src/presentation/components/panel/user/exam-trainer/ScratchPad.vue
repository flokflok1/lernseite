<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
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

// --- Position & size ---
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
    w: Math.max(320, resizeStart.w + (e.clientX - resizeStart.x)),
    h: Math.max(240, resizeStart.h + (e.clientY - resizeStart.y)),
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

// --- Content ---
type PadMode = 'text' | 'table'
const mode = ref<PadMode>('text')
const textContent = ref('')

// Angebotsvergleich table template
interface CalcRow { label: string; values: string[] }
const offerCount = ref(2)
const calcRows = ref<CalcRow[]>(createDefaultRows())

function createDefaultRows(): CalcRow[] {
  return [
    { label: 'Listeneinkaufspreis', values: ['', ''] },
    { label: '- Rabatt', values: ['', ''] },
    { label: '= Zieleinkaufspreis', values: ['', ''] },
    { label: '- Skonto', values: ['', ''] },
    { label: '= Bareinkaufspreis', values: ['', ''] },
    { label: '+ Bezugskosten', values: ['', ''] },
    { label: '= Bezugspreis', values: ['', ''] },
  ]
}

const resetTable = () => { calcRows.value = createDefaultRows() }
</script>

<template>
  <Teleport to="body">
    <div class="scratch-panel" :style="panelStyle" @mousedown="emit('focus')">
      <!-- Header -->
      <div class="scratch-header" @mousedown.prevent="startDrag">
        <div class="scratch-title-row">
          <svg class="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <span class="scratch-title">{{ t('panel.examTrainer.scratchPad.title') }}</span>
        </div>
        <div class="scratch-actions">
          <!-- Mode toggle -->
          <button
            class="scratch-mode-btn"
            :class="{ active: mode === 'text' }"
            @mousedown.stop
            @click="mode = 'text'"
          >{{ t('panel.examTrainer.scratchPad.modeText') }}</button>
          <button
            class="scratch-mode-btn"
            :class="{ active: mode === 'table' }"
            @mousedown.stop
            @click="mode = 'table'"
          >{{ t('panel.examTrainer.scratchPad.modeTable') }}</button>
          <button class="scratch-close" aria-label="Close" @mousedown.stop @click="emit('close')">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="scratch-body">
        <!-- Text mode -->
        <textarea
          v-if="mode === 'text'"
          v-model="textContent"
          class="scratch-textarea"
          :placeholder="t('panel.examTrainer.scratchPad.placeholder')"
        />

        <!-- Table mode: Angebotsvergleich -->
        <div v-else class="scratch-table-wrap">
          <div class="scratch-table-header">
            <span class="text-xs text-[var(--color-text-secondary)]">
              {{ t('panel.examTrainer.scratchPad.tableHint') }}
            </span>
            <button class="scratch-reset-btn" @click="resetTable">
              {{ t('panel.examTrainer.scratchPad.reset') }}
            </button>
          </div>
          <table class="scratch-calc-table">
            <thead>
              <tr>
                <th></th>
                <th v-for="i in offerCount" :key="i">
                  {{ t('panel.examTrainer.anlagen.offer') }} {{ i }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in calcRows" :key="ri" :class="{ 'result-row': row.label.startsWith('=') }">
                <td class="label-cell">{{ row.label }}</td>
                <td v-for="(_, ci) in offerCount" :key="ci">
                  <input
                    v-model="row.values[ci]"
                    type="text"
                    class="calc-input"
                    inputmode="decimal"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Resize handle -->
      <div class="scratch-resize" @mousedown="startResize" />
    </div>
  </Teleport>
</template>

<style scoped>
.scratch-panel {
  position: fixed;
  display: flex;
  flex-direction: column;
  background: var(--color-surface, #1e2030);
  border: 1px solid var(--color-border, #2e3348);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.scratch-header {
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

.scratch-header:active { cursor: grabbing; }

.scratch-title-row { display: flex; align-items: center; gap: 6px; }
.scratch-title { font-size: 13px; font-weight: 600; color: var(--color-text, #e2e4ea); }

.scratch-actions { display: flex; align-items: center; gap: 4px; }

.scratch-mode-btn {
  padding: 2px 8px; font-size: 11px; border-radius: 4px;
  color: var(--color-text-secondary, #9094a6);
  border: 1px solid transparent;
  transition: all 0.15s;
}
.scratch-mode-btn:hover { color: var(--color-text, #e2e4ea); }
.scratch-mode-btn.active {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-border, #2e3348);
  color: var(--color-text, #e2e4ea);
}

.scratch-close {
  padding: 4px; border-radius: 4px;
  color: var(--color-text-secondary, #9094a6); transition: all 0.15s;
}
.scratch-close:hover { background: rgba(255, 255, 255, 0.1); color: var(--color-text, #e2e4ea); }

.scratch-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }

.scratch-textarea {
  flex: 1; width: 100%; padding: 12px; resize: none;
  background: var(--color-surface, #1e2030);
  color: var(--color-text, #e2e4ea);
  border: none; outline: none;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px; line-height: 1.6;
}

.scratch-table-wrap { flex: 1; padding: 8px 12px; overflow-y: auto; }
.scratch-table-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px;
}

.scratch-reset-btn {
  font-size: 11px; padding: 2px 8px; border-radius: 4px;
  color: var(--color-text-secondary); border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.scratch-reset-btn:hover { color: var(--color-text); background: rgba(255,255,255,0.05); }

.scratch-calc-table { width: 100%; border-collapse: collapse; }
.scratch-calc-table th {
  padding: 6px 8px; font-size: 12px; font-weight: 600;
  color: var(--color-text, #e2e4ea); text-align: center;
  border-bottom: 2px solid var(--color-border, #2e3348);
}
.scratch-calc-table td { padding: 4px 6px; }
.label-cell {
  font-size: 12px; color: var(--color-text-secondary, #9094a6);
  white-space: nowrap; padding-right: 12px;
}
.result-row .label-cell { font-weight: 600; color: var(--color-text, #e2e4ea); }
.result-row { border-top: 1px solid var(--color-border, #2e3348); }

.calc-input {
  width: 100%; padding: 4px 8px; text-align: right;
  font-size: 13px; font-family: 'JetBrains Mono', monospace;
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text, #e2e4ea);
  border: 1px solid var(--color-border, #2e3348);
  border-radius: 4px; outline: none;
  transition: border-color 0.15s;
}
.calc-input:focus { border-color: #60a5fa; }

.scratch-resize {
  position: absolute; right: 0; bottom: 0; width: 16px; height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 50%, var(--color-text-secondary, #9094a6) 50%);
  opacity: 0.3; border-radius: 0 0 10px 0; transition: opacity 0.15s;
}
.scratch-resize:hover { opacity: 0.6; }
</style>
