/**
 * LSX Desktop Panel Manager Store
 *
 * Manages floating panels in the admin desktop environment.
 * Provides multi-panel support with focus, minimize, and drag functionality.
 *
 * Phase: B24-06 - Admin Desktop OS
 * Phase: Admin Desktop - DB-Persisted Panel Sizes
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
// import { getPanelSizes, updatePanelSize as apiUpdatePanelSize } from '@/application/services/api/user'
// TODO: Implement getPanelSizes and updatePanelSize APIs in @/application/services/api/user domain

/**
 * Available panel types
 */
export type PanelType =
  | 'admin-course-create'
  | 'admin-course-editor'
  | 'admin-kapitel-editor'  // Refactored: modules → chapters (2025-11-27)
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
function loadPersistedSizesFromStorage(): Record<string, { width: number; height: number }> {
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
function savePersistedSizesToStorage(sizes: Record<string, { width: number; height: number }>): void {
  try {
    localStorage.setItem(PANEL_SIZES_STORAGE_KEY, JSON.stringify(sizes))
  } catch {
    // Ignore storage errors
  }
}

// Debounce timer for API calls
let saveDebounceTimer: ReturnType<typeof setTimeout> | null = null

export const usePanelStore = defineStore('panel', () => {
  // ============================================================================
  // State
  // ============================================================================

  const panels = ref<LsxPanel[]>([])
  const activePanelId = ref<string | null>(null)
  const baseZIndex = ref(1000)
  const nextZIndex = ref(1000)

  // Persisted sizes by panel type (initially from localStorage as fallback)
  const persistedSizes = ref<Record<string, { width: number; height: number }>>(loadPersistedSizesFromStorage())

  // Flag to track if sizes have been loaded from server
  const sizesLoadedFromServer = ref(false)

  // Offset for cascading new panels
  const cascadeOffset = 30
  let lastPanelPosition = { x: 80, y: 20 }

  // ============================================================================
  // Getters
  // ============================================================================

  /**
   * Get panel by ID
   */
  const getPanelById = computed(() => {
    return (id: string): LsxPanel | undefined => {
      return panels.value.find(p => p.id === id)
    }
  })

  /**
   * Get all panels of a specific type
   */
  const getPanelsByType = computed(() => {
    return (type: PanelType): LsxPanel[] => {
      return panels.value.filter(p => p.type === type)
    }
  })

  /**
   * Get currently active panel
   */
  const activePanel = computed(() => {
    if (!activePanelId.value) return null
    return panels.value.find(p => p.id === activePanelId.value) || null
  })

  /**
   * Get all non-minimized panels sorted by zIndex
   */
  const visiblePanels = computed(() => {
    return panels.value
      .filter(p => !p.minimized)
      .sort((a, b) => a.zIndex - b.zIndex)
  })

  /**
   * Get all minimized panels
   */
  const minimizedPanels = computed(() => {
    return panels.value.filter(p => p.minimized)
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Generate unique panel ID
   */
  function generatePanelId(): string {
    return `panel-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Calculate position for new panel with cascading
   */
  function calculatePosition(preferredPosition?: { x: number; y: number }): { x: number; y: number } {
    if (preferredPosition) {
      return preferredPosition
    }

    // Cascade from last position
    const x = lastPanelPosition.x + cascadeOffset
    const y = lastPanelPosition.y + cascadeOffset

    // Reset if getting too far down/right (keep panels visible)
    if (x > 500 || y > 200) {
      lastPanelPosition = { x: 80, y: 20 }
      return { x: 80, y: 20 }
    }

    lastPanelPosition = { x, y }
    return { x, y }
  }

  /**
   * Open a new panel
   * Returns the panel ID
   */
  function openPanel(params: OpenPanelParams): string {
    const id = generatePanelId()
    const now = new Date().toISOString()
    const position = calculatePosition(params.preferredPosition)

    // Use persisted size if available (has priority), otherwise use provided or default
    const persistedSize = persistedSizes.value[params.type]
    const size = persistedSize || params.size

    const newPanel: LsxPanel = {
      id,
      type: params.type,
      title: params.title,
      icon: params.icon,
      minimized: false,
      maximized: false,
      position,
      size,
      payload: params.payload || {},
      createdAt: now,
      updatedAt: now,
      zIndex: nextZIndex.value++
    }

    panels.value.push(newPanel)
    activePanelId.value = id

    return id
  }

  /**
   * Close a panel
   */
  function closePanel(id: string): void {
    const index = panels.value.findIndex(p => p.id === id)
    if (index === -1) return

    panels.value.splice(index, 1)

    // Update active panel
    if (activePanelId.value === id) {
      // Set focus to highest zIndex panel
      const sortedPanels = [...panels.value].sort((a, b) => b.zIndex - a.zIndex)
      activePanelId.value = sortedPanels[0]?.id || null
    }
  }

  /**
   * Minimize a panel
   */
  function minimizePanel(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.minimized = true
    panel.updatedAt = new Date().toISOString()

    // Clear active if minimizing active panel
    if (activePanelId.value === id) {
      // Find next highest non-minimized panel
      const sortedPanels = [...panels.value]
        .filter(p => !p.minimized && p.id !== id)
        .sort((a, b) => b.zIndex - a.zIndex)
      activePanelId.value = sortedPanels[0]?.id || null
    }
  }

  /**
   * Restore a minimized panel
   */
  function restorePanel(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.minimized = false
    panel.zIndex = nextZIndex.value++
    panel.updatedAt = new Date().toISOString()
    activePanelId.value = id
  }

  /**
   * Focus a panel (bring to front)
   */
  function focusPanel(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    // Don't change focus if already active
    if (activePanelId.value === id && !panel.minimized) return

    // Restore if minimized
    if (panel.minimized) {
      restorePanel(id)
      return
    }

    panel.zIndex = nextZIndex.value++
    panel.updatedAt = new Date().toISOString()
    activePanelId.value = id
  }

  /**
   * Update panel position
   */
  function updatePanelPosition(id: string, position: { x: number; y: number }): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.position = { ...position }
    panel.updatedAt = new Date().toISOString()
  }

  /**
   * Update panel size and persist it (to API with debounce, localStorage as fallback)
   */
  function updatePanelSize(id: string, size: { width: number; height: number }): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    // Apply minimum size constraints
    const minWidth = 400
    const minHeight = 300
    const constrainedSize = {
      width: Math.max(size.width, minWidth),
      height: Math.max(size.height, minHeight)
    }

    panel.size = { ...constrainedSize }
    panel.updatedAt = new Date().toISOString()

    // Update local state
    persistedSizes.value[panel.type] = { ...constrainedSize }

    // Save to localStorage immediately (fallback)
    savePersistedSizesToStorage(persistedSizes.value)

    // Debounced save to API (500ms delay to avoid too many requests while resizing)
    if (saveDebounceTimer) {
      clearTimeout(saveDebounceTimer)
    }
    saveDebounceTimer = setTimeout(async () => {
      try {
        // TODO: Implement updatePanelSize API call in @/application/services/api/user domain
        // await apiUpdatePanelSize(panel.type, constrainedSize.width, constrainedSize.height)
        // For now, localStorage fallback is already saved above
      } catch (error) {
        // Silently fail - localStorage fallback is already in place
        console.warn('[PanelStore] Failed to save panel size to server:', error)
      }
    }, 500)
  }

  /**
   * Load panel sizes from server (call after user login)
   */
  async function loadPanelSizesFromServer(): Promise<void> {
    try {
      // TODO: Implement getPanelSizes API call in @/application/services/api/user domain
      // Stub response for now - using localStorage fallback
      // const serverSizes = await getPanelSizes()
      // if (serverSizes && Object.keys(serverSizes).length > 0) {
      //   // Merge server sizes with local (server takes priority)
      //   persistedSizes.value = { ...persistedSizes.value, ...serverSizes }
      //   // Also update localStorage for offline access
      //   savePersistedSizesToStorage(persistedSizes.value)
      // }
      sizesLoadedFromServer.value = true
    } catch (error) {
      // If API fails (not logged in, etc.), keep using localStorage
      console.warn('[PanelStore] Failed to load panel sizes from server, using localStorage:', error)
      sizesLoadedFromServer.value = false
    }
  }

  /**
   * Update panel payload
   */
  function updatePanelPayload(id: string, payloadPartial: Record<string, unknown>): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.payload = {
      ...panel.payload,
      ...payloadPartial
    }
    panel.updatedAt = new Date().toISOString()
  }

  /**
   * Update panel title
   */
  function updatePanelTitle(id: string, title: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.title = title
    panel.updatedAt = new Date().toISOString()
  }

  /**
   * Update panel live preview data
   */
  function updatePanelLivePreview(id: string, previewData: PanelLivePreview): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    panel.livePreview = {
      ...panel.livePreview,
      ...previewData,
      updatedAt: new Date().toISOString()
    }
    panel.updatedAt = new Date().toISOString()
  }

  /**
   * Toggle minimize/restore
   */
  function toggleMinimize(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    if (panel.minimized) {
      restorePanel(id)
    } else {
      minimizePanel(id)
    }
  }

  /**
   * Toggle maximize/restore
   */
  function toggleMaximize(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    if (panel.maximized) {
      // Restore from maximized state
      if (panel.preMaximizeState) {
        panel.position = { ...panel.preMaximizeState.position }
        panel.size = { ...panel.preMaximizeState.size }
        panel.preMaximizeState = undefined
      }
      panel.maximized = false
    } else {
      // Save current state and maximize
      panel.preMaximizeState = {
        position: { ...panel.position },
        size: panel.size ? { ...panel.size } : { width: 800, height: 600 }
      }
      panel.maximized = true
      // Position will be handled by CSS, but we set logical values
      panel.position = { x: 0, y: 0 }
    }
    panel.updatedAt = new Date().toISOString()
    panel.zIndex = nextZIndex.value++
    activePanelId.value = id
  }

  /**
   * Close all panels
   */
  function closeAllPanels(): void {
    panels.value = []
    activePanelId.value = null
  }

  /**
   * Close all panels of a specific type
   */
  function closePanelsByType(type: PanelType): void {
    const toClose = panels.value.filter(p => p.type === type)
    toClose.forEach(p => closePanel(p.id))
  }

  // ============================================================================
  // Return Store API
  // ============================================================================

  return {
    // State
    panels,
    activePanelId,
    baseZIndex,
    sizesLoadedFromServer,

    // Getters
    getPanelById,
    getPanelsByType,
    activePanel,
    visiblePanels,
    minimizedPanels,

    // Actions
    openPanel,
    closePanel,
    minimizePanel,
    restorePanel,
    focusPanel,
    updatePanelPosition,
    updatePanelSize,
    updatePanelPayload,
    updatePanelTitle,
    updatePanelLivePreview,
    toggleMinimize,
    toggleMaximize,
    closeAllPanels,
    closePanelsByType,
    loadPanelSizesFromServer
  }
})
