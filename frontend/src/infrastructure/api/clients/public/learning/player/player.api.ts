/**
 * LernsystemX - Player API
 *
 * Pattern: Transform backend DTOs to domain models at API layer
 * All snake_case backend fields transformed to camelCase at API layer
 *
 * API endpoints for Course Player, Lessons, Progress & Learning Methods
 *
 * Refactored: modules -> chapters (2025-11-27)
 * Refactored: types extracted to player.types.ts (G01 compliance)
 */

import http from '@/infrastructure/api/http'
import {
  transformSavedTaskExecutionFromAPI,
  transformQuizDataFromAPI,
  transformQuizResultFromAPI
} from '@/infrastructure/api/utils/transformers'

import type {
  Course,
  Chapter,
  Lesson,
  LessonProgress,
  ChapterProgress,
  CourseProgress,
  LearningMethod,
  MethodProgress,
  ExecuteMethodRequest,
  ExecuteMethodResponse,
  AnalyticsEventRequest,
  QuizData,
  QuizSubmitRequest,
  QuizResult,
  SavedTaskExecution
} from './player.types'

// Re-export all types for backward compatibility
export type {
  Course,
  Chapter,
  Lesson,
  LessonProgress,
  ChapterProgress,
  CourseProgress,
  LearningMethod,
  MethodProgress,
  ExecuteMethodRequest,
  ExecuteMethodResponse,
  AnalyticsEventRequest,
  QuizQuestionType,
  QuizQuestionOption,
  QuizQuestion,
  QuizData,
  QuizAnswerSubmission,
  QuizSubmitRequest,
  QuizQuestionResult,
  QuizResult,
  SavedTaskExecution
} from './player.types'

// ============================================================================
// Course API Functions
// ============================================================================

/**
 * Get course details with chapters
 */
export const getCourse = async (courseId: string): Promise<Course> => {
  const response = await http.get<{
    success: boolean
    course: Course
  }>(`/courses/${courseId}`)

  return response.data.course
}

/**
 * Get all chapters for a course
 * Refactored: getCourseModules -> getCourseChapters (2025-11-27)
 */
export const getCourseChapters = async (courseId: string): Promise<Chapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: Chapter[]
  }>(`/courses/${courseId}/chapters`)

  return response.data.chapters
}

/**
 * Get chapter details with lessons
 * Refactored: getModule -> getChapter (2025-11-27)
 */
export const getChapter = async (courseId: string, chapterId: string): Promise<Chapter> => {
  const response = await http.get<{
    success: boolean
    chapter: Chapter
  }>(`/courses/${courseId}/chapters/${chapterId}`)

  return response.data.chapter
}

/**
 * Get lesson details
 * Note: Backend uses /lessons/:id directly, not nested under courses/chapters
 */
export const getLesson = async (
  courseId: string,
  chapterId: string,
  lessonId: string  // UUID string
): Promise<Lesson> => {
  const response = await http.get<{
    success: boolean
    lesson: Lesson
  }>(`/lessons/${lessonId}`)

  return response.data.lesson
}

// ============================================================================
// Progress API Functions
// ============================================================================

/**
 * Get course progress
 */
export const getCourseProgress = async (courseId: string): Promise<CourseProgress> => {
  const response = await http.get<{
    success: boolean
    progress: CourseProgress
  }>(`/courses/${courseId}/progress`)

  return response.data.progress
}

/**
 * Get chapter progress
 * Refactored: getModuleProgress -> getChapterProgress (2025-11-27)
 */
export const getChapterProgress = async (
  courseId: string,
  chapterId: string
): Promise<ChapterProgress> => {
  const response = await http.get<{
    success: boolean
    progress: ChapterProgress
  }>(`/courses/${courseId}/chapters/${chapterId}/progress`)

  return response.data.progress
}

/**
 * Get lesson progress
 * Note: Using direct /lessons/:id/progress endpoint
 */
export const getLessonProgress = async (
  courseId: string,
  chapterId: string,
  lessonId: string  // UUID string
): Promise<LessonProgress> => {
  const response = await http.get<{
    success: boolean
    progress: LessonProgress
  }>(`/lessons/${lessonId}/progress`)

  return response.data.progress
}

/**
 * Mark lesson as started
 * Note: Using direct /lessons/:id/start endpoint
 */
export const markLessonStarted = async (
  courseId: string,
  chapterId: string,
  lessonId: string  // UUID string
): Promise<void> => {
  await http.post(`/lessons/${lessonId}/start`)
}

/**
 * Mark lesson as completed
 * Note: Using direct /lessons/:id/complete endpoint
 */
export const markLessonCompleted = async (
  courseId: string,
  chapterId: string,
  lessonId: string  // UUID string
): Promise<void> => {
  await http.post(`/lessons/${lessonId}/complete`)
}

/**
 * Update lesson progress
 * Note: Using direct /lessons/:id/progress endpoint
 */
export const updateLessonProgress = async (
  courseId: string,
  chapterId: string,
  lessonId: string,  // UUID string
  progressPercentage: number,
  timeSpentMinutes?: number
): Promise<void> => {
  await http.patch(`/lessons/${lessonId}/progress`, {
    progress_percentage: progressPercentage,
    time_spent_minutes: timeSpentMinutes
  })
}

// ============================================================================
// Learning Methods API Functions
// ============================================================================

/**
 * Get learning methods for a specific lesson
 * Uses lesson-specific endpoint to get methods assigned to this lesson
 */
export const getLessonMethods = async (lessonId: string): Promise<LearningMethod[]> => {  // UUID string
  const response = await http.get<{
    success: boolean
    methods: LearningMethod[]
    total: number
  }>(`/lessons/${lessonId}/methods`)

  return response.data.methods
}

/**
 * Get user's progress for all learning methods in a lesson
 */
export const getLessonMethodsProgress = async (
  lessonId: string
): Promise<Record<string, MethodProgress>> => {
  const response = await http.get<{
    success: boolean
    progress: Record<string, MethodProgress>
  }>(`/lessons/${lessonId}/methods/progress`)

  return response.data.progress
}

/**
 * Execute a learning method (AI-powered)
 * Route: POST /api/v1/learning-methods/:method_id/execute
 *
 * Backend returns: { success: true, execution: { execution_id, result, ... } }
 */
export const executeMethod = async (
  request: ExecuteMethodRequest
): Promise<ExecuteMethodResponse> => {
  const { method_id, ...requestBody } = request

  console.log('[API] executeMethod called with:', { method_id, lesson_id: request.lesson_id })

  const response = await http.post<{ success: boolean; execution: any }>(
    `/learning-methods/${method_id}/execute`,
    {
      user_input: requestBody.input_data?.user_input || '',
      context: requestBody.input_data?.context,
      lesson_id: request.lesson_id,
      ...requestBody.input_data
    }
  )

  console.log('[API] executeMethod response:', response.data)

  // Extract execution from nested response
  const execution = response.data.execution || response.data

  return {
    success: response.data.success,
    method_execution_id: execution.execution_id,
    // Backend returns 'output_text', not 'result'
    result: execution.output_text || execution.result || execution.content,
    tokens_used: execution.billing?.tokens_charged || execution.total_tokens || 0,
    processing_time_ms: execution.latency_ms || execution.processing_time_ms || 0,
    message: execution.message,
    // Full execution data for task rendering
    execution,
  }
}

// ============================================================================
// Quiz & Exam API Functions
// ============================================================================

/**
 * Get quiz data for a lesson
 */
export const getLessonQuiz = async (lessonId: string): Promise<QuizData> => {  // UUID string
  const response = await http.get<{
    success: boolean
    quiz: QuizData
  }>(`/courses/lessons/${lessonId}/quiz`)

  return transformQuizDataFromAPI(response.data.quiz)
}

/**
 * Submit quiz answers
 */
export const submitQuizAnswers = async (request: QuizSubmitRequest): Promise<QuizResult> => {
  const response = await http.post<{
    success: boolean
    result: QuizResult
  }>(`/courses/lessons/${request.lesson_id}/quiz/submit`, {
    quiz_id: request.quiz_id,
    answers: request.answers,
    time_spent_seconds: request.time_spent_seconds
  })

  return transformQuizResultFromAPI(response.data.result)
}

/**
 * Start exam (for exam-type quizzes)
 */
export const startExam = async (lessonId: number, quizId?: number): Promise<void> => {
  await http.post(`/courses/lessons/${lessonId}/exam/start`, {
    quiz_id: quizId
  })
}

/**
 * Get quiz attempt history
 */
export const getQuizAttempts = async (lessonId: number): Promise<QuizResult[]> => {
  const response = await http.get<{
    success: boolean
    attempts: QuizResult[]
  }>(`/courses/lessons/${lessonId}/quiz/attempts`)

  return response.data.attempts.map(transformQuizResultFromAPI)
}

// ============================================================================
// Analytics API Functions
// ============================================================================

/**
 * Send analytics event (fire-and-forget, never throws)
 */
export const sendAnalyticsEvent = async (request: AnalyticsEventRequest): Promise<void> => {
  try {
    await http.post('/analytics/event', {
      event_type: request.event_type,
      resource_type: request.resource_type,
      resource_id: request.resource_id,
      payload: request.metadata || {}  // Backend expects 'payload', not 'metadata'
    })
  } catch {
    // Analytics is non-critical — silently ignore failures
  }
}

// ============================================================================
// Saved Task Executions API Functions
// ============================================================================

/**
 * Get saved task executions for a lesson
 * Route: GET /api/v1/lessons/:lesson_id/executions
 */
export const getLessonExecutions = async (
  lessonId: string,
  methodId?: string,
  limit: number = 50
): Promise<SavedTaskExecution[]> => {
  const params = new URLSearchParams()
  if (methodId) params.append('method_id', methodId)
  if (limit !== 50) params.append('limit', limit.toString())

  const queryString = params.toString()
  const url = `/lessons/${lessonId}/executions${queryString ? `?${queryString}` : ''}`

  const response = await http.get<{
    success: boolean
    executions: SavedTaskExecution[]
    total: number
  }>(url)

  return response.data.executions.map(transformSavedTaskExecutionFromAPI)
}

/**
 * Delete a task execution
 * Route: DELETE /api/v1/executions/:execution_id
 */
export const deleteExecution = async (executionId: string): Promise<boolean> => {
  const response = await http.delete<{
    success: boolean
    message?: string
  }>(`/executions/${executionId}`)

  return response.data.success
}
