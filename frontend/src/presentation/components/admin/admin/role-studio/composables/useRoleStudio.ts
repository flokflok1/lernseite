/**
 * useRoleStudio Composable
 *
 * Manages role studio mode data and operations
 * Provides methods for fetching, creating, updating, and deleting roles
 * Delegates API communication to role-studio.api.ts service
 */

import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  RoleStudioMode,
  CreateRoleStudioRequest,
  RoleChangeHistory
} from '../types'
import * as roleStudioApi from '@/api/admin/role-studio.api'

export function useRoleStudio() {
  const { t } = useI18n()

  // State
  const roles = ref<RoleStudioMode[]>([])
  const selectedRole = ref<RoleStudioMode | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalRoles = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const changeHistory = ref<RoleChangeHistory[]>([])

  // Computed
  const sortedRoles = computed(() =>
    [...roles.value].sort((a, b) => a.display_name.localeCompare(b.display_name))
  )

  const activeRoles = computed(() =>
    sortedRoles.value.filter(role => role.is_active)
  )

  const organizationRoles = computed(() =>
    sortedRoles.value.filter(role => role.requires_organization)
  )

  /**
   * Fetch all roles with pagination
   */
  async function fetchRoles(filter?: 'active' | 'inactive') {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.fetchRoles(currentPage.value, pageSize.value, filter)
      roles.value = data.roles || []
      totalRoles.value = data.total || 0
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error fetching roles:', error.value)
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch single role by code
   */
  async function fetchRole(roleCode: string) {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.fetchRole(roleCode)
      selectedRole.value = data
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error fetching role:', error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new role studio mode
   */
  async function createRole(request: CreateRoleStudioRequest) {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.createRole(request)
      roles.value.push(data)
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error creating role:', error.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update existing role studio mode
   */
  async function updateRole(roleCode: string, request: Partial<CreateRoleStudioRequest>) {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.updateRole(roleCode, request)
      const index = roles.value.findIndex(r => r.role_code === roleCode)
      if (index !== -1) {
        roles.value[index] = data
      }
      if (selectedRole.value?.role_code === roleCode) {
        selectedRole.value = data
      }
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error updating role:', error.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Deactivate (soft delete) role
   */
  async function deactivateRole(roleCode: string) {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.deactivateRole(roleCode)
      const index = roles.value.findIndex(r => r.role_code === roleCode)
      if (index !== -1) {
        roles.value[index] = data
      }
      if (selectedRole.value?.role_code === roleCode) {
        selectedRole.value = data
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error deactivating role:', error.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch change history for a role
   */
  async function fetchChangeHistory(roleCode: string, page: number = 1) {
    loading.value = true
    error.value = null

    try {
      const data = await roleStudioApi.fetchChangeHistory(roleCode, page, 10)
      changeHistory.value = data.history || []
      return changeHistory.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[useRoleStudio] Error fetching history:', error.value)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Select a role for editing
   */
  function selectRole(role: RoleStudioMode) {
    selectedRole.value = role
  }

  /**
   * Clear selection
   */
  function clearSelection() {
    selectedRole.value = null
  }

  /**
   * Reset error
   */
  function clearError() {
    error.value = null
  }

  // Lifecycle
  onMounted(async () => {
    await fetchRoles()
  })

  return {
    // State
    roles: computed(() => roles.value),
    selectedRole: computed(() => selectedRole.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    totalRoles: computed(() => totalRoles.value),
    currentPage: computed(() => currentPage.value),
    pageSize: computed(() => pageSize.value),
    changeHistory: computed(() => changeHistory.value),

    // Computed
    sortedRoles,
    activeRoles,
    organizationRoles,

    // Methods
    fetchRoles,
    fetchRole,
    createRole,
    updateRole,
    deactivateRole,
    fetchChangeHistory,
    selectRole,
    clearSelection,
    clearError,

    // Mutations
    setCurrentPage: (page: number) => {
      currentPage.value = page
    },
    setPageSize: (size: number) => {
      pageSize.value = size
    }
  }
}
