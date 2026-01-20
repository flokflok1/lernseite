/**
 * Shared Pagination Types
 *
 * Standardized pagination interfaces used across all API domains.
 * Single source of truth for paginated responses.
 *
 * Usage:
 * import type { PaginatedResponse, PaginationParams } from '@/api/shared'
 */

/**
 * Standard paginated response wrapper.
 *
 * @template T - The type of items in the paginated list
 *
 * @example
 * const response: PaginatedResponse<User> = {
 *   items: [user1, user2, ...],
 *   total: 150,
 *   page: 1,
 *   limit: 20,
 *   total_pages: 8
 * }
 */
export interface StandardPaginatedResponse<T> {
  /** Array of items for current page */
  items: T[]

  /** Total number of items across all pages */
  total: number

  /** Current page number (1-indexed) */
  page: number

  /** Items per page (limit) */
  limit: number

  /** Total number of pages */
  total_pages: number
}

/**
 * Alias for standard paginated response (primary type).
 *
 * Use this type for all new API responses and types.
 */
export type PaginatedResponse<T> = StandardPaginatedResponse<T>

/**
 * Alternative pagination format with has_more flag.
 *
 * Useful for infinite scroll / "load more" patterns.
 *
 * @template T - The type of items in the list
 *
 * @example
 * const response: InfinitePaginatedResponse<Post> = {
 *   items: [...posts],
 *   has_more: true,
 *   cursor: 'next_page_token_xyz'
 * }
 */
export interface InfinitePaginatedResponse<T> {
  /** Array of items for current page */
  items: T[]

  /** Whether more items are available */
  has_more: boolean

  /** Token for fetching next page (optional) */
  cursor?: string
}

/**
 * Cursor-based pagination response.
 *
 * Better for large, frequently-updated datasets (feeds, timelines).
 *
 * @template T - The type of items
 *
 * @example
 * const response: CursorPaginatedResponse<Post> = {
 *   items: [...posts],
 *   next_cursor: 'abc123',
 *   prev_cursor: 'xyz789',
 *   total: 1000  // Optional, may be expensive to calculate
 * }
 */
export interface CursorPaginatedResponse<T> {
  /** Array of items for current page */
  items: T[]

  /** Cursor for next page */
  next_cursor?: string

  /** Cursor for previous page */
  prev_cursor?: string

  /** Total count (optional, may be omitted for performance) */
  total?: number
}

/**
 * Pagination metadata and helper information.
 *
 * Attached to responses for additional pagination context.
 */
export interface PaginationMetadata {
  /** Page number (1-indexed) */
  page: number

  /** Items per page */
  per_page: number

  /** Total items */
  total: number

  /** Total pages */
  total_pages: number

  /** Whether there's a next page */
  has_next: boolean

  /** Whether there's a previous page */
  has_prev: boolean
}

/**
 * Standard pagination request parameters.
 *
 * Use this for paginated API requests across all domains.
 *
 * @example
 * const params: PaginationParams = {
 *   page: 1,
 *   per_page: 20
 * }
 *
 * // In request:
 * api.get('/users', { params })
 */
export interface PaginationParams {
  /** Page number (1-indexed, default: 1) */
  page?: number

  /** Items per page (default: 20, max: 100) */
  per_page?: number

  /** Alias for per_page (for backward compatibility) */
  limit?: number

  /** Alias for page (for backward compatibility) */
  offset?: number
}

/**
 * Sortable pagination parameters.
 *
 * Extends pagination with sort capability.
 *
 * @example
 * const params: SortablePaginationParams = {
 *   page: 1,
 *   per_page: 20,
 *   sort_by: 'created_at',
 *   order: 'desc'
 * }
 */
export interface SortablePaginationParams extends PaginationParams {
  /** Field to sort by */
  sort_by?: string

  /** Sort order: 'asc' or 'desc' */
  order?: 'asc' | 'desc'
}

/**
 * Date range filterable pagination parameters.
 *
 * Extends pagination with date filtering.
 *
 * @example
 * const params: DateFilteredPaginationParams = {
 *   page: 1,
 *   per_page: 20,
 *   from_date: '2026-01-01',
 *   to_date: '2026-12-31'
 * }
 */
export interface DateFilteredPaginationParams extends PaginationParams {
  /** Filter from date (ISO format) */
  from_date?: string

  /** Filter to date (ISO format) */
  to_date?: string
}

/**
 * Searchable pagination parameters.
 *
 * Extends pagination with search capability.
 *
 * @example
 * const params: SearchablePaginationParams = {
 *   page: 1,
 *   per_page: 20,
 *   search: 'user@example.com',
 *   search_fields: ['email', 'name']
 * }
 */
export interface SearchablePaginationParams extends SortablePaginationParams {
  /** Search query string */
  search?: string

  /** Fields to search in */
  search_fields?: string[]
}

/**
 * Calculate offset from page number.
 *
 * @param page - Page number (1-indexed)
 * @param perPage - Items per page
 * @returns Offset value for database queries
 *
 * @example
 * const offset = calculateOffset(2, 20)  // Returns 20 (skip first 20)
 */
export function calculateOffset(page: number, perPage: number): number {
  return (page - 1) * perPage
}

/**
 * Calculate total pages.
 *
 * @param total - Total number of items
 * @param perPage - Items per page
 * @returns Total number of pages
 *
 * @example
 * const pages = calculateTotalPages(150, 20)  // Returns 8 (150/20 = 7.5 → ceil = 8)
 */
export function calculateTotalPages(total: number, perPage: number): number {
  return Math.ceil(total / perPage)
}

/**
 * Create standard paginated response.
 *
 * @template T - Type of items
 * @param items - Array of items
 * @param total - Total number of items
 * @param page - Current page
 * @param limit - Items per page
 * @returns Standard paginated response
 *
 * @example
 * const response = createPaginatedResponse(
 *   users,
 *   totalUsers,
 *   1,
 *   20
 * )
 */
export function createPaginatedResponse<T>(
  items: T[],
  total: number,
  page: number,
  limit: number
): PaginatedResponse<T> {
  return {
    items,
    total,
    page,
    limit,
    total_pages: calculateTotalPages(total, limit)
  }
}
