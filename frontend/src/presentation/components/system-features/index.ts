// System Features Domain Components
// 25 System-Features for enhanced learning experience
//
// Structure:
// - interactive/       # Interactive Tools (3 features)
// - exam/              # Exam & Assessment (4 features)
// - math/              # Math Toolkit (4 features)
// - gamification/      # Gamification (3 features)
// - collaboration/     # Collaboration (7 features)
// - it_environments/   # IT Environments (3 features)
// - meta/              # Meta Features (1 feature)
// - visualization/     # Visualization (1 feature)
// - learning_paths/    # Learning Paths (1 feature)
// - tutor/             # Tutor & Coaching (existing)

// =============================================================================
// EXISTING COMPONENTS (Root Directory - Legacy Location)
// =============================================================================
// TODO: Move these to category folders in future refactoring

export { default as ChapterCompletionSystem } from './ChapterCompletionSystem.vue'
export { default as ComprehensionChecker } from './ComprehensionChecker.vue'
export { default as IHKExamSystem } from './IHKExamSystem.vue'
export { default as InvertedClassroom } from './InvertedClassroom.vue'
export { default as ITSandbox } from './ITSandbox.vue'
export { default as LearningJournal } from './LearningJournal.vue'
export { default as PeerInstruction } from './PeerInstruction.vue'
export { default as PeerReview } from './PeerReview.vue'
export { default as PracticalExamEngine } from './PracticalExamEngine.vue'
export { default as ProjectBasedLearning } from './ProjectBasedLearning.vue'
export { default as ProjectPortfolio } from './ProjectPortfolio.vue'
export { default as SpeechToText } from './SpeechToText.vue'
export { default as TeamCase } from './TeamCase.vue'
export { default as TimerWrapper } from './TimerWrapper.vue'
export { default as WhiteboardEngine } from './WhiteboardEngine.vue'

// =============================================================================
// CATEGORY EXPORTS (New Structure)
// =============================================================================

// Interactive Tools (3 features)
export * from './interactive'

// Exam & Assessment (4 features)
export * from './exam'

// Math Toolkit (4 features)
export * from './math'

// Gamification (3 features)
export * from './gamification'

// Collaboration (7 features)
export * from './collaboration'

// IT Environments (3 features)
export * from './it_environments'

// Meta Features (1 feature)
export * from './meta'

// Visualization (1 feature)
export * from './visualization'

// Learning Paths (1 feature)
export * from './learning_paths'

// Tutor & Coaching (existing - structured)
export * from './tutor'
