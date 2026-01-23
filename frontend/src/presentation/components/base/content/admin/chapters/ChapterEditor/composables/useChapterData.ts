/**
 * useChapterData Composable
 * Handles chapter loading, saving, and form population
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'
import {
  adminCreateChapter,
  adminUpdateChapter,
  type AdminChapter,
  type AdminChapterCreateRequest,
  type AdminChapterUpdateRequest
} from '@/infrastructure/api/clients/admin'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import type { ChapterForm } from '../types'

export function useChapterData(panel: LsxPanel) {
  const panelStore = usePanelStore()
  const { t } = useI18n()

  // State
  const chapter = ref<AdminChapter | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)
  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const form = ref<ChapterForm>({
    title: '',
    description: ''
  })

  // Auto-save timeout
  let saveTimeout: number | null = null

  // Computed
  const isNewChapter = computed(() => !panel.payload?.chapterId)
  const courseId = computed(() => panel.payload?.courseId as string)
  const courseTitle = computed(() => panel.payload?.courseTitle as string || t('features.chapterEditor.unknown'))
  const chapterId = computed(() => panel.payload?.chapterId as string | undefined)

  /**
   * Load chapter data from API or use provided data
   */
  const loadChapter = async () => {
    if (isNewChapter.value) {
      loading.value = false
      return
    }

    if (!chapterId.value) {
      error.value = t('features.chapterEditor.errors.noChapterId')
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    try {
      if (panel.payload?.chapter) {
        chapter.value = panel.payload.chapter as AdminChapter
        populateForm()
      } else {
        error.value = t('features.chapterEditor.errors.chapterDataUnavailable')
      }
    } catch (err: any) {
      console.error('Error loading chapter:', err)
      error.value = err.response?.data?.message || t('features.chapterEditor.errors.loadError')
    } finally {
      loading.value = false
    }
  }

  /**
   * Populate form from chapter data
   */
  const populateForm = () => {
    if (!chapter.value) return

    form.value = {
      title: chapter.value.title || '',
      description: chapter.value.description || ''
    }
  }

  /**
   * Auto-save with 800ms debounce
   */
  const debouncedSave = () => {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }

    saveTimeout = window.setTimeout(() => {
      saveChapter()
    }, 800) // 800ms debounce as per requirements
  }

  /**
   * Save chapter (create or update)
   */
  const saveChapter = async () => {
    if (!courseId.value || !form.value.title.trim()) return

    saveStatus.value = 'saving'

    try {
      const data = {
        title: form.value.title.trim(),
        description: form.value.description.trim() || undefined
      }

      if (isNewChapter.value) {
        // Create new chapter
        const newChapter = await adminCreateChapter(courseId.value, data as AdminChapterCreateRequest)
        chapter.value = newChapter

        // Update panel payload
        panelStore.updatePanelPayload(panel.id, {
          chapterId: newChapter.chapter_id,
          chapter: newChapter
        })

        console.log('Kapitel erstellt:', newChapter.chapter_id)
      } else {
        // Update existing chapter
        if (!chapterId.value) return

        const updatedChapter = await adminUpdateChapter(chapterId.value, data as AdminChapterUpdateRequest)
        chapter.value = updatedChapter

        // Update panel payload
        panelStore.updatePanelPayload(panel.id, {
          chapter: updatedChapter
        })

        console.log('Kapitel aktualisiert:', chapterId.value)
      }

      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)

      // Notify parent to refresh
      window.dispatchEvent(new CustomEvent('chapter-updated'))
    } catch (err: any) {
      console.error('Fehler beim Speichern:', err)
      saveStatus.value = 'error'
      setTimeout(() => { saveStatus.value = 'idle' }, 3000)
    }
  }

  /**
   * Save and enable tab (for new chapters)
   */
  const saveAndEnableTab = async () => {
    if (!form.value.title.trim()) {
      alert(t('features.chapterEditor.errors.enterTitle'))
      return
    }

    await saveChapter()
  }

  return {
    // State
    chapter,
    loading,
    error,
    saveStatus,
    form,

    // Computed
    isNewChapter,
    courseId,
    courseTitle,
    chapterId,

    // Methods
    loadChapter,
    populateForm,
    debouncedSave,
    saveChapter,
    saveAndEnableTab
  }
}
