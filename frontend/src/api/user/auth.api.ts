/**
 * User Authentication API
 * ========================
 *
 * Authentication endpoints for login, registration, token refresh, and logout.
 * Part of the User Domain (DDD Architecture).
 */

import http from '../http'

export interface LoginRequest {
  email: string
  password: string
  totp_code?: string // Optional 2FA code
}

export interface RegisterRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  role?: string
  organisation_id?: number
}

export interface LoginResponse {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: User
  two_factor_required?: boolean
}

export interface RegisterResponse {
  success: boolean
  message: string
  user: User
  email_verification_required: boolean
}

export interface User {
  user_id: string
  email: string
  first_name: string
  last_name: string
  role: string
  hierarchy_level?: number // RBAC 2.0: Dynamic hierarchy level (1-10, owner=10)
  organisation_id: number | null
  is_active: boolean
  created_at: string
  two_factor_enabled?: boolean
}

export interface UserProfileResponse {
  success: boolean
  user: User
}

/**
 * Login user with email and password
 *
 * @param credentials - Login request credentials
 * @returns Promise with access token and user profile
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await http.post<LoginResponse>('/auth/login', credentials)
  return response.data
}

/**
 * Register new user account
 *
 * @param data - Registration data
 * @returns Promise with created user profile
 */
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await http.post<RegisterResponse>('/auth/register', data)
  return response.data
}

/**
 * Refresh access token using refresh token
 *
 * @param refreshToken - Valid refresh token
 * @returns Promise with new access token
 */
export const refreshToken = async (refreshToken: string): Promise<{ access_token: string; expires_in: number }> => {
  const response = await http.post('/auth/refresh', {}, {
    headers: {
      Authorization: `Bearer ${refreshToken}`
    }
  })
  return response.data
}

/**
 * Logout user and invalidate tokens
 *
 * @returns Promise<void>
 */
export const logout = async (): Promise<void> => {
  await http.post('/auth/logout')
}

/**
 * Get current user profile
 *
 * @returns Promise with user profile information
 */
export const getUserProfile = async (): Promise<UserProfileResponse> => {
  const response = await http.get<UserProfileResponse>('/auth/me')
  return response.data
}
