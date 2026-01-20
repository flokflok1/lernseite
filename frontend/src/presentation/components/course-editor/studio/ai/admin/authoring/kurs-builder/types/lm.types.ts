/**
 * Learning Method Types - LM Suggestions & Metadata
 *
 * Defines types for learning method suggestions and configuration.
 *
 * @module kurs-builder/types/lm
 */

/**
 * Learning Method Type
 *
 * Metadata about a learning method type (0-11).
 */
export interface LearningMethodType {
  /** Method ID (0-11) */
  lm_id: number

  /** Method name */
  name: string

  /** Method description */
  description: string

  /** Group (A=Erklärend, B=Praxis, C=Prüfung) */
  group: 'A' | 'B' | 'C'

  /** Tier (basic/premium) */
  tier: 'basic' | 'premium'

  /** AI usage level */
  ki_usage: 'intensive' | 'medium' | 'optional'

  /** Icon emoji */
  icon: string
}

/**
 * LM Suggestion
 *
 * AI-suggested learning method for a lesson.
 */
export interface LMSuggestion {
  /** Method ID */
  lm_id: number

  /** Method name */
  name: string

  /** Method group */
  group: 'A' | 'B' | 'C'

  /** Suggestion reason */
  reason: string

  /** Confidence score (0-1) */
  confidence: number

  /** Recommended priority */
  priority: 'high' | 'medium' | 'low'

  /** Icon */
  icon?: string

  /** Tier */
  tier?: 'basic' | 'premium'
}

/**
 * LM Configuration
 *
 * Configuration for a learning method instance.
 */
export interface LMConfiguration {
  /** Method type */
  method_type: number

  /** Display title */
  title: string

  /** Method-specific config (varies by type) */
  config: Record<string, any>

  /** Method-specific content (varies by type) */
  content?: Record<string, any>

  /** Active status */
  active: boolean

  /** Display order */
  order: number
}

/**
 * LM Suggestion Request
 *
 * Request parameters for AI LM suggestions.
 */
export interface LMSuggestionRequest {
  /** Target lesson ID */
  lesson_id: string

  /** Context files for analysis */
  context_files?: string[]

  /** Maximum suggestions to return */
  max_suggestions?: number

  /** Filter by group */
  group_filter?: ('A' | 'B' | 'C')[]

  /** Filter by tier */
  tier_filter?: ('basic' | 'premium')[]
}

/**
 * LM Creation Request
 *
 * Request to create a new learning method instance.
 */
export interface LMCreationRequest {
  /** Target lesson ID */
  lesson_id: string

  /** Method type (0-11) */
  method_type: number

  /** Method title */
  title: string

  /** Initial configuration */
  config?: Record<string, any>

  /** Generate content with AI */
  generate_content?: boolean

  /** Content generation instructions */
  generation_instructions?: string
}
