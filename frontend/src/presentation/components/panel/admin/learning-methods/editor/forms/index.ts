/**
 * Learning Method Forms (Barrel Export)
 *
 * Forms for editing all 12 Content-Lernmethoden (LM00-LM11).
 *
 * IMPORTANT: Grouping & metadata come from:
 * - learning-methods.registry.ts (SOURCE OF TRUTH)
 * - useGroupTier composable (database-driven groups)
 *
 * Do NOT add grouping logic here - keep as simple exports only.
 */

// Base Form (used by all method types)
export { default as BaseLearningMethodForm } from './BaseLearningMethodForm.vue'

// Individual Form Components (grouped by LM ID in registry, not here)
export { default as DeepExplanationForm } from './DeepExplanationForm.vue'
export { default as InteractiveTheoryForm } from './InteractiveTheoryForm.vue'
export { default as VisualStorytellingForm } from './VisualStorytellingForm.vue'
export { default as DiagramVisualizationForm } from './DiagramVisualizationForm.vue'
export { default as StepByStepGuideForm } from './StepByStepGuideForm.vue'
export { default as FillInTheBlanksForm } from './FillInTheBlanksForm.vue'
export { default as DragAndDropForm } from './DragAndDropForm.vue'
export { default as FlashcardsForm } from './Flashcards.vue'
export { default as ExampleScenarioForm } from './ExampleScenario.vue'
export { default as MultipleChoiceQuizForm } from './MultipleChoiceQuiz.vue'
export { default as TrueFalseForm } from './TrueFalse.vue'
export { default as EssayExamForm } from './EssayExamForm.vue'
export { default as FinalAssessmentForm } from './FinalAssessmentForm.vue'
