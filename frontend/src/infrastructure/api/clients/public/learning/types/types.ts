/**
 * Public Learning API - Types
 *
 * Types for course player, lessons, progress tracking, quiz, and learning methods.
 */

// ============================================================================
// Player API Types
// ============================================================================

export interface Course {
  course_id: string
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
  chapter_id: string
  course_id: string
  title: string
  description?: string
  order: number
  duration_minutes?: number
  lessons?: Lesson[]
  is_published: boolean
  created_at: string
}

export interface Lesson {
  lesson_id: string
  chapter_id: string
  course_id: string
  title: string
  description?: string
  order: number
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  content: any
  duration_minutes?: number
  is_published: boolean
  created_at: string
}

export interface LessonProgress {
  lesson_id: string
  user_id: string
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  time_spent_minutes: number
  started_at?: string
  completed_at?: string
  last_accessed_at?: string
}

export interface ChapterProgress {
  chapter_id: string
  user_id: number
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  lessons_completed: number
  total_lessons: number
  started_at?: string
  completed_at?: string
}

export interface CourseProgress {
  course_id: string
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

/**
 * LearningMethod re-exported from domain.
 * Canonical definition lives in domain/models/learning/types.ts
 */
export type { LearningMethod } from '@/domain/models/learning/types'

export interface ExecuteMethodRequest {
  lesson_id: string | number
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
  resource_id: number | string
  metadata?: any
}

export type QuizQuestionType = 'single_choice' | 'multiple_choice' | 'true_false' | 'fill_blank' | 'matching'

export interface QuizQuestionOption {
  id: string | number
  text: string
  is_correct?: boolean
}

export interface QuizQuestion {
  question_id: number
  type: QuizQuestionType
  question_text: string
  points: number
  options?: QuizQuestionOption[]
}

export interface QuizData {
  quiz_id: number
  lesson_id: number
  title: string
  description?: string
  questions: QuizQuestion[]
  passing_percentage: number
  allow_retry: boolean
}

export interface QuizAnswerSubmission {
  question_id: number
  answer: any
  time_spent_seconds: number
}

export interface QuizSubmitRequest {
  quiz_id: number
  answers: QuizAnswerSubmission[]
}

/**
 * QuizQuestionResult and QuizResult re-exported from domain.
 * Canonical definitions live in domain/models/learning/types.ts
 */
export type { QuizQuestionResult, QuizResult } from '@/domain/models/learning/types'

export interface SavedTaskExecution {
  execution_id: number
  lesson_id: number
  method_id: number
  result: any
  created_at: string
}
