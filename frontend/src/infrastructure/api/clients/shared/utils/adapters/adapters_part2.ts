/**
 * Response Adapters - Part 2
 *
 * Generic mapping and caching/memoization utilities.
 * Split from adapters.ts for G01 compliance (max 500 LOC).
 */

// ============================================
// Generic Mapping
// ============================================

/**
 * Map API response using custom mapper function.
 *
 * @param response - API response
 * @param mapper - Function to transform response
 * @returns Mapped response
 *
 * @example
 * const user = mapApiResponse(response.data, (data) => ({
 *   ...data,
 *   displayName: `${data.firstName} ${data.lastName}`
 * }))
 */
export function mapApiResponse<T, R>(response: T, mapper: (data: T) => R): R {
  return mapper(response)
}

/**
 * Apply multiple transformations to response.
 *
 * @param response - API response
 * @param transformers - Array of transformer functions
 * @returns Transformed response
 */
export function transformResponse<T>(response: T, ...transformers: Array<(data: any) => any>): any {
  let result = response

  for (const transformer of transformers) {
    result = transformer(result)
  }

  return result
}

// ============================================
// Caching & Memoization
// ============================================

/**
 * Create memoized version of adapter function.
 *
 * @param adapter - Adapter function to memoize
 * @param keyGenerator - Function to generate cache key from arguments
 * @returns Memoized adapter function
 */
export function memoizeAdapter<T, R>(
  adapter: (input: T) => R,
  keyGenerator: (input: T) => string = (input) => JSON.stringify(input)
): (input: T) => R {
  const cache = new Map<string, R>()

  return (input: T): R => {
    const key = keyGenerator(input)

    if (cache.has(key)) {
      return cache.get(key)!
    }

    const result = adapter(input)
    cache.set(key, result)

    return result
  }
}

/**
 * Cache adapter results with TTL.
 *
 * @param adapter - Adapter function to cache
 * @param ttlMs - Time to live in milliseconds (default: 5 minutes)
 * @returns Cached adapter function
 */
export function cacheAdapter<T, R>(
  adapter: (input: T) => R,
  ttlMs: number = 5 * 60 * 1000
): (input: T) => R {
  const cache = new Map<string, { result: R; expiry: number }>()

  return (input: T): R => {
    const key = JSON.stringify(input)
    const now = Date.now()

    // Check cache and validity
    if (cache.has(key)) {
      const { result, expiry } = cache.get(key)!

      if (now < expiry) {
        return result
      }

      // Expired, remove from cache
      cache.delete(key)
    }

    // Compute and cache result
    const result = adapter(input)
    cache.set(key, { result, expiry: now + ttlMs })

    return result
  }
}
