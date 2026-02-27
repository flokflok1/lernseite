/**
 * Shared Course Editor Modules
 *
 * These components are shared between ManualEditor and AIEditor.
 * They provide core editing functionality that both modes require.
 */

export { default as ContentEditor } from './ContentEditor.vue'
export { default as MediaUpload } from './MediaUpload.vue'
export { default as PreviewPanel } from './PreviewPanel.vue'
export { default as StructurePanel } from './StructurePanel.vue'
export { default as ToolbarActions } from './ToolbarActions.vue'
export { default as CreatorCoursesView } from './CreatorCoursesView.vue'
export { default as CourseEditorView } from './CourseEditorView.vue'
export { default as ConfirmBanner } from './ConfirmBanner.vue'
export { useCourseActions } from './composables'
export type { CourseAction } from './composables'
