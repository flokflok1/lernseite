/**
 * Helper functions for learning method lookups and tier resolution.
 *
 * All functions operate on the static LEARNING_METHODS / ACTIVE_LEARNING_METHODS
 * arrays from learningMethods.data.ts.
 */

import type { LearningMethodGroup, LearningMethod } from './learningMethods.types.js'
import type { LearningMethodCategory } from './learningMethods.js'
import { LEARNING_METHODS, ACTIVE_LEARNING_METHODS } from './learningMethods.data.js'

// ==========================================================================
// Lookup by various keys
// ==========================================================================

export function getLearningMethodsByCategory(category: LearningMethodCategory): LearningMethod[] {
  return ACTIVE_LEARNING_METHODS.filter(m => m.category === category)
}

export function getLearningMethodsByGroup(group: LearningMethodGroup): LearningMethod[] {
  return ACTIVE_LEARNING_METHODS.filter(m => m.group === group)
}

export function getLearningMethodByCode(code: number): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.code === code)
}

export function getActiveLearningMethodByCode(code: number): LearningMethod | undefined {
  return ACTIVE_LEARNING_METHODS.find(m => m.code === code)
}

export function getLearningMethodById(id: string): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.id === id)
}

export function getLearningMethodByPromptKey(promptKey: string): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.promptKey === promptKey)
}

// ==========================================================================
// Tier helpers
// ==========================================================================

/**
 * Tier-Berechnung basierend auf Gruppe (nur Content-LMs).
 *
 * DEPRECATED: Diese Funktion ist ein LOCAL FALLBACK mit hardcodierten Tiers.
 * Fuer echte Tier-Information aus der Datenbank verwende die useGroupTier Composable:
 *
 * @example
 * import { useGroupTier } from '@/application/composables/learning/useGroupTier'
 * const { getTierFromGroup, loadGroups } = useGroupTier()
 * onMounted(async () => await loadGroups())
 */
export function getTierFromGroup(group: LearningMethodGroup): 'basic' | 'premium' | 'enterprise' {
  if (group === 'A' || group === 'B') return 'basic'
  return 'premium'
}

/**
 * Tier basierend auf Learning Method Code ermitteln.
 */
export function getTierFromCode(code: number): 'basic' | 'premium' | 'enterprise' | 'system-feature' {
  const method = getLearningMethodByCode(code)
  if (!method) return 'basic'
  if (!method.active) return 'system-feature'
  return getTierFromGroup(method.group as LearningMethodGroup)
}

// ==========================================================================
// Boolean checks
// ==========================================================================

/** Prueft ob Code eine aktive Content-LM ist */
export function isContentLearningMethod(code: number): boolean {
  const method = getLearningMethodByCode(code)
  return method?.active ?? false
}

/** Prueft ob Code ein System-Feature ist */
export function isSystemFeature(code: number): boolean {
  const method = getLearningMethodByCode(code)
  return method ? !method.active : false
}
