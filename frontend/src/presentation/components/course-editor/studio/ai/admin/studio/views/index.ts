/**
 * AI Editor Views - Barrel Export
 * =====================================
 * Clean imports for AI Editor components
 */

// Main View
export { default as AiEditorPanel } from './AiEditorPanel.vue'

// Components
export { default as AiEditorHeader } from './components/AiEditorHeader.vue'
export { default as CourseSelector } from './components/CourseSelector.vue'
export { default as NewCourseModal } from './components/NewCourseModal.vue'
export { default as CourseStructureSidebar } from './components/CourseStructureSidebar.vue'
export { default as TutorSubNavigation } from './components/TutorSubNavigation.vue'

// Composables
export { useAiEditorState } from './composables/useAiEditorState'
export { useCourseManagement } from './composables/useCourseManagement'
export { useChatManagement } from '../composables/useChatManagement'
export { useTabManagement } from '../composables/useTabManagement'

// Types
export type {
  Course,
  Chapter,
  Lesson
} from './composables/useAiEditorState'

export type {
  Category,
  Profile,
  NewCourseData,
  AIAnalysisResult
} from './composables/useCourseManagement'

export type {
  TabConfig
} from '../composables/useTabManagement'
