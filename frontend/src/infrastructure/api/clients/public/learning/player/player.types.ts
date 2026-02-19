/**
 * LernsystemX - Player API Types
 *
 * Type definitions for Course Player, Lessons, Progress,
 * Learning Methods, Quiz/Exam, Analytics, and Task Executions.
 *
 * Refactored: Extracted from player.api.ts for file size compliance (G01)
 */

// ============================================================================
// Course & Content Types
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
  total_chapters?: number
  total_lessons?: number
  total_duration_minutes?: number
  created_at: string
  updated_at?: string
}

export interface Chapter {
  chapter_id: string  // UUID
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
  lesson_id: string  // UUID
  chapter_id: string // UUID
  course_id: string  // UUID
  title: string
  description?: string
  order: number
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  content: any // JSON content structure
  duration_minutes?: number
  is_published: boolean
  created_at: string
}

// ============================================================================
// Progress Types
// ============================================================================

export interface LessonProgress {
  lesson_id: string  // UUID
  user_id: string    // UUID
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  time_spent_minutes: number
  started_at?: string
  completed_at?: string
  last_accessed_at?: string
}

export interface ChapterProgress {
  chapter_id: string // UUID
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
  chapters_completed: number
  total_chapters: number
  lessons_completed: number
  total_lessons: number
  last_accessed_at?: string
  enrolled_at: string
  completed_at?: string
}

// ============================================================================
// Learning Method Types
// ============================================================================

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

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsEventRequest {
  event_type: string
  resource_type: string
  resource_id: number | string
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
// Saved Task Execution Types
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
