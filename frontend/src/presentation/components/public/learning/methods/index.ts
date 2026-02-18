// Learning Method Components (Barrel Export)

// Core Lesson Types (Method Execution)
export { default as TextLesson } from './TextLesson.vue'
export { default as VideoLesson } from './VideoLesson.vue'
export { default as AiLesson } from './AiLesson.vue'

// Quiz Components
export * from './quiz'

// Shared Lesson Components
export { default as MethodExecutionPanel } from './MethodExecutionPanel.vue'
export { default as DetailedSteps } from './DetailedSteps.vue'
export { default as MathTaskModal } from './MathTaskModal.vue'
export { default as MathTaskSolutionPanel } from './MathTaskSolutionPanel.vue'

// Composables (moved to system-features/math/)
export { useMathTaskChecker } from '@/presentation/components/public/system-features/math/useMathTaskChecker'
export type { TaskData, TaskStep } from '@/presentation/components/public/system-features/math/useMathTaskChecker'

// Method Execution Sub-Components
export * from './method-execution'

// 12 Content-Lernmethoden Display Components
export { default as Flashcards } from './Flashcards.vue'
export { default as Lueckentext } from './Lueckentext.vue'
export { default as Freitext } from './Freitext.vue'
export { default as MultipleChoice } from './MultipleChoice.vue'
export { default as TrueFalse } from './TrueFalse.vue'
export { default as CaseStudy } from './CaseStudy.vue'
export { default as Simulation } from './Simulation.vue'
export { default as ObjectiveAssessment } from './ObjectiveAssessment.vue'

// NOTE: System-Feature components (21 files) moved to
// @/presentation/components/public/system-features/ (Phase 4 Task 17)
