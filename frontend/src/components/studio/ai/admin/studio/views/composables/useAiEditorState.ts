/**
 * useAiEditorState Composable
 * ============================
 * Central state management for AI Studio Pro
 */
import { ref, computed, readonly } from 'vue'
import http from '@/api/http'

// ============================================================================
// Types
// ============================================================================

export interface Course {
  course_id: string
  title: string
  description?: string
  category_id?: number | null
  category_name?: string | null
}

export interface Chapter {
  chapter_id: string
  title: string
  order_index: number
  lessons?: Lesson[]
}

export interface Lesson {
  lesson_id: string
  title: string
  order_index: number
  lm_type?: string
  has_video?: boolean
  video_generating?: boolean
  content?: Record<string, unknown>
}

// ============================================================================
// Composable
// ============================================================================

export function useAiEditorState() {
  // ==========================================================================
  // State
  // ==========================================================================

  // Selected State
  const selectedCourseId = ref<string | null>(null)
  const selectedChapterId = ref<string | null>(null)
  const selectedLessonId = ref<string | null>(null)

  // Data
  const courses = ref<Course[]>([])
  const chapters = ref<Chapter[]>([])
  const expandedChapters = ref<Set<string>>(new Set())

  // Loading & Error
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==========================================================================
  // Computed
  // ==========================================================================

  const selectedCourse = computed<Course | null>(() => {
    if (!selectedCourseId.value) return null
    return courses.value.find(c => c.course_id === selectedCourseId.value) || null
  })

  const selectedChapter = computed<Chapter | null>(() => {
    if (!selectedChapterId.value) return null
    return chapters.value.find(c => c.chapter_id === selectedChapterId.value) || null
  })

  const selectedLesson = computed<Lesson | null>(() => {
    if (!selectedLessonId.value) return null

    for (const chapter of chapters.value) {
      if (!chapter.lessons) continue
      const lesson = chapter.lessons.find(l => l.lesson_id === selectedLessonId.value)
      if (lesson) return lesson
    }
    return null
  })

  const hasSelectedCourse = computed(() => selectedCourseId.value !== null)
  const hasSelectedChapter = computed(() => selectedChapterId.value !== null)
  const hasSelectedLesson = computed(() => selectedLessonId.value !== null)

  const totalChapters = computed(() => chapters.value.length)
  const totalLessons = computed(() => {
    return chapters.value.reduce((sum, chapter) => {
      return sum + (chapter.lessons?.length || 0)
    }, 0)
  })

  // ==========================================================================
  // Methods - Selection
  // ==========================================================================

  function selectCourse(courseId: string | null): void {
    selectedCourseId.value = courseId
    // Reset chapter/lesson when course changes
    selectedChapterId.value = null
    selectedLessonId.value = null
    expandedChapters.value.clear()

    // Load chapters for new course
    if (courseId) {
      loadChapters(courseId)
    } else {
      chapters.value = []
    }
  }

  function selectChapter(chapterId: string | null): void {
    selectedChapterId.value = chapterId
    // Reset lesson when chapter changes
    selectedLessonId.value = null
  }

  function selectLesson(lessonId: string | null, chapterId?: string): void {
    selectedLessonId.value = lessonId

    // If chapterId provided, also select and expand chapter
    if (chapterId) {
      selectedChapterId.value = chapterId
      expandedChapters.value.add(chapterId)
    } else if (lessonId) {
      // Find chapter that contains this lesson
      for (const chapter of chapters.value) {
        if (chapter.lessons?.some(l => l.lesson_id === lessonId)) {
          selectedChapterId.value = chapter.chapter_id
          expandedChapters.value.add(chapter.chapter_id)
          break
        }
      }
    }
  }

  function toggleChapterExpanded(chapterId: string): void {
    if (expandedChapters.value.has(chapterId)) {
      expandedChapters.value.delete(chapterId)
    } else {
      expandedChapters.value.add(chapterId)
    }
  }

  function expandAllChapters(): void {
    chapters.value.forEach(chapter => {
      expandedChapters.value.add(chapter.chapter_id)
    })
  }

  function collapseAllChapters(): void {
    expandedChapters.value.clear()
  }

  // ==========================================================================
  // Methods - Data Loading
  // ==========================================================================

  async function loadCourses(): Promise<void> {
    try {
      loading.value = true
      error.value = null

      const response = await http.get('/courses')

      if (response.data.success) {
        courses.value = response.data.data || []
      } else {
        throw new Error('Failed to load courses')
      }
    } catch (err: any) {
      console.error('Load courses error:', err)
      error.value = err.message || 'Failed to load courses'
      courses.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadChapters(courseId: string): Promise<void> {
    try {
      loading.value = true
      error.value = null

      const response = await http.get(`/courses/${courseId}/chapters`)

      if (response.data.success) {
        chapters.value = response.data.data || []
      } else {
        throw new Error('Failed to load chapters')
      }
    } catch (err: any) {
      console.error('Load chapters error:', err)
      error.value = err.message || 'Failed to load chapters'
      chapters.value = []
    } finally {
      loading.value = false
    }
  }

  async function reloadChapters(): Promise<void> {
    if (selectedCourseId.value) {
      await loadChapters(selectedCourseId.value)
    }
  }

  async function reloadCourses(): Promise<void> {
    await loadCourses()
  }

  // ==========================================================================
  // Methods - Helpers
  // ==========================================================================

  function findChapterByLessonId(lessonId: string): Chapter | null {
    for (const chapter of chapters.value) {
      if (chapter.lessons?.some(l => l.lesson_id === lessonId)) {
        return chapter
      }
    }
    return null
  }

  function getChapterLessons(chapterId: string): Lesson[] {
    const chapter = chapters.value.find(c => c.chapter_id === chapterId)
    return chapter?.lessons || []
  }

  function isChapterExpanded(chapterId: string): boolean {
    return expandedChapters.value.has(chapterId)
  }

  // ==========================================================================
  // Methods - Reset
  // ==========================================================================

  function resetSelection(): void {
    selectedCourseId.value = null
    selectedChapterId.value = null
    selectedLessonId.value = null
    expandedChapters.value.clear()
  }

  function reset(): void {
    resetSelection()
    courses.value = []
    chapters.value = []
    loading.value = false
    error.value = null
  }

  function clearError(): void {
    error.value = null
  }

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State (readonly)
    selectedCourseId: readonly(selectedCourseId),
    selectedChapterId: readonly(selectedChapterId),
    selectedLessonId: readonly(selectedLessonId),
    courses: readonly(courses),
    chapters: readonly(chapters),
    expandedChapters, // Mutable Set
    loading: readonly(loading),
    error: readonly(error),

    // Computed
    selectedCourse,
    selectedChapter,
    selectedLesson,
    hasSelectedCourse,
    hasSelectedChapter,
    hasSelectedLesson,
    totalChapters,
    totalLessons,

    // Methods - Selection
    selectCourse,
    selectChapter,
    selectLesson,
    toggleChapterExpanded,
    expandAllChapters,
    collapseAllChapters,

    // Methods - Data Loading
    loadCourses,
    loadChapters,
    reloadChapters,
    reloadCourses,

    // Methods - Helpers
    findChapterByLessonId,
    getChapterLessons,
    isChapterExpanded,

    // Methods - Reset
    resetSelection,
    reset,
    clearError
  }
}
