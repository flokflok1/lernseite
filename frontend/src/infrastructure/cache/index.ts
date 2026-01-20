/**
 * Cache Layer - Barrel Export
 *
 * Infrastructure Layer: Cache Abstraction
 * ========================================
 *
 * This module provides a unified cache abstraction with multiple strategies:
 * - MemoryCache: Fast, session-only (best for temporary data)
 * - LocalStorageCache: Persistent, survives refresh (best for user preferences)
 * - SessionCache: Session-only, persists during tab lifetime (middle ground)
 *
 * Usage:
 *   import { MemoryCache, CACHE_KEYS, CACHE_TTL } from '@/infrastructure/cache'
 *
 *   const cache = new MemoryCache()
 *   cache.set(CACHE_KEYS.currentUser, user, CACHE_TTL.MEDIUM)
 *   const cachedUser = cache.get(CACHE_KEYS.currentUser)
 */

// Core interfaces
export { ICacheService, CacheStrategy, CacheEntry } from './CacheService'

// Cache strategies (implementations)
export { MemoryCache } from './strategies/MemoryCache'
export { LocalStorageCache } from './strategies/LocalStorageCache'
export { SessionCache } from './strategies/SessionCache'

// Cache keys and constants
export {
  CACHE_KEY_USER_PROFILE,
  CACHE_KEY_CURRENT_USER,
  CACHE_KEY_USER_PERMISSIONS,
  CACHE_KEY_USER_ROLES,
  CACHE_KEY_CURRENT_COURSES,
  CACHE_KEY_COURSE_DETAIL,
  CACHE_KEY_COURSE_CHAPTERS,
  CACHE_KEY_COURSE_LESSONS,
  CACHE_KEY_COURSE_PROGRESS,
  CACHE_KEY_LEARNING_METHODS,
  CACHE_KEY_THEME_PREFERENCE,
  CACHE_KEY_LANGUAGE_PREFERENCE,
  CACHE_KEY_DASHBOARD_DATA,
  CACHE_KEY_FEATURE_FLAGS,
  CACHE_KEY_NOTIFICATIONS,
  CACHE_KEY_SEARCH_RESULTS,
  CACHE_KEY_API_RESPONSE,
  CACHE_KEY_FORM_STATE,
  CACHE_KEY_UPLOAD_STATE,
  CACHE_KEY_TOKEN_REFRESH,
  CACHE_KEYS,
  CACHE_TTL,
} from './keys'
