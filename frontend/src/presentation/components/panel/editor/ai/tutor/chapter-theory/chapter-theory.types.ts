/**
 * Shared types for ChapterTheoryView and its sub-components.
 */

import type { Ref } from 'vue'
import type { ChapterTheory, TheoryListItem } from '@/application/composables/learning/useTheoryManagement'

export interface Course {
  course_id: string
  title: string
}

export interface Chapter {
  chapter_id: string
  title: string
}

export type TheoryStyle = 'standard' | 'compact' | 'detailed' | 'visual' | 'exam'

export type { ChapterTheory, TheoryListItem }

/**
 * Return type for the useChapterTheoryActions composable.
 */
export interface ChapterTheoryActions {
  showCreateForm: Ref<boolean>
  newTitle: Ref<string>
  selectedStyle: Ref<TheoryStyle>
  generateWithAudio: Ref<boolean>
  isGenerating: Ref<boolean>
  localError: Ref<string | null>
  generateNewTheory: () => Promise<void>
  regenerateTheory: () => void
  copyToClipboard: () => void
  printTheory: () => void
  clearError: () => void
}
