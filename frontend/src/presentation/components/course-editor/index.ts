/**
 * Course Editor - Barrel Export
 *
 * Exports all course editor components organized by editor mode.
 */

// Main Components
export { default as CourseEditorMain } from './CourseEditorMain.vue'
export { default as EditorSwitcher } from './EditorSwitcher.vue'

// Manual Editor Components
export { default as ManualEditorContainer } from './manual-editor/ManualEditorContainer.vue'
export { default as ChapterEditor } from './manual-editor/ChapterEditor.vue'
export { default as LessonEditor } from './manual-editor/LessonEditor.vue'

// AI Editor Components
export { default as AIEditorContainer } from './ai-editor/AIEditorContainer.vue'
export { default as ChatInterface } from './ai-editor/ChatInterface.vue'
export { default as PromptBuilder } from './ai-editor/PromptBuilder.vue'
export { default as ContentGenerator } from './ai-editor/ContentGenerator.vue'
export { default as VariantSelector } from './ai-editor/VariantSelector.vue'
export { default as TemplateLibrary } from './ai-editor/TemplateLibrary.vue'
export { default as GenerationHistory } from './ai-editor/GenerationHistory.vue'
export { default as AISettings } from './ai-editor/AISettings.vue'
export { default as AIPreview } from './ai-editor/AIPreview.vue'
