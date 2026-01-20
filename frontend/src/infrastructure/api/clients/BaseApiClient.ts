/**
 * Base API Client
 *
 * Core HTTP client with built-in interceptors for:
 * - Authentication (JWT injection)
 * - Error handling (global error transformation)
 * - Retry logic (automatic retry for network failures)
 *
 * All API clients extend this base class.
 * Single point of configuration for HTTP behavior.
 */

import axios, { AxiosInstance, AxiosConfig, AxiosError, AxiosResponse } from 'axios'
import { getApiConfig, MAX_RETRIES, RETRY_DELAY, RETRYABLE_STATUS_CODES, RETRYABLE_METHODS } from '../config/api.config'

/**
 * API Error response format
 */
export interface ApiError {
  code: string
  message: string
  field?: string
  details?: Record<string, any>
  status: number
}

/**
 * Success API response format
 */
export interface ApiSuccess<T> {
  success: true
  data: T
  message?: string
}

/**
 * Error API response format
 */
export interface ApiErrorResponse {
  success: false
  error: ApiError
}

/**
 * Unified API response type
 */
export type ApiResponse<T> = ApiSuccess<T> | ApiErrorResponse

export class BaseApiClient {
  protected client: AxiosInstance
  private retryCount: Map<string, number> = new Map()

  constructor() {
    const config = getApiConfig()

    // Create axios instance
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: config.headers,
      withCredentials: config.withCredentials
    })

    // Setup interceptors
    this.setupRequestInterceptors()
    this.setupResponseInterceptors()
  }

  /**
   * Setup request interceptors
   * - Inject JWT token from localStorage
   * - Add request ID for tracing
   * - Log requests in development
   */
  private setupRequestInterceptors(): void {
    this.client.interceptors.request.use(
      (config) => {
        // Inject JWT token from localStorage
        const token = localStorage.getItem('accessToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request ID for tracing
        config.headers['X-Request-ID'] = this.generateRequestId()

        // Log in development
        if (import.meta.env.DEV) {
          console.log(
            `[API Request] ${config.method?.toUpperCase()} ${config.url}`,
            config.data ? { data: config.data } : ''
          )
        }

        return config
      },
      (error) => {
        console.error('[API Request Error]', error)
        return Promise.reject(error)
      }
    )
  }

  /**
   * Setup response interceptors
   * - Global error handling
   * - Automatic retry for network failures
   * - Response logging in development
   */
  private setupResponseInterceptors(): void {
    this.client.interceptors.response.use(
      (response) => {
        // Log successful responses in development
        if (import.meta.env.DEV) {
          console.log(
            `[API Response] ${response.config.url} (${response.status})`,
            response.data
          )
        }

        // Clear retry count on success
        const key = this.getRetryKey(response.config)
        this.retryCount.delete(key)

        return response
      },
      async (error: AxiosError) => {
        return this.handleError(error)
      }
    )
  }

  /**
   * Handle API errors with retry logic
   *
   * Automatically retries failed requests if:
   * - Status code is retryable (408, 429, 500-504)
   * - Request method is idempotent (GET, HEAD, etc.)
   * - Max retries not exceeded
   * - Network error (no response)
   */
  private async handleError(error: AxiosError): Promise<never> {
    const config = error.config

    // Check if request is retryable
    if (config && this.isRetryableRequest(error)) {
      const key = this.getRetryKey(config)
      const retries = (this.retryCount.get(key) || 0) + 1

      if (retries <= MAX_RETRIES) {
        this.retryCount.set(key, retries)

        // Calculate exponential backoff: 1s, 2s, 4s
        const delay = RETRY_DELAY * Math.pow(2, retries - 1)

        if (import.meta.env.DEV) {
          console.warn(
            `[API Retry] Attempt ${retries}/${MAX_RETRIES} after ${delay}ms`,
            { url: config.url, status: error.response?.status }
          )
        }

        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, delay))

        // Retry the request
        return this.client.request(config)
      }
    }

    // Clear retry count on final failure
    if (config) {
      const key = this.getRetryKey(config)
      this.retryCount.delete(key)
    }

    // Handle error response
    return Promise.reject(this.transformError(error))
  }

  /**
   * Check if request is eligible for retry
   */
  private isRetryableRequest(error: AxiosError): boolean {
    const { config, response } = error

    // Network error (no response at all) - always retry
    if (!response) {
      return true
    }

    // Check if status code is retryable
    if (!RETRYABLE_STATUS_CODES.includes(response.status)) {
      return false
    }

    // Check if method is idempotent (safe to retry)
    const method = config?.method?.toUpperCase() || 'GET'
    return RETRYABLE_METHODS.includes(method)
  }

  /**
   * Transform axios error to standardized ApiError
   */
  private transformError(error: AxiosError): Error {
    // Handle network error (no response)
    if (!error.response) {
      const networkError = new Error(
        'Network error. Please check your connection.'
      ) as Error & { code?: string; status?: number }
      networkError.code = 'NETWORK_ERROR'
      networkError.status = 0
      return networkError
    }

    const { status, data } = error.response

    // Handle API error response
    if (typeof data === 'object' && data !== null && 'error' in data) {
      const apiError = (data as ApiErrorResponse).error
      const err = new Error(apiError.message) as Error & ApiError
      err.code = apiError.code
      err.field = apiError.field
      err.details = apiError.details
      err.status = status
      return err
    }

    // Handle other HTTP errors
    let message = 'An error occurred'
    if (status === 401) {
      message = 'Unauthorized. Please log in again.'
    } else if (status === 403) {
      message = 'Forbidden. You do not have permission.'
    } else if (status === 404) {
      message = 'Resource not found.'
    } else if (status === 429) {
      message = 'Too many requests. Please slow down.'
    } else if (status && status >= 500) {
      message = 'Server error. Please try again later.'
    }

    const err = new Error(message) as Error & { code?: string; status?: number }
    err.code = `HTTP_${status}`
    err.status = status
    return err
  }

  /**
   * Generate unique request ID for tracing
   */
  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Generate unique key for retry tracking
   */
  private getRetryKey(config: AxiosConfig): string {
    return `${config.method}:${config.url}`
  }

  /**
   * GET request
   *
   * @param url - Endpoint path (relative to baseURL)
   * @param config - Optional axios config
   * @returns Promise with response data
   */
  async get<T = any>(url: string, config?: AxiosConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config)
  }

  /**
   * POST request
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config)
  }

  /**
   * PUT request
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config)
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config)
  }

  /**
   * DELETE request
   */
  async delete<T = any>(url: string, config?: AxiosConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config)
  }

  /**
   * Get underlying axios instance for advanced usage
   */
  getClient(): AxiosInstance {
    return this.client
  }
}

/**
 * Create singleton instance
 */
export const apiClient = new BaseApiClient()

export default apiClient
