/**
 * Chapter Management Views
 *
 * MIGRATION COMPLETE:
 * - KapitelEditorPanel.vue: DELETED (Redundant)
 * - All chapter editing now goes through: course-editor (with manual + AI modes)
 */

export { default as ChapterPreviewPanel } from './ChapterPreviewPanel.vue'
// KapitelEditorPanel REMOVED - use course-editor instead
export { default as KapitelManagerPanel } from './KapitelManagerPanel.vue'
