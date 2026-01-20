/**
 * LernsystemX - HTTP Client with JWT Support
 *
 * Centralized Axios instance with:
 * - JWT token auto-injection
 * - Auto-logout on 401
 * - Request/Response interceptors
 */

import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/application/stores/auth.store'
import router from '@/presentation/router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

// Create Axios instance
const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds - AI requests need more time
})

// Request Interceptor - Inject JWT token
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()

    // Add Authorization header if token exists
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response Interceptor - Handle errors
http.interceptors.response.use(
  (response) => {
    // Return data directly from successful responses
    return response
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()

    // Handle 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401) {
      // Logout user and redirect to login
      await authStore.logout()
      router.push('/login')

      return Promise.reject({
        message: 'Session expired. Please login again.',
        status: 401,
      })
    }

    // Handle 403 Forbidden - Insufficient permissions
    if (error.response?.status === 403) {
      return Promise.reject({
        message: 'You do not have permission to access this resource.',
        status: 403,
      })
    }

    // Handle 429 Too Many Requests - Rate limiting
    if (error.response?.status === 429) {
      return Promise.reject({
        message: 'Too many requests. Please try again later.',
        status: 429,
      })
    }

    // Handle 500+ Server Errors
    if (error.response && error.response.status >= 500) {
      return Promise.reject({
        message: 'Server error. Please try again later.',
        status: error.response.status,
      })
    }

    // Return error for other cases
    return Promise.reject(error)
  }
)

export default http
