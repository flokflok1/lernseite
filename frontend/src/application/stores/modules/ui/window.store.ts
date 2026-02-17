/**
 * Window Store Alias Wrapper
 *
 * Wraps panel store with window-compatible naming for backward compatibility.
 * The underlying implementation uses "panel" terminology, but this wrapper
 * provides "window" aliases used by DesktopLayer, Taskbar, and other components.
 */

import { usePanelStore } from '../workspace/panel.store'

// Re-export types with window-compatible aliases
export type { LsxPanel as LsxWindow } from '../workspace/panel.store'
export type { PanelType as WindowType } from '../workspace/panel.store'
export type { OpenPanelParams as OpenWindowParams } from '../workspace/panel.store'
export type { PanelLivePreview } from '../workspace/panel.store'

/**
 * Window store composable providing window-named aliases for the panel store.
 * Used by DesktopLayer, Taskbar, PanelLayout, and EditorLayout.
 */
export function useWindowStore() {
  const store = usePanelStore()

  return {
    // Pass through all original store properties
    ...store,

    // Property aliases (used by DesktopLayer + Taskbar)
    get visibleWindows() { return store.visiblePanels },
    get activeWindowId() { return store.activePanelId },

    // Method aliases (used by DesktopLayer handlers)
    openWindow: store.openPanel,
    closeWindow: store.closePanel,
    minimizeWindow: store.minimizePanel,
    restoreWindow: store.restorePanel,
    focusWindow: store.focusPanel,
    updateWindowPosition: store.updatePanelPosition,
    updateWindowSize: store.updatePanelSize,
    loadWindowSizesFromServer: store.loadPanelSizesFromServer,
  }
}
