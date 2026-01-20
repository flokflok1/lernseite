/**
 * useTheoryManagement - Composable for managing chapter theories and lesson explanations
 *
 * Shared logic extracted from TutorTab.vue and KursBuilderTab.vue.
 * Provides loading, selecting, deleting, and generating theories/explanations.
 *
 * Usage:
 * ```ts
 * const {
 *   chapterTheories,
 *   lessonExplanations,
 *   isLoading,
 *   selectedTheoryId,
 *   loadChapterTheories,
 *   loadLessonExplanations,
 *   selectTheory,
 *   deleteTheory,
 *   deleteExplanation,
 *   reset
 * } = useTheoryManagement()
 *
 * // Load theories for a chapter
 * await loadChapterTheories(chapterId)
 *
 * // Select and load a specific theory
 * const theory = await selectTheory(theoryId)
 * ```
 */

import { ref, computed, readonly } from 'vue'
import http from '@/infrastructure/api/http'

// ============================================================================
// Types
// ============================================================================

export interface TheoryListItem {
  theoryId: string
  title: string
  style: string
  createdAt: string
  audioUrl?: string
}

export interface ChapterTheory {
  overview: string
  learningGoals: string[]
  concepts: { name: string; description: string }[]
  terms: { term: string; definition: string }[]
  examRelevance: string
  examTips: string[]
}

export interface ExplanationListItem {
  explanationId: string
  title: string
  stepCount: number
  createdAt: string
}

export interface LessonExplanation {
  explanationId: string
  title: string
  steps: TeachingStep[]
  createdAt: string
}

export interface TeachingStep {
  stepNumber: number
  speech: string
  whiteboard?: any[]
  calculatorHint?: {
    prompt: string
    expectedValue?: number
    tolerance?: number
  }
}

// ============================================================================
// Composable
// ============================================================================

export function useTheoryManagement() {
  // State
  const chapterTheories = ref<TheoryListItem[]>([])
  const lessonExplanations = ref<ExplanationListItem[]>([])
  const isLoading = ref(false)
  const selectedTheoryId = ref<string | null>(null)
  const selectedTheory = ref<ChapterTheory | null>(null)
  const currentTheoryTitle = ref('')
  const currentTheoryStyle = ref('')
  const error = ref<string | null>(null)

  // Selected explanation for lessons
  const selectedExplanationId = ref<string | null>(null)
  const currentExplanation = ref<LessonExplanation | null>(null)

  // ============================================================================
  // Chapter Theories
  // ============================================================================

  /**
   * Load all theories for a chapter
   */
  async function loadChapterTheories(chapterId: string): Promise<TheoryListItem[]> {
    if (!chapterId) return []

    isLoading.value = true
    error.value = null

    try {
      const response = await http.get(`/chapters/${chapterId}/theories`)

      if (response.data.success) {
        const theories = (response.data.data?.theories || []).map((t: any) => ({
          theoryId: t.theoryId || t.theory_id,
          title: t.title || 'Theorieblatt',
          style: t.style || 'standard',
          createdAt: t.createdAt || t.created_at,
          audioUrl: t.audioUrl || t.audio_url
        }))

        chapterTheories.value = theories

        // Auto-select first if none selected
        if (theories.length > 0 && !selectedTheoryId.value) {
          await selectTheory(theories[0].theoryId)
        }

        return theories
      }

      return []
    } catch (err: any) {
      console.error('Failed to load chapter theories:', err)
      error.value = err.message || 'Fehler beim Laden der Theorieblätter'
      chapterTheories.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Select and load a specific theory
   */
  async function selectTheory(theoryId: string): Promise<ChapterTheory | null> {
    if (!theoryId) return null

    selectedTheoryId.value = theoryId
    selectedTheory.value = null

    try {
      const response = await http.get(`/chapter-theory/${theoryId}`)

      if (response.data.success) {
        const data = response.data.data
        currentTheoryTitle.value = data.title || 'Theorieblatt'
        currentTheoryStyle.value = data.style || 'standard'

        const theoryData = data.theory || data
        selectedTheory.value = {
          overview: theoryData.overview || '',
          learningGoals: theoryData.learningGoals || theoryData.learning_goals || [],
          concepts: theoryData.concepts || [],
          terms: theoryData.terms || [],
          examRelevance: theoryData.examRelevance || theoryData.exam_relevance || '',
          examTips: theoryData.examTips || theoryData.exam_tips || []
        }

        return selectedTheory.value
      }

      return null
    } catch (err: any) {
      console.error('Failed to load theory:', err)
      error.value = err.message || 'Fehler beim Laden des Theorieblatts'
      selectedTheory.value = null
      return null
    }
  }

  /**
   * Delete a theory
   */
  async function deleteTheory(theoryId: string): Promise<boolean> {
    try {
      const response = await http.delete(`/chapter-theory/${theoryId}`)

      if (response.data.success) {
        // Remove from list
        chapterTheories.value = chapterTheories.value.filter(t => t.theoryId !== theoryId)

        // Clear selection if deleted
        if (selectedTheoryId.value === theoryId) {
          selectedTheoryId.value = null
          selectedTheory.value = null

          // Select next available
          if (chapterTheories.value.length > 0) {
            await selectTheory(chapterTheories.value[0].theoryId)
          }
        }

        return true
      }

      return false
    } catch (err: any) {
      console.error('Failed to delete theory:', err)
      error.value = err.message || 'Fehler beim Löschen'
      return false
    }
  }

  // ============================================================================
  // Lesson Explanations
  // ============================================================================

  /**
   * Load all explanations for a lesson
   */
  async function loadLessonExplanations(lessonId: string): Promise<ExplanationListItem[]> {
    if (!lessonId) return []

    isLoading.value = true
    error.value = null

    try {
      const response = await http.get(`/lessons/${lessonId}/explanations`)

      if (response.data.success) {
        const explanations = (response.data.data?.explanations || []).map((e: any) => ({
          explanationId: e.explanationId || e.explanation_id,
          title: e.title || 'Erklärung',
          stepCount: e.stepCount || e.step_count || 0,
          createdAt: e.createdAt || e.created_at
        }))

        lessonExplanations.value = explanations
        return explanations
      }

      return []
    } catch (err: any) {
      console.error('Failed to load lesson explanations:', err)
      error.value = err.message || 'Fehler beim Laden der Erklärungen'
      lessonExplanations.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Select and load a specific explanation
   */
  async function selectExplanation(explanationId: string): Promise<LessonExplanation | null> {
    if (!explanationId) return null

    selectedExplanationId.value = explanationId

    try {
      const response = await http.get(`/lesson-explanations/${explanationId}`)

      if (response.data.success) {
        const data = response.data.data
        currentExplanation.value = {
          explanationId: data.explanation_id || explanationId,
          title: data.title || 'Erklärung',
          steps: data.steps || [],
          createdAt: data.created_at
        }

        return currentExplanation.value
      }

      return null
    } catch (err: any) {
      console.error('Failed to load explanation:', err)
      error.value = err.message || 'Fehler beim Laden der Erklärung'
      currentExplanation.value = null
      return null
    }
  }

  /**
   * Delete an explanation
   */
  async function deleteExplanation(explanationId: string): Promise<boolean> {
    try {
      const response = await http.delete(`/lesson-explanations/${explanationId}`)

      if (response.data.success) {
        // Remove from list
        lessonExplanations.value = lessonExplanations.value.filter(
          e => e.explanationId !== explanationId
        )

        // Clear selection if deleted
        if (selectedExplanationId.value === explanationId) {
          selectedExplanationId.value = null
          currentExplanation.value = null

          // Select next available
          if (lessonExplanations.value.length > 0) {
            await selectExplanation(lessonExplanations.value[0].explanationId)
          }
        }

        return true
      }

      return false
    } catch (err: any) {
      console.error('Failed to delete explanation:', err)
      error.value = err.message || 'Fehler beim Löschen'
      return false
    }
  }

  // ============================================================================
  // Utilities
  // ============================================================================

  /**
   * Reset all state
   */
  function reset() {
    chapterTheories.value = []
    lessonExplanations.value = []
    selectedTheoryId.value = null
    selectedTheory.value = null
    selectedExplanationId.value = null
    currentExplanation.value = null
    currentTheoryTitle.value = ''
    currentTheoryStyle.value = ''
    error.value = null
  }

  /**
   * Get style emoji
   */
  function getStyleEmoji(style: string): string {
    const styles: Record<string, string> = {
      standard: '📄',
      compact: '📋',
      detailed: '📚',
      visual: '🎨',
      exam: '📝'
    }
    return styles[style?.toLowerCase()] || '📄'
  }

  /**
   * Get style display name
   */
  function getStyleName(style: string): string {
    const names: Record<string, string> = {
      standard: 'Standard',
      compact: 'Kompakt',
      detailed: 'Detailliert',
      visual: 'Visuell',
      exam: 'Prüfungsfokus'
    }
    return names[style?.toLowerCase()] || style || 'Standard'
  }

  /**
   * Format date for display
   */
  function formatDate(dateStr: string): string {
    if (!dateStr) return ''
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
      })
    } catch {
      return dateStr
    }
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State (readonly)
    chapterTheories: readonly(chapterTheories),
    lessonExplanations: readonly(lessonExplanations),
    isLoading: readonly(isLoading),
    error: readonly(error),
    selectedTheoryId: readonly(selectedTheoryId),
    selectedTheory: readonly(selectedTheory),
    currentTheoryTitle: readonly(currentTheoryTitle),
    currentTheoryStyle: readonly(currentTheoryStyle),
    selectedExplanationId: readonly(selectedExplanationId),
    currentExplanation: readonly(currentExplanation),

    // Computed
    hasTheories: computed(() => chapterTheories.value.length > 0),
    hasExplanations: computed(() => lessonExplanations.value.length > 0),

    // Methods - Theories
    loadChapterTheories,
    selectTheory,
    deleteTheory,

    // Methods - Explanations
    loadLessonExplanations,
    selectExplanation,
    deleteExplanation,

    // Utilities
    reset,
    getStyleEmoji,
    getStyleName,
    formatDate
  }
}

export default useTheoryManagement
