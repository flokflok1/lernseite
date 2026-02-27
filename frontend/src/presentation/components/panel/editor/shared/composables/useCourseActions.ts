/**
 * useCourseActions — Shared composable for course lifecycle actions with
 * inline confirmation state. Used by both AI Editor and Manual Editor.
 *
 * Wraps the courseEditor store's lifecycle methods (trash, archive, restore,
 * unarchive, purge) behind a request → confirm/cancel flow.
 */
import { ref, computed } from 'vue'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

export type CourseAction = 'trash' | 'archive' | 'restore' | 'unarchive' | 'purge'

export function useCourseActions() {
  const store = useCourseEditorStore()

  const pendingAction = ref<CourseAction | null>(null)
  const pendingCourseId = ref<number | null>(null)

  /** Begin confirmation flow for a course action. */
  function requestAction(action: CourseAction, courseId: number) {
    pendingAction.value = action
    pendingCourseId.value = courseId
  }

  /** Cancel the pending confirmation. */
  function cancelAction() {
    pendingAction.value = null
    pendingCourseId.value = null
  }

  /**
   * Execute the pending action against the store.
   * Returns true on success, false on failure or if no action was pending.
   */
  async function confirmAction(): Promise<boolean> {
    if (!pendingAction.value || pendingCourseId.value == null) return false

    const action = pendingAction.value
    const id = pendingCourseId.value
    cancelAction()

    try {
      switch (action) {
        case 'trash': await store.trashCourse(id); break
        case 'archive': await store.archiveCourse(id); break
        case 'restore': await store.restoreFromTrash(id); break
        case 'unarchive': await store.unarchiveCourse(id); break
        case 'purge': await store.permanentDelete(id); break
      }
      return true
    } catch {
      return false
    }
  }

  const isConfirming = computed(() => pendingAction.value !== null)

  /**
   * Check whether a specific course is currently in confirmation state.
   * Useful for per-card confirmation in list views (Manual Editor).
   */
  function isConfirmingCourse(courseId: number): boolean {
    return pendingCourseId.value === courseId
  }

  return {
    pendingAction,
    pendingCourseId,
    requestAction,
    cancelAction,
    confirmAction,
    isConfirming,
    isConfirmingCourse,
  }
}
