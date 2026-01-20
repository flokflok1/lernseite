/**
 * Response Adapters & Transformers
 *
 * Centralized functions for adapting/transforming API responses to frontend types.
 * Ensures consistent data transformation across all domains.
 *
 * Usage:
 * import {
 *   adaptPaginatedResponse,
 *   adaptEntityResponse,
 *   flattenNestedArray,
 *   normalizeCollection,
 *   mapApiResponse
 * } from '@/api/shared/utils/adapters'
 *
 * const adapted = adaptPaginatedResponse(apiResponse)
 * const normalized = normalizeCollection(items, 'id')
 */

import type { PaginatedResponse, ApiError } from '@/api/shared/types'

// ============================================
// Response Adaptation
// ============================================

/**
 * Adapt paginated API response to standard format.
 *
 * @param response - API response object
 * @returns Adapted paginated response
 *
 * @example
 * const response = await api.get('/posts')
 * // Raw: { data: [...], total: 100, page: 1, limit: 20 }
 *
 * const adapted = adaptPaginatedResponse(response.data)
 * // Adapted: { data: [...], total: 100, limit: 20, offset: 0 }
 */
export function adaptPaginatedResponse<T>(
  response: Record<string, any>
): PaginatedResponse<T> {
  const data = response.data || response.items || []
  const total = response.total || response.totalItems || data.length
  const limit = response.limit || response.pageSize || response.per_page || 20
  const page = response.page || response.currentPage || 1
  const offset = (page - 1) * limit

  return {
    data: Array.isArray(data) ? data : [data],
    total,
    limit,
    offset
  }
}

/**
 * Adapt single entity response.
 *
 * @param response - API response object
 * @param defaultValue - Default value if response is empty
 * @returns Adapted entity or default value
 *
 * @example
 * const response = await api.get('/users/123')
 * // Raw: { data: { id: '123', name: 'John' } } or { id: '123', name: 'John' }
 *
 * const user = adaptEntityResponse(response.data)
 * // Returns: { id: '123', name: 'John' }
 */
export function adaptEntityResponse<T>(response: Record<string, any>, defaultValue: T | null = null): T | null {
  if (!response) return defaultValue

  // If response has 'data' property, unwrap it
  if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
    return response.data as T
  }

  // Otherwise return as-is
  return response as T
}

/**
 * Adapt error response to standardized format.
 *
 * @param error - Error response from API
 * @returns Standardized error object
 *
 * @example
 * try {
 *   await api.post('/users', userData)
 * } catch (err) {
 *   const apiError = adaptErrorResponse(err.response?.data)
 *   console.error(apiError.code, apiError.message)
 * }
 */
export function adaptErrorResponse(error: any): ApiError {
  if (!error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unknown error occurred'
    }
  }

  // Already structured error
  if (error.code && error.message) {
    return error as ApiError
  }

  // Wrapped error response
  if (error.error && error.error.code) {
    return error.error as ApiError
  }

  // Extract from nested structure
  return {
    code: error.code || error.type || 'ERROR',
    message: error.message || error.error || 'An error occurred',
    details: error.details || error.data
  }
}

/**
 * Adapt collection response to array.
 *
 * @param response - API response object
 * @returns Array of items
 *
 * @example
 * const response = await api.get('/posts')
 * // Raw: { posts: [...] } or { data: [...] } or [...]
 *
 * const posts = adaptCollectionResponse(response.data)
 * // Returns: [...]
 */
export function adaptCollectionResponse<T>(response: any): T[] {
  if (Array.isArray(response)) {
    return response as T[]
  }

  if (!response) {
    return []
  }

  // Try common property names
  const commonFields = ['data', 'items', 'results', 'list', 'records']

  for (const field of commonFields) {
    if (Array.isArray(response[field])) {
      return response[field] as T[]
    }
  }

  // If nothing found, return empty array
  return []
}

// ============================================
// Data Transformation
// ============================================

/**
 * Flatten nested array (one level deep).
 *
 * @param items - Array of items with nested arrays
 * @param nestedField - Field name containing nested items
 * @returns Flattened array
 *
 * @example
 * const posts = [
 *   { id: 1, comments: [{ id: 'c1' }, { id: 'c2' }] },
 *   { id: 2, comments: [{ id: 'c3' }] }
 * ]
 *
 * const allComments = flattenNestedArray(posts, 'comments')
 * // Returns: [{ id: 'c1' }, { id: 'c2' }, { id: 'c3' }]
 */
export function flattenNestedArray<T, N>(
  items: T[],
  nestedField: keyof T
): N[] {
  return items.reduce((flattened: N[], item) => {
    const nested = item[nestedField]

    if (Array.isArray(nested)) {
      return flattened.concat(nested as N[])
    }

    return flattened
  }, [])
}

/**
 * Normalize collection into object indexed by key.
 *
 * @param items - Array of items to normalize
 * @param keyField - Field to use as key (default: 'id')
 * @returns Object with items indexed by key
 *
 * @example
 * const users = [
 *   { id: '1', name: 'Alice' },
 *   { id: '2', name: 'Bob' }
 * ]
 *
 * const normalized = normalizeCollection(users, 'id')
 * // Returns: { '1': { id: '1', name: 'Alice' }, '2': { id: '2', name: 'Bob' } }
 */
export function normalizeCollection<T extends Record<string, any>>(
  items: T[],
  keyField: keyof T = 'id' as keyof T
): Record<string | number, T> {
  return items.reduce((normalized, item) => {
    const key = item[keyField]

    if (key !== undefined && key !== null) {
      normalized[key] = item
    }

    return normalized
  }, {} as Record<string | number, T>)
}

/**
 * Denormalize collection from object to array.
 *
 * @param normalized - Object with items indexed by key
 * @returns Array of items
 *
 * @example
 * const normalized = { '1': { id: '1', name: 'Alice' }, '2': { id: '2', name: 'Bob' } }
 *
 * const items = denormalizeCollection(normalized)
 * // Returns: [{ id: '1', name: 'Alice' }, { id: '2', name: 'Bob' }]
 */
export function denormalizeCollection<T>(normalized: Record<string | number, T>): T[] {
  return Object.values(normalized)
}

/**
 * Group array items by field value.
 *
 * @param items - Array of items to group
 * @param groupField - Field to group by
 * @returns Object with arrays grouped by field value
 *
 * @example
 * const posts = [
 *   { id: 1, status: 'draft' },
 *   { id: 2, status: 'published' },
 *   { id: 3, status: 'draft' }
 * ]
 *
 * const grouped = groupByField(posts, 'status')
 * // Returns: {
 * //   draft: [{ id: 1, status: 'draft' }, { id: 3, status: 'draft' }],
 * //   published: [{ id: 2, status: 'published' }]
 * // }
 */
export function groupByField<T extends Record<string, any>>(
  items: T[],
  groupField: keyof T
): Record<string | number, T[]> {
  return items.reduce((grouped, item) => {
    const key = item[groupField]

    if (key !== undefined && key !== null) {
      if (!grouped[key]) {
        grouped[key] = []
      }

      grouped[key].push(item)
    }

    return grouped
  }, {} as Record<string | number, T[]>)
}

/**
 * Map array with field extraction or transformation.
 *
 * @param items - Array of items
 * @param field - Field to extract or mapping function
 * @returns Array of extracted values or transformed items
 *
 * @example
 * const users = [{ id: '1', name: 'Alice' }, { id: '2', name: 'Bob' }]
 *
 * const names = extractField(users, 'name')
 * // Returns: ['Alice', 'Bob']
 *
 * const display = extractField(users, (user) => `${user.id}: ${user.name}`)
 * // Returns: ['1: Alice', '2: Bob']
 */
export function extractField<T extends Record<string, any>, R>(
  items: T[],
  field: keyof T | ((item: T) => R)
): R[] {
  return items.map((item) => {
    if (typeof field === 'function') {
      return field(item) as R
    }

    return item[field] as R
  })
}

/**
 * Filter items by field value.
 *
 * @param items - Array of items to filter
 * @param field - Field to filter by
 * @param values - Value or array of values to match
 * @returns Filtered array
 *
 * @example
 * const posts = [
 *   { id: 1, status: 'draft' },
 *   { id: 2, status: 'published' }
 * ]
 *
 * const published = filterByField(posts, 'status', 'published')
 * // Returns: [{ id: 2, status: 'published' }]
 *
 * const multiple = filterByField(posts, 'status', ['draft', 'published'])
 * // Returns: all posts
 */
export function filterByField<T extends Record<string, any>>(
  items: T[],
  field: keyof T,
  values: any | any[]
): T[] {
  const valueArray = Array.isArray(values) ? values : [values]

  return items.filter((item) => valueArray.includes(item[field]))
}

/**
 * Merge two arrays by field, keeping items from first array unique.
 *
 * @param items1 - Primary array
 * @param items2 - Secondary array to merge
 * @param keyField - Field to use for uniqueness (default: 'id')
 * @returns Merged array with unique items
 *
 * @example
 * const oldPosts = [{ id: 1, name: 'Post 1' }]
 * const newPosts = [{ id: 2, name: 'Post 2' }]
 *
 * const merged = mergeArraysByKey(oldPosts, newPosts, 'id')
 * // Returns: [{ id: 1, name: 'Post 1' }, { id: 2, name: 'Post 2' }]
 *
 * // With duplicate ID
 * const newPosts2 = [{ id: 1, name: 'Updated Post 1' }]
 * const merged2 = mergeArraysByKey(oldPosts, newPosts2, 'id')
 * // Returns: [{ id: 1, name: 'Post 1' }] (old item kept)
 */
export function mergeArraysByKey<T extends Record<string, any>>(
  items1: T[],
  items2: T[],
  keyField: keyof T = 'id' as keyof T
): T[] {
  const keys = new Set(items1.map((item) => item[keyField]))

  const merged = [...items1]

  for (const item of items2) {
    if (!keys.has(item[keyField])) {
      merged.push(item)
      keys.add(item[keyField])
    }
  }

  return merged
}

/**
 * Sort array by field value.
 *
 * @param items - Array to sort
 * @param field - Field to sort by
 * @param order - Sort order ('asc' or 'desc', default: 'asc')
 * @returns Sorted array
 *
 * @example
 * const users = [
 *   { id: 3, name: 'Charlie' },
 *   { id: 1, name: 'Alice' },
 *   { id: 2, name: 'Bob' }
 * ]
 *
 * const sorted = sortByField(users, 'name', 'asc')
 * // Returns: [{ id: 1, ... }, { id: 2, ... }, { id: 3, ... }]
 *
 * const descending = sortByField(users, 'id', 'desc')
 * // Returns: [{ id: 3, ... }, { id: 2, ... }, { id: 1, ... }]
 */
export function sortByField<T extends Record<string, any>>(
  items: T[],
  field: keyof T,
  order: 'asc' | 'desc' = 'asc'
): T[] {
  const sorted = [...items].sort((a, b) => {
    const valueA = a[field]
    const valueB = b[field]

    if (valueA === valueB) return 0

    const comparison = valueA > valueB ? 1 : -1

    return order === 'asc' ? comparison : -comparison
  })

  return sorted
}

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
 * const response = await api.get('/users/123')
 *
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
 *
 * @example
 * const result = transformResponse(apiData,
 *   (data) => adaptCollectionResponse(data),
 *   (items) => normalizeCollection(items),
 *   (normalized) => denormalizeCollection(normalized)
 * )
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
 *
 * @example
 * const memoizedAdapt = memoizeAdapter(
 *   adaptPaginatedResponse,
 *   (response) => JSON.stringify(response)
 * )
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
 *
 * @example
 * const cachedAdapt = cacheAdapter(adaptPaginatedResponse, 5 * 60 * 1000)
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
