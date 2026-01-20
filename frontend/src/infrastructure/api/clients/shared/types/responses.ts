/**
 * Shared API Response Types
 *
 * Standardized response wrappers used across all API domains.
 * Ensures consistent API response format across entire backend.
 *
 * Usage:
 * import type { ApiResponse, ApiSuccessResponse, ApiErrorResponse } from '@/infrastructure/api/shared'
 */

import type { PaginatedResponse } from './pagination'

/**
 * Standard error information structure.
 *
 * @example
 * const error: ApiError = {
 *   code: 'VALIDATION_ERROR',
 *   message: 'Email is required',
 *   details: {
 *     field: 'email',
 *     reason: 'required'
 *   }
 * }
 */
export interface ApiError {
  /** Error code (for i18n and programmatic handling) */
  code: string

  /** Human-readable error message */
  message: string

  /** Additional error details */
  details?: Record<string, any>
}

/**
 * Standard metadata about the API response.
 *
 * Attached to responses for context about timing, versioning, etc.
 */
export interface ApiMetadata {
  /** When response was generated (ISO timestamp) */
  timestamp?: string

  /** Request ID for tracing */
  request_id?: string

  /** API version that generated response */
  api_version?: string

  /** Additional metadata */
  [key: string]: any
}

/**
 * Standard success response wrapper.
 *
 * All successful API responses should follow this format.
 *
 * @template T - The type of response data
 *
 * @example
 * const response: ApiSuccessResponse<User> = {
 *   success: true,
 *   data: { id: '123', email: 'user@example.com', ... },
 *   meta: { timestamp: '2026-01-20T12:00:00Z' }
 * }
 */
export interface ApiSuccessResponse<T> {
  /** Always true for success responses */
  success: true

  /** Response data (single object) */
  data: T

  /** Optional metadata about response */
  meta?: ApiMetadata
}

/**
 * Standard error response wrapper.
 *
 * All error API responses should follow this format.
 *
 * @example
 * const response: ApiErrorResponse = {
 *   success: false,
 *   error: {
 *     code: 'NOT_FOUND',
 *     message: 'User not found',
 *     details: { user_id: '123' }
 *   }
 * }
 */
export interface ApiErrorResponse {
  /** Always false for error responses */
  success: false

  /** Error information */
  error: ApiError
}

/**
 * Union type for any API response (success or error).
 *
 * @template T - Type of successful response data
 */
export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse

/**
 * Paginated success response wrapper.
 *
 * Combines pagination metadata with standard success response.
 *
 * @template T - Type of items in paginated list
 *
 * @example
 * const response: ApiPaginatedResponse<User> = {
 *   success: true,
 *   data: {
 *     items: [user1, user2, ...],
 *     total: 150,
 *     page: 1,
 *     limit: 20,
 *     total_pages: 8
 *   },
 *   meta: { timestamp: '...' }
 * }
 */
export interface ApiPaginatedResponse<T> extends ApiSuccessResponse<PaginatedResponse<T>> {
  /** Pagination data in standard format */
  data: PaginatedResponse<T>
}

/**
 * Simple list response wrapper (non-paginated).
 *
 * For endpoints that return a simple array without pagination.
 *
 * @template T - Type of items in list
 *
 * @example
 * const response: ApiListResponse<Tag> = {
 *   success: true,
 *   data: [{ id: '1', name: 'urgent' }, ...],
 *   meta: { count: 25 }
 * }
 */
export interface ApiListResponse<T> extends ApiSuccessResponse<T[]> {
  /** Array of items */
  data: T[]

  /** Metadata (count, etc.) */
  meta?: ApiMetadata & { count?: number }
}

/**
 * Bulk operation response (create/update/delete multiple items).
 *
 * For endpoints that perform operations on multiple items.
 *
 * @template T - Type of items operated on
 *
 * @example
 * const response: ApiBulkResponse<User> = {
 *   success: true,
 *   data: {
 *     created: [user1, user2],
 *     updated: [user3],
 *     failed: [{ item_id: '5', reason: 'duplicate' }]
 *   }
 * }
 */
export interface ApiBulkResponse<T> extends ApiSuccessResponse<ApiBulkResult<T>> {
  /** Bulk operation results */
  data: ApiBulkResult<T>
}

/**
 * Result of a bulk operation.
 *
 * @template T - Type of items in bulk operation
 */
export interface ApiBulkResult<T> {
  /** Successfully created items */
  created?: T[]

  /** Successfully updated items */
  updated?: T[]

  /** Successfully deleted items (may only contain IDs) */
  deleted?: string[]

  /** Items that failed operation */
  failed?: Array<{ item_id?: string; reason: string }>

  /** Summary statistics */
  summary?: {
    total_processed: number
    successful: number
    failed: number
  }
}

/**
 * Async operation response (job creation).
 *
 * For long-running operations that return a job ID for polling.
 *
 * @example
 * const response: ApiJobResponse = {
 *   success: true,
 *   data: {
 *     job_id: 'job-abc123',
 *     status: 'queued',
 *     estimated_completion: '2026-01-20T13:00:00Z'
 *   }
 * }
 */
export interface ApiJobResponse extends ApiSuccessResponse<ApiJob> {
  /** Job information */
  data: ApiJob
}

/**
 * Async job information.
 */
export interface ApiJob {
  /** Unique job ID */
  job_id: string

  /** Job status */
  status: 'queued' | 'processing' | 'completed' | 'failed'

  /** When job was created */
  created_at: string

  /** When job started processing */
  started_at?: string

  /** When job completed */
  completed_at?: string

  /** Estimated completion time */
  estimated_completion?: string

  /** Progress percentage (0-100) */
  progress?: number

  /** Result (when completed) */
  result?: any

  /** Error (if failed) */
  error?: ApiError
}

/**
 * File download response metadata.
 *
 * For endpoints that return file downloads.
 *
 * @example
 * const response: ApiFileResponse = {
 *   success: true,
 *   data: {
 *     file_name: 'export.csv',
 *     file_size: 1024,
 *     mime_type: 'text/csv',
 *     download_url: 'https://...'
 *   }
 * }
 */
export interface ApiFileResponse extends ApiSuccessResponse<ApiFile> {
  /** File download information */
  data: ApiFile
}

/**
 * File download information.
 */
export interface ApiFile {
  /** File name */
  file_name: string

  /** File size in bytes */
  file_size: number

  /** MIME type */
  mime_type: string

  /** Download URL (if not streaming) */
  download_url?: string

  /** File content (base64, if streaming) */
  content?: string

  /** Content encoding */
  encoding?: string
}

/**
 * Check if response is successful.
 *
 * @param response - API response to check
 * @returns true if success response, false otherwise
 *
 * @example
 * if (isSuccessResponse(response)) {
 *   console.log(response.data)
 * }
 */
export function isSuccessResponse<T>(
  response: ApiResponse<T>
): response is ApiSuccessResponse<T> {
  return response.success === true
}

/**
 * Check if response is an error.
 *
 * @param response - API response to check
 * @returns true if error response, false otherwise
 */
export function isErrorResponse(
  response: any
): response is ApiErrorResponse {
  return response.success === false
}

/**
 * Create success response.
 *
 * @template T - Type of response data
 * @param data - Response data
 * @param meta - Optional metadata
 * @returns Success response
 *
 * @example
 * return createSuccessResponse(user, { timestamp: new Date().toISOString() })
 */
export function createSuccessResponse<T>(
  data: T,
  meta?: ApiMetadata
): ApiSuccessResponse<T> {
  return {
    success: true,
    data,
    ...(meta && { meta })
  }
}

/**
 * Create error response.
 *
 * @param code - Error code
 * @param message - Error message
 * @param details - Optional error details
 * @returns Error response
 *
 * @example
 * return createErrorResponse('NOT_FOUND', 'User not found', { user_id: '123' })
 */
export function createErrorResponse(
  code: string,
  message: string,
  details?: Record<string, any>
): ApiErrorResponse {
  return {
    success: false,
    error: {
      code,
      message,
      ...(details && { details })
    }
  }
}
