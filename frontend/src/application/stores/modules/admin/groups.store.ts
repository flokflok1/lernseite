/**
 * Groups Management Store (GBA)
 * =============================
 * Pinia store for Owner-Admin group management with custom groups and feature assignments.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  RoleWithStats,
  RoleTemplate,
  SystemFeature,
  CreateRoleRequest,
  UpdateRoleRequest,
  AssignFeaturesRequest,
  AssignPermissionsRequest,
  CreateFromTemplateRequest
} from '@/application/services/api/admin'
import {
  getRolesV2,
  getRoleV2,
  createRoleV2,
  updateRoleV2,
  deleteRoleV2,
  assignRoleFeatures,
  assignRolePermissionsV2,
  getRoleTemplates,
  createRoleFromTemplate,
  getSystemFeatures
} from '@/application/services/api/admin'

export const useGroupsStore = defineStore('groups', () => {
  // =============================================================================
  // State
  // =============================================================================

  const roles = ref<RoleWithStats[]>([])
  const selectedRole = ref<RoleWithStats | null>(null)
  const templates = ref<RoleTemplate[]>([])
  const systemFeatures = ref<SystemFeature[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // =============================================================================
  // Computed
  // =============================================================================

  const customRoles = computed(() => roles.value.filter((r) => r.is_custom))
  const systemRoles = computed(() => roles.value.filter((r) => r.is_system))
  const totalRoles = computed(() => roles.value.length)
  const hasOwnerRole = computed(() => {
    // Check if current user is owner (from auth store)
    return true // TODO: Implement auth store check
  })

  // =============================================================================
  // Actions
  // =============================================================================

  /**
   * Fetch all groups with optional filtering
   */
  async function fetchRoles(params?: {
    is_custom?: boolean
    hierarchy_min?: number
    hierarchy_max?: number
    search?: string
    include_features?: boolean
    include_permissions?: boolean
  }) {
    loading.value = true
    error.value = null

    try {
      const response = await getRolesV2(params)
      roles.value = response.roles
      return response.roles
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch groups'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch single group with details
   */
  async function fetchRole(roleId: number) {
    loading.value = true
    error.value = null

    try {
      const role = await getRoleV2(roleId)
      selectedRole.value = role
      return role
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch group'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create custom group
   */
  async function createRole(data: CreateRoleRequest) {
    loading.value = true
    error.value = null

    try {
      const newRole = await createRoleV2(data)
      roles.value.push(newRole)
      return newRole
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to create group'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update existing group
   */
  async function updateRole(roleId: number, data: UpdateRoleRequest) {
    loading.value = true
    error.value = null

    try {
      const updatedRole = await updateRoleV2(roleId, data)
      const index = roles.value.findIndex((r) => r.role_id === roleId)
      if (index !== -1) {
        roles.value[index] = { ...roles.value[index], ...updatedRole }
      }
      if (selectedRole.value?.role_id === roleId) {
        selectedRole.value = { ...selectedRole.value, ...updatedRole }
      }
      return updatedRole
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to update group'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete custom group with user reassignment
   */
  async function deleteRole(roleId: number, reassignTo?: number) {
    loading.value = true
    error.value = null

    try {
      const result = await deleteRoleV2(roleId, reassignTo)
      roles.value = roles.value.filter((r) => r.role_id !== roleId)
      if (selectedRole.value?.role_id === roleId) {
        selectedRole.value = null
      }
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to delete group'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Assign system features to group
   */
  async function assignFeatures(roleId: number, data: AssignFeaturesRequest) {
    loading.value = true
    error.value = null

    try {
      const result = await assignRoleFeatures(roleId, data)
      // Refresh group to get updated feature count
      await fetchRole(roleId)
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to assign features'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Assign permissions to group
   */
  async function assignPermissions(roleId: number, data: AssignPermissionsRequest) {
    loading.value = true
    error.value = null

    try {
      const result = await assignRolePermissionsV2(roleId, data)
      // Refresh group to get updated permission count
      await fetchRole(roleId)
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to assign permissions'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch group templates
   */
  async function fetchTemplates() {
    loading.value = true
    error.value = null

    try {
      const templateList = await getRoleTemplates()
      templates.value = templateList
      return templateList
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch templates'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create group from template
   */
  async function createFromTemplate(data: CreateFromTemplateRequest) {
    loading.value = true
    error.value = null

    try {
      const newRole = await createRoleFromTemplate(data)
      roles.value.push(newRole)
      return newRole
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to create group from template'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch all system features
   */
  async function fetchSystemFeatures() {
    loading.value = true
    error.value = null

    try {
      const features = await getSystemFeatures()
      systemFeatures.value = features
      return features
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch system features'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error message
   */
  function clearError() {
    error.value = null
  }

  /**
   * Reset store state
   */
  function reset() {
    roles.value = []
    selectedRole.value = null
    templates.value = []
    systemFeatures.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    roles,
    selectedRole,
    templates,
    systemFeatures,
    loading,
    error,
    // Computed
    customRoles,
    systemRoles,
    totalRoles,
    hasOwnerRole,
    // Actions
    fetchRoles,
    fetchRole,
    createRole,
    updateRole,
    deleteRole,
    assignFeatures,
    assignPermissions,
    fetchTemplates,
    createFromTemplate,
    fetchSystemFeatures,
    clearError,
    reset
  }
})
