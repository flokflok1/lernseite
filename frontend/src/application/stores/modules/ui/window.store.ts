/**
 * Window Store Barrel Export
 *
 * Re-exports panel store with window-compatible naming for backward compatibility.
 * The underlying implementation uses "panel" terminology, but this barrel file
 * provides "window" aliases to support components expecting that terminology.
 */

// Re-export panel store with aliases for backward compatibility
export { usePanelStore as useWindowStore } from '../workspace/panel.store'
export type { LsxPanel as LsxWindow } from '../workspace/panel.store'
export type { PanelType } from '../workspace/panel.store'
export type { OpenPanelParams } from '../workspace/panel.store'
export type { PanelLivePreview } from '../workspace/panel.store'
