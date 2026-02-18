/**
 * LernsystemX - Player Store (Pinia)
 *
 * Manages:
 * - Current course, chapter, lesson state
 * - Progress tracking
 * - Learning methods
 * - Player navigation
 *
 * Quiz-specific logic is in playerQuiz.store.ts
 *
 * Refactored: modules -> chapters (2025-11-27)
 * Refactored: quiz split to playerQuiz.store.ts (2026-02-18)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as playerApi from '@/application/services/api/learning'
import type {
  Course,
  Chapter,
  Lesson,
  CourseProgress,
  ChapterProgress,
  LessonProgress,
  LearningMethod,
  ExecuteMethodRequest
} from '@/application/services/api/learning'
import { usePlayerQuizStore } from './playerQuiz.store'

export const usePlayerStore = defineStore('player', () => {
  // ============================================================================
  // State
  // ============================================================================

  const course = ref<Course | null>(null)
  const chapters = ref<Chapter[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const currentLesson = ref<Lesson | null>(null)

  const courseProgress = ref<CourseProgress | null>(null)
  const chapterProgress = ref<ChapterProgress | null>(null)
  const lessonProgress = ref<LessonProgress | null>(null)

  const availableMethods = ref<LearningMethod[]>([])

  const loading = ref(false)
  const error = ref<string | null>(null)

  const methodExecuting = ref(false)
  const methodResult = ref<any>(null)
  const methodError = ref<string | null>(null)

  // ============================================================================
  // Quiz Store (delegated)
  // ============================================================================

  const quizStore = usePlayerQuizStore()

  // ============================================================================
  // Getters
  // ============================================================================

  /**
   * Check if course is loaded
   */
  const hasCourse = computed(() => !!course.value)

  /**
   * Get current lesson index in chapter
   */
  const currentLessonIndex = computed(() => {
    if (!currentChapter.value || !currentLesson.value) return -1
    return (
      currentChapter.value.lessons?.findIndex(
        (l) => l.lesson_id === currentLesson.value!.lesson_id
      ) ?? -1
    )
  })

  /**
   * Check if there's a next lesson
   */
  const hasNextLesson = computed(() => {
    if (!currentChapter.value?.lessons) return false
    return currentLessonIndex.value < (currentChapter.value.lessons.length - 1)
  })

  /**
   * Check if there's a previous lesson
   */
  const hasPreviousLesson = computed(() => {
    return currentLessonIndex.value > 0
  })

  /**
   * Get next lesson
   */
  const nextLesson = computed(() => {
    if (!hasNextLesson.value || !currentChapter.value?.lessons) return null
    return currentChapter.value.lessons[currentLessonIndex.value + 1]
  })

  /**
   * Get previous lesson
   */
  const previousLesson = computed(() => {
    if (!hasPreviousLesson.value || !currentChapter.value?.lessons) return null
    return currentChapter.value.lessons[currentLessonIndex.value - 1]
  })

  /**
   * Get lesson completion status
   */
  const isLessonCompleted = computed(() => {
    return lessonProgress.value?.status === 'completed'
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Load course with chapters
   */
  const loadCourse = async (courseId: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const [courseData, chaptersData, progressData] = await Promise.all([
        playerApi.getCourse(courseId),
        playerApi.getCourseChapters(courseId),
        playerApi.getCourseProgress(courseId).catch(() => null)
      ])

      course.value = courseData
      chapters.value = chaptersData
      courseProgress.value = progressData

      // Send analytics event (non-blocking, errors are ignored)
      playerApi.sendAnalyticsEvent({
        event_type: 'course_view',
        resource_type: 'course',
        resource_id: courseId
      }).catch(() => {
        // Analytics errors should not break the user experience
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Kurs konnte nicht geladen werden'
      console.error('Failed to load course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load chapter with lessons
   */
  const loadChapter = async (courseId: string, chapterId: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const [chapterData, progressData] = await Promise.all([
        playerApi.getChapter(courseId, chapterId),
        playerApi.getChapterProgress(courseId, chapterId).catch(() => null)
      ])

      currentChapter.value = chapterData
      chapterProgress.value = progressData

      // Send analytics event
      await playerApi.sendAnalyticsEvent({
        event_type: 'chapter_start',
        resource_type: 'chapter',
        resource_id: chapterId
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Kapitel konnte nicht geladen werden'
      console.error('Failed to load chapter:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load lesson with progress and methods
   */
  const loadLesson = async (
    courseId: string,
    chapterId: string,
    lessonId: string
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const [lessonData, progressData, methodsData] = await Promise.all([
        playerApi.getLesson(courseId, chapterId, lessonId),
        playerApi.getLessonProgress(courseId, chapterId, lessonId).catch(() => null),
        playerApi.getLessonMethods(lessonId).catch(() => [])
      ])

      currentLesson.value = lessonData
      lessonProgress.value = progressData
      availableMethods.value = methodsData

      // Mark as started if not already
      if (!progressData || progressData.status === 'not_started') {
        await markLessonStarted(courseId, chapterId, lessonId)
      }

      // Send analytics event
      await playerApi.sendAnalyticsEvent({
        event_type: 'lesson_start',
        resource_type: 'lesson',
        resource_id: lessonId
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Lektion konnte nicht geladen werden'
      console.error('Failed to load lesson:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Mark lesson as started
   */
  const markLessonStarted = async (
    courseId: string,
    chapterId: string,
    lessonId: string
  ): Promise<void> => {
    try {
      await playerApi.markLessonStarted(courseId, chapterId, lessonId)

      if (lessonProgress.value) {
        lessonProgress.value.status = 'in_progress'
        lessonProgress.value.started_at = new Date().toISOString()
      }
    } catch (err) {
      console.error('Failed to mark lesson as started:', err)
    }
  }

  /**
   * Mark lesson as completed
   */
  const markLessonCompleted = async (
    courseId: string,
    chapterId: string,
    lessonId: string
  ): Promise<void> => {
    try {
      await playerApi.markLessonCompleted(courseId, chapterId, lessonId)

      if (lessonProgress.value) {
        lessonProgress.value.status = 'completed'
        lessonProgress.value.progress_percentage = 100
        lessonProgress.value.completed_at = new Date().toISOString()
      }

      // Send analytics event
      await playerApi.sendAnalyticsEvent({
        event_type: 'lesson_complete',
        resource_type: 'lesson',
        resource_id: lessonId
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fortschritt konnte nicht gespeichert werden'
      console.error('Failed to mark lesson as completed:', err)
      throw err
    }
  }

  /**
   * Execute learning method
   */
  const executeLearningMethod = async (request: ExecuteMethodRequest): Promise<any> => {
    methodExecuting.value = true
    methodError.value = null
    methodResult.value = null

    try {
      const response = await playerApi.executeMethod(request)

      console.log('[PlayerStore] executeMethod response:', response)
      console.log('[PlayerStore] Setting methodResult to:', response.result)

      methodResult.value = response.result

      // Send analytics event
      await playerApi.sendAnalyticsEvent({
        event_type: 'method_execute',
        resource_type: 'learning_method',
        resource_id: request.method_id,
        metadata: {
          lesson_id: request.lesson_id,
          tokens_used: response.tokens_used
        }
      })

      return response
    } catch (err: any) {
      methodError.value = err.response?.data?.message || 'Aufgabe konnte nicht geladen werden'
      console.error('Failed to execute method:', err)
      throw err
    } finally {
      methodExecuting.value = false
    }
  }

  /**
   * Sync progress (update percentage & time spent)
   */
  const syncProgress = async (
    courseId: string,
    chapterId: string,
    lessonId: string,
    percentage: number,
    timeSpent?: number
  ): Promise<void> => {
    try {
      await playerApi.updateLessonProgress(courseId, chapterId, lessonId, percentage, timeSpent)

      if (lessonProgress.value) {
        lessonProgress.value.progress_percentage = percentage
        if (timeSpent) {
          lessonProgress.value.time_spent_minutes = timeSpent
        }
      }
    } catch (err) {
      console.error('Failed to sync progress:', err)
    }
  }

  /**
   * Submit quiz (delegates to quiz store, passes lesson completion callback)
   */
  const submitQuiz = async (
    courseId: string,
    chapterId: string,
    lessonId: string
  ): Promise<any> => {
    return quizStore.submitQuiz(
      lessonId,
      async (id: string) => markLessonCompleted(courseId, chapterId, id)
    )
  }

  /**
   * Clear player state
   */
  const clearPlayer = (): void => {
    course.value = null
    chapters.value = []
    currentChapter.value = null
    currentLesson.value = null
    courseProgress.value = null
    chapterProgress.value = null
    lessonProgress.value = null
    availableMethods.value = []
    methodResult.value = null
    error.value = null
    quizStore.resetQuizState()
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    course,
    chapters,
    currentChapter,
    currentLesson,
    courseProgress,
    chapterProgress,
    lessonProgress,
    availableMethods,
    loading,
    error,
    methodExecuting,
    methodResult,
    methodError,

    // Quiz State (re-exported from quiz store for backward compatibility)
    quiz: quizStore.quiz,
    quizAnswers: quizStore.quizAnswers,
    quizResult: quizStore.quizResult,
    quizLoading: quizStore.quizLoading,
    quizSubmitting: quizStore.quizSubmitting,
    quizError: quizStore.quizError,
    quizStartedAt: quizStore.quizStartedAt,
    quizAttempts: quizStore.quizAttempts,

    // Getters
    hasCourse,
    currentLessonIndex,
    hasNextLesson,
    hasPreviousLesson,
    nextLesson,
    previousLesson,
    isLessonCompleted,

    // Quiz Getters (re-exported)
    isQuizLoaded: quizStore.isQuizLoaded,
    quizQuestions: quizStore.quizQuestions,
    quizProgress: quizStore.quizProgress,
    allQuestionsAnswered: quizStore.allQuestionsAnswered,
    isQuizCompleted: quizStore.isQuizCompleted,
    isExamMode: quizStore.isExamMode,
    quizTimeSpent: quizStore.quizTimeSpent,

    // Actions
    loadCourse,
    loadChapter,
    loadLesson,
    markLessonStarted,
    markLessonCompleted,
    executeLearningMethod,
    syncProgress,
    clearPlayer,

    // Quiz Actions (re-exported)
    loadQuizForLesson: quizStore.loadQuizForLesson,
    updateQuizAnswer: quizStore.updateQuizAnswer,
    submitQuiz,
    resetQuizState: quizStore.resetQuizState
  }
})
