<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/workspace/panel.types'

interface Props {
  window: LsxPanel
}

defineProps<Props>()
const { t } = useI18n()

type PadMode = 'text' | 'table'
const mode = ref<PadMode>('text')
const textContent = ref('')

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
  <div class="scratch-content">
    <!-- Mode toggle -->
    <div class="scratch-toolbar">
      <div class="scratch-modes">
        <button class="scratch-mode-btn" :class="{ active: mode === 'text' }" @click="mode = 'text'">
          {{ t('panel.examTrainer.scratchPad.modeText') }}
        </button>
        <button class="scratch-mode-btn" :class="{ active: mode === 'table' }" @click="mode = 'table'">
          {{ t('panel.examTrainer.scratchPad.modeTable') }}
        </button>
      </div>
    </div>

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
              <input v-model="row.values[ci]" type="text" class="calc-input" inputmode="decimal" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.scratch-content { display: flex; flex-direction: column; height: 100%; }

.scratch-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px; border-bottom: 1px solid var(--color-border, #2e3348); flex-shrink: 0;
}
.scratch-modes { display: flex; gap: 4px; }
.scratch-mode-btn {
  padding: 4px 10px; font-size: 12px; border-radius: 4px;
  color: var(--color-text-secondary, #9094a6); border: 1px solid transparent; transition: all 0.15s;
}
.scratch-mode-btn:hover { color: var(--color-text, #e2e4ea); }
.scratch-mode-btn.active {
  background: rgba(255,255,255,0.1); border-color: var(--color-border, #2e3348);
  color: var(--color-text, #e2e4ea);
}

.scratch-textarea {
  flex: 1; width: 100%; padding: 12px; resize: none;
  background: var(--color-surface, #1e2030); color: var(--color-text, #e2e4ea);
  border: none; outline: none; font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px; line-height: 1.6;
}

.scratch-table-wrap { flex: 1; padding: 8px 12px; overflow-y: auto; }
.scratch-table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.scratch-reset-btn {
  font-size: 11px; padding: 2px 8px; border-radius: 4px;
  color: var(--color-text-secondary); border: 1px solid var(--color-border); transition: all 0.15s;
}
.scratch-reset-btn:hover { color: var(--color-text); background: rgba(255,255,255,0.05); }

.scratch-calc-table { width: 100%; border-collapse: collapse; }
.scratch-calc-table th {
  padding: 6px 8px; font-size: 12px; font-weight: 600;
  color: var(--color-text, #e2e4ea); text-align: center;
  border-bottom: 2px solid var(--color-border, #2e3348);
}
.scratch-calc-table td { padding: 4px 6px; }
.label-cell { font-size: 12px; color: var(--color-text-secondary, #9094a6); white-space: nowrap; padding-right: 12px; }
.result-row .label-cell { font-weight: 600; color: var(--color-text, #e2e4ea); }
.result-row { border-top: 1px solid var(--color-border, #2e3348); }
.calc-input {
  width: 100%; padding: 4px 8px; text-align: right;
  font-size: 13px; font-family: 'JetBrains Mono', monospace;
  background: rgba(255,255,255,0.05); color: var(--color-text, #e2e4ea);
  border: 1px solid var(--color-border, #2e3348); border-radius: 4px; outline: none;
  transition: border-color 0.15s;
}
.calc-input:focus { border-color: #60a5fa; }
</style>
