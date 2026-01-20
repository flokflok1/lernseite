/**
 * useRolesManagement Composable
 * ==============================
 * Shared logic for roles management
 */
import { ref, computed } from 'vue'
import rolesApi, {
  type Role,
  type Permission,
  type RoleUser
} from '@/infrastructure/api/clients/admin'

export function useRolesManagement() {
  // State
  const roles = ref<Role[]>([])
  const permissions = ref<Record<string, Permission[]>>({})
  const selectedRole = ref<Role | null>(null)
  const roleUsers = ref<RoleUser[]>([])
  const loading = ref(false)

  // Computed
  const systemRoles = computed(() => roles.value.filter(r => r.is_system))
  const customRoles = computed(() => roles.value.filter(r => r.is_custom))

  // Load data
  async function loadRoles() {
    loading.value = true
    try {
      roles.value = await rolesApi.getRoles(true)
    } catch (e) {
      console.error('Failed to load roles:', e)
    } finally {
      loading.value = false
    }
  }

  async function loadPermissions() {
    try {
      permissions.value = await rolesApi.getPermissionsGrouped()
    } catch (e) {
      console.error('Failed to load permissions:', e)
    }
  }

  async function selectRole(role: Role) {
    selectedRole.value = role

    try {
      const [fullRole, users] = await Promise.all([
        rolesApi.getRole(role.role_id),
        rolesApi.getRoleUsers(role.role_id, 50)
      ])
      selectedRole.value = fullRole
      roleUsers.value = users
    } catch (e) {
      console.error('Failed to load role details:', e)
    }
  }

  // CRUD operations
  async function createRole(data: {
    role_name: string
    display_name: string
    description: string
    hierarchy_level: number
    color: string
    icon: string
  }) {
    try {
      await rolesApi.createRole(data)
      await loadRoles()
      return true
    } catch (e) {
      console.error('Failed to create role:', e)
      return false
    }
  }

  async function updateRole(roleId: number, data: Partial<Role>) {
    try {
      await rolesApi.updateRole(roleId, data)
      await loadRoles()
      if (selectedRole.value?.role_id === roleId) {
        await selectRole({ ...selectedRole.value, ...data } as Role)
      }
      return true
    } catch (e) {
      console.error('Failed to update role:', e)
      return false
    }
  }

  async function deleteRole(role: Role) {
    if (role.is_system) return false

    try {
      await rolesApi.deleteRole(role.role_id)
      if (selectedRole.value?.role_id === role.role_id) {
        selectedRole.value = null
      }
      await loadRoles()
      return true
    } catch (e) {
      console.error('Failed to delete role:', e)
      return false
    }
  }

  // Permission management
  async function setRolePermissions(roleId: number, permissionIds: number[]) {
    try {
      await rolesApi.setRolePermissions(roleId, permissionIds)
      if (selectedRole.value?.role_id === roleId) {
        const fullRole = await rolesApi.getRole(roleId)
        selectedRole.value = fullRole
      }
      return true
    } catch (e) {
      console.error('Failed to save permissions:', e)
      return false
    }
  }

  // Initialize
  async function initialize() {
    await Promise.all([loadRoles(), loadPermissions()])
  }

  return {
    // State
    roles,
    permissions,
    selectedRole,
    roleUsers,
    loading,
    // Computed
    systemRoles,
    customRoles,
    // Methods
    loadRoles,
    loadPermissions,
    selectRole,
    createRole,
    updateRole,
    deleteRole,
    setRolePermissions,
    initialize
  }
}
