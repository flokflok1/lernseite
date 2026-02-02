/**
 * Learning Methods Registry (LM00-LM11)
 *
 * Central registry for all 12 Content-Lernmethoden (Learning Methods).
 * Provides metadata and lazy-loaded form components.
 *
 * Architecture:
 * - Group A (LM00-LM04): Explanatory methods (theory, explanation, context)
 * - Group B (LM05-LM08): Practice methods (exercises, simulations, drills)
 * - Group C (LM09-LM11): Assessment methods (quizzes, exams, tests)
 *
 * Database Constraint: method_type BETWEEN 0 AND 11
 * Note: LM12-32 do NOT exist (were legacy System-Features, not Content-LMs)
 *
 * @see LernsystemX-Doku/01_Core/02_Lernmethoden.md - Complete LM specification
 */

import { defineAsyncComponent } from 'vue'
import type { Component } from 'vue'

export type LMGroup = 'A' | 'B' | 'C'
export type LMTier = 'basic' | 'premium'
export type KIUsage = 'intensive' | 'medium' | 'optional'

/**
 * Configuration for a single Learning Method
 */
export interface LearningMethodConfig {
  /** Learning Method ID (0-11) */
  id: number

  /** Human-readable name */
  name: string

  /** UI icon */
  icon: string

  /** Short description (1-2 sentences) */
  description: string

  /** Group classification */
  group: LMGroup

  /** Subscription tier required */
  tier: LMTier

  /** AI usage intensity */
  kiUsage: KIUsage

  /** Lazy-loaded form component (null if not yet implemented) */
  form: Component | null
}

/**
 * Central registry of all 12 Content-Lernmethoden
 *
 * Only includes LMs where form components exist.
 * Non-existent LMs (07-09) return null and use fallback component.
 */
export const LEARNING_METHOD_REGISTRY: Record<number, LearningMethodConfig> = {
  // GROUP A: Explanatory Methods (LM00-LM04) - Theory & Context
  0: {
    id: 0,
    name: 'Deep Explanation',
    icon: '📖',
    description: 'In-depth explanations with text, images, and multimedia content',
    group: 'A',
    tier: 'basic',
    kiUsage: 'medium',
    form: defineAsyncComponent(() => import('./forms/DeepExplanationForm.vue'))
  },

  1: {
    id: 1,
    name: 'Interactive Theory',
    icon: '🔍',
    description: 'Interactive theory modules with guided discovery and exploration',
    group: 'A',
    tier: 'basic',
    kiUsage: 'medium',
    form: defineAsyncComponent(() => import('./forms/InteractiveTheoryForm.vue'))
  },

  2: {
    id: 2,
    name: 'Visual Storytelling',
    icon: '🎬',
    description: 'Narrative-driven content with visual sequences and animations',
    group: 'A',
    tier: 'premium',
    kiUsage: 'intensive',
    form: defineAsyncComponent(() => import('./forms/VisualStorytellingForm.vue'))
  },

  3: {
    id: 3,
    name: 'Diagram Visualization',
    icon: '📊',
    description: 'Complex concepts explained through diagrams, charts, and visual models',
    group: 'A',
    tier: 'basic',
    kiUsage: 'medium',
    form: defineAsyncComponent(() => import('./forms/DiagramVisualizationForm.vue'))
  },

  4: {
    id: 4,
    name: 'Step-by-Step Guide',
    icon: '👣',
    description: 'Procedural learning with numbered steps and progression',
    group: 'A',
    tier: 'basic',
    kiUsage: 'medium',
    form: defineAsyncComponent(() => import('./forms/StepByStepGuideForm.vue'))
  },

  // GROUP B: Practice Methods (LM05-LM08) - Exercises & Application
  5: {
    id: 5,
    name: 'Fill In The Blanks',
    icon: '✏️',
    description: 'Complete sentences or passages by filling in missing words',
    group: 'B',
    tier: 'basic',
    kiUsage: 'optional',
    form: defineAsyncComponent(() => import('./forms/FillInTheBlanksForm.vue'))
  },

  6: {
    id: 6,
    name: 'Drag and Drop',
    icon: '🎯',
    description: 'Interactive drag-and-drop exercises for categorization and matching',
    group: 'B',
    tier: 'basic',
    kiUsage: 'optional',
    form: defineAsyncComponent(() => import('./forms/DragAndDropForm.vue'))
  },

  7: {
    id: 7,
    name: 'Interactive Simulation',
    icon: '🎮',
    description: 'Interactive simulations for real-world problem-solving practice',
    group: 'B',
    tier: 'premium',
    kiUsage: 'intensive',
    form: null // Not yet implemented
  },

  8: {
    id: 8,
    name: 'Multiple Choice Quiz',
    icon: '❓',
    description: 'Practice with multiple-choice questions and immediate feedback',
    group: 'B',
    tier: 'basic',
    kiUsage: 'optional',
    form: null // Not yet implemented
  },

  // GROUP C: Assessment Methods (LM09-LM11) - Evaluation & Testing
  9: {
    id: 9,
    name: 'Knowledge Check',
    icon: '✅',
    description: 'Quick knowledge verification through varied question types',
    group: 'C',
    tier: 'basic',
    kiUsage: 'optional',
    form: null // Not yet implemented
  },

  10: {
    id: 10,
    name: 'Essay Exam',
    icon: '📝',
    description: 'Open-ended essay questions for comprehensive assessment',
    group: 'C',
    tier: 'premium',
    kiUsage: 'intensive',
    form: defineAsyncComponent(() => import('./forms/EssayExamForm.vue'))
  },

  11: {
    id: 11,
    name: 'Final Assessment',
    icon: '🏆',
    description: 'Comprehensive final exam assessing all course learning objectives',
    group: 'C',
    tier: 'premium',
    kiUsage: 'intensive',
    form: defineAsyncComponent(() => import('./forms/FinalAssessmentForm.vue'))
  }
}

/**
 * Get learning method configuration by ID
 *
 * @param id - Learning Method ID (0-11)
 * @returns Learning method config or undefined if ID out of range
 */
export function getLearningMethod(id: number): LearningMethodConfig | undefined {
  if (!Number.isInteger(id) || id < 0 || id > 11) {
    return undefined
  }
  return LEARNING_METHOD_REGISTRY[id]
}

/**
 * Get all learning methods in a specific group
 *
 * @param group - Group code ('A', 'B', or 'C')
 * @returns Array of learning methods in group
 */
export function getLearningMethodsByGroup(group: LMGroup): LearningMethodConfig[] {
  return Object.values(LEARNING_METHOD_REGISTRY).filter(lm => lm.group === group)
}

/**
 * Get implemented learning methods (where form component exists)
 *
 * @returns Array of learning methods with implemented form components
 */
export function getImplementedLearningMethods(): LearningMethodConfig[] {
  return Object.values(LEARNING_METHOD_REGISTRY).filter(lm => lm.form !== null)
}

/**
 * Get non-implemented learning methods (where form component is null)
 *
 * @returns Array of learning methods without implemented form components
 */
export function getNotImplementedLearningMethods(): LearningMethodConfig[] {
  return Object.values(LEARNING_METHOD_REGISTRY).filter(lm => lm.form === null)
}

/**
 * Check if a learning method is implemented
 *
 * @param id - Learning Method ID
 * @returns true if implementation exists, false otherwise
 */
export function isLearningMethodImplemented(id: number): boolean {
  const lm = getLearningMethod(id)
  return lm !== undefined && lm.form !== null
}

/**
 * Get form component for learning method
 *
 * @param id - Learning Method ID
 * @returns Lazy-loaded component or null
 */
export function getLearningMethodForm(id: number): Component | null {
  const lm = getLearningMethod(id)
  return lm?.form ?? null
}
