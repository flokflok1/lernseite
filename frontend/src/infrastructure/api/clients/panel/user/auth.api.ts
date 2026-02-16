/**
 * LernsystemX - Authentication API Service
 *
 * NOTE: Phase B - Group-Based Authorization (GBA) System
 * - NO role field - authorization via groups
 * - full_name (not first_name/last_name)
 * - groups[] with hierarchy_level (0-1000)
 * - permissions[] derived from group memberships
 *
 * Types imported from ./types.ts (Single Source of Truth)
 */

import http from '@/infrastructure/api/http'
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserGroup,
  UserProfileResponse,
} from './types'

// Re-export types for consumers who import directly from auth.api
export type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserGroup,
  UserProfileResponse,
}

// ============================================
// INTERNAL BACKEND DTO (for API response typing)
// ============================================

/**
 * Backend LoginResponse DTO (internal - what backend actually sends)
 */
interface BackendLoginResponseDTO {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: User
  groups: UserGroup[]
  permissions: string[]
  two_factor_required?: boolean
}

/**
 * Backend RegisterResponse DTO (internal)
 */
interface BackendRegisterResponseDTO {
  success: boolean
  message: string
  user: User
  email_verification_required: boolean
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Login user with authentication
 *
 * @param credentials - Login credentials
 * @returns LoginResponse with user, groups[], and permissions[] (GBA)
 * @throws UnauthorizedError if credentials invalid
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await http.post<BackendLoginResponseDTO>('/auth/login', credentials)
  const data = response.data

  return {
    success: data.success,
    message: data.message,
    access_token: data.access_token,
    token_type: data.token_type,
    expires_in: data.expires_in,
    refresh_token: data.refresh_token,
    user: data.user,
    groups: data.groups || [],           // GBA: Pass through groups
    permissions: data.permissions || [], // GBA: Pass through permissions
    two_factor_required: data.two_factor_required
  }
}

/**
 * Register new user account
 *
 * @param data - Registration data
 * @returns RegisterResponse with user
 */
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await http.post<BackendRegisterResponseDTO>('/auth/register', data)

  return {
    success: response.data.success,
    message: response.data.message,
    user: response.data.user,
    email_verification_required: response.data.email_verification_required
  }
}

/**
 * Refresh access token using refresh token
 *
 * @param refreshToken - Refresh token from login
 * @returns New access token and expiration
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
 * Logout user and invalidate session
 */
export const logout = async (): Promise<void> => {
  await http.post('/auth/logout')
}

/**
 * Get current user profile
 *
 * @returns UserProfileResponse with user
 */
export const getUserProfile = async (): Promise<UserProfileResponse> => {
  const response = await http.get<{ success: boolean; user: User }>('/auth/me')

  return {
    success: response.data.success,
    user: response.data.user
  }
}
