/**
 * Pagination Utilities - Part 2
 *
 * Batch processing and pagination state management.
 * Split from pagination.ts for G01 compliance (max 500 LOC).
 */

import { calculateTotalPages } from './pagination'

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
 */
export function resetPaginationState(state: PaginationState): PaginationState {
  return createPaginationState(state.pageSize)
}

/**
 * Go to specific page in pagination state.
 */
export function goToPage(state: PaginationState, page: number): PaginationState {
  const validPage = Math.max(1, Math.min(page, state.totalPages))

  return { ...state, currentPage: validPage }
}

/**
 * Navigate to next page in pagination state.
 */
export function nextPage(state: PaginationState): PaginationState {
  if (state.currentPage >= state.totalPages) {
    return state
  }

  return { ...state, currentPage: state.currentPage + 1 }
}

/**
 * Navigate to previous page in pagination state.
 */
export function previousPage(state: PaginationState): PaginationState {
  if (state.currentPage <= 1) {
    return state
  }

  return { ...state, currentPage: state.currentPage - 1 }
}
