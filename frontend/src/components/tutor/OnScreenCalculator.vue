<!--
  OnScreenCalculator - Kompakter, schöner Taschenrechner

  REDESIGNED: Smaller, cleaner, professional design
-->

<template>
  <div class="calc-wrapper" :class="{ 'has-challenge': !!challenge }">
    <!-- Challenge Header -->
    <div v-if="challenge" class="calc-challenge">
      <span class="challenge-icon">🧮</span>
      <span class="challenge-text">{{ challenge.prompt }}</span>
    </div>

    <!-- Display -->
    <div class="calc-display">
      <div class="display-input" :class="{ error: hasError }">
        {{ displayFormula || '0' }}
      </div>
      <div v-if="currentResult !== null" class="display-result">
        = {{ formatNumber(currentResult) }}
      </div>
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
      Ergebnis prüfen
    </button>

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

interface CalculatorChallenge {
  prompt: string
  expectedResult: number
  tolerance?: number
  hint?: string
}

const props = defineProps<{
  challenge?: CalculatorChallenge
  showHistory?: boolean
}>()

const emit = defineEmits<{
  (e: 'result-submitted', result: number): void
  (e: 'correct', result: number): void
  (e: 'wrong', result: number, expected: number): void
  (e: 'calculate', result: number): void
}>()

// State
const displayFormula = ref('')
const currentResult = ref<number | null>(null)
const hasError = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref<'correct' | 'wrong'>('correct')
const waitingForOperator = ref(false)

// Format number German style
function formatNumber(num: number): string {
  return num.toLocaleString('de-DE', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

function inputDigit(digit: string) {
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

function calculate() {
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
  } catch {
    hasError.value = true
    currentResult.value = null
  }
}

function clear() {
  displayFormula.value = ''
  currentResult.value = null
  hasError.value = false
  waitingForOperator.value = false
}

function backspace() {
  if (displayFormula.value.length > 0) {
    displayFormula.value = displayFormula.value.slice(0, -1)
    currentResult.value = null
  }
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
      feedbackMessage.value = 'Richtig!'
      emit('correct', currentResult.value)
    } else {
      feedbackType.value = 'wrong'
      feedbackMessage.value = `Erwartet: ${formatNumber(props.challenge.expectedResult)}`
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

defineExpose({ clear, calculate, submitResult, currentResult, displayFormula })
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
