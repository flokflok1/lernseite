/**
 * ChapterEditor Module Barrel Export
 * Complete chapter editing interface with tabs, composables, and types
 */

// Main component
export { default as ChapterEditor } from './ChapterEditorMain.vue'

// Tab components
export { InfoTab, TheoryTab, VideosTab, MethodsTab, LessonsTab } from './tabs'

// Composables
export {
  useChapterData,
  useLessonManagement,
  useLearningMethodStats,
  useVideoManagement
} from './composables'

// Types
export type {
  ChapterEditorProps,
  ChapterEditorEmits,
  ChapterForm,
  VideoItem,
  MethodGroupStats,
  DragState,
  GroupInfo,
  ChapterEditorState
} from './types'
