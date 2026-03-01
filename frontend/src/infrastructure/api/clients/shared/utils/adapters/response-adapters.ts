/**
 * Response Adapters
 *
 * Functions for adapting/transforming API responses to frontend types.
 * Handles paginated, entity, error, and collection response formats.
 *
 * Usage:
 * import {
 *   adaptPaginatedResponse,
 *   adaptEntityResponse,
 *   adaptErrorResponse,
 *   adaptCollectionResponse
 * } from '@/infrastructure/api/shared/utils/response-adapters'
 */

import type { PaginatedResponse, ApiError } from '@/infrastructure/api/clients/shared/types'

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
