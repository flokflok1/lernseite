/**
 * Shared Filter Parameter Types
 *
 * Standardized filter interfaces for API requests across all domains.
 * Use these as base types for domain-specific filters.
 *
 * Usage:
 * import type {
 *   BaseFilterParams,
 *   SearchableFilterParams,
 *   DateRangeFilterParams
 * } from '@/api/shared'
 */

/**
 * Base filter parameters (pagination + sorting).
 *
 * Extended by more specific filter types.
 * Include in every API list request.
 *
 * @example
 * const filters: BaseFilterParams = {
 *   page: 1,
 *   per_page: 20,
 *   sort_by: 'created_at',
 *   order: 'desc'
 * }
 */
export interface BaseFilterParams {
  /** Page number (1-indexed, default: 1) */
  page?: number

  /** Items per page (default: 20, max: 100) */
  per_page?: number

  /** Field to sort by (default: created_at) */
  sort_by?: string

  /** Sort order: 'asc' or 'desc' (default: desc) */
  order?: 'asc' | 'desc'
}

/**
 * Status filter mixin.
 *
 * Add to filter params for endpoints that support status filtering.
 *
 * @example
 * interface UserFilters extends BaseFilterParams, StatusFilterParams {}
 */
export interface StatusFilterParams {
  /** Filter by status */
  status?: string | string[]

  /** Multiple statuses (OR logic if supported) */
  statuses?: string[]
}

/**
 * Priority filter mixin.
 *
 * Add to filter params for endpoints that support priority filtering.
 */
export interface PriorityFilterParams {
  /** Filter by priority level */
  priority?: string

  /** Minimum priority (if ranged) */
  min_priority?: string

  /** Maximum priority (if ranged) */
  max_priority?: string
}

/**
 * Date range filter mixin.
 *
 * Add to filter params for endpoints that support date filtering.
 *
 * @example
 * interface AuditFilters extends BaseFilterParams, DateRangeFilterParams {}
 *
 * const filters: AuditFilters = {
 *   page: 1,
 *   per_page: 20,
 *   from_date: '2026-01-01',
 *   to_date: '2026-12-31'
 * }
 */
export interface DateRangeFilterParams {
  /** Filter from date (ISO 8601 format) */
  from_date?: string

  /** Filter to date (ISO 8601 format) */
  to_date?: string

  /** Date field to filter on (default: created_at) */
  date_field?: string
}

/**
 * Time range filter with relative dates.
 *
 * Alternative to DateRangeFilterParams for relative time filtering.
 */
export interface RelativeTimeFilterParams {
  /** Relative time filter (e.g., 'last_7_days', 'last_month') */
  time_range?: 'today' | 'yesterday' | 'last_7_days' | 'last_30_days' | 'last_90_days' | 'all_time'

  /** Date field to filter on */
  date_field?: string
}

/**
 * Category/type filter mixin.
 *
 * Add to filter params for endpoints with category filtering.
 */
export interface CategoryFilterParams {
  /** Filter by category ID */
  category_id?: string

  /** Filter by category IDs (multiple) */
  category_ids?: string[]

  /** Category type filter */
  category_type?: string
}

/**
 * Searchable filter mixin.
 *
 * Add to filter params for endpoints with search capability.
 *
 * @example
 * interface UserSearchFilters extends BaseFilterParams, SearchableFilterParams {}
 *
 * const filters: UserSearchFilters = {
 *   page: 1,
 *   per_page: 20,
 *   search: 'john@example.com',
 *   search_fields: ['email', 'name']
 * }
 */
export interface SearchableFilterParams {
  /** Search query string */
  search?: string

  /** Fields to search in (default: all indexed fields) */
  search_fields?: string[]

  /** Exact match search (default: false = fuzzy search) */
  exact_match?: boolean
}

/**
 * User/ownership filter mixin.
 *
 * Add to filter params for endpoints filtering by user/owner.
 */
export interface OwnershipFilterParams {
  /** Filter by creator/owner user ID */
  created_by?: string

  /** Filter by multiple creators */
  created_by_ids?: string[]

  /** Filter by assigned user */
  assigned_to?: string

  /** Filter by multiple assignees */
  assigned_to_ids?: string[]
}

/**
 * Pagination + sorting + status composite.
 *
 * Common combination for moderation, reviews, compliance queues.
 *
 * @example
 * interface QueueFilters extends PaginatedSortableStatusFilters {}
 */
export interface PaginatedSortableStatusFilters
  extends BaseFilterParams,
    StatusFilterParams {}

/**
 * Pagination + sorting + date range composite.
 *
 * Common for audit logs, analytics, reporting endpoints.
 */
export interface PaginatedSortableDateFilters
  extends BaseFilterParams,
    DateRangeFilterParams {}

/**
 * Complete filter composite with all common options.
 *
 * Use for complex list endpoints with multiple filter options.
 */
export interface ComplexFilterParams
  extends BaseFilterParams,
    StatusFilterParams,
    PriorityFilterParams,
    DateRangeFilterParams,
    CategoryFilterParams,
    SearchableFilterParams,
    OwnershipFilterParams {}

/**
 * Compliance/audit log filter parameters.
 *
 * Specialized for compliance and audit log endpoints.
 *
 * @example
 * const filters: ComplianceAuditFilters = {
 *   page: 1,
 *   per_page: 20,
 *   status: 'completed',
 *   from_date: '2026-01-01',
 *   action_type: 'gdpr_export'
 * }
 */
export interface ComplianceAuditFilters
  extends BaseFilterParams,
    DateRangeFilterParams,
    StatusFilterParams {
  /** Filter by action type (gdpr_export, gdpr_delete, etc) */
  action_type?: string

  /** Filter by affected user ID */
  user_id?: string

  /** Filter by initiated by user ID */
  initiated_by?: string
}

/**
 * Moderation queue filter parameters.
 *
 * Specialized for moderation queue endpoints.
 *
 * @example
 * const filters: ModerationQueueFilters = {
 *   page: 1,
 *   per_page: 20,
 *   status: 'pending',
 *   priority: 'high',
 *   content_type: 'post'
 * }
 */
export interface ModerationQueueFilters
  extends BaseFilterParams,
    StatusFilterParams,
    PriorityFilterParams {
  /** Filter by content type */
  content_type?: string

  /** Filter by assigned moderator */
  assigned_to?: string

  /** Filter by reported by user ID */
  reported_by?: string
}

/**
 * Utility to normalize filter parameters.
 *
 * Converts various filter formats to standard format.
 *
 * @param filters - Raw filter params
 * @returns Normalized filters
 *
 * @example
 * const normalized = normalizeFilters({
 *   page: '2',
 *   per_page: '50',
 *   sort_by: 'created_at',
 *   order: 'DESC'  // Will be normalized to 'desc'
 * })
 */
export function normalizeFilters(filters: Record<string, any>): Record<string, any> {
  const normalized: Record<string, any> = {}

  // Normalize numeric fields
  if ('page' in filters && filters.page) {
    normalized.page = Math.max(1, parseInt(String(filters.page), 10)) || 1
  }

  if ('per_page' in filters && filters.per_page) {
    normalized.per_page = Math.min(100, Math.max(1, parseInt(String(filters.per_page), 10))) || 20
  }

  // Copy string fields
  if ('sort_by' in filters && filters.sort_by) {
    normalized.sort_by = filters.sort_by
  }

  // Normalize order
  if ('order' in filters && filters.order) {
    normalized.order = String(filters.order).toLowerCase() === 'asc' ? 'asc' : 'desc'
  }

  // Copy other fields as-is
  Object.keys(filters).forEach(key => {
    if (!['page', 'per_page', 'sort_by', 'order'].includes(key)) {
      normalized[key] = filters[key]
    }
  })

  return normalized
}

/**
 * Check if filters have any active filtering (beyond pagination/sorting).
 *
 * @param filters - Filter params to check
 * @returns true if any non-pagination filters are set
 *
 * @example
 * const hasFilters = hasActiveFilters({ page: 1, status: 'pending' })  // true
 * const hasFilters = hasActiveFilters({ page: 1, per_page: 20 })  // false
 */
export function hasActiveFilters(filters: Record<string, any>): boolean {
  const paginationKeys = ['page', 'per_page', 'sort_by', 'order']
  return Object.keys(filters).some(
    key => !paginationKeys.includes(key) && filters[key] !== undefined && filters[key] !== null && filters[key] !== ''
  )
}

/**
 * Remove pagination-only filters, keeping only actual filters.
 *
 * @param filters - Filter params
 * @returns Filters with pagination removed
 *
 * @example
 * const activeFilters = getActiveFilters({
 *   page: 1,
 *   per_page: 20,
 *   status: 'pending',
 *   priority: 'high'
 * })
 * // Returns: { status: 'pending', priority: 'high' }
 */
export function getActiveFilters(filters: Record<string, any>): Record<string, any> {
  const paginationKeys = ['page', 'per_page', 'sort_by', 'order']
  const active: Record<string, any> = {}

  Object.keys(filters).forEach(key => {
    if (!paginationKeys.includes(key) && filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      active[key] = filters[key]
    }
  })

  return active
}

/**
 * Convert filter params to query string.
 *
 * @param filters - Filter parameters
 * @returns Query string (without leading ?)
 *
 * @example
 * const qs = filtersToQueryString({ page: 1, status: 'pending' })
 * // Returns: 'page=1&status=pending'
 */
export function filtersToQueryString(filters: Record<string, any>): string {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(v => params.append(key, String(v)))
    } else if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })

  return params.toString()
}
