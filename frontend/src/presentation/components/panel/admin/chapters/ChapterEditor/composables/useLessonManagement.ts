/**
 * useLessonManagement Composable
 * Handles lesson CRUD operations, drag & drop, and reordering
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/workspace'
import {
  adminGetChapterLessons,
  adminDeleteLesson,
  adminReorderLessons,
  type AdminLesson
} from '@/application/services/api/panel-admin'
import type { DragState } from '../types'

export function useLessonManagement(courseId: string, chapterId: string | undefined, isNewChapter: boolean) {
  const panelStore = usePanelStore()
  const { t } = useI18n()

  // State
  const lessons = ref<AdminLesson[]>([])
  const loadingLessons = ref(false)

  // Drag & Drop State
  const dragState = ref<DragState>({
    draggedIndex: null,
    targetIndex: null
  })

  // Computed
  const sortedLessons = computed(() => {
    return [...lessons.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
  })

  /**
   * Load lessons from API
   */
  const loadLessons = async () => {
    if (!chapterId) return

    loadingLessons.value = true
    try {
      const data = await adminGetChapterLessons(chapterId)
      lessons.value = data
    } catch (err: any) {
      console.error('Error loading lessons:', err)
      lessons.value = []
    } finally {
      loadingLessons.value = false
    }
  }

  /**
   * Add new lesson by opening editor panel
   */
  const addLesson = () => {
    if (isNewChapter || !chapterId) {
      alert(t('features.chapterEditor.lessons.saveFirstAlert'))
      return
    }

    panelStore.openPanel({
      type: 'admin-lesson-editor',
      title: t('features.chapterEditor.lessons.panelNew'),
      icon: '📄',
      payload: {
        courseId: courseId,
        chapterId: chapterId,
        lessonId: null,
        lesson: null
      }
    })
  }

  /**
   * Edit lesson by opening editor panel
   */
  const editLesson = (lesson: AdminLesson) => {
    panelStore.openPanel({
      type: 'admin-lesson-editor',
      title: t('features.chapterEditor.lessons.panelEdit', { title: lesson.title }),
      icon: '📄',
      payload: {
        courseId: courseId,
        chapterId: chapterId,
        lessonId: lesson.lesson_id,
        lesson: lesson
      }
    })
  }

  /**
   * Delete lesson
   */
  const deleteLesson = async (lessonId: string) => {
    if (!confirm(t('features.chapterEditor.lessons.deleteConfirm'))) return

    try {
      await adminDeleteLesson(lessonId)
      await loadLessons()
    } catch (err: any) {
      console.error('Error deleting lesson:', err)
      alert(t('features.chapterEditor.lessons.deleteError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  /**
   * Handle drag start
   */
  const handleDragStart = (index: number) => {
    dragState.value.draggedIndex = index
  }

  /**
   * Handle drag over
   */
  const handleDragOver = (index: number) => {
    dragState.value.targetIndex = index
  }

  /**
   * Handle drop and reorder
   */
  const handleDrop = async (targetIndex: number) => {
    const draggedIndex = dragState.value.draggedIndex
    if (draggedIndex === null || draggedIndex === targetIndex) return

    // Reorder lessons array
    const lessonsCopy = [...lessons.value]
    const [removed] = lessonsCopy.splice(draggedIndex, 1)
    lessonsCopy.splice(targetIndex, 0, removed)

    // Update order_index for all lessons
    lessonsCopy.forEach((lesson, idx) => {
      lesson.order_index = idx + 1
    })

    lessons.value = lessonsCopy

    // Call backend reorder endpoint
    if (chapterId) {
      try {
        await adminReorderLessons(chapterId, lessonsCopy.map(l => l.lesson_id))
      } catch (err: any) {
        console.error('Error reordering lessons:', err)
        await loadLessons()
      }
    }

    dragState.value.draggedIndex = null
    dragState.value.targetIndex = null
  }

  /**
   * Handle drag end
   */
  const handleDragEnd = () => {
    dragState.value.draggedIndex = null
    dragState.value.targetIndex = null
  }

  /**
   * Get lesson type label with icon
   */
  const getLessonTypeLabel = (type: string): string => {
    const icons: Record<string, string> = {
      text: '📄',
      video: '🎥',
      quiz: '❓',
      interactive: '🎮',
      exercise: '💪',
      ai: '🤖',
      exam: '📝'
    }
    const icon = icons[type] || ''
    const label = t(`features.chapterEditor.lessonTypes.${type}`) || type
    return icon ? `${icon} ${label}` : label
  }

  return {
    // State
    lessons,
    loadingLessons,
    dragState,

    // Computed
    sortedLessons,

    // Methods
    loadLessons,
    addLesson,
    editLesson,
    deleteLesson,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    getLessonTypeLabel
  }
}
