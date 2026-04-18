<template>
  <div class="ft-container">
    <!-- Anweisungstext -->
    <div v-if="tableData.instructions" class="ft-instructions">
      <span class="ft-instructions-icon">&#128221;</span>
      {{ tableData.instructions }}
    </div>

    <!-- Tabelle -->
    <div class="ft-table-wrap">
      <table class="ft-table">
        <thead>
          <tr>
            <th
              v-for="(header, ci) in tableData.headers"
              :key="ci"
              :style="colStyle(ci)"
              class="ft-th"
            >
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, ri) in tableData.rows" :key="ri" class="ft-row">
            <td
              v-for="(cell, ci) in row"
              :key="ci"
              :style="colStyle(ci)"
              :class="cellClass(ri, ci, cell)"
              class="ft-td"
            >
              <!-- Editierbare Zelle -->
              <template v-if="cell.editable">
                <input
                  v-if="!submitted"
                  :value="answers[`${ri}-${ci}`] || ''"
                  @input="onInput(ri, ci, ($event.target as HTMLInputElement).value)"
                  :placeholder="cell.hint || ''"
                  :disabled="submitted"
                  class="ft-input"
                  :class="{ 'ft-input-filled': !!answers[`${ri}-${ci}`] }"
                  spellcheck="false"
                  autocomplete="off"
                />
                <!-- Nach Abgabe: Ergebnis anzeigen -->
                <div v-else class="ft-result-cell">
                  <span class="ft-user-answer" :class="getCellResultClass(ri, ci)">
                    {{ answers[`${ri}-${ci}`] || '(leer)' }}
                  </span>
                  <span v-if="getCellResult(ri, ci)?.correct" class="ft-check">&#10003;</span>
                  <span v-else-if="getCellResult(ri, ci)" class="ft-cross">
                    &#10007;
                    <span class="ft-expected">{{ getCellResult(ri, ci)?.expected }}</span>
                  </span>
                </div>
              </template>

              <!-- Read-only Zelle -->
              <template v-else>
                <span class="ft-static">{{ cell.value }}</span>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Score-Anzeige nach Abgabe -->
    <div v-if="submitted && gradingResult" class="ft-score-bar">
      <div class="ft-score-fill" :style="{ width: gradingResult.pct + '%' }" :class="scoreClass"></div>
      <span class="ft-score-text">
        {{ gradingResult.correctCount }}/{{ gradingResult.editableCount }} Zellen korrekt
        ({{ gradingResult.pct }}%)
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FillableTableData, TableGradingResult, FillableCell } from '../types'
import { gradeTable } from '../utils/tableGrading'

const props = defineProps<{
  tableData: FillableTableData
  submitted: boolean
  modelValue?: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, string>): void
  (e: 'graded', result: TableGradingResult): void
}>()

// Interne Antworten
const answers = ref<Record<string, string>>(props.modelValue || {})
const gradingResult = ref<TableGradingResult | null>(null)

// Spaltenbreite berechnen
function colStyle(colIndex: number): Record<string, string> {
  if (props.tableData.columnWidths?.[colIndex]) {
    return { width: props.tableData.columnWidths[colIndex] + '%' }
  }
  return { width: (100 / props.tableData.headers.length) + '%' }
}

// Input-Handler
function onInput(row: number, col: number, value: string) {
  answers.value[`${row}-${col}`] = value
  emit('update:modelValue', { ...answers.value })
}

// Zellen-Klassen
function cellClass(row: number, col: number, cell: FillableCell): string[] {
  const classes: string[] = []
  if (cell.editable) classes.push('ft-editable')
  if (!cell.editable) classes.push('ft-readonly')
  if (row % 2 === 0) classes.push('ft-row-even')
  return classes
}

// Ergebnis für eine bestimmte Zelle
function getCellResult(row: number, col: number) {
  return gradingResult.value?.cellResults.find(r => r.row === row && r.col === col)
}

function getCellResultClass(row: number, col: number): string {
  const result = getCellResult(row, col)
  if (!result) return ''
  return result.correct ? 'ft-correct' : 'ft-incorrect'
}

// Score-Klasse
const scoreClass = computed(() => {
  if (!gradingResult.value) return ''
  if (gradingResult.value.pct >= 80) return 'ft-score-great'
  if (gradingResult.value.pct >= 50) return 'ft-score-ok'
  return 'ft-score-bad'
})

// Bewertung auslösen wenn submitted sich ändert
watch(() => props.submitted, (isSubmitted) => {
  if (isSubmitted) {
    const result = gradeTable(props.tableData, answers.value)
    gradingResult.value = result
    emit('graded', result)
  }
})

// Externe modelValue-Änderungen übernehmen
watch(() => props.modelValue, (newVal) => {
  if (newVal) answers.value = { ...newVal }
})
</script>

<style scoped>
.ft-container {
  width: 100%;
  margin: 12px 0;
}

.ft-instructions {
  background: rgba(26, 115, 232, 0.08);
  border-left: 3px solid #1a73e8;
  padding: 10px 14px;
  margin-bottom: 12px;
  border-radius: 0 6px 6px 0;
  font-size: 0.9rem;
  color: #b0bec5;
  line-height: 1.5;
}
.ft-instructions-icon {
  margin-right: 6px;
}

.ft-table-wrap {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}

.ft-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.ft-th {
  background: rgba(13, 71, 161, 0.35);
  color: #e3f2fd;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 2px solid rgba(26, 115, 232, 0.3);
  white-space: nowrap;
}

.ft-td {
  padding: 6px 8px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  vertical-align: middle;
}

.ft-row-even {
  background: rgba(255,255,255,0.015);
}

.ft-editable {
  background: rgba(26, 115, 232, 0.04);
}

.ft-readonly .ft-static {
  color: #90a4ae;
  font-size: 0.86rem;
}

/* Input-Feld */
.ft-input {
  width: 100%;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 4px;
  padding: 7px 10px;
  color: #e0e0e0;
  font-size: 0.88rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  transition: all 0.2s ease;
  outline: none;
  box-sizing: border-box;
}
.ft-input::placeholder {
  color: rgba(255,255,255,0.2);
  font-style: italic;
  font-family: inherit;
}
.ft-input:focus {
  border-color: #1a73e8;
  background: rgba(26, 115, 232, 0.08);
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.15);
}
.ft-input-filled {
  border-color: rgba(255,255,255,0.2);
}
.ft-input:disabled {
  opacity: 0.5;
}

/* Ergebnis-Anzeige */
.ft-result-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
}

.ft-user-answer {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.88rem;
  padding: 4px 8px;
  border-radius: 4px;
}

.ft-correct {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.25);
}
.ft-incorrect {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
  text-decoration: line-through;
}

.ft-check {
  color: #22c55e;
  font-size: 1.1rem;
  font-weight: 700;
}
.ft-cross {
  color: #ef4444;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 4px;
}
.ft-expected {
  color: #22c55e;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.82rem;
  opacity: 0.9;
}

/* Score-Leiste */
.ft-score-bar {
  position: relative;
  height: 32px;
  background: rgba(255,255,255,0.04);
  border-radius: 6px;
  margin-top: 12px;
  overflow: hidden;
}
.ft-score-fill {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  border-radius: 6px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.ft-score-great { background: rgba(34, 197, 94, 0.25); }
.ft-score-ok { background: rgba(245, 158, 11, 0.25); }
.ft-score-bad { background: rgba(239, 68, 68, 0.2); }

.ft-score-text {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.82rem;
  font-weight: 600;
  color: #e0e0e0;
  white-space: nowrap;
}
</style>
