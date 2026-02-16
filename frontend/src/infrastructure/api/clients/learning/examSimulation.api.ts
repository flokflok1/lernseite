/**
 * LernsystemX - Exam Simulation API
 *
 * API functions for KI-Prüfungssimulation:
 * - Get exam context for a course
 * - Create and manage exam simulations
 * - Start and submit exam attempts
 */

import http from '@/infrastructure/api/http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface TopicScore {
  topic: string
  score: number
}

export interface ExamContext {
  profession?: string
  profession_detail?: string
  exam_level?: string
  region?: string
  ihk?: string
  ihk_standard?: string
  training_year?: number
  exam_date?: string
  weak_topics: TopicScore[]
  strong_topics: TopicScore[]
  normal_topics: TopicScore[]
  detected_topics: string[]
  detected_files: Array<{
    file_id: string
    filename: string
    type: string
    is_exam_relevant: boolean
    topics: string[]
    summary?: string
  }>
  course_title?: string
  user_name?: string
  preferred_difficulty?: string
  recommended_focus: Record<string, number>
  confidence: number
}

export interface ExamSimulationConfig {
  mode: 'smart' | 'manual'
  difficulty: 'easy' | 'realistic' | 'hard'
  time_limit_minutes: number
  focus_distribution?: Record<string, number>
  extra_instructions?: string
  selected_files?: string[]
  title?: string
}

export interface ExamQuestion {
  question_id: string
  type: 'mc' | 'calculation' | 'scenario' | 'free_text'
  topic: string
  difficulty: string
  points: number
  question: string
  options?: string[]
  correct_answer?: string
  explanation?: string
  ihk_reference?: string
}

export interface ExamSimulation {
  simulation_id: string
  course_id: string
  course_title: string
  user_id: string
  title: string
  description?: string
  context: ExamContext
  config: ExamSimulationConfig
  result?: {
    summary: string
    topics_covered: string[]
    total_points: number
    questions: ExamQuestion[]
  }
  status: 'pending' | 'generating' | 'ready' | 'failed'
  error_message?: string
  generation_started_at?: string
  generation_completed_at?: string
  tokens_used?: number
  model_used?: string
  attempt_count: number
  best_score?: number
  avg_score?: number
  created_at: string
  updated_at?: string
}

export interface ExamAttempt {
  attempt_id: string
  simulation_id: string
  started_at: string
  completed_at?: string
  time_spent_seconds?: number
  score?: number
  max_score?: number
  percentage?: number
  passed?: boolean
  results_by_topic?: Record<string, {
    correct: number
    total: number
    points: number
    max_points: number
  }>
  status: 'in_progress' | 'completed' | 'abandoned'
}

export interface SubmitAnswers {
  attempt_id: string
  answers: Array<{
    question_id: string
    answer: string
  }>
  time_spent_seconds: number
}

export interface AttemptResult {
  attempt_id: string
  score: number
  max_score: number
  percentage: number
  passed: boolean
  time_spent_seconds: number
  results_by_topic: Record<string, any>
  answers: Array<{
    question_id: string
    user_answer: string
    correct_answer: string
    is_correct: boolean
    points_earned: number
    points_possible: number
    explanation?: string
  }>
}

export interface UserExamProfile {
  profession?: string
  profession_detail?: string
  training_year?: number
  target_exam?: string
  exam_date?: string
  region?: string
  ihk?: string
  preferred_difficulty?: string
  preferred_question_types?: string[]
}

// ============================================================================
// Exam Context API
// ============================================================================

/**
 * Get detected exam context for a course
 */
export const getExamContext = async (courseId: string): Promise<ExamContext> => {
  const response = await http.get<{
    success: boolean
    context: ExamContext
  }>(`/courses/${courseId}/exam-context`)

  return response.data.context
}

// ============================================================================
// Exam Simulation CRUD API
// ============================================================================

/**
 * Create a new exam simulation
 */
export const createExamSimulation = async (
  courseId: string,
  config: ExamSimulationConfig
): Promise<ExamSimulation> => {
  const response = await http.post<{
    success: boolean
    simulation: ExamSimulation
  }>(`/courses/${courseId}/exam-simulations`, config)

  return response.data.simulation
}

/**
 * List user's exam simulations
 */
export const listExamSimulations = async (params: {
  course_id?: string
  status?: string
  page?: number
  per_page?: number
} = {}): Promise<{
  simulations: ExamSimulation[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}> => {
  const response = await http.get<{
    success: boolean
    simulations: ExamSimulation[]
    pagination: {
      page: number
      per_page: number
      total: number
      total_pages: number
    }
  }>('/exam-simulations', { params })

  return {
    simulations: response.data.simulations,
    pagination: response.data.pagination
  }
}

/**
 * Get exam simulation details
 */
export const getExamSimulation = async (simulationId: string): Promise<ExamSimulation> => {
  const response = await http.get<{
    success: boolean
    simulation: ExamSimulation
  }>(`/exam-simulations/${simulationId}`)

  return response.data.simulation
}

/**
 * Delete an exam simulation
 */
export const deleteExamSimulation = async (simulationId: string): Promise<void> => {
  await http.delete(`/exam-simulations/${simulationId}`)
}

// ============================================================================
// Exam Generation API
// ============================================================================

/**
 * Start exam generation (queues Celery task)
 */
export const generateExamSimulation = async (simulationId: string): Promise<{
  status: string
}> => {
  const response = await http.post<{
    success: boolean
    message: string
    status: string
  }>(`/exam-simulations/${simulationId}/generate`)

  return { status: response.data.status }
}

// ============================================================================
// Exam Attempt API
// ============================================================================

/**
 * Start a new exam attempt
 */
export const startExamAttempt = async (simulationId: string): Promise<{
  attempt: ExamAttempt
  questions: ExamQuestion[]
}> => {
  const response = await http.post<{
    success: boolean
    attempt: ExamAttempt & { time_limit_minutes: number; max_score: number }
    questions: ExamQuestion[]
  }>(`/exam-simulations/${simulationId}/start`)

  return {
    attempt: response.data.attempt,
    questions: response.data.questions
  }
}

/**
 * List attempts for a simulation
 */
export const listExamAttempts = async (simulationId: string): Promise<ExamAttempt[]> => {
  const response = await http.get<{
    success: boolean
    attempts: ExamAttempt[]
    total: number
  }>(`/exam-simulations/${simulationId}/attempts`)

  return response.data.attempts
}

/**
 * Submit exam answers
 */
export const submitExamAttempt = async (
  simulationId: string,
  data: SubmitAnswers
): Promise<AttemptResult> => {
  const response = await http.post<{
    success: boolean
    result: AttemptResult
  }>(`/exam-simulations/${simulationId}/submit`, data)

  return response.data.result
}

// ============================================================================
// User Profile API
// ============================================================================

/**
 * Get user's exam-related profile settings
 */
export const getUserExamProfile = async (): Promise<UserExamProfile> => {
  const response = await http.get<{
    success: boolean
    profile: UserExamProfile
  }>('/user-profile/exam-settings')

  return response.data.profile
}

/**
 * Update user's exam-related profile settings
 */
export const updateUserExamProfile = async (
  profile: Partial<UserExamProfile>
): Promise<UserExamProfile> => {
  const response = await http.put<{
    success: boolean
    profile: UserExamProfile
  }>('/user-profile/exam-settings', profile)

  return response.data.profile
}
