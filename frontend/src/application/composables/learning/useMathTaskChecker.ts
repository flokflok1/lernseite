/**
 * useMathTaskChecker - Composable for math task answer checking logic.
 *
 * Handles answer normalization, numeric comparison with tolerance,
 * and task state management (submit, reset).
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface TaskData {
  title?: string
  question: string
  steps?: TaskStep[]
  solution: string
  explanation?: string
}

interface TaskStep {
  step?: number
  description: string
  calculation?: string
}

export type { TaskData, TaskStep }

export function useMathTaskChecker(getTaskData: () => TaskData) {
  const { t } = useI18n()

  const userAnswer = ref('')
  const hasSubmitted = ref(false)
  const isCorrect = ref(false)
  const showSteps = ref(false)
  const showSolution = ref(false)
  const showExplanation = ref(false)

  const canShowSolution = computed(() => hasSubmitted.value)

  const feedbackClass = computed(() => ({
    'feedback-correct': isCorrect.value,
    'feedback-incorrect': !isCorrect.value
  }))

  function getPlaceholder(): string {
    const solution = getTaskData().solution?.toLowerCase() || ''
    if (solution.includes('euro') || solution.includes('\u20AC')) {
      return t('lesson.mathTask.placeholderEuro')
    }
    if (solution.includes('%')) {
      return t('lesson.mathTask.placeholderPercent')
    }
    return t('lesson.mathTask.placeholderDefault')
  }

  function normalizeAnswer(answer: string): string {
    return answer
      .toLowerCase()
      .replace(/\s+/g, '')
      .replace(/euro/g, '\u20AC')
      .replace(/prozent/g, '%')
      .replace(/,/g, '.')
      .replace(/[^\d.\u20AC%]/g, '')
  }

  function checkAnswer(): void {
    if (!userAnswer.value.trim()) return

    hasSubmitted.value = true

    const userNormalized = normalizeAnswer(userAnswer.value)
    const solutionNormalized = normalizeAnswer(getTaskData().solution)

    const userNumbers = userNormalized.match(/[\d.]+/g) || []
    const solutionNumbers = solutionNormalized.match(/[\d.]+/g) || []

    if (userNumbers.length > 0 && solutionNumbers.length > 0) {
      const userNum = parseFloat(userNumbers[0])
      const solutionNum = parseFloat(solutionNumbers[0])
      isCorrect.value = Math.abs(userNum - solutionNum) < 0.01
    } else {
      isCorrect.value = userNormalized === solutionNormalized
    }

    showSolution.value = true
  }

  function toggleSolution(): void {
    if (canShowSolution.value) {
      showSolution.value = !showSolution.value
    }
  }

  function toggleSteps(): void {
    if (canShowSolution.value) {
      showSteps.value = !showSteps.value
    }
  }

  function resetTask(): void {
    userAnswer.value = ''
    hasSubmitted.value = false
    isCorrect.value = false
    showSolution.value = false
    showSteps.value = false
    showExplanation.value = false
  }

  return {
    userAnswer,
    hasSubmitted,
    isCorrect,
    showSteps,
    showSolution,
    showExplanation,
    canShowSolution,
    feedbackClass,
    getPlaceholder,
    checkAnswer,
    toggleSolution,
    toggleSteps,
    resetTask
  }
}
