/**
 * LernsystemX - Authentication Store (Pinia) - REFACTORED
 *
 * Manages:
 * - User authentication state (via domain model delegation)
 * - JWT tokens (access + refresh)
 * - User profile data
 * - Login/Logout actions with User.fromAPI() transformation
 *
 * REFACTORING NOTE: All business logic delegated to User domain model.
 * Store maintains state ONLY; all permission/role checks go through domain.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User as UserAPIDTO, LoginRequest, RegisterRequest } from '@/application/services/api/user'
import type { ProfileResponse } from '@/application/services/api/user'
import * as authApi from '@/application/services/api/user'
import * as profileApi from '@/application/services/api/user'
import { User as UserModel } from '@/domain/models/user/User.model'
import { UserRoleEnum } from '@/domain/models/user/UserRole.vo'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserAPIDTO | null>(null)
  const profile = ref<ProfileResponse | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed domain model wrapper (CRITICAL: Single transformation point)
  // Transforms raw API DTO (snake_case) to domain model (camelCase) in ONE place
  // This enables all other computed properties to delegate to domain model methods
  // instead of duplicating business logic
  const domainUser = computed(() => {
    if (!user.value) return null
    try {
      // Transform API response to domain model instance
      // User.fromAPI() handles:
      // - Property name conversion (first_name → firstName, etc.)
      // - Value object creation (Email, UserRole with validation)
      // - Date parsing and conversion
      return UserModel.fromAPI(user.value)
    } catch (err: any) {
      // Log transformation errors for debugging
      console.error('Failed to transform user to domain model:', err)
      error.value = `User data transformation error: ${err.message}`
      return null
    }
  })

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  const fullName = computed(() => domainUser.value?.fullName || '')

  const userRole = computed(() => domainUser.value?.role.toString() || 'user')

  const isPremium = computed(() => domainUser.value?.isPremium ?? false)

  const isTeacher = computed(() => domainUser.value?.role.rawValue === UserRoleEnum.TEACHER)

  const isCreator = computed(() => domainUser.value?.role.rawValue === UserRoleEnum.CREATOR)

  const isOrgAdmin = computed(() =>
    domainUser.value?.role.rawValue === UserRoleEnum.SCHOOL_ADMIN ||
    domainUser.value?.role.rawValue === UserRoleEnum.COMPANY_ADMIN
  )

  const isSystemAdmin = computed(() => domainUser.value?.isSystemAdmin ?? false)

  const isOwner = computed(() => domainUser.value?.role.rawValue === UserRoleEnum.OWNER)

  const currentOrganisationId = computed(() => {
    return user.value?.organisation_id || null
  })

  // Actions

  /**
   * Login user
   */
  const login = async (credentials: LoginRequest): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)

      // Store tokens
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token

      // Store user data (as raw DTO - domainUser computed will transform to domain model)
      user.value = response.user

      // Save to localStorage for persistence
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Register new user
   */
  const register = async (data: RegisterRequest): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await authApi.register(data)

      // Note: User must verify email before login
      // For now, we don't auto-login after registration

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout user
   */
  const logout = async (): Promise<void> => {
    try {
      // Try to logout with current access token
      if (accessToken.value) {
        try {
          await authApi.logout()
        } catch (err: any) {
          // If token expired (401), try to refresh first
          if (err.response?.status === 401 && refreshToken.value) {
            try {
              console.log('Access token expired, attempting refresh before logout...')
              const refreshResponse = await authApi.refreshToken(refreshToken.value!)
              // Update tokens and retry logout
              accessToken.value = refreshResponse.access_token
              localStorage.setItem('access_token', refreshResponse.access_token)
              // Now try logout again with fresh token
              await authApi.logout()
            } catch (refreshErr) {
              // Refresh also failed - just proceed with local logout
              console.log('Refresh failed during logout, proceeding with local logout')
            }
          } else {
            // Other error - just log and proceed
            console.log('Logout API error:', err)
          }
        }
      }
    } catch (err) {
      // Unexpected error - just log
      console.error('Logout error:', err)
    } finally {
      // Always clear local state
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      error.value = null

      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  /**
   * Load user profile from API
   */
  const loadProfile = async (): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      const profileData = await profileApi.getProfile()
      profile.value = profileData

      // Also update user object with basic info (store as raw DTO - domainUser computed will transform)
      user.value = profileData

      // Update localStorage
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('profile', JSON.stringify(profileData))

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to load profile'

      // If unauthorized, logout
      if (err.response?.status === 401) {
        await logout()
      }

      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load extended profile with tokens and subscription
   */
  const loadExtendedProfile = async (): Promise<void> => {
    await loadProfile()
  }

  /**
   * Restore session from localStorage
   */
  const restoreSession = (): void => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')
    const storedProfile = localStorage.getItem('profile')

    if (storedToken && storedUser) {
      accessToken.value = storedToken
      refreshToken.value = storedRefreshToken
      user.value = JSON.parse(storedUser)

      if (storedProfile) {
        profile.value = JSON.parse(storedProfile)
      }
    }
  }

  /**
   * Refresh access token
   */
  const refresh = async (): Promise<void> => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await authApi.refreshToken(refreshToken.value)

      // Update access token
      accessToken.value = response.access_token
      localStorage.setItem('access_token', response.access_token)

    } catch (err) {
      // If refresh fails, logout
      await logout()
      throw err
    }
  }

  // Initialize: Restore session on store creation
  restoreSession()

  return {
    // State
    user,
    profile,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    fullName,
    userRole,
    isPremium,
    isTeacher,
    isCreator,
    isOrgAdmin,
    isSystemAdmin,
    isOwner,
    currentOrganisationId,

    // Actions
    login,
    register,
    logout,
    loadProfile,
    loadExtendedProfile,
    restoreSession,
    refresh,
  }
})
