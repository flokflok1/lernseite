/**
 * Pagination & Cursor Utilities
 *
 * Centralized pagination helpers for cursor-based and offset-based pagination.
 * Supports infinite scroll, batch processing, and pagination state management.
 *
 * Usage:
 * import {
 *   getCursorFromItem,
 *   getNextPageParams,
 *   calculatePageBoundaries,
 *   calculateTotalPages,
 *   isPaginationComplete
 * } from '@/infrastructure/api/shared/utils/pagination'
 *
 * const nextParams = getNextPageParams(currentPage, pageSize)
 * const totalPages = calculateTotalPages(totalItems, pageSize)
 * const isComplete = isPaginationComplete(items.length, pageSize, hasMore)
 */

// ============================================
// Pagination Calculations
// ============================================

/**
 * Calculate pagination parameters for next page.
 *
 * @param currentPage - Current page number (1-indexed)
 * @param pageSize - Items per page
 * @returns { page: number, offset: number, limit: number }
 *
 * @example
 * const { page, offset, limit } = getNextPageParams(1, 20)
 * // Returns: { page: 2, offset: 20, limit: 20 }
 */
export function getNextPageParams(
  currentPage: number,
  pageSize: number
): { page: number; offset: number; limit: number } {
  const nextPage = currentPage + 1
  const offset = currentPage * pageSize

  return {
    page: nextPage,
    offset,
    limit: pageSize
  }
}

/**
 * Calculate pagination parameters for previous page.
 *
 * @param currentPage - Current page number (1-indexed)
 * @param pageSize - Items per page
 * @returns { page: number, offset: number, limit: number }
 *
 * @example
 * const { page, offset, limit } = getPreviousPageParams(2, 20)
 * // Returns: { page: 1, offset: 0, limit: 20 }
 */
export function getPreviousPageParams(
  currentPage: number,
  pageSize: number
): { page: number; offset: number; limit: number } {
  if (currentPage <= 1) {
    return { page: 1, offset: 0, limit: pageSize }
  }

  const previousPage = currentPage - 1
  const offset = (previousPage - 1) * pageSize

  return {
    page: previousPage,
    offset,
    limit: pageSize
  }
}

/**
 * Calculate total pages based on item count and page size.
 *
 * @param totalItems - Total number of items
 * @param pageSize - Items per page
 * @returns Total number of pages
 *
 * @example
 * const totalPages = calculateTotalPages(100, 20)
 * // Returns: 5
 *
 * const totalPages = calculateTotalPages(105, 20)
 * // Returns: 6 (rounded up)
 */
export function calculateTotalPages(totalItems: number, pageSize: number): number {
  if (totalItems === 0) return 1

  return Math.ceil(totalItems / pageSize)
}

/**
 * Calculate page boundaries (first and last item indices on current page).
 *
 * @param currentPage - Current page number (1-indexed)
 * @param pageSize - Items per page
 * @param totalItems - Total number of items (optional)
 * @returns { firstIndex: number, lastIndex: number }
 *
 * @example
 * const { firstIndex, lastIndex } = calculatePageBoundaries(2, 20, 100)
 * // Returns: { firstIndex: 20, lastIndex: 39 }
 *
 * const { firstIndex, lastIndex } = calculatePageBoundaries(1, 20)
 * // Returns: { firstIndex: 0, lastIndex: 19 }
 */
export function calculatePageBoundaries(
  currentPage: number,
  pageSize: number,
  totalItems?: number
): { firstIndex: number; lastIndex: number } {
  const firstIndex = (currentPage - 1) * pageSize
  let lastIndex = firstIndex + pageSize - 1

  if (totalItems !== undefined) {
    lastIndex = Math.min(lastIndex, totalItems - 1)
  }

  return { firstIndex, lastIndex }
}

/**
 * Get current page range display text (e.g., "1-20 of 100").
 *
 * @param currentPage - Current page number (1-indexed)
 * @param pageSize - Items per page
 * @param totalItems - Total number of items
 * @returns Formatted range text
 *
 * @example
 * const rangeText = getPageRangeText(2, 20, 100)
 * // Returns: "21-40 of 100"
 *
 * const rangeText = getPageRangeText(5, 20, 95)
 * // Returns: "81-95 of 95"
 */
export function getPageRangeText(currentPage: number, pageSize: number, totalItems: number): string {
  const { firstIndex, lastIndex } = calculatePageBoundaries(currentPage, pageSize, totalItems)
  const displayFirst = firstIndex + 1
  const displayLast = lastIndex + 1

  return `${displayFirst}-${displayLast} of ${totalItems}`
}

// ============================================
// Cursor-Based Pagination
// ============================================

/**
 * Extract cursor value from item for cursor-based pagination.
 *
 * @param item - Item to extract cursor from
 * @param cursorField - Field name to use as cursor (default: 'id')
 * @returns Cursor string (base64 encoded)
 *
 * @example
 * const cursor = getCursorFromItem({ id: '123', name: 'Item' }, 'id')
 * // Returns: "MTIz" (base64 encoded)
 *
 * const cursor = getCursorFromItem(post, 'createdAt')
 * // Uses 'createdAt' field as cursor for time-based pagination
 */
export function getCursorFromItem<T extends Record<string, any>>(
  item: T,
  cursorField: string = 'id'
): string {
  const cursorValue = item[cursorField]

  if (!cursorValue) {
    throw new Error(`Cursor field "${cursorField}" not found in item`)
  }

  return Buffer.from(String(cursorValue)).toString('base64')
}

/**
 * Decode cursor value.
 *
 * @param cursor - Encoded cursor string
 * @returns Decoded cursor value
 *
 * @example
 * const value = decodeCursor('MTIz')
 * // Returns: "123"
 */
export function decodeCursor(cursor: string): string {
  try {
    return Buffer.from(cursor, 'base64').toString('utf-8')
  } catch {
    return cursor // Return as-is if decoding fails
  }
}

/**
 * Check if pagination is complete (no more items to fetch).
 *
 * @param itemsCount - Number of items in current batch
 * @param pageSize - Expected items per page
 * @param hasMore - Explicit hasMore flag from API (takes precedence)
 * @returns true if pagination is complete
 *
 * @example
 * const isComplete = isPaginationComplete(15, 20)
 * // Returns: true (got fewer items than page size)
 *
 * const isComplete = isPaginationComplete(20, 20, false)
 * // Returns: false (hasMore explicitly false)
 *
 * const isComplete = isPaginationComplete(20, 20, true)
 * // Returns: false (hasMore explicitly true)
 */
export function isPaginationComplete(
  itemsCount: number,
  pageSize: number,
  hasMore?: boolean
): boolean {
  if (hasMore !== undefined) {
    return !hasMore
  }

  return itemsCount < pageSize
}

// ============================================
// Infinite Scroll Helpers
// ============================================

/**
 * Calculate if more items should be fetched based on scroll position.
 *
 * @param containerHeight - Height of scrollable container (px)
 * @param scrollPosition - Current scroll position from top (px)
 * @param contentHeight - Total height of scrollable content (px)
 * @param threshold - Distance from bottom to trigger load (default: 200px)
 * @returns true if should fetch more items
 *
 * @example
 * const shouldFetch = shouldFetchMore(500, 300, 2000, 200)
 * // Returns: true if within 200px of bottom
 */
export function shouldFetchMore(
  containerHeight: number,
  scrollPosition: number,
  contentHeight: number,
  threshold: number = 200
): boolean {
  const distanceFromBottom = contentHeight - (scrollPosition + containerHeight)

  return distanceFromBottom < threshold && contentHeight > containerHeight
}

/**
 * Calculate scroll progress as percentage (0-100).
 *
 * @param scrollPosition - Current scroll position from top (px)
 * @param containerHeight - Height of scrollable container (px)
 * @param contentHeight - Total height of scrollable content (px)
 * @returns Progress percentage (0-100)
 *
 * @example
 * const progress = getScrollProgress(500, 400, 2000)
 * // Returns: 45 (scrolled 45% through content)
 */
export function getScrollProgress(
  scrollPosition: number,
  containerHeight: number,
  contentHeight: number
): number {
  const scrollableHeight = Math.max(contentHeight - containerHeight, 1)
  const progress = (scrollPosition / scrollableHeight) * 100

  return Math.min(Math.round(progress), 100)
}

/**
 * Check if reached end of scrollable content.
 *
 * @param scrollPosition - Current scroll position from top (px)
 * @param containerHeight - Height of scrollable container (px)
 * @param contentHeight - Total height of scrollable content (px)
 * @param tolerance - Tolerance in pixels (default: 10)
 * @returns true if at end of content
 *
 * @example
 * const atEnd = isAtScrollEnd(1500, 400, 1900, 10)
 * // Returns: true (within 10px of end)
 */
export function isAtScrollEnd(
  scrollPosition: number,
  containerHeight: number,
  contentHeight: number,
  tolerance: number = 10
): boolean {
  const distanceFromBottom = contentHeight - (scrollPosition + containerHeight)

  return distanceFromBottom <= tolerance
}

/**
 * Get distance from bottom of scrollable content.
 *
 * @param scrollPosition - Current scroll position from top (px)
 * @param containerHeight - Height of scrollable container (px)
 * @param contentHeight - Total height of scrollable content (px)
 * @returns Distance from bottom in pixels
 *
 * @example
 * const distance = getDistanceFromBottom(500, 400, 2000)
 * // Returns: 1100 (1100px until end)
 */
export function getDistanceFromBottom(
  scrollPosition: number,
  containerHeight: number,
  contentHeight: number
): number {
  return Math.max(0, contentHeight - (scrollPosition + containerHeight))
}

// ============================================
// Batch Processing
// ============================================

/**
 * Split array into batches of specified size.
 *
 * @param items - Array of items to batch
 * @param batchSize - Size of each batch
 * @returns Array of batches
 *
 * @example
 * const batches = batchArray([1, 2, 3, 4, 5], 2)
 * // Returns: [[1, 2], [3, 4], [5]]
 */
export function batchArray<T>(items: T[], batchSize: number): T[][] {
  if (batchSize <= 0) {
    throw new Error('Batch size must be greater than 0')
  }

  const batches: T[][] = []

  for (let i = 0; i < items.length; i += batchSize) {
    batches.push(items.slice(i, i + batchSize))
  }

  return batches
}

/**
 * Process array in batches with async function.
 *
 * @param items - Array of items to process
 * @param batchSize - Size of each batch
 * @param processor - Async function to process each batch
 * @param onProgress - Optional callback for progress tracking
 * @returns Array of results
 *
 * @example
 * const results = await processBatchesAsync(
 *   [1, 2, 3, 4, 5],
 *   2,
 *   async (batch) => {
 *     const response = await api.processItems(batch)
 *     return response.data
 *   },
 *   (completed, total) => console.log(`${completed}/${total} batches processed`)
 * )
 */
export async function processBatchesAsync<T, R>(
  items: T[],
  batchSize: number,
  processor: (batch: T[]) => Promise<R>,
  onProgress?: (completed: number, total: number) => void
): Promise<R[]> {
  const batches = batchArray(items, batchSize)
  const results: R[] = []

  for (let i = 0; i < batches.length; i++) {
    const result = await processor(batches[i])
    results.push(result)

    if (onProgress) {
      onProgress(i + 1, batches.length)
    }
  }

  return results
}

// ============================================
// Pagination State
// ============================================

/**
 * Pagination state object.
 *
 * @typedef {Object} PaginationState
 * @property {number} currentPage - Current page (1-indexed)
 * @property {number} pageSize - Items per page
 * @property {number} totalItems - Total number of items
 * @property {number} totalPages - Calculated total pages
 * @property {boolean} isLoading - Loading state
 * @property {boolean} hasMore - More items available
 * @property {Error | null} error - Error if occurred
 */
export interface PaginationState {
  currentPage: number
  pageSize: number
  totalItems: number
  totalPages: number
  isLoading: boolean
  hasMore: boolean
  error: Error | null
}

/**
 * Create initial pagination state.
 *
 * @param pageSize - Items per page (default: 20)
 * @returns Initial pagination state
 *
 * @example
 * const state = createPaginationState(20)
 * // Returns: { currentPage: 1, pageSize: 20, totalItems: 0, ... }
 */
export function createPaginationState(pageSize: number = 20): PaginationState {
  return {
    currentPage: 1,
    pageSize,
    totalItems: 0,
    totalPages: 1,
    isLoading: false,
    hasMore: true,
    error: null
  }
}

/**
 * Update pagination state with new data.
 *
 * @param state - Current pagination state
 * @param data - Update data
 * @returns Updated pagination state
 *
 * @example
 * const updated = updatePaginationState(state, {
 *   totalItems: 100,
 *   hasMore: false,
 *   isLoading: false
 * })
 */
export function updatePaginationState(
  state: PaginationState,
  data: Partial<PaginationState>
): PaginationState {
  const updated = { ...state, ...data }

  // Recalculate totalPages if totalItems changed
  if (data.totalItems !== undefined) {
    updated.totalPages = calculateTotalPages(data.totalItems, state.pageSize)
  }

  return updated
}

/**
 * Reset pagination state to initial.
 *
 * @param state - Current pagination state
 * @returns Reset pagination state
 *
 * @example
 * const reset = resetPaginationState(state)
 */
export function resetPaginationState(state: PaginationState): PaginationState {
  return createPaginationState(state.pageSize)
}

/**
 * Go to specific page in pagination state.
 *
 * @param state - Current pagination state
 * @param page - Page number to go to (1-indexed)
 * @returns Updated pagination state
 *
 * @example
 * const updated = goToPage(state, 3)
 */
export function goToPage(state: PaginationState, page: number): PaginationState {
  const validPage = Math.max(1, Math.min(page, state.totalPages))

  return { ...state, currentPage: validPage }
}

/**
 * Navigate to next page in pagination state.
 *
 * @param state - Current pagination state
 * @returns Updated pagination state (or same if at end)
 *
 * @example
 * const updated = nextPage(state)
 */
export function nextPage(state: PaginationState): PaginationState {
  if (state.currentPage >= state.totalPages) {
    return state
  }

  return { ...state, currentPage: state.currentPage + 1 }
}

/**
 * Navigate to previous page in pagination state.
 *
 * @param state - Current pagination state
 * @returns Updated pagination state (or same if at start)
 *
 * @example
 * const updated = previousPage(state)
 */
export function previousPage(state: PaginationState): PaginationState {
  if (state.currentPage <= 1) {
    return state
  }

  return { ...state, currentPage: state.currentPage - 1 }
}
