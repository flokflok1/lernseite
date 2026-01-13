/**
 * AI Studio Pro Views - Barrel Export
 * =====================================
 * Clean imports for AI Studio components
 */

// Main View
export { default as AiStudioProWindow } from './AiStudioProWindow.vue'

// Components
export { default as AiStudioHeader } from './components/AiStudioHeader.vue'
export { default as CourseSelector } from './components/CourseSelector.vue'
export { default as NewCourseModal } from './components/NewCourseModal.vue'
export { default as CourseStructureSidebar } from './components/CourseStructureSidebar.vue'

// Composables
export { useAiStudioState } from './composables/useAiStudioState'
export { useCourseManagement } from './composables/useCourseManagement'
export { useChatManagement } from '../composables/useChatManagement'
export { useTabManagement } from '../composables/useTabManagement'

// Types
export type {
  Course,
  Chapter,
  Lesson
} from './composables/useAiStudioState'

export type {
  Category,
  Profile,
  NewCourseData,
  AIAnalysisResult
} from './composables/useCourseManagement'

export type {
  TabConfig
} from '../composables/useTabManagement'
