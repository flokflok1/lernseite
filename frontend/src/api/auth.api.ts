/**
 * LernsystemX - Authentication API Service
 */

import http from './http'

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
 * Login user
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await http.post<LoginResponse>('/auth/login', credentials)
  return response.data
}

/**
 * Register new user
 */
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await http.post<RegisterResponse>('/auth/register', data)
  return response.data
}

/**
 * Refresh access token
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
 * Logout user
 */
export const logout = async (): Promise<void> => {
  await http.post('/auth/logout')
}

/**
 * Get current user profile
 */
export const getUserProfile = async (): Promise<UserProfileResponse> => {
  const response = await http.get<UserProfileResponse>('/auth/me')
  return response.data
}
