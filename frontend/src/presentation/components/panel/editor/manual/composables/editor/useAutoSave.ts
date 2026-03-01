/**
 * useAutoSave - Debounced auto-save for the course editor
 *
 * Watches the store's dirty state. When dirty for 2 seconds,
 * triggers saveAllChanges(). Provides toggle, status display,
 * and error feedback with automatic retry.
 */

import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

export type AutoSaveStatus = 'saved' | 'saving' | 'unsaved' | 'error'

const MAX_RETRIES = 3

export function useAutoSave() {
  const { t } = useI18n()
  const store = useCourseEditorStore()

  const autoSaveEnabled = ref(true)
  const lastSaved = ref<Date | null>(null)
  const saveError = ref<string | null>(null)
  const retryCount = ref(0)
  let timer: ReturnType<typeof setTimeout> | null = null

  const saveStatus = computed<AutoSaveStatus>(() => {
    if (store.saving) return 'saving'
    if (saveError.value) return 'error'
    if (store.isDirty) return 'unsaved'
    return 'saved'
  })

  const triggerSave = async (): Promise<void> => {
    if (store.saving) return  // Concurrent guard
    saveError.value = null
    try {
      await store.saveAllChanges()
      lastSaved.value = new Date()
      retryCount.value = 0
    } catch (err: unknown) {
      saveError.value = t('panel.manualEditor.toolbar.error')
      retryCount.value++
      if (retryCount.value < MAX_RETRIES) {
        scheduleRetry()
      }
      // else: stop retrying, user must click Save manually
    }
  }

  const clearTimer = (): void => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  const scheduleRetry = (): void => {
    clearTimer()
    if (autoSaveEnabled.value) {
      timer = setTimeout(() => {
        void triggerSave()
      }, 5000)
    }
  }

  const dismissError = (): void => {
    saveError.value = null
    retryCount.value = 0  // Reset on manual dismiss
  }

  watch(
    () => store.isDirty,
    (isDirty) => {
      clearTimer()
      if (isDirty && autoSaveEnabled.value) {
        timer = setTimeout(() => {
          void triggerSave()
        }, 2000)
      }
    },
  )

  onUnmounted(() => {
    clearTimer()
  })

  return {
    autoSaveEnabled,
    lastSaved,
    saveError,
    saveStatus,
    triggerSave,
    dismissError,
  }
}
