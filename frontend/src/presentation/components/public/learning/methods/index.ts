// Learning Method Components (Barrel Export)

// Core Lesson Types (Method Execution)
export { default as TextLesson } from './explanatory/TextLesson.vue'
export { default as VideoLesson } from './explanatory/VideoLesson.vue'
export { default as AiLesson } from './explanatory/AiLesson.vue'

// Quiz Components
export * from './quiz'

// Shared Lesson Components
export { default as MethodExecutionPanel } from './core/MethodExecutionPanel.vue'
export { default as DetailedSteps } from './explanatory/DetailedSteps.vue'
export { default as MathTaskModal } from './practice/MathTaskModal.vue'
export { default as MathTaskSolutionPanel } from './practice/MathTaskSolutionPanel.vue'

// Composables (moved to application/composables/learning/)
export { useMathTaskChecker } from '@/application/composables/learning/useMathTaskChecker'
export type { TaskData, TaskStep } from '@/application/composables/learning/useMathTaskChecker'

// Method Execution Sub-Components
export * from './method-execution'

// 12 Content-Lernmethoden Display Components
export { default as Flashcards } from './practice/Flashcards.vue'
export { default as Lueckentext } from './practice/Lueckentext.vue'
export { default as Freitext } from './assessment/Freitext.vue'
export { default as MultipleChoice } from './practice/MultipleChoice.vue'
export { default as TrueFalse } from './practice/TrueFalse.vue'
export { default as CaseStudy } from './explanatory/CaseStudy.vue'
export { default as Simulation } from './explanatory/Simulation.vue'
export { default as ObjectiveAssessment } from './assessment/ObjectiveAssessment.vue'

// NOTE: System-Feature components (21 files) moved to
// @/presentation/components/public/system-features/ (Phase 4 Task 17)
