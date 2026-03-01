/**
 * useTheorySheets.ts
 *
 * Composable for managing theory sheets (chapter-level or lesson-level).
 * Wraps infrastructure API calls per DDD layer rules.
 */
import { ref, watch, toValue, type Ref, type MaybeRefOrGetter } from 'vue'
import { useI18n } from 'vue-i18n'
import * as theoriesApi from '@/infrastructure/api/clients/panel/editor/courses/theories.api'
import type { TheorySheet } from '@/infrastructure/api/clients/panel/editor/courses/theories.api'

export type { TheorySheet }

export function useTheorySheets(
  parentId: Ref<string | null>,
  parentType: MaybeRefOrGetter<'chapter' | 'lesson'>
) {
  const { t } = useI18n()
  const theories = ref<TheorySheet[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const getType = () => toValue(parentType)

  const loadTheories = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      theories.value = getType() === 'chapter'
        ? await theoriesApi.getChapterTheories(id)
        : await theoriesApi.getLessonTheories(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('panel.manualEditor.knowledge.loadFailed')
      theories.value = []
    } finally {
      loading.value = false
    }
  }

  watch(parentId, async (id) => {
    if (id) {
      await loadTheories(id)
    } else {
      theories.value = []
      error.value = null
    }
  }, { immediate: true })

  const addTheory = async (title: string, content: string): Promise<TheorySheet | null> => {
    if (!parentId.value) return null
    error.value = null
    try {
      const theory = getType() === 'chapter'
        ? await theoriesApi.createChapterTheory(parentId.value, title, content)
        : await theoriesApi.createLessonTheory(parentId.value, title, content)
      theories.value.push(theory)
      return theory
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('panel.manualEditor.knowledge.saveFailed')
      return null
    }
  }

  const updateTheory = async (theoryId: string, payload: Partial<Pick<TheorySheet, 'title' | 'content'>>): Promise<boolean> => {
    error.value = null
    try {
      const updated = await theoriesApi.updateTheory(theoryId, payload)
      const idx = theories.value.findIndex(t => t.theory_id === theoryId)
      if (idx !== -1) theories.value[idx] = updated
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('panel.manualEditor.knowledge.saveFailed')
      return false
    }
  }

  const removeTheory = async (theoryId: string): Promise<boolean> => {
    error.value = null
    try {
      await theoriesApi.deleteTheory(theoryId)
      theories.value = theories.value.filter(t => t.theory_id !== theoryId)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('panel.manualEditor.knowledge.deleteFailed')
      return false
    }
  }

  const clearError = () => { error.value = null }

  return {
    theories,
    loading,
    error,
    clearError,
    addTheory,
    updateTheory,
    removeTheory,
  }
}
