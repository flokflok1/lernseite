/**
 * Shared Error Handling Utilities
 *
 * Centralized error handling and transformation for API responses.
 * Provides type-safe error parsing, creation, and HTTP status handling.
 *
 * Usage:
 * import {
 *   parseApiError,
 *   createApiError,
 *   getErrorMessage,
 *   isApiError
 * } from '@/api/shared/utils/errors'
 *
 * try {
 *   // API call
 * } catch (err) {
 *   const apiError = parseApiError(err)
 *   console.error(apiError.message)
 * }
 */

import type { ApiError, ApiErrorResponse } from '@/api/shared/types'

// ============================================
// Error Type Guards
// ============================================

/**
 * Check if error is API error response.
 *
 * @param error - Error to check
 * @returns true if error is API error response
 *
 * @example
 * if (isApiError(error)) {
 *   console.log(error.code, error.message)
 * }
 */
export function isApiError(error: unknown): error is ApiError {
  if (typeof error !== 'object' || error === null) return false

  const obj = error as Record<string, unknown>
  return (
    typeof obj.code === 'string' &&
    typeof obj.message === 'string'
  )
}

/**
 * Check if error is API error response object.
 *
 * @param error - Error to check
 * @returns true if error is API error response object
 *
 * @example
 * if (isApiErrorResponse(error)) {
 *   console.log(error.error.code)
 * }
 */
export function isApiErrorResponse(error: unknown): error is ApiErrorResponse {
  if (typeof error !== 'object' || error === null) return false

  const obj = error as Record<string, unknown>
  return (
    obj.success === false &&
    typeof obj.error === 'object' &&
    obj.error !== null &&
    isApiError(obj.error)
  )
}

/**
 * Check if error is HTTP error (status >= 400).
 *
 * @param error - Error to check
 * @returns true if error has status >= 400
 *
 * @example
 * if (isHttpError(error)) {
 *   console.log('HTTP status:', error.status)
 * }
 */
export function isHttpError(
  error: unknown
): error is { status: number; statusText: string; data?: unknown } {
  if (typeof error !== 'object' || error === null) return false

  const obj = error as Record<string, unknown>
  return typeof obj.status === 'number' && obj.status >= 400
}

/**
 * Check if error is validation error.
 *
 * @param error - Error to check
 * @returns true if error is validation error
 *
 * @example
 * if (isValidationError(error)) {
 *   error.details?.forEach(field => console.log(field))
 * }
 */
export function isValidationError(
  error: unknown
): error is ApiError & { details?: Array<{ field: string; message: string }> } {
  return isApiError(error) && error.code === 'VALIDATION_ERROR'
}

// ============================================
// Error Parsing
// ============================================

/**
 * Parse various error formats into standard ApiError.
 *
 * @param error - Error from API, Axios, or JavaScript
 * @returns Standardized ApiError object
 *
 * @example
 * try {
 *   await apiClient.get('/users')
 * } catch (err) {
 *   const apiError = parseApiError(err)
 *   console.log(apiError.code, apiError.message)
 * }
 */
export function parseApiError(error: unknown): ApiError {
  // Already an ApiError
  if (isApiError(error)) {
    return error
  }

  // Axios or HTTP error response
  if (isHttpError(error)) {
    if (isApiErrorResponse(error.data)) {
      return error.data.error
    }

    return {
      code: `HTTP_${error.status}`,
      message: error.statusText || `HTTP Error ${error.status}`,
      details: error.data instanceof Object ? (error.data as Record<string, unknown>) : undefined
    }
  }

  // Error response object with .error property
  if (typeof error === 'object' && error !== null && 'error' in error) {
    const errorProp = (error as Record<string, unknown>).error
    if (isApiError(errorProp)) {
      return errorProp
    }
  }

  // JavaScript Error
  if (error instanceof Error) {
    return {
      code: error.name || 'ERROR',
      message: error.message || 'An error occurred',
      details: {
        stack: error.stack
      }
    }
  }

  // String error message
  if (typeof error === 'string') {
    return {
      code: 'ERROR',
      message: error,
      details: {}
    }
  }

  // Fallback for unknown error
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
    details: {
      originalError: String(error)
    }
  }
}

// ============================================
// Error Creation
// ============================================

/**
 * Create standardized API error object.
 *
 * @param code - Error code (e.g., 'VALIDATION_ERROR', 'NOT_FOUND')
 * @param message - User-friendly error message
 * @param details - Optional error details (validation errors, stack trace, etc.)
 * @returns ApiError object
 *
 * @example
 * throw createApiError('EMAIL_EXISTS', 'This email is already registered')
 * throw createApiError(
 *   'VALIDATION_ERROR',
 *   'Form has errors',
 *   { fields: [{ field: 'email', message: 'Invalid format' }] }
 * )
 */
export function createApiError(
  code: string,
  message: string,
  details?: Record<string, unknown>
): ApiError {
  return {
    code,
    message,
    ...(details && { details })
  }
}

/**
 * Create HTTP error from status code.
 *
 * @param status - HTTP status code
 * @param message - Custom error message (optional)
 * @param data - Response data (optional)
 * @returns ApiError object
 *
 * @example
 * throw createHttpError(404, 'User not found')
 * throw createHttpError(500, 'Server error', { details: '...' })
 */
export function createHttpError(
  status: number,
  message?: string,
  data?: unknown
): ApiError {
  const statusMessages: Record<number, string> = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    409: 'Conflict',
    422: 'Unprocessable Entity',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable'
  }

  return {
    code: `HTTP_${status}`,
    message: message || statusMessages[status] || `HTTP ${status}`,
    ...(data && { details: typeof data === 'object' ? (data as Record<string, unknown>) : { data } })
  }
}

/**
 * Create validation error with field-level details.
 *
 * @param fields - Array of field errors
 * @returns ApiError object with validation details
 *
 * @example
 * throw createValidationError([
 *   { field: 'email', message: 'Invalid email format' },
 *   { field: 'password', message: 'Too short (min 8 characters)' }
 * ])
 */
export function createValidationError(
  fields: Array<{ field: string; message: string; value?: unknown }>
): ApiError {
  return {
    code: 'VALIDATION_ERROR',
    message: 'Validation failed',
    details: {
      fields
    }
  }
}

// ============================================
// Error Message Handling
// ============================================

/**
 * Get user-friendly error message from error.
 *
 * @param error - Error object
 * @param defaultMessage - Fallback message if error can't be parsed
 * @returns User-friendly error message
 *
 * @example
 * try {
 *   await apiCall()
 * } catch (err) {
 *   const message = getErrorMessage(err, 'Something went wrong')
 *   toast.error(message)
 * }
 */
export function getErrorMessage(error: unknown, defaultMessage: string = 'An error occurred'): string {
  const apiError = parseApiError(error)
  return apiError.message || defaultMessage
}

/**
 * Get detailed error description including code and details.
 *
 * @param error - Error object
 * @param includeDetails - Include details in description
 * @returns Detailed error description
 *
 * @example
 * const description = getErrorDescription(error, true)
 * console.log(description)
 * // Output: "VALIDATION_ERROR: Form has errors. Fields: email (required)"
 */
export function getErrorDescription(error: unknown, includeDetails: boolean = false): string {
  const apiError = parseApiError(error)
  let description = `${apiError.code}: ${apiError.message}`

  if (includeDetails && apiError.details) {
    const detailsStr = JSON.stringify(apiError.details, null, 2)
    description += `\n\nDetails:\n${detailsStr}`
  }

  return description
}

/**
 * Get error codes from validation error.
 *
 * @param error - Error object (expected to be validation error)
 * @returns Array of field error codes
 *
 * @example
 * const error = createValidationError([
 *   { field: 'email', message: 'Invalid' }
 * ])
 * getValidationErrorFields(error)  // Returns: [{ field: 'email', message: 'Invalid' }]
 */
export function getValidationErrorFields(
  error: unknown
): Array<{ field: string; message: string; value?: unknown }> {
  const apiError = parseApiError(error)

  if (!isValidationError(apiError) || !apiError.details?.fields) {
    return []
  }

  return apiError.details.fields as Array<{ field: string; message: string; value?: unknown }>
}

/**
 * Get error message for specific field from validation error.
 *
 * @param error - Error object
 * @param field - Field name to get error for
 * @returns Field error message or undefined
 *
 * @example
 * const error = createValidationError([
 *   { field: 'email', message: 'Invalid email' }
 * ])
 * getFieldError(error, 'email')  // Returns: "Invalid email"
 */
export function getFieldError(error: unknown, field: string): string | undefined {
  const fields = getValidationErrorFields(error)
  return fields.find((f) => f.field === field)?.message
}

// ============================================
// HTTP Status Handling
// ============================================

/**
 * Get HTTP status category (4xx, 5xx, etc.).
 *
 * @param status - HTTP status code
 * @returns Status category name
 *
 * @example
 * getStatusCategory(404)  // Returns: "CLIENT_ERROR"
 * getStatusCategory(500)  // Returns: "SERVER_ERROR"
 */
export function getStatusCategory(status: number): string {
  if (status < 200) return 'INFORMATIONAL'
  if (status < 300) return 'SUCCESS'
  if (status < 400) return 'REDIRECT'
  if (status < 500) return 'CLIENT_ERROR'
  return 'SERVER_ERROR'
}

/**
 * Check if HTTP status indicates success.
 *
 * @param status - HTTP status code
 * @returns true if status is 2xx
 *
 * @example
 * isSuccessStatus(200)  // Returns: true
 * isSuccessStatus(404)  // Returns: false
 */
export function isSuccessStatus(status: number): boolean {
  return status >= 200 && status < 300
}

/**
 * Check if HTTP status is client error (4xx).
 *
 * @param status - HTTP status code
 * @returns true if status is 4xx
 *
 * @example
 * isClientError(400)  // Returns: true
 * isClientError(500)  // Returns: false
 */
export function isClientError(status: number): boolean {
  return status >= 400 && status < 500
}

/**
 * Check if HTTP status is server error (5xx).
 *
 * @param status - HTTP status code
 * @returns true if status is 5xx
 *
 * @example
 * isServerError(500)  // Returns: true
 * isServerError(400)  // Returns: false
 */
export function isServerError(status: number): boolean {
  return status >= 500 && status < 600
}

/**
 * Check if error is retryable (5xx or 429).
 *
 * @param status - HTTP status code
 * @returns true if error is retryable
 *
 * @example
 * isRetryableError(500)  // Returns: true (server error)
 * isRetryableError(429)  // Returns: true (rate limit)
 * isRetryableError(404)  // Returns: false (not found)
 */
export function isRetryableError(status: number): boolean {
  return isServerError(status) || status === 429
}

// ============================================
// Error Logging
// ============================================

/**
 * Log error with context for debugging.
 *
 * @param error - Error to log
 * @param context - Additional context (function name, action, etc.)
 * @param level - Log level (default: 'error')
 *
 * @example
 * logError(error, { function: 'fetchUser', userId: 'abc123' })
 */
export function logError(
  error: unknown,
  context?: Record<string, unknown>,
  level: 'error' | 'warn' | 'info' = 'error'
): void {
  const apiError = parseApiError(error)

  const logData = {
    timestamp: new Date().toISOString(),
    code: apiError.code,
    message: apiError.message,
    ...context,
    details: apiError.details
  }

  if (level === 'error') {
    console.error('[API Error]', logData)
  } else if (level === 'warn') {
    console.warn('[API Warning]', logData)
  } else {
    console.info('[API Info]', logData)
  }
}
