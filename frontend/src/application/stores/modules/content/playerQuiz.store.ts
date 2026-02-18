/**
 * LernsystemX - Player Quiz Store (Pinia)
 *
 * Manages quiz-specific state for the learning player:
 * - Quiz data and questions
 * - Answer tracking
 * - Quiz submission and results
 * - Exam mode handling
 *
 * Split from player.store.ts for Quality Gate G01 compliance.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as playerApi from '@/application/services/api/learning'
import type {
  QuizData,
  QuizAnswerSubmission,
  QuizResult
} from '@/application/services/api/learning'

export const usePlayerQuizStore = defineStore('playerQuiz', () => {
  // ============================================================================
  // State
  // ============================================================================

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
      } catch (_err) {
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
    lessonId: string,
    onLessonCompleted?: (lessonId: string) => Promise<void>
  ): Promise<QuizResult> => {
    if (!quiz.value) {
      throw new Error('Kein Quiz geladen')
    }

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
      if (result.passed && onLessonCompleted) {
        await onLessonCompleted(lessonId)
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

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    quiz,
    quizAnswers,
    quizResult,
    quizLoading,
    quizSubmitting,
    quizError,
    quizStartedAt,
    quizAttempts,

    // Getters
    isQuizLoaded,
    quizQuestions,
    quizProgress,
    allQuestionsAnswered,
    isQuizCompleted,
    isExamMode,
    quizTimeSpent,

    // Actions
    loadQuizForLesson,
    updateQuizAnswer,
    submitQuiz,
    resetQuizState
  }
})
