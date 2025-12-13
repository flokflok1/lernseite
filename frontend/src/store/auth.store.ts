/**
 * LernsystemX - Authentication Store (Pinia)
 *
 * Manages:
 * - User authentication state
 * - JWT tokens (access + refresh)
 * - User profile data
 * - Login/Logout actions
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest } from '@/api/auth.api'
import type { ProfileResponse } from '@/api/profile.api'
import * as authApi from '@/api/auth.api'
import * as profileApi from '@/api/profile.api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const profile = ref<ProfileResponse | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`
  })

  const userRole = computed(() => user.value?.role || 'user')

  const isPremium = computed(() => {
    // Check role-based premium access
    const premiumRoles = ['premium', 'creator', 'teacher', 'admin', 'school', 'company']
    if (premiumRoles.includes(userRole.value)) {
      return true
    }

    // Check subscription-based premium access
    if (profile.value) {
      const premiumPlans = ['premium', 'pro', 'enterprise', 'school', 'company']
      const isPremiumPlan = premiumPlans.includes(profile.value.subscription_plan?.toLowerCase() || '')
      const isActiveSubscription = ['active', 'trial', 'trialing'].includes(profile.value.subscription_status?.toLowerCase() || '')
      if (isPremiumPlan && isActiveSubscription) {
        return true
      }
    }

    return false
  })

  const isTeacher = computed(() => {
    return user.value?.role === 'teacher'
  })

  const isCreator = computed(() => {
    return user.value?.role === 'creator'
  })

  const isOrgAdmin = computed(() => {
    const orgAdminRoles = ['school_admin', 'company_admin']
    return orgAdminRoles.includes(user.value?.role || '')
  })

  const isSystemAdmin = computed(() => {
    const systemAdminRoles = ['admin', 'superadmin']
    return systemAdminRoles.includes(user.value?.role || '')
  })

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

      // Store user data
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
      // Call logout API (optional - to blacklist token)
      if (accessToken.value) {
        await authApi.logout()
      }
    } catch (err) {
      // Ignore errors during logout
      console.error('Logout API error:', err)
    } finally {
      // Clear state
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

      // Also update user object with basic info
      user.value = {
        user_id: profileData.user_id,
        email: profileData.email,
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        role: profileData.role,
        organisation_id: profileData.organisation_id,
        is_active: profileData.is_active
      }

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
