/**
 * useChapterDetail Composable
 * ============================
 * Manages chapter data, lessons, theory sheets, and progress.
 * Uses DDD-compliant API clients (no direct http imports).
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getChapterDetail,
  getChapterProgress,
  getChapterTheories,
  getChapterTheory,
  getTheoryById,
} from '@/infrastructure/api/clients/panel/user/courses/chapters.api'

export function useChapterDetail(courseId: string, chapterId: string) {
  const { t } = useI18n()

  // State
  const loading = ref(true)
  const error = ref<string | null>(null)
  const chapter = ref<any>(null)
  const courseName = ref<string>('')
  const lessons = ref<any[]>([])
  const lessonProgress = ref<Record<string, any>>({})
  const theorySheets = ref<any[]>([])
  const theorySheetsLoading = ref(false)

  // Computed — Progress
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

  // Computed — Navigation
  const firstIncompleteLesson = computed(() => {
    return lessons.value.find((l, i) => !isLessonCompleted(l) && !isLessonLocked(l, i))
  })

  // Computed — Stats
  const totalDuration = computed(() => {
    return lessons.value.reduce((sum, l) => sum + (l.duration_minutes || 0), 0)
  })

  // Title-based classification for exam-generated text lessons
  const TITLE_TYPE_MAP: Record<string, string> = {
    'erklärung': 'explanation',
    'rechenaufgaben': 'math',
    'lückentext': 'cloze',
    'ihk-prüfungsaufgaben': 'ihk',
    'lernkarten': 'flashcards',
    'zuordnung': 'matching',
    'fallstudien': 'casestudy',
  }

  function classifyLesson(lesson: any): string {
    const type = lesson.lesson_type || 'text'
    if (type === 'text' && lesson.title) {
      const lower = lesson.title.toLowerCase()
      for (const [key, label] of Object.entries(TITLE_TYPE_MAP)) {
        if (lower.includes(key)) return label
      }
    }
    return type
  }

  const lessonTypeBreakdown = computed(() => {
    const map: Record<string, number> = {}
    lessons.value.forEach(l => {
      const type = classifyLesson(l)
      map[type] = (map[type] || 0) + 1
    })
    return map
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
      const data = await getChapterDetail(courseId, chapterId)

      chapter.value = data.chapter
      courseName.value = data.chapter?.course_title || ''
      lessons.value = data.chapter?.lessons || []

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
      const data = await getChapterProgress(courseId, chapterId)
      const progressData = data.progress || data.data || {}
      lessonProgress.value = progressData.lessons || {}
    } catch (e) {
      console.warn('Could not load progress:', e)
    }
  }

  async function loadAllTheories() {
    theorySheetsLoading.value = true
    try {
      // Try the theories list endpoint first
      const theories = await getChapterTheories(chapterId)
      if (theories.length > 0) {
        theorySheets.value = theories
        return
      }

      // Fallback: single theory endpoint (AI-generated)
      const data = await getChapterTheory(chapterId)
      if (data?.hasTheory && data?.theory) {
        theorySheets.value = [{
          theoryId: data.theoryId || 'ai-theory',
          title: data.title || t('chapterTheory.theorySheet'),
          style: data.style || 'standard',
          createdAt: data.createdAt,
          // Inline content for AI theories (no lazy load needed)
          _inlineContent: {
            ...data.theory,
            title: data.title,
            created_at: data.createdAt,
            style: data.style,
          }
        }]
      } else {
        theorySheets.value = []
      }
    } catch (e) {
      console.warn('Could not load theories:', e)
      theorySheets.value = []
    } finally {
      theorySheetsLoading.value = false
    }
  }

  async function loadTheoryContent(theoryId: string) {
    // Check if already inline
    const sheet = theorySheets.value.find(s => s.theoryId === theoryId)
    if (sheet?._inlineContent) return sheet._inlineContent

    return await getTheoryById(theoryId)
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
    // Load theory + progress in parallel (non-blocking)
    loadAllTheories()
    loadLessonsProgress()
  }

  return {
    // State
    loading,
    error,
    chapter,
    courseName,
    lessons,
    lessonProgress,
    theorySheets,
    theorySheetsLoading,
    // Computed
    progress,
    completedLessons,
    isChapterCompleted,
    firstIncompleteLesson,
    totalDuration,
    lessonTypeBreakdown,
    // Methods
    isLessonCompleted,
    isLessonLocked,
    getLessonStatusClass,
    loadChapterData,
    loadLessonsProgress,
    loadAllTheories,
    loadTheoryContent,
    initialize
  }
}
