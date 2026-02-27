/**
 * useEditorState — Core state management for the Unified AI Editor
 *
 * Manages: course/chapter/lesson selection, active tab, loading states.
 */
import { ref, computed, type ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'

export interface EditorTab {
  id: string
  icon: string
  label: string
  badge?: string | number
}

export interface CourseContext {
  courseId: string
  courseTitle: string
  chapterId?: string
  chapterTitle?: string
  lessonId?: string
  lessonTitle?: string
}

export function useEditorState() {
  const { t } = useI18n()

  // ── Core State ──────────────────────────────────────────────────
  const activeTab = ref('chat')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Course context
  const courseId = ref<string | null>(null)
  const courseTitle = ref('')
  const chapterId = ref<string | null>(null)
  const chapterTitle = ref('')
  const lessonId = ref<string | null>(null)
  const lessonTitle = ref('')

  // Available courses (loaded from API)
  const courses = ref<Array<{ id: string; title: string }>>([])

  // ── Computed ────────────────────────────────────────────────────
  const hasCourseSelected = computed(() => !!courseId.value)

  const courseContext = computed<CourseContext | null>(() => {
    if (!courseId.value) return null
    return {
      courseId: courseId.value,
      courseTitle: courseTitle.value,
      chapterId: chapterId.value ?? undefined,
      chapterTitle: chapterTitle.value || undefined,
      lessonId: lessonId.value ?? undefined,
      lessonTitle: lessonTitle.value || undefined,
    }
  })

  const fileCount = ref(0)

  const tabs: ComputedRef<EditorTab[]> = computed(() => [
    { id: 'chat', icon: '💬', label: t('aiEditor.tabs.chat') },
    { id: 'course', icon: '📚', label: t('aiEditor.tabs.course') },
    { id: 'files', icon: '📎', label: t('aiEditor.tabs.files'), badge: fileCount.value || undefined },
    { id: 'plan', icon: '📋', label: t('aiEditor.tabs.plan') },
    { id: 'skills', icon: '⚡', label: t('aiEditor.tabs.skills') },
    { id: 'prompts', icon: '📝', label: t('aiEditor.tabs.prompts') },
    { id: 'history', icon: '📊', label: t('aiEditor.tabs.history') },
  ])

  // ── Actions ─────────────────────────────────────────────────────
  function selectCourse(id: string, title: string) {
    courseId.value = id
    courseTitle.value = title
    chapterId.value = null
    chapterTitle.value = ''
    lessonId.value = null
    lessonTitle.value = ''
  }

  function selectChapter(id: string, title: string) {
    chapterId.value = id
    chapterTitle.value = title
    lessonId.value = null
    lessonTitle.value = ''
  }

  function selectLesson(id: string, title: string) {
    lessonId.value = id
    lessonTitle.value = title
  }

  function setTab(tabId: string) {
    activeTab.value = tabId
  }

  function clearError() {
    error.value = null
  }

  async function loadCourses() {
    isLoading.value = true
    error.value = null
    try {
      const { listEditorCourses } = await import('@/infrastructure/api/clients/panel/editor')
      const result = await listEditorCourses()
      courses.value = (result || []).map((c: any) => ({ id: c.course_id, title: c.title }))
    } catch (e: any) {
      error.value = e.message || 'Failed to load courses'
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    activeTab,
    isLoading,
    error,
    courseId,
    courseTitle,
    chapterId,
    chapterTitle,
    lessonId,
    lessonTitle,
    courses,
    fileCount,
    // Computed
    hasCourseSelected,
    courseContext,
    tabs,
    // Actions
    selectCourse,
    selectChapter,
    selectLesson,
    setTab,
    clearError,
    loadCourses,
  }
}
