/**
 * LernsystemX - Panel Users Sub-Store (Pinia)
 *
 * Manages admin user management:
 * - User listing with pagination and filters
 * - User CRUD operations
 * - Ban/unban, token grants, creator verification
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as adminApi from '@/application/services/api/panel-admin'
import type {
  AdminUser,
  UsersFilterParams,
  PaginatedResponse,
  BanUserRequest
} from '@/application/services/api/panel-admin'

export const usePanelUsersStore = defineStore('panel-users', () => {
  // State
  const users = ref<AdminUser[]>([])
  const usersTotal = ref(0)
  const usersPage = ref(1)
  const usersLimit = ref(20)
  const usersTotalPages = ref(0)
  const userFilters = ref<UsersFilterParams>({})
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions

  /**
   * Load users with filters
   */
  const loadUsers = async (params: UsersFilterParams = {}): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminUser> = await adminApi.adminGetUsers(params)

      users.value = response.items
      usersTotal.value = response.total
      usersPage.value = response.page
      usersLimit.value = response.limit
      usersTotalPages.value = response.total_pages
      userFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Benutzer'
      console.error('Failed to load users:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update user role
   */
  const updateUserRole = async (userId: number, role: string): Promise<void> => {
    try {
      await adminApi.adminUpdateUserRole(userId, role)

      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.role = role
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern der Rolle'
      console.error('Failed to update user role:', err)
      throw err
    }
  }

  /**
   * Toggle user active status
   */
  const toggleUserActive = async (userId: number): Promise<void> => {
    const user = users.value.find(u => u.user_id === userId)
    if (!user) return

    try {
      const newStatus = !user.is_active
      await adminApi.adminToggleUserActive(userId, newStatus)

      user.is_active = newStatus
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern des Status'
      console.error('Failed to toggle user active:', err)
      throw err
    }
  }

  /**
   * Delete user
   */
  const deleteUser = async (userId: number): Promise<void> => {
    try {
      await adminApi.adminDeleteUser(userId)

      users.value = users.value.filter(u => u.user_id !== userId)
      usersTotal.value -= 1
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Benutzers'
      console.error('Failed to delete user:', err)
      throw err
    }
  }

  /**
   * Create new user (admin only)
   */
  const createUser = async (userData: {
    email: string
    password: string
    first_name: string
    last_name: string
    role: string
  }): Promise<AdminUser> => {
    try {
      const user = await adminApi.adminCreateUser(userData)
      return user
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Benutzers'
      console.error('Failed to create user:', err)
      throw err
    }
  }

  /**
   * Ban user (admin only)
   */
  const banUser = async (userId: number, banData: BanUserRequest): Promise<void> => {
    try {
      await adminApi.adminBanUser(userId, banData)

      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.is_active = false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Sperren des Benutzers'
      console.error('Failed to ban user:', err)
      throw err
    }
  }

  /**
   * Unban user (admin only)
   */
  const unbanUser = async (userId: number, reason: string): Promise<void> => {
    try {
      await adminApi.adminUnbanUser(userId, reason)

      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.is_active = true
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Entsperren des Benutzers'
      console.error('Failed to unban user:', err)
      throw err
    }
  }

  /**
   * Grant tokens to user (admin only)
   */
  const grantTokens = async (
    userId: number,
    amount: number,
    reason: string
  ): Promise<number> => {
    try {
      const newBalance = await adminApi.adminGrantTokens(userId, amount, reason)

      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.token_balance = newBalance
      }

      return newBalance
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Gewähren von Tokens'
      console.error('Failed to grant tokens:', err)
      throw err
    }
  }

  /**
   * Verify creator status (admin only)
   */
  const verifyCreator = async (
    userId: number,
    verified: boolean,
    reason: string
  ): Promise<void> => {
    try {
      await adminApi.adminVerifyCreator(userId, verified, reason)
    } catch (err: any) {
      error.value =
        err.response?.data?.message || 'Fehler beim Verifizieren des Creators'
      console.error('Failed to verify creator:', err)
      throw err
    }
  }

  return {
    // State
    users,
    usersTotal,
    usersPage,
    usersLimit,
    usersTotalPages,
    userFilters,
    loading,
    error,

    // Actions
    loadUsers,
    updateUserRole,
    toggleUserActive,
    deleteUser,
    createUser,
    banUser,
    unbanUser,
    grantTokens,
    verifyCreator
  }
})
