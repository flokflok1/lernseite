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
      <span class="challenge-icon">&#x1F9EE;</span>
      <span class="challenge-text">{{ challenge.prompt }}</span>
    </div>

    <!-- Display -->
    <div class="calc-display">
      <div class="display-meta" v-if="memory !== 0 || sessionId">
        <span v-if="memory !== 0" class="memory-indicator">M</span>
        <span v-if="sessionId" class="session-indicator">&#x25CF;</span>
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
      <button @click="memorySubtract" class="btn mem" title="Memory Subtract">M&#x2212;</button>
    </div>

    <!-- Compact Button Grid -->
    <div class="calc-grid">
      <button @click="clear" class="btn fn">C</button>
      <button @click="backspace" class="btn fn">&#x232B;</button>
      <button @click="inputPercent" class="btn fn">%</button>
      <button @click="inputOperator('/')" class="btn op">&#x00F7;</button>

      <button @click="inputDigit('7')" class="btn">7</button>
      <button @click="inputDigit('8')" class="btn">8</button>
      <button @click="inputDigit('9')" class="btn">9</button>
      <button @click="inputOperator('*')" class="btn op">&#x00D7;</button>

      <button @click="inputDigit('4')" class="btn">4</button>
      <button @click="inputDigit('5')" class="btn">5</button>
      <button @click="inputDigit('6')" class="btn">6</button>
      <button @click="inputOperator('-')" class="btn op">&#x2212;</button>

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
      <span class="submit-icon">&#x2713;</span>
      {{ $t('calculator.checkResult') }}
    </button>

    <!-- History Panel (optional) -->
    <CalculatorHistoryPanel
      v-if="showHistory"
      :history="history"
      :format-number="formatNumber"
      @clear="clearHistory"
      @use-entry="useHistoryEntry"
    />

    <!-- Feedback Toast -->
    <Transition name="toast">
      <div v-if="feedbackMessage" class="feedback-toast" :class="feedbackType">
        <span class="feedback-icon">{{ feedbackType === 'correct' ? '\u2713' : '\u2717' }}</span>
        {{ feedbackMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, toRef, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import CalculatorHistoryPanel from './CalculatorHistoryPanel.vue'
import { useCalculator, type CalculatorChallenge } from './composables/useCalculator'

const { t } = useI18n()

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

const feedbackMessage = ref('')
const feedbackType = ref<'correct' | 'wrong'>('correct')

const {
  displayFormula,
  currentResult,
  hasError,
  memory,
  history,
  keystrokes,
  inputDigit,
  inputDecimal,
  inputOperator,
  inputPercent,
  calculate,
  clear,
  backspace,
  memoryAdd,
  memorySubtract,
  memoryRecall,
  memoryClear,
  useHistoryEntry,
  clearHistory,
  formatNumber
} = useCalculator({
  sessionId: toRef(props, 'sessionId'),
  saveToBackend: toRef(props, 'saveToBackend'),
  onKeystroke: (key: string) => emit('keystroke', key),
  onCalculate: (result: number) => emit('calculate', result)
})

function submitResult(): void {
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

function handleKeydown(e: KeyboardEvent): void {
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

.challenge-icon { font-size: 1rem; }
.challenge-text {
  color: #e2e8f0;
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.3;
}

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

.display-input.error { color: #ef4444; }

.display-result {
  color: #6366f1;
  font-size: 1rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

.display-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
}

.memory-indicator { color: #f59e0b; font-weight: 600; }
.session-indicator { color: #10b981; }

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

.btn.mem:hover { background: #334155; color: #f59e0b; }

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

.btn:hover { background: #475569; }
.btn:active { transform: scale(0.95); }
.btn.fn { background: #475569; color: #94a3b8; }
.btn.fn:hover { background: #64748b; }
.btn.op { background: #3b82f6; color: white; }
.btn.op:hover { background: #2563eb; }
.btn.eq { background: #10b981; color: white; }
.btn.eq:hover { background: #059669; }
.btn.zero { grid-column: span 2; }

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

.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.submit-icon { font-size: 1rem; }

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

.feedback-toast.correct { background: rgba(16, 185, 129, 0.95); color: white; }
.feedback-toast.wrong { background: rgba(239, 68, 68, 0.95); color: white; }
.feedback-icon { font-size: 1.125rem; }

.calc-wrapper.expanded { width: 280px; }

.toast-enter-active,
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from,
.toast-leave-to { opacity: 0; transform: translateY(10px); }
</style>
