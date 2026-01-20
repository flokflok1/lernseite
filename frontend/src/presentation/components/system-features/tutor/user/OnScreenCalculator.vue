<!--
  OnScreenCalculator - Kompakter, schöner Taschenrechner

  REDESIGNED: Smaller, cleaner, professional design
  ENHANCED: Backend integration, Memory, History, Keystrokes

  Features:
  - Standard-Rechenoperationen
  - Prozent-Taste
  - Memory (M+, M-, MR, MC)
  - Verlauf (History) mit Backend-Sync
  - Keystroke-Tracking für Replay
  - Session-Integration für MathToolkit
-->

<template>
  <div class="calc-wrapper" :class="{ 'has-challenge': !!challenge, 'expanded': showMemory || showHistory }">
    <!-- Challenge Header -->
    <div v-if="challenge" class="calc-challenge">
      <span class="challenge-icon">🧮</span>
      <span class="challenge-text">{{ challenge.prompt }}</span>
    </div>

    <!-- Display -->
    <div class="calc-display">
      <div class="display-meta" v-if="memory !== 0 || sessionId">
        <span v-if="memory !== 0" class="memory-indicator">M</span>
        <span v-if="sessionId" class="session-indicator">●</span>
      </div>
      <div class="display-input" :class="{ error: hasError }">
        {{ displayFormula || '0' }}
      </div>
      <div v-if="currentResult !== null" class="display-result">
        = {{ formatNumber(currentResult) }}
      </div>
    </div>

    <!-- Memory Row (optional) -->
    <div v-if="showMemory" class="memory-row">
      <button @click="memoryClear" class="btn mem" title="Memory Clear">MC</button>
      <button @click="memoryRecall" class="btn mem" title="Memory Recall">MR</button>
      <button @click="memoryAdd" class="btn mem" title="Memory Add">M+</button>
      <button @click="memorySubtract" class="btn mem" title="Memory Subtract">M−</button>
    </div>

    <!-- Compact Button Grid -->
    <div class="calc-grid">
      <button @click="clear" class="btn fn">C</button>
      <button @click="backspace" class="btn fn">⌫</button>
      <button @click="inputPercent" class="btn fn">%</button>
      <button @click="inputOperator('/')" class="btn op">÷</button>

      <button @click="inputDigit('7')" class="btn">7</button>
      <button @click="inputDigit('8')" class="btn">8</button>
      <button @click="inputDigit('9')" class="btn">9</button>
      <button @click="inputOperator('*')" class="btn op">×</button>

      <button @click="inputDigit('4')" class="btn">4</button>
      <button @click="inputDigit('5')" class="btn">5</button>
      <button @click="inputDigit('6')" class="btn">6</button>
      <button @click="inputOperator('-')" class="btn op">−</button>

      <button @click="inputDigit('1')" class="btn">1</button>
      <button @click="inputDigit('2')" class="btn">2</button>
      <button @click="inputDigit('3')" class="btn">3</button>
      <button @click="inputOperator('+')" class="btn op">+</button>

      <button @click="inputDigit('0')" class="btn zero">0</button>
      <button @click="inputDecimal" class="btn">,</button>
      <button @click="calculate" class="btn eq">=</button>
    </div>

    <!-- Submit Button (Challenge Mode) -->
    <button
      v-if="challenge"
      @click="submitResult"
      class="submit-btn"
      :disabled="currentResult === null"
    >
      <span class="submit-icon">✓</span>
      {{ $t('calculator.checkResult') }}
    </button>

    <!-- History Panel (optional) -->
    <div v-if="showHistory && history.length > 0" class="history-panel">
      <div class="history-header">
        <span>{{ $t('calculator.history') }}</span>
        <button @click="clearHistory" class="history-clear">{{ $t('calculator.clearHistory') }}</button>
      </div>
      <div class="history-list">
        <div
          v-for="(entry, idx) in history.slice(0, 5)"
          :key="idx"
          class="history-entry"
          @click="useHistoryEntry(entry)"
        >
          <span class="entry-formula">{{ entry.formula }}</span>
          <span class="entry-result">= {{ formatNumber(entry.result) }}</span>
        </div>
      </div>
    </div>

    <!-- Feedback Toast -->
    <Transition name="toast">
      <div v-if="feedbackMessage" class="feedback-toast" :class="feedbackType">
        <span class="feedback-icon">{{ feedbackType === 'correct' ? '✓' : '✗' }}</span>
        {{ feedbackMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { mathToolkitApi } from '@/infrastructure/api/mathToolkit.api'

const { t } = useI18n()

interface CalculatorChallenge {
  prompt: string
  expectedResult: number
  tolerance?: number
  hint?: string
}

interface HistoryEntry {
  formula: string
  result: number
  keystrokes?: string[]
  timestamp?: Date
}

const props = withDefaults(defineProps<{
  challenge?: CalculatorChallenge
  showHistory?: boolean
  showMemory?: boolean
  sessionId?: string
  saveToBackend?: boolean
}>(), {
  showHistory: false,
  showMemory: false,
  saveToBackend: false
})

const emit = defineEmits<{
  (e: 'result-submitted', result: number): void
  (e: 'correct', result: number): void
  (e: 'wrong', result: number, expected: number): void
  (e: 'calculate', result: number): void
  (e: 'keystroke', key: string): void
}>()

// State
const displayFormula = ref('')
const currentResult = ref<number | null>(null)
const hasError = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref<'correct' | 'wrong'>('correct')
const waitingForOperator = ref(false)

// Memory State
const memory = ref(0)

// History State
const history = ref<HistoryEntry[]>([])
const keystrokes = ref<string[]>([])

// Format number German style
function formatNumber(num: number): string {
  return num.toLocaleString('de-DE', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

// Track keystrokes
function trackKeystroke(key: string) {
  keystrokes.value.push(key)
  emit('keystroke', key)
}

function inputDigit(digit: string) {
  trackKeystroke(digit)
  hasError.value = false
  if (waitingForOperator.value) {
    displayFormula.value = digit
    waitingForOperator.value = false
  } else {
    displayFormula.value += digit
  }
  currentResult.value = null
}

function inputDecimal() {
  trackKeystroke('.')
  hasError.value = false
  const parts = displayFormula.value.split(/[\+\-\*\/]/)
  const lastPart = parts[parts.length - 1]
  if (!lastPart.includes('.') && !lastPart.includes(',')) {
    if (waitingForOperator.value || displayFormula.value === '') {
      displayFormula.value = '0.'
      waitingForOperator.value = false
    } else {
      displayFormula.value += '.'
    }
  }
}

function inputOperator(op: string) {
  trackKeystroke(op)
  hasError.value = false
  if (displayFormula.value === '' && op === '-') {
    displayFormula.value = '-'
    return
  }
  if (displayFormula.value === '') return

  const lastChar = displayFormula.value.slice(-1)
  if (['+', '-', '*', '/'].includes(lastChar)) {
    displayFormula.value = displayFormula.value.slice(0, -1) + op
  } else {
    displayFormula.value += op
  }
  waitingForOperator.value = false
  currentResult.value = null
}

function inputPercent() {
  trackKeystroke('%')
  if (displayFormula.value === '') return
  try {
    const parts = displayFormula.value.split(/([+\-*/])/)
    const lastPart = parts[parts.length - 1]
    if (lastPart) {
      const num = parseFloat(lastPart.replace(',', '.'))
      parts[parts.length - 1] = (num / 100).toString()
      displayFormula.value = parts.join('')
      calculate()
    }
  } catch {
    hasError.value = true
  }
}

async function calculate() {
  trackKeystroke('=')
  if (displayFormula.value === '') return
  try {
    let formula = displayFormula.value
      .replace(/×/g, '*')
      .replace(/÷/g, '/')
      .replace(/−/g, '-')
      .replace(/,/g, '.')

    const result = Function('"use strict"; return (' + formula + ')')()
    if (isNaN(result) || !isFinite(result)) throw new Error()

    currentResult.value = Math.round(result * 100) / 100
    waitingForOperator.value = true
    emit('calculate', currentResult.value)

    // Add to local history
    const entry: HistoryEntry = {
      formula: displayFormula.value,
      result: currentResult.value,
      keystrokes: [...keystrokes.value],
      timestamp: new Date()
    }
    history.value.unshift(entry)

    // Save to backend if enabled
    if (props.saveToBackend && currentResult.value !== null) {
      try {
        await mathToolkitApi.saveCalculatorEntry({
          expression: displayFormula.value,
          result: currentResult.value,
          result_display: formatNumber(currentResult.value),
          session_id: props.sessionId,
          keystrokes: keystrokes.value,
          memory_used: memory.value !== 0,
          memory_value: memory.value
        })
      } catch (e) {
        console.warn('Could not save to backend:', e)
      }
    }

    // Reset keystrokes for next calculation
    keystrokes.value = []
  } catch {
    hasError.value = true
    currentResult.value = null
  }
}

function clear() {
  trackKeystroke('C')
  displayFormula.value = ''
  currentResult.value = null
  hasError.value = false
  waitingForOperator.value = false
  keystrokes.value = []
}

function backspace() {
  trackKeystroke('⌫')
  if (displayFormula.value.length > 0) {
    displayFormula.value = displayFormula.value.slice(0, -1)
    currentResult.value = null
  }
}

// Memory Functions
function memoryAdd() {
  trackKeystroke('M+')
  const value = currentResult.value ?? parseFloat(displayFormula.value.replace(',', '.'))
  if (!isNaN(value)) {
    memory.value += value
  }
}

function memorySubtract() {
  trackKeystroke('M-')
  const value = currentResult.value ?? parseFloat(displayFormula.value.replace(',', '.'))
  if (!isNaN(value)) {
    memory.value -= value
  }
}

function memoryRecall() {
  trackKeystroke('MR')
  displayFormula.value = memory.value.toString()
  currentResult.value = null
  waitingForOperator.value = true
}

function memoryClear() {
  trackKeystroke('MC')
  memory.value = 0
}

// History Functions
function useHistoryEntry(entry: HistoryEntry) {
  displayFormula.value = entry.result.toString()
  currentResult.value = entry.result
  waitingForOperator.value = true
}

function clearHistory() {
  history.value = []
}

function submitResult() {
  if (currentResult.value === null) {
    calculate()
    if (currentResult.value === null) return
  }

  emit('result-submitted', currentResult.value)

  if (props.challenge) {
    const tolerance = props.challenge.tolerance ?? 0.01
    const diff = Math.abs(currentResult.value - props.challenge.expectedResult)

    if (diff <= tolerance) {
      feedbackType.value = 'correct'
      feedbackMessage.value = t('calculator.correct')
      emit('correct', currentResult.value)
    } else {
      feedbackType.value = 'wrong'
      feedbackMessage.value = t('calculator.expected', { value: formatNumber(props.challenge.expectedResult) })
      emit('wrong', currentResult.value, props.challenge.expectedResult)
    }

    setTimeout(() => { feedbackMessage.value = '' }, 2500)
  }
}

// Keyboard support
function handleKeydown(e: KeyboardEvent) {
  const keys = ['0','1','2','3','4','5','6','7','8','9','.',',','+','-','*','/','=','Enter','Escape','Backspace','%']
  if (keys.includes(e.key)) e.preventDefault()

  if (/^[0-9]$/.test(e.key)) inputDigit(e.key)
  else if (e.key === '.' || e.key === ',') inputDecimal()
  else if (e.key === '+') inputOperator('+')
  else if (e.key === '-') inputOperator('-')
  else if (e.key === '*') inputOperator('*')
  else if (e.key === '/') inputOperator('/')
  else if (e.key === '%') inputPercent()
  else if (e.key === '=' || e.key === 'Enter') {
    if (props.challenge && currentResult.value !== null) submitResult()
    else calculate()
  }
  else if (e.key === 'Escape') clear()
  else if (e.key === 'Backspace') backspace()
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

watch(() => props.challenge, () => {
  clear()
  feedbackMessage.value = ''
})

defineExpose({
  clear,
  calculate,
  submitResult,
  currentResult,
  displayFormula,
  memory,
  history,
  keystrokes,
  memoryAdd,
  memorySubtract,
  memoryRecall,
  memoryClear,
  clearHistory
})
</script>

<style scoped>
.calc-wrapper {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 1rem;
  padding: 1rem;
  width: 260px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

/* Challenge Header */
.calc-challenge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
}

.challenge-icon {
  font-size: 1rem;
}

.challenge-text {
  color: #e2e8f0;
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.3;
}

/* Display */
.calc-display {
  background: #0f172a;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  text-align: right;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.display-input {
  color: #f1f5f9;
  font-size: 1.5rem;
  font-weight: 400;
  font-family: 'SF Mono', 'Fira Code', monospace;
  word-break: break-all;
  transition: color 0.2s;
}

.display-input.error {
  color: #ef4444;
}

.display-result {
  color: #6366f1;
  font-size: 1rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Button Grid */
.calc-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.375rem;
}

.btn {
  height: 44px;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.1s;
  background: #334155;
  color: #f1f5f9;
}

.btn:hover {
  background: #475569;
}

.btn:active {
  transform: scale(0.95);
}

.btn.fn {
  background: #475569;
  color: #94a3b8;
}

.btn.fn:hover {
  background: #64748b;
}

.btn.op {
  background: #3b82f6;
  color: white;
}

.btn.op:hover {
  background: #2563eb;
}

.btn.eq {
  background: #10b981;
  color: white;
}

.btn.eq:hover {
  background: #059669;
}

.btn.zero {
  grid-column: span 2;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.625rem;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-icon {
  font-size: 1rem;
}

/* Feedback Toast */
.feedback-toast {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.feedback-toast.correct {
  background: rgba(16, 185, 129, 0.95);
  color: white;
}

.feedback-toast.wrong {
  background: rgba(239, 68, 68, 0.95);
  color: white;
}

.feedback-icon {
  font-size: 1.125rem;
}

/* Display Meta (Memory & Session indicators) */
.display-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
}

.memory-indicator {
  color: #f59e0b;
  font-weight: 600;
}

.session-indicator {
  color: #10b981;
}

/* Memory Row */
.memory-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.btn.mem {
  height: 32px;
  font-size: 0.75rem;
  background: #1e293b;
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn.mem:hover {
  background: #334155;
  color: #f59e0b;
}

/* History Panel */
.history-panel {
  margin-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.75rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.history-clear {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.6875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.history-clear:hover {
  background: rgba(239, 68, 68, 0.1);
}

.history-list {
  max-height: 100px;
  overflow-y: auto;
}

.history-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0.5rem;
  margin-bottom: 0.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.15s;
}

.history-entry:hover {
  background: rgba(99, 102, 241, 0.15);
}

.entry-formula {
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.entry-result {
  color: #6366f1;
  font-weight: 500;
}

/* Expanded state */
.calc-wrapper.expanded {
  width: 280px;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
