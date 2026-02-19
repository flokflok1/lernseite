/**
 * useAutoSave - Debounced auto-save for the course editor
 *
 * Watches the store's dirty state. When dirty for 2 seconds,
 * triggers saveAllChanges(). Provides toggle and status display.
 */

import { ref, computed, watch, onUnmounted } from 'vue'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

export function useAutoSave() {
  const store = useCourseEditorStore()

  const autoSaveEnabled = ref(true)
  const lastSaved = ref<Date | null>(null)
  let timer: ReturnType<typeof setTimeout> | null = null

  const isSaving = computed(() => store.saving)

  const saveStatus = computed<'saved' | 'saving' | 'unsaved'>(() => {
    if (store.saving) return 'saving'
    if (store.isDirty) return 'unsaved'
    return 'saved'
  })

  const triggerSave = async (): Promise<void> => {
    try {
      await store.saveAllChanges()
      lastSaved.value = new Date()
    } catch {
      // Save failed — store.error will be set
    }
  }

  const clearTimer = (): void => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  watch(
    () => store.isDirty,
    (isDirty) => {
      clearTimer()
      if (isDirty && autoSaveEnabled.value) {
        timer = setTimeout(() => {
          triggerSave()
        }, 2000)
      }
    },
  )

  const toggleAutoSave = (): void => {
    autoSaveEnabled.value = !autoSaveEnabled.value
    if (!autoSaveEnabled.value) {
      clearTimer()
    }
  }

  onUnmounted(() => {
    clearTimer()
  })

  return {
    autoSaveEnabled,
    lastSaved,
    isSaving,
    saveStatus,
    triggerSave,
    toggleAutoSave,
  }
}
