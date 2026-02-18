import { ref, type Ref } from 'vue'
import { mathToolkitApi } from '@/application/services/api/panel-user'

export interface CalculatorChallenge {
  prompt: string
  expectedResult: number
  tolerance?: number
  hint?: string
}

export interface HistoryEntry {
  formula: string
  result: number
  keystrokes?: string[]
  timestamp?: Date
}

interface UseCalculatorOptions {
  sessionId?: Ref<string | undefined>
  saveToBackend?: Ref<boolean>
  onKeystroke?: (key: string) => void
  onCalculate?: (result: number) => void
}

interface UseCalculatorReturn {
  displayFormula: Ref<string>
  currentResult: Ref<number | null>
  hasError: Ref<boolean>
  waitingForOperator: Ref<boolean>
  memory: Ref<number>
  history: Ref<HistoryEntry[]>
  keystrokes: Ref<string[]>
  inputDigit: (digit: string) => void
  inputDecimal: () => void
  inputOperator: (op: string) => void
  inputPercent: () => void
  calculate: () => Promise<void>
  clear: () => void
  backspace: () => void
  memoryAdd: () => void
  memorySubtract: () => void
  memoryRecall: () => void
  memoryClear: () => void
  useHistoryEntry: (entry: HistoryEntry) => void
  clearHistory: () => void
  formatNumber: (num: number) => string
}

export function useCalculator(options: UseCalculatorOptions = {}): UseCalculatorReturn {
  const displayFormula = ref('')
  const currentResult = ref<number | null>(null)
  const hasError = ref(false)
  const waitingForOperator = ref(false)
  const memory = ref(0)
  const history = ref<HistoryEntry[]>([])
  const keystrokes = ref<string[]>([])

  function formatNumber(num: number): string {
    return num.toLocaleString('de-DE', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    })
  }

  function trackKeystroke(key: string): void {
    keystrokes.value.push(key)
    options.onKeystroke?.(key)
  }

  function inputDigit(digit: string): void {
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

  function inputDecimal(): void {
    trackKeystroke('.')
    hasError.value = false
    const parts = displayFormula.value.split(/[+\-*/]/)
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

  function inputOperator(op: string): void {
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

  function inputPercent(): void {
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

  async function calculate(): Promise<void> {
    trackKeystroke('=')
    if (displayFormula.value === '') return
    try {
      const formula = displayFormula.value
        .replace(/\u00d7/g, '*')
        .replace(/\u00f7/g, '/')
        .replace(/\u2212/g, '-')
        .replace(/,/g, '.')

      const result = Function('"use strict"; return (' + formula + ')')()
      if (isNaN(result) || !isFinite(result)) throw new Error()

      currentResult.value = Math.round(result * 100) / 100
      waitingForOperator.value = true
      options.onCalculate?.(currentResult.value)

      const entry: HistoryEntry = {
        formula: displayFormula.value,
        result: currentResult.value,
        keystrokes: [...keystrokes.value],
        timestamp: new Date()
      }
      history.value.unshift(entry)

      if (options.saveToBackend?.value && currentResult.value !== null) {
        try {
          await mathToolkitApi.saveCalculatorEntry({
            expression: displayFormula.value,
            result: currentResult.value,
            result_display: formatNumber(currentResult.value),
            session_id: options.sessionId?.value,
            keystrokes: keystrokes.value,
            memory_used: memory.value !== 0,
            memory_value: memory.value
          })
        } catch (e) {
          console.warn('Could not save to backend:', e)
        }
      }

      keystrokes.value = []
    } catch {
      hasError.value = true
      currentResult.value = null
    }
  }

  function clear(): void {
    trackKeystroke('C')
    displayFormula.value = ''
    currentResult.value = null
    hasError.value = false
    waitingForOperator.value = false
    keystrokes.value = []
  }

  function backspace(): void {
    trackKeystroke('\u232b')
    if (displayFormula.value.length > 0) {
      displayFormula.value = displayFormula.value.slice(0, -1)
      currentResult.value = null
    }
  }

  function memoryAdd(): void {
    trackKeystroke('M+')
    const value = currentResult.value ?? parseFloat(displayFormula.value.replace(',', '.'))
    if (!isNaN(value)) {
      memory.value += value
    }
  }

  function memorySubtract(): void {
    trackKeystroke('M-')
    const value = currentResult.value ?? parseFloat(displayFormula.value.replace(',', '.'))
    if (!isNaN(value)) {
      memory.value -= value
    }
  }

  function memoryRecall(): void {
    trackKeystroke('MR')
    displayFormula.value = memory.value.toString()
    currentResult.value = null
    waitingForOperator.value = true
  }

  function memoryClear(): void {
    trackKeystroke('MC')
    memory.value = 0
  }

  function useHistoryEntry(entry: HistoryEntry): void {
    displayFormula.value = entry.result.toString()
    currentResult.value = entry.result
    waitingForOperator.value = true
  }

  function clearHistory(): void {
    history.value = []
  }

  return {
    displayFormula,
    currentResult,
    hasError,
    waitingForOperator,
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
  }
}
