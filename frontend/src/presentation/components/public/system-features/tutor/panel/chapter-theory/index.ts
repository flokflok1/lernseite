/**
 * System Features - Tutor - Admin - Chapter Theory
 * =================================================
 * Admin components for managing chapter theories.
 *
 * ChapterTheoryView is the main orchestrator, composed of:
 * - TheoryListPanel: Left column (theory list)
 * - TheoryDetailPanel: Middle column (create form / detail view)
 * - TheorySettingsPanel: Right column (TTS settings / quick actions)
 */

export { default as ChapterTheoryView } from './ChapterTheoryView.vue'
export { default as TheoryListPanel } from './TheoryListPanel.vue'
export { default as TheoryDetailPanel } from './TheoryDetailPanel.vue'
export { default as TheorySettingsPanel } from './TheorySettingsPanel.vue'
export { useChapterTheoryActions } from './useChapterTheoryActions'
export type * from './chapter-theory.types'
