/**
 * Lesson Explanation Components
 * ==============================
 * Barrel export for clean imports
 */

// Main Orchestrator
export { default as LessonExplanationView } from './LessonExplanationView.vue'

// Sub-Components
export { default as ExplanationList } from './ExplanationList.vue'
export { default as ExplanationViewer } from './ExplanationViewer.vue'
export { default as ExplanationSettings } from './ExplanationSettings.vue'

// Composables
export { useExplanationManager } from './composables/useExplanationManager'
export type { GenerateOptions } from './composables/useExplanationManager'
