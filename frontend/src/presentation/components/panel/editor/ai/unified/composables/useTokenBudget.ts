/**
 * useTokenBudget — Token tracking and budget enforcement
 */
import { ref, computed } from 'vue'

const DEFAULT_BUDGET = 100_000

export function useTokenBudget(budget = DEFAULT_BUDGET) {
  const totalBudget = ref(budget)
  const tokensUsed = ref(0)

  const tokensRemaining = computed(() => Math.max(0, totalBudget.value - tokensUsed.value))
  const usagePercent = computed(() =>
    totalBudget.value > 0 ? Math.round((tokensUsed.value / totalBudget.value) * 100) : 0,
  )
  const isOverBudget = computed(() => tokensUsed.value >= totalBudget.value)
  const isWarning = computed(() => usagePercent.value >= 80 && !isOverBudget.value)

  function addUsage(input: number, output: number) {
    tokensUsed.value += input + output
  }

  function setBudget(newBudget: number) {
    totalBudget.value = newBudget
  }

  function reset() {
    tokensUsed.value = 0
  }

  return {
    totalBudget,
    tokensUsed,
    tokensRemaining,
    usagePercent,
    isOverBudget,
    isWarning,
    addUsage,
    setBudget,
    reset,
  }
}
