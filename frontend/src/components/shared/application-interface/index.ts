/**
 * Application Interface - Desktop System
 *
 * Core components for the desktop-style window system.
 * Used by both Admin and User interfaces.
 *
 * @module shared/application-interface
 */

export { default as DesktopLayer } from './DesktopLayer.vue'
export { default as WindowComponent } from './WindowComponent.vue'
export { default as Taskbar } from './Taskbar.vue'
export { default as MiniPreview } from './MiniPreview.vue'

// Legacy exports (for backward compatibility during migration)
export { default as LsxDesktopLayer } from './DesktopLayer.vue'
export { default as LsxDesktopWindow } from './WindowComponent.vue'
export { default as LsxTaskbar } from './Taskbar.vue'
export { default as LsxMiniPreview } from './MiniPreview.vue'
