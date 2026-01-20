/**
 * LocalStorage Cache Strategy
 *
 * Persistent cache using browser's localStorage.
 * Data survives page refresh and browser restart.
 * Useful for user preferences, theme settings, etc.
 * Limit: ~5-10MB depending on browser.
 */

import type { ICacheService, CacheEntry } from '../CacheService'

export class LocalStorageCache implements ICacheService {
  private prefix = 'lsx:cache:'
  private readonly maxSize = 5 * 1024 * 1024  // 5MB limit

  /**
   * Get value from localStorage
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
      console.error(`[LocalStorageCache] Error getting key ${key}:`, error)
      return null
    }
  }

  /**
   * Set value in localStorage
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

      // Check size before storing
      const currentSize = this.getStorageSize()
      const newSize = currentSize + serialized.length

      if (newSize > this.maxSize) {
        console.warn(`[LocalStorageCache] Storage quota exceeded, removing old entries`)
        this.cleanup()
      }

      localStorage.setItem(storageKey, serialized)

      if (import.meta.env.DEV) {
        console.debug(`[LocalStorageCache] Set ${key} (${serialized.length} bytes)`)
      }
    } catch (error) {
      console.error(`[LocalStorageCache] Error setting key ${key}:`, error)

      // Storage might be full, try cleanup
      if (error instanceof DOMException && error.code === 22) {
        console.warn(`[LocalStorageCache] Storage full, clearing old entries`)
        this.cleanup()
      }
    }
  }

  /**
   * Delete value from localStorage
   */
  delete(key: string): void {
    try {
      const storageKey = this.prefix + key
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.error(`[LocalStorageCache] Error deleting key ${key}:`, error)
    }
  }

  /**
   * Clear all cached values
   */
  clear(): void {
    try {
      const keys = Object.keys(localStorage)

      for (const key of keys) {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key)
        }
      }

      if (import.meta.env.DEV) {
        console.debug(`[LocalStorageCache] Cleared all entries`)
      }
    } catch (error) {
      console.error('[LocalStorageCache] Error clearing cache:', error)
    }
  }

  /**
   * Check if key exists in localStorage
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
      console.error(`[LocalStorageCache] Error checking key ${key}:`, error)
      return false
    }
  }

  /**
   * Get all cache keys
   */
  keys(): string[] {
    try {
      const keys: string[] = []
      const storageKeys = Object.keys(localStorage)

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
      console.error('[LocalStorageCache] Error getting keys:', error)
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
      const raw = localStorage.getItem(storageKey)

      if (!raw) {
        return null
      }

      return JSON.parse(raw) as CacheEntry
    } catch (error) {
      console.error(`[LocalStorageCache] Error parsing key ${key}:`, error)
      return null
    }
  }

  /**
   * Get total storage size in bytes
   * @private
   */
  private getStorageSize(): number {
    let size = 0

    for (const key in localStorage) {
      if (key.startsWith(this.prefix)) {
        size += localStorage[key].length + key.length
      }
    }

    return size
  }

  /**
   * Clean up expired entries
   * @private
   */
  private cleanup(): void {
    try {
      const now = Date.now()
      const keysToDelete: string[] = []
      const storageKeys = Object.keys(localStorage)

      for (const storageKey of storageKeys) {
        if (storageKey.startsWith(this.prefix)) {
          const key = storageKey.substring(this.prefix.length)
          const entry = this.getRawEntry(key)

          if (entry && entry.expiresAt !== null && now > entry.expiresAt) {
            keysToDelete.push(key)
          }
        }
      }

      for (const key of keysToDelete) {
        this.delete(key)
      }

      if (import.meta.env.DEV && keysToDelete.length > 0) {
        console.debug(`[LocalStorageCache] Cleaned up ${keysToDelete.length} expired entries`)
      }
    } catch (error) {
      console.error('[LocalStorageCache] Error during cleanup:', error)
    }
  }
}
