/**
 * Explanation Generation Module
 *
 * Provides lesson explanation generation and management components for course editing.
 * Shared between manual-editor and ai-editor.
 *
 * Exports:
 * - ExplanationGenerationContainer - Main component for explanation management
 * - useExplanationGeneration - Composable for explanation business logic
 * - ExplanationListPanel - Left panel with explanation list
 * - ExplanationViewPanel - Middle panel with detail/creation
 * - ExplanationSettingsPanel - Right panel with settings
 *
 * Types:
 * - LessonExplanation, ExplanationStep, ExplanationStyle - Domain models
 */

// Components
export { default as ExplanationGenerationContainer } from './ExplanationGenerationContainer.vue'
export { default as ExplanationListPanel } from './panels/ExplanationListPanel.vue'
export { default as ExplanationViewPanel } from './panels/ExplanationViewPanel.vue'
export { default as ExplanationSettingsPanel } from './panels/ExplanationSettingsPanel.vue'

// Composables
export { useExplanationGeneration } from './composables/useExplanationGeneration.ts'

// Types
export type {
  LessonExplanation,
  Lesson,
  Course,
  ExplanationStep,
  ExplanationStyle,
  WhiteboardData,
  QuizData,
  GenerateExplanationRequest
} from './types/explanation.types.ts'
