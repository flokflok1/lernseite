/**
 * LSX Desktop Panel Types & Persistence
 *
 * Type definitions and localStorage persistence helpers for the panel store.
 *
 * Phase: B24-06 - Admin Desktop OS
 * Phase: Admin Desktop - DB-Persisted Panel Sizes
 */

/**
 * Available panel types
 */
export type PanelType =
  | 'admin-course-create'
  | 'admin-course-editor'
  | 'admin-kapitel-editor'  // Refactored: modules -> chapters (2025-11-27)
  | 'admin-kapitel-manager'  // NEW: Kapitel Manager (2025-12-03)
  | 'admin-ai-kapitel-generator'  // NEW: AI Kapitel Generator (2025-11-27)
  | 'admin-ai-editor'  // Phase D4: KI-Authoring-Editor (renamed from Studio 2026-01)
  | 'admin-lesson-editor'
  | 'admin-learning-method-editor'  // Phase D3.4: Learning Methods Editor (19 Content-LMs)
  | 'admin-exam-manager'
  | 'admin-ai-job'
  | 'admin-panel-manager'
  | 'admin-prompt-browser'
  | 'admin-model-selector'
  | 'admin-course-files'  // Phase: Desktop OS - Files Manager
  | 'admin-file-preview'  // Phase D4: File Preview Panel
  | 'admin-lesson-preview'  // Phase D4: Lesson Preview Panel
  | 'admin-chapter-preview'  // Phase D4: Chapter Preview Panel
  | 'admin-system-settings'  // Phase D4: System Settings Panel with Tabs
  | 'admin-user-group-management'  // Phase D4: User & Group Management Panel with Tabs
  | 'admin-kurs-editor-select'  // Phase D4: Kurs-Editor Mode Selector Modal
  // Editor Windows (Course Authoring - /editor route)
  | 'editor-manual'        // Manual Course Editor
  | 'editor-ai-studio'     // AI-Assisted Course Editor
  // Lernmethoden-Formulare (Legacy: 00-31, aktiv: 19 Content-LMs) - Phase D3.5
  | 'learning-method-0-form'
  | 'learning-method-1-form'
  | 'learning-method-2-form'
  | 'learning-method-3-form'
  | 'learning-method-4-form'
  | 'learning-method-5-form'
  | 'learning-method-6-form'
  | 'learning-method-7-form'
  | 'learning-method-8-form'
  | 'learning-method-9-form'
  | 'learning-method-10-form'
  | 'learning-method-11-form'
  | 'learning-method-12-form'
  | 'learning-method-13-form'
  | 'learning-method-14-form'
  | 'learning-method-15-form'
  | 'learning-method-16-form'
  | 'learning-method-17-form'
  | 'learning-method-18-form'
  | 'learning-method-19-form'
  | 'learning-method-20-form'
  | 'learning-method-21-form'
  | 'learning-method-22-form'
  | 'learning-method-23-form'
  | 'learning-method-24-form'
  | 'learning-method-25-form'
  | 'learning-method-26-form'
  | 'learning-method-27-form'
  | 'learning-method-28-form'
  | 'learning-method-29-form'
  | 'learning-method-30-form'
  | 'learning-method-31-form'
  | 'learning-method-32-form'

/**
 * Live preview data for minimized panels
 */
export interface PanelLivePreview {
  progress?: number
  status?: string
  title?: string
  pdfName?: string
  previewChapters?: number
  previewLessons?: number
  updatedAt?: string
}

/**
 * Panel instance definition
 */
export interface LsxPanel {
  id: string
  type: PanelType
  title: string
  icon?: string
  minimized: boolean
  maximized: boolean
  position: { x: number; y: number }
  size?: { width: number; height: number }
  // Store position/size before maximize to restore later
  preMaximizeState?: { position: { x: number; y: number }; size: { width: number; height: number } }
  payload?: Record<string, unknown>
  livePreview?: PanelLivePreview
  createdAt: string
  updatedAt: string
  zIndex: number
}

/**
 * Parameters for opening a new panel
 */
export interface OpenPanelParams {
  type: PanelType
  title: string
  icon?: string
  payload?: Record<string, unknown>
  preferredPosition?: { x: number; y: number }
  size?: { width: number; height: number }
}

// LocalStorage key for persisting panel sizes (fallback if not logged in)
const PANEL_SIZES_STORAGE_KEY = 'lsx-panel-sizes'

/**
 * Load persisted panel sizes from localStorage (fallback)
 */
export function loadPersistedSizesFromStorage(): Record<string, { width: number; height: number }> {
  try {
    const stored = localStorage.getItem(PANEL_SIZES_STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

/**
 * Save panel sizes to localStorage (fallback)
 */
export function savePersistedSizesToStorage(sizes: Record<string, { width: number; height: number }>): void {
  try {
    localStorage.setItem(PANEL_SIZES_STORAGE_KEY, JSON.stringify(sizes))
  } catch {
    // Ignore storage errors
  }
}
