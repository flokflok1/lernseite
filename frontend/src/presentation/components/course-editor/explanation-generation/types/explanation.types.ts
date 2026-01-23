/**
 * Explanation Generation Types
 *
 * TypeScript interfaces for lesson explanation management.
 * Defines domain models and contracts for explanation system.
 */

export type ExplanationStyle = 'brief' | 'standard' | 'detailed' | 'visual' | 'interactive'

export interface Lesson {
  lesson_id: string
  title: string
  description?: string
}

export interface Course {
  course_id: string
  title: string
}

export interface LessonExplanation {
  explanationId: string
  lessonId: string
  title: string
  style: ExplanationStyle
  overview?: string
  learningGoals?: string[]
  steps: ExplanationStep[]
  createdAt: Date
  updatedAt?: Date
}

export interface ExplanationStep {
  stepId: string
  index: number
  title: string
  content: string
  speech?: string
  whiteboard_data?: WhiteboardData
  visualization?: string
  quiz?: QuizData
}

export interface WhiteboardData {
  elements: WhiteboardElement[]
  animationDuration: number
}

export interface WhiteboardElement {
  id: string
  type: 'line' | 'text' | 'shape' | 'image'
  data: Record<string, any>
}

export interface QuizData {
  question: string
  options: string[]
  correctAnswer: number
}

export interface GenerateExplanationRequest {
  lesson_id: string
  style: ExplanationStyle
  generate_tts: boolean
  voice?: string
}
