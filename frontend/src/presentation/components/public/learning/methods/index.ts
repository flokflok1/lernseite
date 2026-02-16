// Learning Method Components (Barrel Export)

// Core Lesson Types (Method Execution)
export { default as TextLesson } from './TextLesson.vue'
export { default as VideoLesson } from './VideoLesson.vue'
export { default as AiLesson } from './AiLesson.vue'
export { default as OralExplanationLesson } from './OralExplanationLesson.vue'
export { default as WhiteboardTutorLesson } from './WhiteboardTutorLesson.vue'

// Quiz Components
export * from './quiz'

// Shared Lesson Components
export { default as MethodExecutionPanel } from './MethodExecutionPanel.vue'
export { default as DetailedSteps } from './DetailedSteps.vue'
export { default as MathTaskModal } from './MathTaskModal.vue'

// Method Execution Sub-Components
export * from './method-execution'

// 12 Content-Lernmethoden Display Components
// Group A: Erklärend (Explanation/Theory)
export { default as Flashcards } from './Flashcards.vue'
export { default as Lueckentext } from './Lueckentext.vue'
export { default as Freitext } from './Freitext.vue'
export { default as MultipleChoice } from './MultipleChoice.vue'
export { default as TrueFalse } from './TrueFalse.vue'

// Group B: Praxis (Practice/Exercises)
export { default as CodeChallenge } from './CodeChallenge.vue'
export { default as CaseStudy } from './CaseStudy.vue'
export { default as Simulation } from './Simulation.vue'
export { default as PeerReviewExercise } from './PeerReviewExercise.vue'

// Group C: Prüfung (Assessment/Exams)
export { default as ObjectiveAssessment } from './ObjectiveAssessment.vue'
export { default as PracticalExam } from './PracticalExam.vue'
export { default as PortfolioAssessment } from './PortfolioAssessment.vue'
