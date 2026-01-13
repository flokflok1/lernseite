/**
 * Store Module Barrel Exports
 * ===========================
 * Central re-export of all Pinia stores organized by domain
 */

// Core stores (auth, app)
export * from './modules/core'

// Admin stores
export * from './modules/admin'

// UI stores (theme, avatar)
export * from './modules/ui'

// Content stores (courseEditor, player)
export * from './modules/content'

// Learning stores (dashboard, tutor)
export * from './modules/learning'

// System stores (gamification)
export * from './modules/system'

// Desktop stores (window workspace system)
export * from './modules/desktop'
