/**
 * useExplanationManager Composable
 * =================================
 * State management and API calls for lesson explanations
 */
import { ref, computed, readonly } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheoryManagement, type LessonExplanation, type TeachingStep } from '@/features/useTheoryManagement'
import http from '@/api/http'

// ============================================================================
// Types
// ============================================================================

export interface ExplanationStyle {
  value: string
  label: string
}

export interface GenerateOptions {
  lessonId: string
  style: string
  generateTTS: boolean
  voice: string
}

// ============================================================================
// Composable
// ============================================================================

export function useExplanationManager() {
  const { t } = useI18n()
  const theoryMgmt = useTheoryManagement()

  // ==========================================================================
  // State
  // ==========================================================================

  // Selected Explanation
  const selectedExplanationId = ref<string | null>(null)
  const currentExplanation = ref<LessonExplanation | null>(null)
  const steps = ref<TeachingStep[]>([])
  const currentStep = ref(0)

  // UI State
  const isGenerating = ref(false)
  const error = ref<string | null>(null)

  // ==========================================================================
  // Computed
  // ==========================================================================

  const explanations = computed(() => theoryMgmt.lessonExplanations.value)
  const isLoading = computed(() => theoryMgmt.isLoading.value)

  const currentStepData = computed(() => {
    if (steps.value.length === 0 || currentStep.value >= steps.value.length) {
      return null
    }
    return steps.value[currentStep.value]
  })

  const hasExplanations = computed(() => explanations.value.length > 0)
  const hasSelectedExplanation = computed(() => currentExplanation.value !== null)
  const hasSteps = computed(() => steps.value.length > 0)

  const progressPercent = computed(() => {
    if (steps.value.length === 0) return 0
    return ((currentStep.value + 1) / steps.value.length) * 100
  })

  const canGoPrev = computed(() => currentStep.value > 0)
  const canGoNext = computed(() => currentStep.value < steps.value.length - 1)

  // ==========================================================================
  // Methods - Loading
  // ==========================================================================

  async function loadExplanations(lessonId: string): Promise<void> {
    await theoryMgmt.loadLessonExplanations(lessonId)
  }

  async function selectExplanation(explanationId: string): Promise<void> {
    selectedExplanationId.value = explanationId
    currentStep.value = 0
    error.value = null

    try {
      const response = await http.get(`/lesson-explanations/${explanationId}`)

      if (response.data.success) {
        const data = response.data.data
        currentExplanation.value = {
          explanationId: data.explanation_id || explanationId,
          title: data.title || t('windows.lessonExplanationView.defaultTitle'),
          steps: data.steps || [],
          createdAt: data.created_at
        }
        steps.value = data.steps || []
      }
    } catch (err: any) {
      console.error('Failed to load explanation:', err)
      error.value = err.message || t('windows.lessonExplanationView.loadError')
      throw err
    }
  }

  async function deleteExplanation(explanationId: string): Promise<boolean> {
    const success = await theoryMgmt.deleteExplanation(explanationId)

    if (success) {
      if (selectedExplanationId.value === explanationId) {
        resetSelection()
      }
    }

    return success
  }

  async function generateExplanation(options: GenerateOptions): Promise<string | null> {
    isGenerating.value = true
    error.value = null

    try {
      const response = await http.post('/admin/ai/generate-lesson-explanation', {
        lesson_id: options.lessonId,
        style: options.style,
        generate_tts: options.generateTTS,
        voice: options.voice
      })

      if (response.data.success) {
        await loadExplanations(options.lessonId)
        return response.data.data?.explanation_id || null
      } else {
        throw new Error(
          response.data.error?.message ||
          t('windows.lessonExplanationView.generationFailed')
        )
      }
    } catch (err: any) {
      console.error('Explanation generation failed:', err)
      error.value =
        err.response?.data?.error?.message ||
        err.message ||
        t('windows.lessonExplanationView.generationError')
      throw err
    } finally {
      isGenerating.value = false
    }
  }

  // ==========================================================================
  // Methods - Navigation
  // ==========================================================================

  function nextStep(): void {
    if (canGoNext.value) {
      currentStep.value++
    }
  }

  function prevStep(): void {
    if (canGoPrev.value) {
      currentStep.value--
    }
  }

  function goToStep(index: number): void {
    if (index >= 0 && index < steps.value.length) {
      currentStep.value = index
    }
  }

  function resetStep(): void {
    currentStep.value = 0
  }

  // ==========================================================================
  // Methods - Reset
  // ==========================================================================

  function resetSelection(): void {
    selectedExplanationId.value = null
    currentExplanation.value = null
    steps.value = []
    currentStep.value = 0
  }

  function reset(): void {
    theoryMgmt.reset()
    resetSelection()
    error.value = null
  }

  function clearError(): void {
    error.value = null
  }

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State (readonly)
    selectedExplanationId: readonly(selectedExplanationId),
    currentExplanation: readonly(currentExplanation),
    steps: readonly(steps),
    currentStep: readonly(currentStep),
    isGenerating: readonly(isGenerating),
    error: readonly(error),

    // Computed
    explanations,
    isLoading,
    currentStepData,
    hasExplanations,
    hasSelectedExplanation,
    hasSteps,
    progressPercent,
    canGoPrev,
    canGoNext,

    // Methods - Loading
    loadExplanations,
    selectExplanation,
    deleteExplanation,
    generateExplanation,

    // Methods - Navigation
    nextStep,
    prevStep,
    goToStep,
    resetStep,

    // Methods - Reset
    resetSelection,
    reset,
    clearError
  }
}
