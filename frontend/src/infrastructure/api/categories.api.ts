import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string
  parent_id?: number | null
  level: number
  path: string
  icon?: string
  color?: string
  order_index: number
  is_active: boolean
  course_count?: number
  total_course_count?: number
  children?: Category[]
  created_at?: string
  updated_at?: string
}

export interface CategoryTreeNode extends Category {
  children: CategoryTreeNode[]
}

export interface CategoryTreeResponse {
  categories: CategoryTreeNode[]
  total_categories: number
  max_level: number
  active_categories: number
}

export interface PaginatedCategoryResponse {
  categories: Category[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

// ============================================================================
// Category API Functions
// ============================================================================

/**
 * Get all categories (flat list)
 */
export const getCategories = async (params: {
  active_only?: boolean
  page?: number
  per_page?: number
} = {}): Promise<PaginatedCategoryResponse> => {
  const response = await http.get<{
    success: boolean
    categories: Category[]
    pagination: PaginatedCategoryResponse['pagination']
  }>('/categories', {
    params: {
      active_only: params.active_only ?? false,
      page: params.page ?? 1,
      per_page: params.per_page ?? 100
    }
  })

  return {
    categories: response.data.categories,
    pagination: response.data.pagination
  }
}

/**
 * Get category tree (hierarchical structure)
 */
export const getCategoryTree = async (activeOnly = false): Promise<CategoryTreeResponse> => {
  const response = await http.get<{
    success: boolean
    tree: CategoryTreeResponse
  }>('/categories/tree', {
    params: { active_only: activeOnly }
  })

  return response.data.tree
}

/**
 * Get root categories only (top-level)
 */
export const getRootCategories = async (activeOnly = true): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    categories: Category[]
    total: number
  }>('/categories/roots', {
    params: { active_only: activeOnly }
  })

  return response.data.categories
}

/**
 * Get single category by ID
 */
export const getCategory = async (categoryId: number): Promise<Category> => {
  const response = await http.get<{
    success: boolean
    category: Category
  }>(`/categories/${categoryId}`)

  return response.data.category
}

/**
 * Get category breadcrumb path
 */
export const getCategoryBreadcrumb = async (categoryId: number): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    breadcrumb: Category[]
  }>(`/categories/${categoryId}/breadcrumb`)

  return response.data.breadcrumb
}

/**
 * Search categories by name
 */
export const searchCategories = async (query: string, activeOnly = false): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    categories: Category[]
    total: number
    query: string
  }>('/categories/search', {
    params: { q: query, active_only: activeOnly }
  })

  return response.data.categories
}

/**
 * Get category statistics
 */
export const getCategoryStats = async (): Promise<{
  total_categories: number
  active_categories: number
  level_1_count: number
  level_2_count: number
  level_3_count: number
  level_4_count: number
  level_5_count: number
  max_level: number
}> => {
  const response = await http.get<{
    success: boolean
    stats: {
      total_categories: number
      active_categories: number
      level_1_count: number
      level_2_count: number
      level_3_count: number
      level_4_count: number
      level_5_count: number
      max_level: number
    }
  }>('/categories/stats')

  return response.data.stats
}

/**
 * Get all descendants of a category
 */
export const getCategoryDescendants = async (
  categoryId: number,
  includeSelf = false,
  activeOnly = false
): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    category_id: number
    category_name: string
    category_path: string
    descendants: Category[]
    total: number
  }>(`/categories/${categoryId}/descendants`, {
    params: { include_self: includeSelf, active_only: activeOnly }
  })

  return response.data.descendants
}
