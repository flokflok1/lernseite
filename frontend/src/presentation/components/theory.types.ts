/**
 * Theory Types - Theory Content & Explanations
 *
 * Defines types for chapter theories and lesson explanations.
 *
 * @module kurs-builder/types/theory
 */

/**
 * Chapter Theory
 *
 * A theory/summary document for a chapter.
 */
export interface Theory {
  /** Unique theory identifier */
  theoryId: string

  /** Parent chapter ID */
  chapterId: string

  /** Theory title */
  title: string

  /** Theory content (markdown) */
  content: string

  /** Presentation style */
  style: 'default' | 'structured' | 'detailed' | 'simple'

  /** Audio URL (if TTS generated) */
  audioUrl?: string

  /** Audio status */
  audioStatus?: 'none' | 'generating' | 'ready' | 'error'

  /** Created timestamp */
  createdAt: string

  /** Updated timestamp */
  updatedAt?: string

  /** View count */
  viewCount?: number
}

/**
 * Lesson Explanation
 *
 * A step-by-step explanation for a lesson.
 */
export interface Explanation {
  /** Unique explanation identifier */
  explanationId: string

  /** Parent lesson ID */
  lessonId: string

  /** Explanation title */
  title: string

  /** Number of steps */
  stepCount: number

  /** Explanation steps */
  steps: ExplanationStep[]

  /** Created timestamp */
  createdAt: string

  /** Updated timestamp */
  updatedAt?: string

  /** Difficulty level */
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
}

/**
 * Explanation Step
 *
 * A single step in a lesson explanation.
 */
export interface ExplanationStep {
  /** Step number */
  step: number

  /** Step title */
  title: string

  /** Step content (markdown) */
  content: string

  /** Optional code examples */
  codeExample?: {
    language: string
    code: string
  }

  /** Optional image URL */
  imageUrl?: string

  /** Key points/tips */
  keyPoints?: string[]
}

/**
 * Theory Generation Request
 *
 * Request parameters for generating chapter theory.
 */
export interface TheoryGenerationRequest {
  /** Target chapter ID */
  chapter_id: string

  /** Style preference */
  style: 'default' | 'structured' | 'detailed' | 'simple'

  /** Include audio generation */
  generate_audio?: boolean

  /** Context files (optional) */
  context_files?: string[]

  /** Additional instructions */
  instructions?: string
}

/**
 * Explanation Generation Request
 *
 * Request parameters for generating lesson explanation.
 */
export interface ExplanationGenerationRequest {
  /** Target lesson ID */
  lesson_id: string

  /** Number of steps to generate */
  step_count?: number

  /** Difficulty level */
  difficulty?: 'beginner' | 'intermediate' | 'advanced'

  /** Context files (optional) */
  context_files?: string[]

  /** Additional instructions */
  instructions?: string
}
