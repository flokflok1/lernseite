/**
 * Memory Cache Strategy
 *
 * Fast in-memory cache (not persisted).
 * Useful for session data and temporary caching.
 * Data is lost on page refresh.
 */

import type { ICacheService, CacheEntry } from '../CacheService'

export class MemoryCache implements ICacheService {
  private cache: Map<string, CacheEntry> = new Map()
  private cleanupInterval: NodeJS.Timeout | null = null

  constructor() {
    // Start cleanup interval every 60 seconds
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000)
  }

  /**
   * Get value from memory cache
   */
  get<T = any>(key: string): T | null {
    const entry = this.cache.get(key)

    if (!entry) {
      return null
    }

    // Check if expired
    if (entry.expiresAt !== null && Date.now() > entry.expiresAt) {
      this.cache.delete(key)
      return null
    }

    return entry.value as T
  }

  /**
   * Set value in memory cache
   */
  set(key: string, value: any, ttlSeconds: number = 0): void {
    const expiresAt = ttlSeconds > 0 ? Date.now() + ttlSeconds * 1000 : null

    this.cache.set(key, {
      value,
      expiresAt,
      createdAt: Date.now()
    })
  }

  /**
   * Delete value from memory cache
   */
  delete(key: string): void {
    this.cache.delete(key)
  }

  /**
   * Clear all cached values
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * Check if key exists in memory cache
   */
  has(key: string): boolean {
    const entry = this.cache.get(key)

    if (!entry) {
      return false
    }

    // Check if expired
    if (entry.expiresAt !== null && Date.now() > entry.expiresAt) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  /**
   * Get all cache keys
   */
  keys(): string[] {
    const keys: string[] = []

    for (const [key, entry] of this.cache.entries()) {
      // Check if expired
      if (entry.expiresAt === null || Date.now() <= entry.expiresAt) {
        keys.push(key)
      }
    }

    return keys
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.keys().length
  }

  /**
   * Pop (get and delete)
   */
  pop<T = any>(key: string): T | null {
    const value = this.get<T>(key)
    this.delete(key)
    return value
  }

  /**
   * Clean up expired entries
   * @private
   */
  private cleanup(): void {
    const now = Date.now()
    const keysToDelete: string[] = []

    for (const [key, entry] of this.cache.entries()) {
      if (entry.expiresAt !== null && now > entry.expiresAt) {
        keysToDelete.push(key)
      }
    }

    for (const key of keysToDelete) {
      this.cache.delete(key)
    }

    if (import.meta.env.DEV && keysToDelete.length > 0) {
      console.debug(`[MemoryCache] Cleaned up ${keysToDelete.length} expired entries`)
    }
  }

  /**
   * Stop cleanup interval
   */
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval)
      this.cleanupInterval = null
    }
  }
}
