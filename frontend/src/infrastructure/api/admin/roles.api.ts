/**
 * Admin Roles & Permissions API
 * ==============================
 * API client for managing roles, permissions, and user assignments.
 */

import http from '../http'

// =============================================================================
// Types
// =============================================================================

export interface Role {
  role_id: number
  role_name: string
  display_name: string
  description: string | null
  hierarchy_level: number
  is_system: boolean
  is_custom: boolean
  color: string
  icon: string
  created_by?: string
  created_at: string
  permission_count?: number
  user_count?: number
  permissions?: Permission[]
}

export interface Permission {
  permission_id: number
  permission_key: string
  display_name: string
  description?: string
  module: string
  category: string
  is_system?: boolean
  sort_order?: number
}

export interface UserPermissionOverride {
  permission_id: number
  permission_key: string
  display_name: string
  category: string
  granted: boolean
  granted_by: string
  granted_by_username: string
  granted_at: string
  expires_at: string | null
  reason: string | null
}

export interface RoleUser {
  user_id: string
  username: string
  email: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  created_at: string
  last_login: string | null
}

// =============================================================================
// Roles CRUD
// =============================================================================

/**
 * Get all roles
 */
export async function getRoles(includeSystem = true): Promise<Role[]> {
  const response = await http.get('/admin/roles', {
    params: { include_system: includeSystem }
  })
  return response.data.data
}

/**
 * Get single role with permissions
 */
export async function getRole(roleId: number): Promise<Role> {
  const response = await http.get(`/admin/roles/${roleId}`)
  return response.data.data
}

/**
 * Create a new custom role
 */
export async function createRole(data: {
  role_name: string
  display_name: string
  description?: string
  hierarchy_level?: number
  color?: string
  icon?: string
}): Promise<{ role_id: number }> {
  const response = await http.post('/admin/roles', data)
  return response.data.data
}

/**
 * Update a role
 */
export async function updateRole(
  roleId: number,
  data: {
    display_name?: string
    description?: string
    hierarchy_level?: number
    color?: string
    icon?: string
  }
): Promise<void> {
  await http.put(`/admin/roles/${roleId}`, data)
}

/**
 * Delete a custom role
 */
export async function deleteRole(roleId: number): Promise<void> {
  await http.delete(`/admin/roles/${roleId}`)
}

// =============================================================================
// Permissions
// =============================================================================

/**
 * Get all available permissions
 */
export async function getPermissions(params?: {
  category?: string
  grouped?: boolean
}): Promise<Permission[] | Record<string, Permission[]>> {
  const response = await http.get('/admin/roles/permissions', { params })
  return response.data.data
}

/**
 * Get permissions grouped by category
 */
export async function getPermissionsGrouped(): Promise<Record<string, Permission[]>> {
  const response = await http.get('/admin/roles/permissions', {
    params: { grouped: true }
  })
  return response.data.data
}

// =============================================================================
// Role-Permission Assignments
// =============================================================================

/**
 * Get permissions for a role
 */
export async function getRolePermissions(roleId: number): Promise<Permission[]> {
  const response = await http.get(`/admin/roles/${roleId}/permissions`)
  return response.data.data
}

/**
 * Set permissions for a role (replaces all existing)
 */
export async function setRolePermissions(
  roleId: number,
  permissionIds: number[]
): Promise<void> {
  await http.put(`/admin/roles/${roleId}/permissions`, {
    permission_ids: permissionIds
  })
}

/**
 * Add single permission to role
 */
export async function addRolePermission(
  roleId: number,
  permissionId: number
): Promise<void> {
  await http.post(`/admin/roles/${roleId}/permissions/${permissionId}`)
}

/**
 * Remove single permission from role
 */
export async function removeRolePermission(
  roleId: number,
  permissionId: number
): Promise<void> {
  await http.delete(`/admin/roles/${roleId}/permissions/${permissionId}`)
}

// =============================================================================
// Role Users
// =============================================================================

/**
 * Get users with a specific role
 */
export async function getRoleUsers(
  roleId: number,
  limit = 100
): Promise<RoleUser[]> {
  const response = await http.get(`/admin/roles/${roleId}/users`, {
    params: { limit }
  })
  return response.data.data
}

/**
 * Assign role to a user
 */
export async function assignUserRole(
  roleId: number,
  userId: string
): Promise<void> {
  await http.put(`/admin/roles/${roleId}/users/${userId}`)
}

// =============================================================================
// User Permission Overrides
// =============================================================================

/**
 * Get user's effective permissions and overrides
 */
export async function getUserPermissions(userId: string): Promise<{
  effective: Array<{
    permission_key: string
    display_name: string
    module: string
    source: 'role' | 'user_override'
  }>
  overrides: UserPermissionOverride[]
}> {
  const response = await http.get(`/admin/roles/users/${userId}/permissions`)
  return response.data.data
}

/**
 * Set user permission override
 */
export async function setUserPermissionOverride(
  userId: string,
  permissionId: number,
  data: {
    granted: boolean
    expires_at?: string
    reason?: string
  }
): Promise<void> {
  await http.put(
    `/admin/roles/users/${userId}/permissions/${permissionId}`,
    data
  )
}

/**
 * Remove user permission override
 */
export async function removeUserPermissionOverride(
  userId: string,
  permissionId: number
): Promise<void> {
  await http.delete(`/admin/roles/users/${userId}/permissions/${permissionId}`)
}

/**
 * Check if user has a specific permission
 */
export async function checkUserPermission(
  userId: string,
  permissionKey: string
): Promise<boolean> {
  const response = await http.get(
    `/admin/roles/users/${userId}/check/${permissionKey}`
  )
  return response.data.data.has_permission
}

export default {
  // Roles
  getRoles,
  getRole,
  createRole,
  updateRole,
  deleteRole,
  // Permissions
  getPermissions,
  getPermissionsGrouped,
  // Role-Permission
  getRolePermissions,
  setRolePermissions,
  addRolePermission,
  removeRolePermission,
  // Role Users
  getRoleUsers,
  assignUserRole,
  // User Overrides
  getUserPermissions,
  setUserPermissionOverride,
  removeUserPermissionOverride,
  checkUserPermission
}
