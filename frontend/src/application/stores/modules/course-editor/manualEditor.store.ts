/**
 * manualEditor.store.ts
 *
 * Manual Editor state management.
 * Handles manual editing state, structure, and content.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ManualEditorState {
  selectedChapterId: string | null
  selectedLessonId: string | null
  content: Record<string, unknown>
  isDirty: boolean
}

export const useManualEditorStore = defineStore('courseEditor/manualEditor', () => {
  const selectedChapterId = ref<string | null>(null)
  const selectedLessonId = ref<string | null>(null)
  const content = ref<Record<string, unknown>>({})
  const isDirty = ref(false)

  const selectChapter = (chapterId: string) => {
    selectedChapterId.value = chapterId
    selectedLessonId.value = null
  }

  const selectLesson = (lessonId: string) => {
    selectedLessonId.value = lessonId
  }

  const updateContent = (key: string, value: unknown) => {
    content.value[key] = value
    isDirty.value = true
  }

  return {
    selectedChapterId,
    selectedLessonId,
    content,
    isDirty,
    selectChapter,
    selectLesson,
    updateContent
  }
})
