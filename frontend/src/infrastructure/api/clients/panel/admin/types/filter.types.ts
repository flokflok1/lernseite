/**
 * Admin API - Filter, Pagination & Response Wrapper Types
 *
 * Shared types for filtering, pagination, and API response envelopes.
 */

export interface UsersFilterParams {
  page?: number
  limit?: number
  search?: string
  role?: string
  status?: 'active' | 'inactive'
  organisation_id?: number
}

export interface OrganisationsFilterParams {
  page?: number
  limit?: number
  search?: string
  type?: 'school' | 'company' | 'teacher_team' | 'creator_team'
  status?: 'active' | 'inactive'
}

export interface CoursesFilterParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'all' | 'draft' | 'published' | 'archived'
  creator_id?: number
  organisation_id?: number
  category?: string
  category_id?: number
  level?: string
  language?: string
  sort?: 'created_at' | 'updated_at' | 'title' | 'enrollment_count'
  order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  total_pages?: number
  current_page?: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  meta?: {
    timestamp: string
    [key: string]: unknown
  }
}
