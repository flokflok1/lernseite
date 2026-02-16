/**
 * LernsystemX - Player API
 *
 * Pattern: Transform backend DTOs to domain models at API layer
 * All snake_case backend fields transformed to camelCase at API layer
 *
 * API endpoints for Course Player, Lessons, Progress & Learning Methods
 *
 * Refactored: modules → chapters (2025-11-27)
 */

import http from '@/infrastructure/api/http'
import {
  transformCourseFromAPI,
  transformChapterFromAPI,
  transformLessonFromAPI,
  transformCourseProgressFromAPI,
  transformChapterProgressFromAPI,
  transformLessonProgressFromAPI,
  transformSavedTaskExecutionFromAPI,
  transformQuizDataFromAPI,
  transformQuizResultFromAPI
} from '@/infrastructure/api/utils/transformers'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface Course {
  course_id: string  // UUID
  title: string
  subtitle?: string
  description: string
  category?: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  language: string
  thumbnail_url?: string
  creator_id: number
  creator_name?: string
  is_published: boolean
  tags?: string[]
  learning_goals?: string[]
  requirements?: string[]
  total_chapters?: number  // Refactored: total_modules → total_chapters (2025-11-27)
  total_lessons?: number
  total_duration_minutes?: number
  created_at: string
  updated_at?: string
}

export interface Chapter {
  chapter_id: string  // UUID (Refactored: module_id → chapter_id 2025-11-27)
  course_id: string   // UUID
  title: string
  description?: string
  order: number
  duration_minutes?: number
  lessons?: Lesson[]
  is_published: boolean
  created_at: string
}

export interface Lesson {
  lesson_id: string  // UUID (2025-12-10)
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  course_id: string   // UUID
  title: string
  description?: string
  order: number
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  content: any // JSON content structure
  duration_minutes?: number
  is_published: boolean
  created_at: string
}

export interface LessonProgress {
  lesson_id: string  // UUID (2025-12-10)
  user_id: string    // UUID (2025-12-10)
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  time_spent_minutes: number
  started_at?: string
  completed_at?: string
  last_accessed_at?: string
}

export interface ChapterProgress {
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  user_id: number
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  lessons_completed: number
  total_lessons: number
  started_at?: string
  completed_at?: string
}

export interface CourseProgress {
  course_id: string  // UUID
  user_id: number
  enrollment_id: number
  status: 'active' | 'completed' | 'cancelled'
  progress_percentage: number
  chapters_completed: number  // Refactored: modules_completed → chapters_completed (2025-11-27)
  total_chapters: number      // Refactored: total_modules → total_chapters (2025-11-27)
  lessons_completed: number
  total_lessons: number
  last_accessed_at?: string
  enrolled_at: string
  completed_at?: string
}

export interface LearningMethod {
  method_id: number
  method_name: string
  category: 'basis' | 'premium' | 'pro'
  description: string
  requires_ai: boolean
  token_cost: number
  is_premium: boolean
  icon?: string
  config?: any
}

export interface ExecuteMethodRequest {
  lesson_id: string | number  // UUID string or legacy number
  method_id: number
  input_data?: any
}

export interface ExecuteMethodResponse {
  success: boolean
  method_execution_id: number
  result: any
  tokens_used: number
  processing_time_ms: number
  message?: string
}

export interface AnalyticsEventRequest {
  event_type: string
  resource_type: string
  resource_id: number | string  // Can be int (lesson_id) or UUID string (course_id)
  metadata?: any
}

// ============================================================================
// Quiz & Exam Types
// ============================================================================

export type QuizQuestionType = 'single_choice' | 'multiple_choice' | 'true_false' | 'fill_blank' | 'matching'

export interface QuizQuestionOption {
  id: string | number
  text: string
  is_correct?: boolean // Only shown in results
}

export interface QuizQuestion {
  question_id: number
  type: QuizQuestionType
  question_text: string
  points: number
  options?: QuizQuestionOption[]
  correct_answer?: string | boolean // For true/false or fill_blank
  explanation?: string | null
  order: number
}

export interface QuizData {
  quiz_id?: number
  lesson_id: string | number  // UUID string or legacy number
  title: string
  description?: string
  questions: QuizQuestion[]
  time_limit_seconds?: number | null
  passing_score_percentage?: number
  is_exam: boolean
  allow_retry: boolean
  show_correct_answers: boolean
  shuffle_questions?: boolean
  shuffle_options?: boolean
}

export interface QuizAnswerSubmission {
  question_id: number
  selected_option_ids?: (string | number)[]
  answer_text?: string
  answer_boolean?: boolean
}

export interface QuizSubmitRequest {
  lesson_id: string | number  // UUID string or legacy number
  quiz_id?: number
  answers: QuizAnswerSubmission[]
  time_spent_seconds?: number
}

export interface QuizQuestionResult {
  question_id: number
  is_correct: boolean
  earned_points: number
  max_points: number
  user_answer: QuizAnswerSubmission
  correct_answer?: any
  explanation?: string
}

export interface QuizResult {
  quiz_attempt_id: number
  quiz_id?: number
  lesson_id: string | number  // UUID string or legacy number
  user_id: string | number    // UUID string or legacy number
  total_points: number
  max_points: number
  score_percentage: number
  passed: boolean
  time_spent_seconds: number
  question_results: QuizQuestionResult[]
  submitted_at: string
  is_exam: boolean
}

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

  return transformCourseFromAPI(response.data.course)
}

/**
 * Get all chapters for a course
 * Refactored: getCourseModules → getCourseChapters (2025-11-27)
 */
export const getCourseChapters = async (courseId: string): Promise<Chapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: Chapter[]
  }>(`/courses/${courseId}/chapters`)

  return response.data.chapters.map(transformChapterFromAPI)
}

/**
 * Get chapter details with lessons
 * Refactored: getModule → getChapter (2025-11-27)
 */
export const getChapter = async (courseId: string, chapterId: string): Promise<Chapter> => {
  const response = await http.get<{
    success: boolean
    chapter: Chapter
  }>(`/courses/${courseId}/chapters/${chapterId}`)

  return transformChapterFromAPI(response.data.chapter)
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

  return transformLessonFromAPI(response.data.lesson)
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

  return transformCourseProgressFromAPI(response.data.progress)
}

/**
 * Get chapter progress
 * Refactored: getModuleProgress → getChapterProgress (2025-11-27)
 */
export const getChapterProgress = async (
  courseId: string,
  chapterId: string
): Promise<ChapterProgress> => {
  const response = await http.get<{
    success: boolean
    progress: ChapterProgress
  }>(`/courses/${courseId}/chapters/${chapterId}/progress`)

  return transformChapterProgressFromAPI(response.data.progress)
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

  return transformLessonProgressFromAPI(response.data.progress)
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
    message: execution.message
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
 * Send analytics event
 */
export const sendAnalyticsEvent = async (request: AnalyticsEventRequest): Promise<void> => {
  await http.post('/analytics/event', {
    event_type: request.event_type,
    resource_type: request.resource_type,
    resource_id: request.resource_id,
    payload: request.metadata || {}  // Backend expects 'payload', not 'metadata'
  })
}

// ============================================================================
// Saved Task Executions API Functions
// ============================================================================

export interface SavedTaskExecution {
  execution_id: string
  method_id: string
  method_name: string
  method_description?: string
  user_input: string
  ai_response: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  model: string
  provider: string
  executed_at: string
}

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
