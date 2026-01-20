/**
 * Cache Service Interface
 *
 * Defines contract for cache implementations.
 * Supports multiple strategies: Memory, LocalStorage, SessionStorage
 */

export interface ICacheService {
  /**
   * Get value from cache
   * @param key - Cache key
   * @returns Cached value or null if not found/expired
   */
  get<T = any>(key: string): T | null

  /**
   * Set value in cache with optional TTL
   * @param key - Cache key
   * @param value - Value to cache
   * @param ttlSeconds - Time to live in seconds (0 = no expiry)
   */
  set(key: string, value: any, ttlSeconds?: number): void

  /**
   * Delete value from cache
   * @param key - Cache key
   */
  delete(key: string): void

  /**
   * Clear all cached values
   */
  clear(): void

  /**
   * Check if key exists in cache
   * @param key - Cache key
   * @returns true if key exists and not expired
   */
  has(key: string): boolean

  /**
   * Get all cache keys
   * @returns Array of all cache keys
   */
  keys(): string[]

  /**
   * Get cache size (number of items)
   * @returns Number of cached items
   */
  size(): number

  /**
   * Get value and delete it from cache (pop operation)
   * @param key - Cache key
   * @returns Cached value or null
   */
  pop<T = any>(key: string): T | null
}

/**
 * Cache Strategy Type
 */
export type CacheStrategy = 'memory' | 'localStorage' | 'sessionStorage'

/**
 * Cache Entry (internal)
 */
export interface CacheEntry {
  value: any
  expiresAt: number | null  // timestamp or null (no expiry)
  createdAt: number
}
