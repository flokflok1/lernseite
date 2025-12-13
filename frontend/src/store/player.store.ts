/**
 * LernsystemX - Player Store (Pinia)
 *
 * Manages:
 * - Current course, chapter, lesson state
 * - Progress tracking
 * - Learning methods
 * - Player navigation
 *
 * Refactored: modules → chapters (2025-11-27)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as playerApi from '@/api/player.api'
import type {
  Course,
  Chapter,
  Lesson,
  CourseProgress,
  ChapterProgress,
  LessonProgress,
  LearningMethod,
  ExecuteMethodRequest,
  QuizData,
  QuizAnswerSubmission,
  QuizResult
} from '@/api/player.api'

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

  // Quiz State
  const quiz = ref<QuizData | null>(null)
  const quizAnswers = ref<Record<number, QuizAnswerSubmission>>({})
  const quizResult = ref<QuizResult | null>(null)
  const quizLoading = ref(false)
  const quizSubmitting = ref(false)
  const quizError = ref<string | null>(null)
  const quizStartedAt = ref<Date | null>(null)
  const quizAttempts = ref<QuizResult[]>([])

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

  /**
   * Check if quiz is loaded
   */
  const isQuizLoaded = computed(() => !!quiz.value)

  /**
   * Get quiz questions
   */
  const quizQuestions = computed(() => quiz.value?.questions || [])

  /**
   * Get quiz progress (% of answered questions)
   */
  const quizProgress = computed(() => {
    if (!quiz.value || quiz.value.questions.length === 0) return 0
    const answeredCount = Object.keys(quizAnswers.value).length
    return (answeredCount / quiz.value.questions.length) * 100
  })

  /**
   * Check if all required questions are answered
   */
  const allQuestionsAnswered = computed(() => {
    if (!quiz.value) return false
    return quiz.value.questions.every(q => !!quizAnswers.value[q.question_id])
  })

  /**
   * Check if quiz is completed
   */
  const isQuizCompleted = computed(() => !!quizResult.value)

  /**
   * Check if lesson is exam mode
   */
  const isExamMode = computed(() => quiz.value?.is_exam || false)

  /**
   * Get time spent on quiz (in seconds)
   */
  const quizTimeSpent = computed(() => {
    if (!quizStartedAt.value) return 0
    return Math.floor((Date.now() - quizStartedAt.value.getTime()) / 1000)
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
      // Load course details
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
   * Refactored: loadModule → loadChapter (2025-11-27)
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
        resource_id: chapterId  // UUID string
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
    lessonId: string  // UUID string
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

      // Update local progress
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

      // Update local progress
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

      // Update local progress
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
   * Load quiz for a lesson
   */
  const loadQuizForLesson = async (lessonId: string): Promise<void> => {
    quizLoading.value = true
    quizError.value = null

    try {
      const quizData = await playerApi.getLessonQuiz(lessonId)

      quiz.value = quizData
      quizAnswers.value = {}
      quizResult.value = null
      quizStartedAt.value = new Date()

      // Load attempt history
      try {
        const attempts = await playerApi.getQuizAttempts(lessonId)
        quizAttempts.value = attempts
      } catch (err) {
        // Attempt history not critical
        quizAttempts.value = []
      }

      // Send analytics event for exam start
      if (quizData.is_exam) {
        await playerApi.startExam(lessonId, quizData.quiz_id)
        await playerApi.sendAnalyticsEvent({
          event_type: 'exam_start',
          resource_type: 'lesson',
          resource_id: lessonId,
          metadata: {
            quiz_id: quizData.quiz_id,
            time_limit_seconds: quizData.time_limit_seconds
          }
        })
      }
    } catch (err: any) {
      quizError.value = err.response?.data?.message || 'Quiz konnte nicht geladen werden'
      console.error('Failed to load quiz:', err)
      throw err
    } finally {
      quizLoading.value = false
    }
  }

  /**
   * Update answer for a question
   */
  const updateQuizAnswer = (questionId: number, answer: QuizAnswerSubmission): void => {
    quizAnswers.value[questionId] = answer
  }

  /**
   * Submit quiz answers
   */
  const submitQuiz = async (
    courseId: string,
    chapterId: string,
    lessonId: string
  ): Promise<QuizResult> => {
    if (!quiz.value) {
      throw new Error('Kein Quiz geladen')
    }

    // Validate all questions are answered
    if (!allQuestionsAnswered.value) {
      throw new Error('Bitte beantworte alle Fragen')
    }

    quizSubmitting.value = true
    quizError.value = null

    try {
      const answersArray = Object.values(quizAnswers.value)

      const result = await playerApi.submitQuizAnswers({
        lesson_id: lessonId,
        quiz_id: quiz.value.quiz_id,
        answers: answersArray,
        time_spent_seconds: quizTimeSpent.value
      })

      quizResult.value = result

      // Send exam_complete analytics event
      if (quiz.value.is_exam) {
        await playerApi.sendAnalyticsEvent({
          event_type: 'exam_complete',
          resource_type: 'lesson',
          resource_id: lessonId,
          metadata: {
            quiz_id: quiz.value.quiz_id,
            score_percentage: result.score_percentage,
            passed: result.passed,
            total_points: result.total_points,
            max_points: result.max_points,
            time_spent_seconds: result.time_spent_seconds
          }
        })
      }

      // Mark lesson as completed if quiz passed
      if (result.passed) {
        await markLessonCompleted(courseId, chapterId, lessonId)
      }

      return result
    } catch (err: any) {
      quizError.value = err.response?.data?.message || 'Quiz konnte nicht abgesendet werden'
      console.error('Failed to submit quiz:', err)
      throw err
    } finally {
      quizSubmitting.value = false
    }
  }

  /**
   * Reset quiz state
   */
  const resetQuizState = (): void => {
    quiz.value = null
    quizAnswers.value = {}
    quizResult.value = null
    quizLoading.value = false
    quizSubmitting.value = false
    quizError.value = null
    quizStartedAt.value = null
    quizAttempts.value = []
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
    resetQuizState()
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

    // Quiz State
    quiz,
    quizAnswers,
    quizResult,
    quizLoading,
    quizSubmitting,
    quizError,
    quizStartedAt,
    quizAttempts,

    // Getters
    hasCourse,
    currentLessonIndex,
    hasNextLesson,
    hasPreviousLesson,
    nextLesson,
    previousLesson,
    isLessonCompleted,

    // Quiz Getters
    isQuizLoaded,
    quizQuestions,
    quizProgress,
    allQuestionsAnswered,
    isQuizCompleted,
    isExamMode,
    quizTimeSpent,

    // Actions
    loadCourse,
    loadChapter,
    loadLesson,
    markLessonStarted,
    markLessonCompleted,
    executeLearningMethod,
    syncProgress,
    clearPlayer,

    // Quiz Actions
    loadQuizForLesson,
    updateQuizAnswer,
    submitQuiz,
    resetQuizState
  }
})
