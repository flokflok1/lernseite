/**
 * Window Store Barrel Export
 *
 * Re-exports panel store with window-compatible naming for backward compatibility.
 * The underlying implementation uses "panel" terminology, but this barrel file
 * provides "window" aliases to support components expecting that terminology.
 */

// Re-export panel store with aliases for backward compatibility
export { usePanelStore as useWindowStore } from './modules/desktop/panel.store'
export type { LsxPanel as LsxWindow } from './modules/desktop/panel.store'
export type { PanelType } from './modules/desktop/panel.store'
export type { OpenPanelParams } from './modules/desktop/panel.store'
export type { PanelLivePreview } from './modules/desktop/panel.store'
