/**
 * SessionStorage Cache Strategy
 *
 * Session-based cache using browser's sessionStorage.
 * Data is cleared when tab/window is closed.
 * Useful for temporary session data, form state, etc.
 * Similar behavior to Memory Cache but persists during session.
 */

import type { ICacheService, CacheEntry } from '../CacheService'

export class SessionCache implements ICacheService {
  private prefix = 'lsx:session:'

  /**
   * Get value from sessionStorage
   */
  get<T = any>(key: string): T | null {
    try {
      const entry = this.getRawEntry(key)

      if (!entry) {
        return null
      }

      // Check if expired
      if (entry.expiresAt !== null && Date.now() > entry.expiresAt) {
        this.delete(key)
        return null
      }

      return entry.value as T
    } catch (error) {
      console.error(`[SessionCache] Error getting key ${key}:`, error)
      return null
    }
  }

  /**
   * Set value in sessionStorage
   */
  set(key: string, value: any, ttlSeconds: number = 0): void {
    try {
      const expiresAt = ttlSeconds > 0 ? Date.now() + ttlSeconds * 1000 : null

      const entry: CacheEntry = {
        value,
        expiresAt,
        createdAt: Date.now()
      }

      const serialized = JSON.stringify(entry)
      const storageKey = this.prefix + key

      sessionStorage.setItem(storageKey, serialized)

      if (import.meta.env.DEV) {
        console.debug(`[SessionCache] Set ${key} (${serialized.length} bytes)`)
      }
    } catch (error) {
      console.error(`[SessionCache] Error setting key ${key}:`, error)
    }
  }

  /**
   * Delete value from sessionStorage
   */
  delete(key: string): void {
    try {
      const storageKey = this.prefix + key
      sessionStorage.removeItem(storageKey)
    } catch (error) {
      console.error(`[SessionCache] Error deleting key ${key}:`, error)
    }
  }

  /**
   * Clear all cached values
   */
  clear(): void {
    try {
      const keys = Object.keys(sessionStorage)

      for (const key of keys) {
        if (key.startsWith(this.prefix)) {
          sessionStorage.removeItem(key)
        }
      }

      if (import.meta.env.DEV) {
        console.debug(`[SessionCache] Cleared all entries`)
      }
    } catch (error) {
      console.error('[SessionCache] Error clearing cache:', error)
    }
  }

  /**
   * Check if key exists in sessionStorage
   */
  has(key: string): boolean {
    try {
      const entry = this.getRawEntry(key)

      if (!entry) {
        return false
      }

      // Check if expired
      if (entry.expiresAt !== null && Date.now() > entry.expiresAt) {
        this.delete(key)
        return false
      }

      return true
    } catch (error) {
      console.error(`[SessionCache] Error checking key ${key}:`, error)
      return false
    }
  }

  /**
   * Get all cache keys
   */
  keys(): string[] {
    try {
      const keys: string[] = []
      const storageKeys = Object.keys(sessionStorage)

      for (const storageKey of storageKeys) {
        if (storageKey.startsWith(this.prefix)) {
          const key = storageKey.substring(this.prefix.length)

          // Check if expired
          if (this.has(key)) {
            keys.push(key)
          }
        }
      }

      return keys
    } catch (error) {
      console.error('[SessionCache] Error getting keys:', error)
      return []
    }
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
   * Get raw entry from storage (internal)
   * @private
   */
  private getRawEntry(key: string): CacheEntry | null {
    try {
      const storageKey = this.prefix + key
      const raw = sessionStorage.getItem(storageKey)

      if (!raw) {
        return null
      }

      return JSON.parse(raw) as CacheEntry
    } catch (error) {
      console.error(`[SessionCache] Error parsing key ${key}:`, error)
      return null
    }
  }
}
