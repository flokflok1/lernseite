/**
 * LernsystemX - Authentication Store (Pinia) - LEVEL-BASED HIERARCHY
 *
 * Manages:
 * - User authentication state
 * - JWT tokens (access + refresh)
 * - User profile data
 * - Hierarchy Level (0-1000) from database
 * - Login/Logout actions
 *
 * NOTE: Phase B - Level-Based Authorization (GBA)
 * All permissions derived from hierarchy_level (0-1000)
 * 1000 = Owner, 900 = SystemAdmin, 750 = Moderator, 500 = OrgAdmin, etc.
 * NO hardcoded enums, NO code changes needed when permissions change
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User as UserAPIDTO, LoginRequest, RegisterRequest } from '@/application/services/api/user'
import type { ProfileResponse } from '@/application/services/api/user'
import * as authApi from '@/application/services/api/user'
import * as profileApi from '@/application/services/api/user'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserAPIDTO | null>(null)
  const profile = ref<ProfileResponse | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)


  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  /**
   * User's full name from API response
   */
  const fullName = computed(() => {
    if (!user.value) return ''
    // Backend returns full_name directly (not first_name/last_name)
    return (user.value as any)?.full_name || ''
  })

  /**
   * User's display role derived from groups (GBA)
   * Uses the highest hierarchy group name as display role
   * No hardcoded 'role' field - determined by group membership
   */
  const userRole = computed(() => {
    if (!user.value) return 'Guest'

    const userGroups = (user.value as any)?.groups || []
    if (userGroups.length === 0) return 'Member'

    // Find the group with highest hierarchy_level
    const highestGroup = userGroups.reduce((highest: any, current: any) => {
      const currentLevel = current.hierarchy_level || 0
      const highestLevel = highest?.hierarchy_level || 0
      return currentLevel > highestLevel ? current : highest
    }, userGroups[0])

    // Return group name as display role
    return highestGroup?.name || 'Member'
  })

  const isPremium = computed(() => {
    return (user.value as any)?.is_premium ?? false
  })

  /**
   * User's hierarchy level from database (0-1000)
   * Determined by highest level among all user's groups
   * 1000 = Owner
   * 900 = SystemAdmin
   * 750 = Moderator
   * 500 = OrgAdmin
   * 250 = Creator/Teacher
   * 100 = Premium Member
   * 10 = Regular Member
   * 0 = Guest
   */
  const userHierarchyLevel = computed(() => {
    if (!user.value) return 0

    const userGroups = (user.value as any)?.groups || []
    if (userGroups.length === 0) return 0

    // Get maximum hierarchy level from all user's groups
    return Math.max(
      ...userGroups.map((g: any) => g.hierarchy_level || 0),
      0
    )
  })

  /**
   * Check if user has at least the required hierarchy level
   * @param requiredLevel - Minimum hierarchy level (0-1000)
   * @returns true if user's level >= requiredLevel
   */
  const hasHierarchyLevel = (requiredLevel: number): boolean => {
    return userHierarchyLevel.value >= requiredLevel
  }

  /**
   * Is user Owner (hierarchy_level >= 1000)
   */
  const isOwner = computed(() => userHierarchyLevel.value >= 1000)

  /**
   * Is user SystemAdmin or higher (hierarchy_level >= 900)
   */
  const isSystemAdmin = computed(() => userHierarchyLevel.value >= 900)

  /**
   * Is user Moderator or higher (hierarchy_level >= 750)
   */
  const isModerator = computed(() => userHierarchyLevel.value >= 750)

  /**
   * Is user OrgAdmin or higher (hierarchy_level >= 500)
   */
  const isOrgAdmin = computed(() => userHierarchyLevel.value >= 500)

  /**
   * Is user Creator/Teacher or higher (hierarchy_level >= 250)
   */
  const isCreator = computed(() => userHierarchyLevel.value >= 250)

  /**
   * Can user access Admin Panel? (OrgAdmin level or higher = 500+)
   */
  const canAccessAdminPanel = computed(() => userHierarchyLevel.value >= 500)

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

      // Store user data with groups merged (GBA - groups come separately in response)
      // This enables userRole and userHierarchyLevel computed properties to work
      const userData = {
        ...response.user,
        groups: response.groups || [],
        permissions: response.permissions || []
      }
      user.value = userData

      // Save to localStorage for persistence
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))

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
            } catch (_refreshErr) {
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

      // IMPORTANT: Preserve existing groups and permissions when updating user
      // The profile endpoint doesn't return groups - they come from login response
      // Merging ensures we don't lose GBA authorization data
      const existingGroups = (user.value as any)?.groups || []
      const existingPermissions = (user.value as any)?.permissions || []

      user.value = {
        ...profileData,
        groups: existingGroups,
        permissions: existingPermissions
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
    currentOrganisationId,

    // Hierarchy Level (0-1000) - Database-driven, no hardcoding
    userHierarchyLevel,
    hasHierarchyLevel,

    // Role Checks (GBA - derived from hierarchy_level)
    isOwner,              // >= 1000
    isSystemAdmin,        // >= 900
    isModerator,          // >= 750
    isOrgAdmin,           // >= 500
    isCreator,            // >= 250
    canAccessAdminPanel,  // >= 500

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
