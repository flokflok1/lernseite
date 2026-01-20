/**
 * Application Stores (DDD Application Layer)
 * ==========================================
 * Central barrel export of all Pinia stores organized by domain
 *
 * Structure follows DDD principles:
 * - /core - App-wide state (auth, app)
 * - /admin - Admin panel state
 * - /content - Content management state (courseEditor, player)
 * - /learning - Learning system state (dashboard, tutor)
 * - /ui - UI state (theme, avatar)
 * - /system - System state (gamification)
 * - /feature-flags - Feature flag state
 * - /desktop - Workspace/panel state
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

// Feature flags stores
export * from './modules/feature-flags'

// System stores (gamification)
export * from './modules/system'

// Desktop stores (window workspace system)
export * from './modules/desktop'
