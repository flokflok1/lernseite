/**
 * useActivityEditor.ts
 *
 * Composable for editing a single lesson activity's data + common fields.
 * Provides debounced auto-save (2s) and status tracking.
 */
import { ref, watch, type Ref } from 'vue'
import * as activitiesApi from '@/infrastructure/api/clients/panel/editor/courses/activities.api'
import type { LessonActivity } from '@/infrastructure/api/clients/panel/editor/courses/activities.api'

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export function useActivityEditor(
  activity: Ref<LessonActivity>,
  onSaved?: (updated: LessonActivity) => void
) {
  const localData = ref<Record<string, unknown>>({ ...activity.value.data })
  const localTitle = ref(activity.value.title)
  const localInstructions = ref(activity.value.instructions ?? '')
  const localDifficulty = ref(activity.value.difficulty)
  const localDuration = ref(activity.value.duration_minutes ?? null)
  const saveStatus = ref<SaveStatus>('idle')

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  const save = async () => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
    saveStatus.value = 'saving'
    try {
      const payload: Record<string, unknown> = {
        title: localTitle.value,
        instructions: localInstructions.value,
        data: localData.value,
        difficulty: localDifficulty.value,
        duration_minutes: localDuration.value,
      }
      const updated = await activitiesApi.updateLessonActivity(activity.value.method_id, payload)
      saveStatus.value = 'saved'
      onSaved?.(updated)
    } catch {
      saveStatus.value = 'error'
    }
  }

  const scheduleSave = () => {
    saveStatus.value = 'idle'
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(save, 2000)
  }

  // Watch all editable fields for changes
  watch(localData, scheduleSave, { deep: true })
  watch(localTitle, scheduleSave)
  watch(localInstructions, scheduleSave)
  watch(localDifficulty, scheduleSave)
  watch(localDuration, scheduleSave)

  // Sync when parent activity ref changes (e.g. after external reload)
  watch(activity, (a) => {
    localData.value = { ...a.data }
    localTitle.value = a.title
    localInstructions.value = a.instructions ?? ''
    localDifficulty.value = a.difficulty
    localDuration.value = a.duration_minutes ?? null
  })

  const cancel = () => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
  }

  return {
    localData,
    localTitle,
    localInstructions,
    localDifficulty,
    localDuration,
    saveStatus,
    save,
    scheduleSave,
    cancel,
  }
}
