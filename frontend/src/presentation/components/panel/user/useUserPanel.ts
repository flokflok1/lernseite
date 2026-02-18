/**
 * useUserPanel Composable
 *
 * Manages user panel state and operations:
 * - Load user statistics
 * - Manage courses (load, filter, create, update, delete)
 * - Handle subscription and profile updates
 * - Load user activity and progress
 *
 * Architecture:
 * - Uses Pinia userStore for current user
 * - Uses API services for data fetching
 * - Reactive state with composables
 */

import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/application/stores/modules/core/auth.store'

export interface UserStats {
  totalCourses: number
  enrolledCourses: number
  completedCourses: number
  inProgressCourses: number
  averageProgress: number
  totalTokens: number
  tokenBalance: number
  lastLoginAt?: string
}

export function useUserPanel() {
  const userStore = useUserStore()

  // State
  const userStats = ref<UserStats>({
    totalCourses: 0,
    enrolledCourses: 0,
    completedCourses: 0,
    inProgressCourses: 0,
    averageProgress: 0,
    totalTokens: 0,
    tokenBalance: 0
  })

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const currentUser = computed(() => userStore.currentUser)

  /**
   * Load user statistics
   */
  const loadUserStats = async () => {
    if (!currentUser.value) {
      error.value = 'User not authenticated'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await userService.getStats(currentUser.value.user_id)
      // userStats.value = response.data

      // Mock data for now
      userStats.value = {
        totalCourses: 12,
        enrolledCourses: 8,
        completedCourses: 3,
        inProgressCourses: 5,
        averageProgress: 62,
        totalTokens: 10000,
        tokenBalance: 2450,
        lastLoginAt: new Date().toISOString()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load user statistics'
      console.error('Error loading user stats:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update user profile
   */
  const updateProfile = async (profileData: {
    name?: string
    email?: string
    bio?: string
  }) => {
    if (!currentUser.value) {
      error.value = 'User not authenticated'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await userService.updateProfile(
      //   currentUser.value.user_id,
      //   profileData
      // )
      // Update store
      // userStore.updateCurrentUser(response.data)

      console.log('Profile updated:', profileData)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update profile'
      console.error('Error updating profile:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update subscription
   */
  const updateSubscription = async (tier: 'free' | 'creator' | 'pro') => {
    if (!currentUser.value) {
      error.value = 'User not authenticated'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await subscriptionService.updateTier(
      //   currentUser.value.user_id,
      //   tier
      // )
      // Update store
      // userStore.updateCurrentUser(response.data)

      console.log('Subscription updated to:', tier)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update subscription'
      console.error('Error updating subscription:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update notification settings
   */
  const updateNotificationSettings = async (settings: Record<string, boolean>) => {
    if (!currentUser.value) {
      error.value = 'User not authenticated'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await userService.updateNotificationSettings(
      //   currentUser.value.user_id,
      //   settings
      // )

      console.log('Notification settings updated:', settings)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update notification settings'
      console.error('Error updating notification settings:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      await userStore.logout()
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to logout'
      console.error('Error logging out:', err)
      return false
    }
  }

  /**
   * Delete user account
   */
  const deleteAccount = async (_password: string) => {
    if (!currentUser.value) {
      error.value = 'User not authenticated'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await userService.deleteAccount(
      //   currentUser.value.user_id,
      //   password
      // )
      // Logout after successful deletion
      // await logout()

      console.log('Account deleted')
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete account'
      console.error('Error deleting account:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Load stats on mount
  onMounted(() => {
    loadUserStats()
  })

  return {
    // State
    userStats,
    isLoading,
    error,
    currentUser,

    // Methods
    loadUserStats,
    updateProfile,
    updateSubscription,
    updateNotificationSettings,
    logout,
    deleteAccount
  }
}
