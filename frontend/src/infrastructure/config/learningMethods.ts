/**
 * Lernmethoden-Konfiguration -- Barrel Export
 *
 * Aufgeteilt in:
 *  - learningMethods.types.ts   -- TypeScript interfaces & type aliases
 *  - learningMethods.data.ts    -- LEARNING_METHODS array, group constants, code lists
 *  - learningMethods.helpers.ts -- lookup / tier / boolean helper functions
 *
 * Alle bisherigen Imports von '@/infrastructure/config/learningMethods'
 * bleiben unveraendert funktionsfaehig.
 */

// Types
export type {
  LearningMethodGroup,
  LegacyGroup,
  AllGroups,
  LearningMethod
} from './learningMethods.types.js'

// Data (arrays, constants, group metadata)
export {
  LEARNING_METHODS,
  ACTIVE_LEARNING_METHODS,
  LEARNING_METHOD_GROUPS,
  SYSTEM_FEATURE_GROUPS,
  LEARNING_METHOD_CATEGORIES,
  VALID_CONTENT_LM_CODES,
  SYSTEM_FEATURE_CODES
} from './learningMethods.data.js'

// Derive the category key type from the re-exported constant
import type { LEARNING_METHOD_CATEGORIES } from './learningMethods.data.js'
export type LearningMethodCategory = keyof typeof LEARNING_METHOD_CATEGORIES

// Helper functions
export {
  getLearningMethodsByCategory,
  getLearningMethodsByGroup,
  getLearningMethodByCode,
  getActiveLearningMethodByCode,
  getLearningMethodById,
  getLearningMethodByPromptKey,
  getTierFromGroup,
  getTierFromCode,
  isContentLearningMethod,
  isSystemFeature
} from './learningMethods.helpers.js'
