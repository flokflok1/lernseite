/**
 * useTheoryGeneration Composable
 *
 * Business logic for chapter theory generation and management.
 * Handles loading, selecting, generating, and deleting theories.
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import type { ChapterTheory, TheoryStyle } from '../types/theory.types'

export function useTheoryGeneration() {
  const { t } = useI18n()

  // ============================================================================
  // State
  // ============================================================================

  const chapterTheories = ref<ChapterTheory[]>([])
  const selectedTheoryId = ref<string | null>(null)
  const isLoading = ref(false)
  const isGenerating = ref(false)
  const error = ref<string | null>(null)

  // ============================================================================
  // Computed
  // ============================================================================

  const selectedTheory = computed<ChapterTheory | null>(() => {
    return chapterTheories.value.find(t => t.theoryId === selectedTheoryId.value) || null
  })

  const currentTheoryTitle = computed(() => selectedTheory.value?.title || '')
  const currentTheoryStyle = computed(() => selectedTheory.value?.style || 'standard')

  // ============================================================================
  // Methods - Data Loading
  // ============================================================================

  async function loadChapterTheories(chapterId: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await http.get(`/chapters/${chapterId}/theories`)

      if (response.data.success) {
        chapterTheories.value = response.data.data || []
      } else {
        throw new Error(response.data.error?.message || t('course-editor.theory.loadError'))
      }
    } catch (err: any) {
      console.error('Failed to load theories:', err)
      error.value = err.message || t('course-editor.theory.loadError')
    } finally {
      isLoading.value = false
    }
  }

  // ============================================================================
  // Methods - Selection & Editing
  // ============================================================================

  async function selectTheory(theoryId: string) {
    selectedTheoryId.value = theoryId
  }

  async function deleteTheory(theoryId: string): Promise<boolean> {
    error.value = null

    try {
      const response = await http.delete(`/theories/${theoryId}`)

      if (response.data.success) {
        // Remove from list
        chapterTheories.value = chapterTheories.value.filter(t => t.theoryId !== theoryId)

        // Clear selection if deleted theory was selected
        if (selectedTheoryId.value === theoryId) {
          selectedTheoryId.value = null
        }

        return true
      } else {
        throw new Error(response.data.error?.message || t('course-editor.theory.deleteError'))
      }
    } catch (err: any) {
      console.error('Failed to delete theory:', err)
      error.value = err.message || t('course-editor.theory.deleteError')
      return false
    }
  }

  // ============================================================================
  // Methods - Generation
  // ============================================================================

  async function generateTheory(
    chapterId: string,
    style: TheoryStyle,
    title: string | undefined,
    generateTTS: boolean
  ): Promise<string | null> {
    isGenerating.value = true
    error.value = null

    try {
      const response = await http.post('/admin/ai/generate-chapter-theory', {
        chapter_id: chapterId,
        style,
        title: title || undefined,
        generate_tts: generateTTS
      })

      if (response.data.success) {
        const newTheoryId = response.data.data?.theory_id

        // Reload theories to get the new one
        await loadChapterTheories(chapterId)

        return newTheoryId || null
      } else {
        throw new Error(response.data.error?.message || t('course-editor.theory.generationError'))
      }
    } catch (err: any) {
      console.error('Theory generation failed:', err)
      error.value = err.message || t('course-editor.theory.generationError')
      return null
    } finally {
      isGenerating.value = false
    }
  }

  // ============================================================================
  // Methods - Utilities
  // ============================================================================

  function getStyleEmoji(style: TheoryStyle | undefined): string {
    const emojis: Record<TheoryStyle, string> = {
      standard: '📚',
      compact: '📋',
      detailed: '📖',
      visual: '🎨',
      exam: '📝'
    }
    return emojis[style || 'standard']
  }

  function getStyleName(style: TheoryStyle | undefined): string {
    const names: Record<TheoryStyle, string> = {
      standard: t('course-editor.theory.styles.standard'),
      compact: t('course-editor.theory.styles.compact'),
      detailed: t('course-editor.theory.styles.detailed'),
      visual: t('course-editor.theory.styles.visual'),
      exam: t('course-editor.theory.styles.exam')
    }
    return names[style || 'standard']
  }

  function formatDate(date: Date | undefined): string {
    if (!date) return ''
    return new Date(date).toLocaleDateString()
  }

  function reset() {
    chapterTheories.value = []
    selectedTheoryId.value = null
    isLoading.value = false
    isGenerating.value = false
    error.value = null
  }

  // ============================================================================
  // Return Composable API
  // ============================================================================

  return {
    // State
    chapterTheories,
    selectedTheoryId,
    selectedTheory,
    isLoading,
    isGenerating,
    error,

    // Computed
    currentTheoryTitle,
    currentTheoryStyle,

    // Methods
    loadChapterTheories,
    selectTheory,
    deleteTheory,
    generateTheory,
    getStyleEmoji,
    getStyleName,
    formatDate,
    reset
  }
}
