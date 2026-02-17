/**
 * API Clients - Barrel Export
 *
 * Consolidated exports for all domain-organized API clients.
 * Structure mirrors backend api/v1/:
 * - panel/admin: Admin operations (users, courses, permissions)
 * - panel/editor: Content authoring (courses, AI editor)
 * - panel/user: User profile, tokens, subscriptions, gamification
 * - public: Setup, i18n (unauthenticated)
 * - learning: Learning player, authoring, editor
 * - shared: Common utilities and types
 * - systemFeatures: 25 system features (10 categories)
 */

export * from './panel/admin'
export * from './panel/editor'
export * from './panel/user'
export * from './public'
export * from './learning'
export * from './shared'
export { systemFeaturesClient } from './systemFeatures.client'
export type * from './systemFeatures.types'
