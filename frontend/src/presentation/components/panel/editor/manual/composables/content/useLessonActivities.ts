/**
 * useLessonActivities.ts
 *
 * Composable for managing lesson-level learning method activities.
 * Wraps infrastructure API calls per DDD layer rules (presentation -> application -> infrastructure).
 */
import { ref, watch, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import * as activitiesApi from '@/infrastructure/api/clients/panel/editor/courses/activities.api'
import type { LessonActivity } from '@/infrastructure/api/clients/panel/editor/courses/activities.api'

export type { LessonActivity }

export function useLessonActivities(lessonId: Ref<string | number | null>) {
  const { t } = useI18n()
  const activities = ref<LessonActivity[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const loadActivities = async (id: string | number) => {
    loading.value = true
    error.value = null
    try {
      activities.value = await activitiesApi.getLessonActivities(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('panel.manualEditor.errors.genericError')
      activities.value = []
    } finally {
      loading.value = false
    }
  }

  watch(lessonId, async (id) => {
    if (id) {
      await loadActivities(id)
    } else {
      activities.value = []
      error.value = null
    }
  }, { immediate: true })

  const addActivity = async (methodType: number, title: string): Promise<LessonActivity | null> => {
    if (!lessonId.value) return null
    const activity = await activitiesApi.createLessonActivity(lessonId.value, methodType, title)
    activities.value.push(activity)
    return activity
  }

  const removeActivity = async (activityId: string) => {
    await activitiesApi.deleteLessonActivity(activityId)
    activities.value = activities.value.filter(a => a.method_id !== activityId)
  }

  const updateActivityLocal = (updated: LessonActivity) => {
    const idx = activities.value.findIndex(a => a.method_id === updated.method_id)
    if (idx !== -1) activities.value[idx] = updated
  }

  const clearError = () => { error.value = null }

  return {
    activities,
    loading,
    error,
    clearError,
    addActivity,
    removeActivity,
    updateActivityLocal,
  }
}
