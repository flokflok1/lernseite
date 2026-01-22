/**
 * LernsystemX - Authentication API Service
 *
 * Pattern: Transform backend DTOs to domain models at API layer
 * This ensures all callers receive consistent domain models, not backend DTOs
 *
 * Transformation Flow:
 * Backend sends snake_case DTO
 *   → transformUserFromAPI() handles naming conversion
 *   → User.fromAPI() validates business rules
 *   → Caller receives domain model (camelCase)
 */

import http from '../http'
import { transformUserFromAPI } from '../../utils/transformers'
import { User as UserDomainModel } from '@/domain/models/user/User.model'

// ============================================
// BACKEND DTO INTERFACES (what backend sends)
// ============================================

/**
 * Backend User DTO (snake_case - raw from API)
 * Represents exactly what backend returns
 */
export interface BackendUserDTO {
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

/**
 * Backend LoginResponse DTO
 */
export interface BackendLoginResponseDTO {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: BackendUserDTO
  two_factor_required?: boolean
}

/**
 * Backend RegisterResponse DTO
 */
export interface BackendRegisterResponseDTO {
  success: boolean
  message: string
  user: BackendUserDTO
  email_verification_required: boolean
}

// ============================================
// DOMAIN RESPONSE INTERFACES (what callers get)
// ============================================

/**
 * Domain LoginResponse (contains transformed domain model)
 * This is what the API function returns to callers
 */
export interface LoginResponse {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: UserDomainModel
  two_factor_required?: boolean
}

/**
 * Domain RegisterResponse
 */
export interface RegisterResponse {
  success: boolean
  message: string
  user: UserDomainModel
  email_verification_required: boolean
}

/**
 * Domain UserProfileResponse
 */
export interface UserProfileResponse {
  success: boolean
  user: UserDomainModel
}

// ============================================
// REQUEST INTERFACES (unchanged)
// ============================================

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

// ============================================
// API FUNCTIONS (with transformation)
// ============================================

/**
 * Login user with authentication
 *
 * Transformation Flow:
 * 1. Send credentials to /auth/login
 * 2. Receive response with BackendUserDTO (snake_case)
 * 3. Transform snake_case → domain model format using transformUserFromAPI()
 * 4. Create User domain entity via User.fromAPI()
 * 5. Return response with domain model (camelCase)
 *
 * @param credentials - Login credentials
 * @returns LoginResponse with transformed User domain model
 * @throws UnauthorizedError if credentials invalid
 * @throws ValidationError if server validation fails
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  // 1. Call backend API with DTO types
  const response = await http.post<BackendLoginResponseDTO>('/auth/login', credentials)

  // 2. Extract backend response (contains snake_case User DTO)
  const backendData = response.data

  // 3. Transform backend DTO to intermediate format (handles naming)
  const transformedUserData = transformUserFromAPI(backendData.user)

  // 4. Create domain model (validates business rules)
  const domainUser = UserDomainModel.fromAPI(transformedUserData)

  // 5. Return response with domain model (not DTO)
  return {
    success: backendData.success,
    message: backendData.message,
    access_token: backendData.access_token,
    token_type: backendData.token_type,
    expires_in: backendData.expires_in,
    refresh_token: backendData.refresh_token,
    user: domainUser,
    two_factor_required: backendData.two_factor_required
  }
}

/**
 * Register new user account
 *
 * @param data - Registration data
 * @returns RegisterResponse with transformed User domain model
 */
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await http.post<BackendRegisterResponseDTO>('/auth/register', data)

  const transformedUserData = transformUserFromAPI(response.data.user)
  const domainUser = UserDomainModel.fromAPI(transformedUserData)

  return {
    success: response.data.success,
    message: response.data.message,
    user: domainUser,
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
 * @returns UserProfileResponse with transformed User domain model
 */
export const getUserProfile = async (): Promise<UserProfileResponse> => {
  const response = await http.get<{ success: boolean; user: BackendUserDTO }>('/auth/me')

  const transformedUserData = transformUserFromAPI(response.data.user)
  const domainUser = UserDomainModel.fromAPI(transformedUserData)

  return {
    success: response.data.success,
    user: domainUser
  }
}
