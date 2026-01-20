/**
 * useChapterDetail Composable
 * ============================
 * Manages chapter data, lessons, theory, and progress
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/api/http'

export function useChapterDetail(courseId: string, chapterId: string) {
  const { t } = useI18n()

  // State
  const loading = ref(true)
  const error = ref<string | null>(null)
  const chapter = ref<any>(null)
  const courseName = ref<string>('')
  const lessons = ref<any[]>([])
  const lessonProgress = ref<Record<string, any>>({})
  const theoryData = ref<any>(null)
  const theoryLoading = ref(false)

  // Computed
  const progress = computed(() => {
    if (!lessons.value.length) return null
    const completed = lessons.value.filter(l => isLessonCompleted(l)).length
    return Math.round((completed / lessons.value.length) * 100)
  })

  const completedLessons = computed(() => {
    return lessons.value.filter(l => isLessonCompleted(l)).length
  })

  const isChapterCompleted = computed(() => {
    return progress.value === 100
  })

  // Helpers
  function isLessonCompleted(lesson: any): boolean {
    const prog = lessonProgress.value[lesson.lesson_id]
    return prog?.completed === true || prog?.progress_percentage === 100
  }

  function isLessonLocked(lesson: any, index: number): boolean {
    if (index === 0) return false
    const prevLesson = lessons.value[index - 1]
    return !isLessonCompleted(prevLesson)
  }

  function getLessonStatusClass(lesson: any, index: number): string {
    if (isLessonCompleted(lesson)) return 'completed'
    if (isLessonLocked(lesson, index)) return 'locked'
    return 'available'
  }

  // Data Loading
  async function loadChapterData() {
    loading.value = true
    error.value = null

    try {
      const [chapterRes, lessonsRes] = await Promise.all([
        http.get(`/chapters/${chapterId}`),
        http.get(`/chapters/${chapterId}/lessons`)
      ])

      chapter.value = chapterRes.data.data
      courseName.value = chapterRes.data.data.course_title || ''
      lessons.value = lessonsRes.data.data || []

      // Load progress for all lessons
      await loadLessonsProgress()

      // Mark chapter as visited
      markAsVisited()
    } catch (e: any) {
      console.error('Failed to load chapter:', e)
      error.value = e.response?.data?.error?.message || t('errors.unknown')
    } finally {
      loading.value = false
    }
  }

  async function loadLessonsProgress() {
    try {
      const response = await http.get(`/chapters/${chapterId}/progress`)
      const progressData = response.data.data || {}

      lessonProgress.value = progressData.lessons || {}
    } catch (e) {
      console.error('Failed to load progress:', e)
    }
  }

  async function loadTheoryById(theoryId: string) {
    theoryLoading.value = true
    try {
      const response = await http.get(`/chapters/${chapterId}/theory/${theoryId}`)
      theoryData.value = response.data.data
    } catch (e) {
      console.error('Failed to load theory:', e)
    } finally {
      theoryLoading.value = false
    }
  }

  async function generateTheory() {
    theoryLoading.value = true
    try {
      const response = await http.post(`/chapters/${chapterId}/theory/generate`)
      theoryData.value = response.data.data
    } catch (e) {
      console.error('Failed to generate theory:', e)
    } finally {
      theoryLoading.value = false
    }
  }

  // LocalStorage helpers
  const VISITED_KEY = 'lsx_visited_chapters'

  function markAsVisited() {
    try {
      const visited = JSON.parse(localStorage.getItem(VISITED_KEY) || '[]')
      if (!visited.includes(chapterId)) {
        visited.push(chapterId)
        localStorage.setItem(VISITED_KEY, JSON.stringify(visited))
      }
    } catch (e) {
      console.error('Failed to mark as visited:', e)
    }
  }

  // Initialize
  async function initialize() {
    await loadChapterData()
  }

  return {
    // State
    loading,
    error,
    chapter,
    courseName,
    lessons,
    lessonProgress,
    theoryData,
    theoryLoading,
    // Computed
    progress,
    completedLessons,
    isChapterCompleted,
    // Methods
    isLessonCompleted,
    isLessonLocked,
    getLessonStatusClass,
    loadChapterData,
    loadLessonsProgress,
    loadTheoryById,
    generateTheory,
    initialize
  }
}
