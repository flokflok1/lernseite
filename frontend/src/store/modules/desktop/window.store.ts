/**
 * LSX Desktop Window Manager Store
 *
 * Manages floating windows in the admin desktop environment.
 * Provides multi-window support with focus, minimize, and drag functionality.
 *
 * Phase: B24-06 - Admin Desktop OS
 * Phase: Admin Desktop - DB-Persisted Window Sizes
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getWindowSizes, updateWindowSize as apiUpdateWindowSize } from '@/api/profile.api'

/**
 * Available window types
 */
export type WindowType =
  | 'admin-course-create'
  | 'admin-course-editor'
  | 'admin-kapitel-editor'  // Refactored: modules → chapters (2025-11-27)
  | 'admin-kapitel-manager'  // NEW: Kapitel Manager (2025-12-03)
  | 'admin-ai-kapitel-generator'  // NEW: AI Kapitel Generator (2025-11-27)
  | 'admin-ai-studio'  // Phase D4: KI-Authoring-Studio (2025-12-02)
  | 'admin-lesson-editor'
  | 'admin-learning-method-editor'  // Phase D3.4: Learning Methods Editor (19 Content-LMs)
  | 'admin-exam-manager'
  | 'admin-ai-job'
  | 'admin-window-manager'
  | 'admin-prompt-browser'
  | 'admin-model-selector'
  | 'admin-course-files'  // Phase: Desktop OS - Files Manager
  | 'admin-file-preview'  // Phase D4: File Preview Window
  | 'admin-lesson-preview'  // Phase D4: Lesson Preview Window
  | 'admin-chapter-preview'  // Phase D4: Chapter Preview Window
  | 'admin-system-settings'  // Phase D4: System Settings Window with Tabs
  | 'admin-user-group-management'  // Phase D4: User & Group Management Window with Tabs
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
 * Live preview data for minimized windows
 */
export interface WindowLivePreview {
  progress?: number
  status?: string
  title?: string
  pdfName?: string
  previewChapters?: number
  previewLessons?: number
  updatedAt?: string
}

/**
 * Window instance definition
 */
export interface LsxWindow {
  id: string
  type: WindowType
  title: string
  icon?: string
  minimized: boolean
  maximized: boolean
  position: { x: number; y: number }
  size?: { width: number; height: number }
  // Store position/size before maximize to restore later
  preMaximizeState?: { position: { x: number; y: number }; size: { width: number; height: number } }
  payload?: Record<string, unknown>
  livePreview?: WindowLivePreview
  createdAt: string
  updatedAt: string
  zIndex: number
}

/**
 * Parameters for opening a new window
 */
export interface OpenWindowParams {
  type: WindowType
  title: string
  icon?: string
  payload?: Record<string, unknown>
  preferredPosition?: { x: number; y: number }
  size?: { width: number; height: number }
}

// LocalStorage key for persisting window sizes (fallback if not logged in)
const WINDOW_SIZES_STORAGE_KEY = 'lsx-window-sizes'

/**
 * Load persisted window sizes from localStorage (fallback)
 */
function loadPersistedSizesFromStorage(): Record<string, { width: number; height: number }> {
  try {
    const stored = localStorage.getItem(WINDOW_SIZES_STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

/**
 * Save window sizes to localStorage (fallback)
 */
function savePersistedSizesToStorage(sizes: Record<string, { width: number; height: number }>): void {
  try {
    localStorage.setItem(WINDOW_SIZES_STORAGE_KEY, JSON.stringify(sizes))
  } catch {
    // Ignore storage errors
  }
}

// Debounce timer for API calls
let saveDebounceTimer: ReturnType<typeof setTimeout> | null = null

export const useWindowStore = defineStore('window', () => {
  // ============================================================================
  // State
  // ============================================================================

  const windows = ref<LsxWindow[]>([])
  const activeWindowId = ref<string | null>(null)
  const baseZIndex = ref(1000)
  const nextZIndex = ref(1000)

  // Persisted sizes by window type (initially from localStorage as fallback)
  const persistedSizes = ref<Record<string, { width: number; height: number }>>(loadPersistedSizesFromStorage())

  // Flag to track if sizes have been loaded from server
  const sizesLoadedFromServer = ref(false)

  // Offset for cascading new windows
  const cascadeOffset = 30
  let lastWindowPosition = { x: 80, y: 20 }

  // ============================================================================
  // Getters
  // ============================================================================

  /**
   * Get window by ID
   */
  const getWindowById = computed(() => {
    return (id: string): LsxWindow | undefined => {
      return windows.value.find(w => w.id === id)
    }
  })

  /**
   * Get all windows of a specific type
   */
  const getWindowsByType = computed(() => {
    return (type: WindowType): LsxWindow[] => {
      return windows.value.filter(w => w.type === type)
    }
  })

  /**
   * Get currently active window
   */
  const activeWindow = computed(() => {
    if (!activeWindowId.value) return null
    return windows.value.find(w => w.id === activeWindowId.value) || null
  })

  /**
   * Get all non-minimized windows sorted by zIndex
   */
  const visibleWindows = computed(() => {
    return windows.value
      .filter(w => !w.minimized)
      .sort((a, b) => a.zIndex - b.zIndex)
  })

  /**
   * Get all minimized windows
   */
  const minimizedWindows = computed(() => {
    return windows.value.filter(w => w.minimized)
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Generate unique window ID
   */
  function generateWindowId(): string {
    return `window-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Calculate position for new window with cascading
   */
  function calculatePosition(preferredPosition?: { x: number; y: number }): { x: number; y: number } {
    if (preferredPosition) {
      return preferredPosition
    }

    // Cascade from last position
    const x = lastWindowPosition.x + cascadeOffset
    const y = lastWindowPosition.y + cascadeOffset

    // Reset if getting too far down/right (keep windows visible)
    if (x > 500 || y > 200) {
      lastWindowPosition = { x: 80, y: 20 }
      return { x: 80, y: 20 }
    }

    lastWindowPosition = { x, y }
    return { x, y }
  }

  /**
   * Open a new window
   * Returns the window ID
   */
  function openWindow(params: OpenWindowParams): string {
    const id = generateWindowId()
    const now = new Date().toISOString()
    const position = calculatePosition(params.preferredPosition)

    // Use persisted size if available (has priority), otherwise use provided or default
    const persistedSize = persistedSizes.value[params.type]
    const size = persistedSize || params.size

    const newWindow: LsxWindow = {
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

    windows.value.push(newWindow)
    activeWindowId.value = id

    return id
  }

  /**
   * Close a window
   */
  function closeWindow(id: string): void {
    const index = windows.value.findIndex(w => w.id === id)
    if (index === -1) return

    windows.value.splice(index, 1)

    // Update active window
    if (activeWindowId.value === id) {
      // Set focus to highest zIndex window
      const sortedWindows = [...windows.value].sort((a, b) => b.zIndex - a.zIndex)
      activeWindowId.value = sortedWindows[0]?.id || null
    }
  }

  /**
   * Minimize a window
   */
  function minimizeWindow(id: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.minimized = true
    window.updatedAt = new Date().toISOString()

    // Clear active if minimizing active window
    if (activeWindowId.value === id) {
      // Find next highest non-minimized window
      const sortedWindows = [...windows.value]
        .filter(w => !w.minimized && w.id !== id)
        .sort((a, b) => b.zIndex - a.zIndex)
      activeWindowId.value = sortedWindows[0]?.id || null
    }
  }

  /**
   * Restore a minimized window
   */
  function restoreWindow(id: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.minimized = false
    window.zIndex = nextZIndex.value++
    window.updatedAt = new Date().toISOString()
    activeWindowId.value = id
  }

  /**
   * Focus a window (bring to front)
   */
  function focusWindow(id: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    // Don't change focus if already active
    if (activeWindowId.value === id && !window.minimized) return

    // Restore if minimized
    if (window.minimized) {
      restoreWindow(id)
      return
    }

    window.zIndex = nextZIndex.value++
    window.updatedAt = new Date().toISOString()
    activeWindowId.value = id
  }

  /**
   * Update window position
   */
  function updateWindowPosition(id: string, position: { x: number; y: number }): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.position = { ...position }
    window.updatedAt = new Date().toISOString()
  }

  /**
   * Update window size and persist it (to API with debounce, localStorage as fallback)
   */
  function updateWindowSize(id: string, size: { width: number; height: number }): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    // Apply minimum size constraints
    const minWidth = 400
    const minHeight = 300
    const constrainedSize = {
      width: Math.max(size.width, minWidth),
      height: Math.max(size.height, minHeight)
    }

    window.size = { ...constrainedSize }
    window.updatedAt = new Date().toISOString()

    // Update local state
    persistedSizes.value[window.type] = { ...constrainedSize }

    // Save to localStorage immediately (fallback)
    savePersistedSizesToStorage(persistedSizes.value)

    // Debounced save to API (500ms delay to avoid too many requests while resizing)
    if (saveDebounceTimer) {
      clearTimeout(saveDebounceTimer)
    }
    saveDebounceTimer = setTimeout(async () => {
      try {
        await apiUpdateWindowSize(window.type, constrainedSize.width, constrainedSize.height)
      } catch (error) {
        // Silently fail - localStorage fallback is already in place
        console.warn('[WindowStore] Failed to save window size to server:', error)
      }
    }, 500)
  }

  /**
   * Load window sizes from server (call after user login)
   */
  async function loadWindowSizesFromServer(): Promise<void> {
    try {
      const serverSizes = await getWindowSizes()
      if (serverSizes && Object.keys(serverSizes).length > 0) {
        // Merge server sizes with local (server takes priority)
        persistedSizes.value = { ...persistedSizes.value, ...serverSizes }
        // Also update localStorage for offline access
        savePersistedSizesToStorage(persistedSizes.value)
      }
      sizesLoadedFromServer.value = true
    } catch (error) {
      // If API fails (not logged in, etc.), keep using localStorage
      console.warn('[WindowStore] Failed to load window sizes from server, using localStorage:', error)
      sizesLoadedFromServer.value = false
    }
  }

  /**
   * Update window payload
   */
  function updateWindowPayload(id: string, payloadPartial: Record<string, unknown>): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.payload = {
      ...window.payload,
      ...payloadPartial
    }
    window.updatedAt = new Date().toISOString()
  }

  /**
   * Update window title
   */
  function updateWindowTitle(id: string, title: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.title = title
    window.updatedAt = new Date().toISOString()
  }

  /**
   * Update window live preview data
   */
  function updateWindowLivePreview(id: string, previewData: WindowLivePreview): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    window.livePreview = {
      ...window.livePreview,
      ...previewData,
      updatedAt: new Date().toISOString()
    }
    window.updatedAt = new Date().toISOString()
  }

  /**
   * Toggle minimize/restore
   */
  function toggleMinimize(id: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    if (window.minimized) {
      restoreWindow(id)
    } else {
      minimizeWindow(id)
    }
  }

  /**
   * Toggle maximize/restore
   */
  function toggleMaximize(id: string): void {
    const window = windows.value.find(w => w.id === id)
    if (!window) return

    if (window.maximized) {
      // Restore from maximized state
      if (window.preMaximizeState) {
        window.position = { ...window.preMaximizeState.position }
        window.size = { ...window.preMaximizeState.size }
        window.preMaximizeState = undefined
      }
      window.maximized = false
    } else {
      // Save current state and maximize
      window.preMaximizeState = {
        position: { ...window.position },
        size: window.size ? { ...window.size } : { width: 800, height: 600 }
      }
      window.maximized = true
      // Position will be handled by CSS, but we set logical values
      window.position = { x: 0, y: 0 }
    }
    window.updatedAt = new Date().toISOString()
    window.zIndex = nextZIndex.value++
    activeWindowId.value = id
  }

  /**
   * Close all windows
   */
  function closeAllWindows(): void {
    windows.value = []
    activeWindowId.value = null
  }

  /**
   * Close all windows of a specific type
   */
  function closeWindowsByType(type: WindowType): void {
    const toClose = windows.value.filter(w => w.type === type)
    toClose.forEach(w => closeWindow(w.id))
  }

  // ============================================================================
  // Return Store API
  // ============================================================================

  return {
    // State
    windows,
    activeWindowId,
    baseZIndex,
    sizesLoadedFromServer,

    // Getters
    getWindowById,
    getWindowsByType,
    activeWindow,
    visibleWindows,
    minimizedWindows,

    // Actions
    openWindow,
    closeWindow,
    minimizeWindow,
    restoreWindow,
    focusWindow,
    updateWindowPosition,
    updateWindowSize,
    updateWindowPayload,
    updateWindowTitle,
    updateWindowLivePreview,
    toggleMinimize,
    toggleMaximize,
    closeAllWindows,
    closeWindowsByType,
    loadWindowSizesFromServer
  }
})
