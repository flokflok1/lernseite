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

import type { LsxPanel, OpenPanelParams, PanelLivePreview, PanelType } from './panel.types'
import { loadPersistedSizesFromStorage, savePersistedSizesToStorage } from './panel.types'

// Debounce timer for API calls
let saveDebounceTimer: ReturnType<typeof setTimeout> | null = null

export const useDesktopPanelStore = defineStore('desktop-panel', () => {
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
   * Open a new panel.
   * Returns the panel ID.
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
        // TODO: Implement updatePanelSize API call in @/infrastructure/api/clients/panel/user domain
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
      // TODO: Implement getPanelSizes API call in @/infrastructure/api/clients/panel/user domain
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
   * Pop out a panel as an independent browser window.
   * Serializes payload to Base64, opens new window, closes the panel.
   */
  function popoutPanel(id: string): void {
    const panel = panels.value.find(p => p.id === id)
    if (!panel) return

    const payload = { ...panel.payload, title: panel.title }
    const encoded = btoa(JSON.stringify(payload))
    const url = `/panel/popout/${panel.type}?p=${encoded}`

    window.open(url, `lsx-popout-${panel.type}-${Date.now()}`, 'popup')
    closePanel(id)

    // Notify other windows via SharedWorker
    import('@/application/composables/useWindowSync').then(({ sendSync }) => {
      sendSync('action:popout', { windowType: panel.type })
    })
  }

  /**
   * Pop a window back in from a pop-out (called via SharedWorker message).
   */
  function popinPanel(windowType: string, payload: Record<string, unknown>): void {
    const title = (payload.title as string) || windowType
    openPanel({
      type: windowType as PanelType,
      title,
      payload,
    })
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
    loadPanelSizesFromServer,
    popoutPanel,
    popinPanel
  }
})
