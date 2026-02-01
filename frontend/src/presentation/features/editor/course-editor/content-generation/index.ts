/**
 * Content Generation Module
 *
 * Provides theory and explanation generation components for course editing.
 * Shared between manual-editor and ai-editor.
 *
 * Exports:
 * - TheoryGenerationContainer - Main component for theory management
 * - useTheoryGeneration - Composable for theory business logic
 * - TheoryGenerationListPanel - Left panel with theory list
 * - TheoryGenerationDetailPanel - Middle panel with detail/creation
 * - TheoryGenerationSettingsPanel - Right panel with settings
 *
 * Types:
 * - ChapterTheory, Concept, Term, TheoryStyle - Domain models
 */

// Components
export { default as TheoryGenerationContainer } from './TheoryGenerationContainer.vue'
export { default as TheoryGenerationListPanel } from './panels/TheoryGenerationListPanel.vue'
export { default as TheoryGenerationDetailPanel } from './panels/TheoryGenerationDetailPanel.vue'
export { default as TheoryGenerationSettingsPanel } from './panels/TheoryGenerationSettingsPanel.vue'

// Composables
export { useTheoryGeneration } from './composables/useTheoryGeneration.ts'

// Types
export type {
  ChapterTheory,
  Chapter,
  Course,
  Concept,
  Term,
  TheoryStyle,
  GenerateTheoryRequest
} from './types/theory.types.ts'
