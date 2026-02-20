/**
 * useLessonActivities.ts
 *
 * Composable for managing lesson-level learning method activities.
 * Wraps infrastructure API calls per DDD layer rules (presentation -> application -> infrastructure).
 */
import { ref, watch, type Ref } from 'vue'
import * as activitiesApi from '@/infrastructure/api/clients/panel/editor/courses/activities.api'
import type { LessonActivity } from '@/infrastructure/api/clients/panel/editor/courses/activities.api'

export type { LessonActivity }

export function useLessonActivities(lessonId: Ref<string | null>) {
  const activities = ref<LessonActivity[]>([])
  const loading = ref(false)

  const loadActivities = async (id: string) => {
    loading.value = true
    try {
      activities.value = await activitiesApi.getLessonActivities(id)
    } catch {
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

  const reorder = async (orderedIds: string[]) => {
    if (!lessonId.value) return
    await activitiesApi.reorderLessonActivities(lessonId.value, orderedIds)
  }

  return {
    activities,
    loading,
    addActivity,
    removeActivity,
    reorder,
  }
}
