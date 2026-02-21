/**
 * useExplanationGeneration Composable
 *
 * Business logic for lesson explanation management.
 * Handles loading, selection, generation, and deletion of explanations.
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import type {
  LessonExplanation,
  ExplanationStyle
} from '../types/explanation.types'

export function useExplanationGeneration() {
  const { t } = useI18n()

  // ========================================================================
  // State
  // ========================================================================

  const explanations = ref<LessonExplanation[]>([])
  const selectedExplanationId = ref<string | null>(null)
  const isLoading = ref(false)
  const isGenerating = ref(false)
  const error = ref<string | null>(null)

  // ========================================================================
  // Computed
  // ========================================================================

  const selectedExplanation = computed(() => {
    if (!selectedExplanationId.value) return null
    return explanations.value.find(e => e.explanationId === selectedExplanationId.value) || null
  })

  const currentExplanationTitle = computed(() => {
    return selectedExplanation.value?.title || ''
  })

  const currentExplanationStyle = computed(() => {
    return selectedExplanation.value?.style || 'standard'
  })

  // ========================================================================
  // Methods - Load
  // ========================================================================

  const loadExplanations = async (lessonId: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await http.get(`/lessons/${lessonId}/explanations`)

      if (response.data.success) {
        const raw = response.data.data
        explanations.value = Array.isArray(raw) ? raw : (raw?.explanations || [])
      } else {
        error.value = t('course-editor.explanation.loadError')
      }
    } catch (err: any) {
      error.value = err.message || t('course-editor.explanation.loadError')
      console.error('Failed to load explanations:', err)
    } finally {
      isLoading.value = false
    }
  }

  // ========================================================================
  // Methods - Select
  // ========================================================================

  const selectExplanation = async (explanationId: string): Promise<void> => {
    try {
      const explanation = explanations.value.find(e => e.explanationId === explanationId)

      if (!explanation) {
        error.value = t('course-editor.explanation.notFound')
        return
      }

      selectedExplanationId.value = explanationId

      // Load detailed explanation if needed
      const response = await http.get(`/explanations/${explanationId}`)
      if (response.data.success && response.data.data) {
        const index = explanations.value.findIndex(e => e.explanationId === explanationId)
        if (index !== -1) {
          explanations.value[index] = response.data.data
        }
      }
    } catch (err: any) {
      error.value = err.message || t('course-editor.explanation.loadError')
      console.error('Failed to select explanation:', err)
    }
  }

  // ========================================================================
  // Methods - Generate
  // ========================================================================

  const generateExplanation = async (
    lessonId: string,
    style: ExplanationStyle,
    generateTTS: boolean = true,
    voice?: string
  ): Promise<string | null> => {
    isGenerating.value = true
    error.value = null

    try {
      const response = await http.post('/admin/ai/generate-lesson-explanation', {
        lesson_id: lessonId,
        style,
        generate_tts: generateTTS,
        voice: voice || undefined
      })

      if (response.data.success) {
        const newExplanationId = response.data.data?.explanation_id

        // Reload explanations to include new one
        await loadExplanations(lessonId)

        return newExplanationId || null
      } else {
        error.value = t('course-editor.explanation.generateError')
        return null
      }
    } catch (err: any) {
      error.value = err.message || t('course-editor.explanation.generateError')
      console.error('Failed to generate explanation:', err)
      return null
    } finally {
      isGenerating.value = false
    }
  }

  // ========================================================================
  // Methods - Delete
  // ========================================================================

  const deleteExplanation = async (explanationId: string): Promise<boolean> => {
    try {
      const response = await http.delete(`/explanations/${explanationId}`)

      if (response.data.success) {
        // Remove from local list
        explanations.value = explanations.value.filter(e => e.explanationId !== explanationId)

        // Clear selection if deleted explanation was selected
        if (selectedExplanationId.value === explanationId) {
          selectedExplanationId.value = null
        }

        return true
      } else {
        error.value = t('course-editor.explanation.deleteError')
        return false
      }
    } catch (err: any) {
      error.value = err.message || t('course-editor.explanation.deleteError')
      console.error('Failed to delete explanation:', err)
      return false
    }
  }

  // ========================================================================
  // Methods - Utility
  // ========================================================================

  const resetStep = (): void => {
    // Step navigation will be in container component
  }

  const reset = (): void => {
    explanations.value = []
    selectedExplanationId.value = null
    isLoading.value = false
    isGenerating.value = false
    error.value = null
  }

  // ========================================================================
  // Return
  // ========================================================================

  return {
    // State
    explanations,
    selectedExplanationId,
    isLoading,
    isGenerating,
    error,

    // Computed
    selectedExplanation,
    currentExplanationTitle,
    currentExplanationStyle,

    // Methods
    loadExplanations,
    selectExplanation,
    generateExplanation,
    deleteExplanation,
    resetStep,
    reset
  }
}

