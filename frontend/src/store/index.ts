/**
 * Store Module Barrel Exports (DEPRECATED)
 * ========================================
 * @deprecated Import directly from @/application/stores/modules/{domain}/
 *
 * This file provides backward compatibility for imports during the DDD migration.
 * Will be removed on 2027-01-20 (12 months from 2026-01-20).
 *
 * Migration timeline:
 * - Until 2026-07-20: ESLint warnings on old imports
 * - Until 2027-01-20: ESLint errors on old imports (still functional)
 * - After 2027-01-20: This barrel will be removed (breaking change)
 */

// Core stores (auth, app)
export * from '@/application/stores/modules/core'

// Admin stores
export * from '@/application/stores/modules/admin'

// UI stores (theme, avatar)
export * from '@/application/stores/modules/ui'

// Content stores (courseEditor, player)
export * from '@/application/stores/modules/content'

// Learning stores (dashboard, tutor)
export * from '@/application/stores/modules/learning'

// Feature flags stores
export * from '@/application/stores/modules/feature-flags'

// System stores (gamification)
export * from '@/application/stores/modules/system'

// Desktop stores (window workspace system)
export * from '@/application/stores/modules/desktop'
