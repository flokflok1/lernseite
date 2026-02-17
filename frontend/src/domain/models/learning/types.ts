/**
 * Learning Domain Types
 *
 * Canonical type definitions for learning-related domain concepts.
 * Infrastructure layer re-exports these for API response typing.
 */

export interface LearningMethod {
  method_id: number
  method_type: number
  method_name: string
  category: 'basis' | 'premium' | 'pro'
  description: string
  requires_ai: boolean
  token_cost: number
  estimated_tokens?: number
  is_premium: boolean
  icon?: string
  config?: Record<string, unknown>
}

export interface QuizQuestionResult {
  question_id: number
  is_correct: boolean
  points_earned: number
  user_answer: any
  correct_answer: any
  explanation?: string
}

export interface QuizResult {
  quiz_id: number
  passed: boolean
  score: number
  total_points: number
  percentage: number
  questions: QuizQuestionResult[]
  completed_at: string
}
