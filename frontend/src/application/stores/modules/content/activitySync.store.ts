/**
 * Activity Sync Store
 *
 * Cross-window signal for activity saves. Allows ActivityEditorWindow
 * to notify LessonActivitiesSection about saves without prop/emit chains.
 */

import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { LessonActivity } from '@/infrastructure/api/clients/panel/editor/courses/activities.api'

export const useActivitySyncStore = defineStore('activitySync', () => {
  const lastSaved = ref<LessonActivity | null>(null)

  function notifySaved(activity: LessonActivity) {
    lastSaved.value = activity
  }

  return { lastSaved, notifySaved }
})
