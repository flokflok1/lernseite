/**
 * Shared Course Editor Modules
 *
 * These components are shared between ManualEditor and AIEditor.
 * They provide core editing functionality that both modes require.
 */

export { default as ContentEditor } from './panels/ContentEditor.vue'
export { default as MediaUpload } from './ui/MediaUpload.vue'
export { default as PreviewPanel } from './panels/PreviewPanel.vue'
export { default as StructurePanel } from './panels/StructurePanel.vue'
export { default as ToolbarActions } from './ui/ToolbarActions.vue'
export { default as CreatorCoursesView } from './views/CreatorCoursesView.vue'
export { default as CourseEditorView } from './views/CourseEditorView.vue'
export { default as ConfirmBanner } from './ui/ConfirmBanner.vue'
export { useCourseActions } from './composables'
export type { CourseAction } from './composables'
