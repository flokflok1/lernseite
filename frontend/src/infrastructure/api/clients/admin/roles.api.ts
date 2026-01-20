/**
 * Admin Roles & Permissions API
 * ==============================
 * API client for managing roles, permissions, and user assignments.
 */

import http from '@/infrastructure/api/http'

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
// RBAC 2.0 Types (Owner-Admin Custom Roles)
// =============================================================================

export interface SystemFeature {
  feature_id: number
  feature_code: string
  feature_name: string
  category: string
  active: boolean
  enabled_for_role?: boolean
}

export interface RoleWithStats extends Role {
  feature_count?: number
  permission_count?: number
  user_count?: number
  features?: SystemFeature[]
}

export interface RoleTemplate {
  template: 'parent' | 'enterprise_admin' | 'auditor' | 'librarian' | 'course_manager'
  display_name: string
  description: string
  recommended_hierarchy: number
  default_features: string[]
  default_color: string
  default_icon: string
}

export interface CreateRoleRequest {
  role_name: string
  display_name: string
  description?: string
  hierarchy_level: number
  color?: string
  icon?: string
  feature_ids?: number[]
  permission_ids?: number[]
}

export interface UpdateRoleRequest {
  display_name?: string
  description?: string
  hierarchy_level?: number
  color?: string
  icon?: string
}

export interface AssignFeaturesRequest {
  feature_ids: number[]
  replace?: boolean
}

export interface AssignPermissionsRequest {
  permission_ids: number[]
  replace?: boolean
}

export interface CreateFromTemplateRequest {
  template: 'parent' | 'enterprise_admin' | 'auditor' | 'librarian' | 'course_manager'
  role_name: string
  display_name?: string
  customize_features?: number[]
}

export interface DeleteRoleResponse {
  success: boolean
  message: string
  affected_users: number
  reassigned_to_role?: string
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

// =============================================================================
// RBAC 2.0 API (Owner-Admin Custom Roles)
// =============================================================================

/**
 * Get all roles with filtering and statistics (RBAC 2.0)
 */
export async function getRolesV2(params?: {
  is_custom?: boolean
  hierarchy_min?: number
  hierarchy_max?: number
  search?: string
  include_features?: boolean
  include_permissions?: boolean
}): Promise<{ roles: RoleWithStats[]; total: number }> {
  const response = await http.get('/admin/roles', { params })
  return response.data.data
}

/**
 * Get role details with features and permissions (RBAC 2.0)
 */
export async function getRoleV2(roleId: number): Promise<RoleWithStats> {
  const response = await http.get(`/admin/roles/${roleId}`)
  return response.data.data
}

/**
 * Create custom role with features and permissions (RBAC 2.0)
 */
export async function createRoleV2(data: CreateRoleRequest): Promise<RoleWithStats> {
  const response = await http.post('/admin/roles', data)
  return response.data.data
}

/**
 * Update custom role (RBAC 2.0)
 */
export async function updateRoleV2(
  roleId: number,
  data: UpdateRoleRequest
): Promise<RoleWithStats> {
  const response = await http.put(`/admin/roles/${roleId}`, data)
  return response.data.data
}

/**
 * Delete custom role with user reassignment (RBAC 2.0)
 */
export async function deleteRoleV2(
  roleId: number,
  reassignTo?: number
): Promise<DeleteRoleResponse> {
  const response = await http.delete(`/admin/roles/${roleId}`, {
    params: { reassign_to: reassignTo }
  })
  return response.data.data
}

/**
 * Assign system features to role (RBAC 2.0)
 */
export async function assignRoleFeatures(
  roleId: number,
  data: AssignFeaturesRequest
): Promise<{ features_assigned: number; total_features: number }> {
  const response = await http.post(`/admin/roles/${roleId}/features`, data)
  return response.data.data
}

/**
 * Assign permissions to role (RBAC 2.0)
 */
export async function assignRolePermissionsV2(
  roleId: number,
  data: AssignPermissionsRequest
): Promise<{ permissions_assigned: number; total_permissions: number }> {
  const response = await http.post(`/admin/roles/${roleId}/permissions`, data)
  return response.data.data
}

/**
 * Get all role templates (RBAC 2.0)
 */
export async function getRoleTemplates(): Promise<RoleTemplate[]> {
  const response = await http.get('/admin/roles/templates')
  return response.data.data.templates
}

/**
 * Create role from template (RBAC 2.0)
 */
export async function createRoleFromTemplate(
  data: CreateFromTemplateRequest
): Promise<RoleWithStats> {
  const response = await http.post('/admin/roles/from-template', data)
  return response.data.data
}

/**
 * Get all system features (for feature assignment)
 */
export async function getSystemFeatures(): Promise<SystemFeature[]> {
  const response = await http.get('/admin/roles/system-features')
  return response.data.data
}

export default {
  // Roles (Legacy)
  getRoles,
  getRole,
  createRole,
  updateRole,
  deleteRole,
  // Permissions (Legacy)
  getPermissions,
  getPermissionsGrouped,
  // Role-Permission (Legacy)
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
  checkUserPermission,
  // RBAC 2.0 (Owner-Admin)
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
}
