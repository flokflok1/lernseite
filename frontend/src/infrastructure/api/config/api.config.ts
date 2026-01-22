/**
 * API Configuration
 *
 * Centralized configuration for HTTP client settings.
 * Environment-specific base URLs, timeouts, and headers.
 */

export interface ApiConfig {
  baseURL: string
  timeout: number
  headers: Record<string, string>
  withCredentials: boolean
}

/**
 * Get API configuration based on environment
 */
export function getApiConfig(): ApiConfig {
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  const timeout = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10)

  return {
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Client-Version': import.meta.env.VITE_APP_VERSION || '2.0.0'
    },
    withCredentials: false // JWT in headers, not cookies
  }
}

/**
 * Maximum retry attempts for failed requests
 */
export const MAX_RETRIES = 3

/**
 * Retry delay in milliseconds
 */
export const RETRY_DELAY = 1000

/**
 * HTTP status codes that should trigger retry
 */
export const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504]

/**
 * HTTP methods that can be safely retried
 */
export const RETRYABLE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE']
