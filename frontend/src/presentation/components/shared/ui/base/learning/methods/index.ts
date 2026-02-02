// Learning Method Components (former base/lessons/)

// Core Lesson Types
export { default as TextLesson } from '../../../../../shared/ui/learning/methods/TextLesson.vue'
export { default as VideoLesson } from '../../../../../shared/ui/learning/methods/VideoLesson.vue'
export { default as AiLesson } from '../../../../../shared/ui/learning/methods/AiLesson.vue'
export { default as OralExplanationLesson } from './OralExplanationLesson.vue'
export { default as WhiteboardTutorLesson } from '../../../../../shared/ui/learning/methods/WhiteboardTutorLesson.vue'

// Quiz Components
export * from './quiz'

// Shared Lesson Components
export { default as MethodExecutionPanel } from '../../../../../shared/ui/learning/methods/MethodExecutionPanel.vue'
export { default as DetailedSteps } from '../../../../../shared/ui/learning/methods/DetailedSteps.vue'
export { default as MathTaskModal } from '../../../../../shared/ui/learning/methods/MathTaskModal.vue'

// Method Execution Sub-Components
export * from './method-execution'
