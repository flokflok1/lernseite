/**
 * Role Studio API Service
 * Handles all API calls for role studio management
 *
 * Endpoints:
 * - GET /api/v1/admin/role-studio/modes - List all roles
 * - POST /api/v1/admin/role-studio/modes - Create new role
 * - PUT /api/v1/admin/role-studio/modes/<code> - Update role
 * - DELETE /api/v1/admin/role-studio/modes/<code> - Deactivate role
 * - GET /api/v1/admin/role-studio/modes/<code>/history - Get change history
 */

import api from '@/infrastructure/api/http'
import type {
  RoleStudioMode,
  CreateRoleStudioRequest,
  RoleChangeHistory,
  StudioConfig as StudioConfigResponse
} from '@/presentation/components/role-studio.types'

const BASE_URL = '/admin/role-studio'

/**
 * Fetch all roles with pagination
 * @param page - Page number (default: 1)
 * @param pageSize - Items per page (default: 20)
 * @param filter - Optional filter for role status (active/inactive)
 * @returns Promise with roles array and total count
 */
export async function fetchRoles(
  page: number = 1,
  pageSize: number = 20,
  filter?: 'active' | 'inactive'
): Promise<{ roles: RoleStudioMode[]; total: number }> {
  const params = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString()
  })

  if (filter) {
    params.append('filter', filter)
  }

  const response = await api.get(`${BASE_URL}/modes?${params.toString()}`)
  return response.data
}

/**
 * Fetch single role by code
 * @param roleCode - The role code identifier
 * @returns Promise with role data
 */
export async function fetchRole(roleCode: string): Promise<RoleStudioMode> {
  const response = await api.get(`${BASE_URL}/modes/${roleCode}`)
  return response.data
}

/**
 * Create new role
 * @param data - Role creation data
 * @returns Promise with created role
 */
export async function createRole(
  data: CreateRoleStudioRequest
): Promise<RoleStudioMode> {
  const response = await api.post(`${BASE_URL}/modes`, data)
  return response.data
}

/**
 * Update existing role
 * @param roleCode - The role code to update
 * @param data - Updated role data
 * @returns Promise with updated role
 */
export async function updateRole(
  roleCode: string,
  data: Partial<CreateRoleStudioRequest>
): Promise<RoleStudioMode> {
  const response = await api.put(`${BASE_URL}/modes/${roleCode}`, data)
  return response.data
}

/**
 * Deactivate role (soft delete)
 * @param roleCode - The role code to deactivate
 * @returns Promise with deactivated role
 */
export async function deactivateRole(roleCode: string): Promise<RoleStudioMode> {
  const response = await api.delete(`${BASE_URL}/modes/${roleCode}`)
  return response.data
}

/**
 * Fetch change history for a role
 * @param roleCode - The role code to get history for
 * @param page - Page number (default: 1)
 * @param pageSize - Items per page (default: 10)
 * @returns Promise with history entries and total count
 */
export async function fetchChangeHistory(
  roleCode: string,
  page: number = 1,
  pageSize: number = 10
): Promise<{ history: RoleChangeHistory[]; total: number }> {
  const params = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString()
  })

  const response = await api.get(
    `${BASE_URL}/modes/${roleCode}/history?${params.toString()}`
  )
  return response.data
}

/**
 * Get studio config for current user
 * Called during login to determine available studio features
 * @returns Promise with studio configuration
 */
export async function getStudioConfig(): Promise<StudioConfigResponse> {
  const response = await api.get(`${BASE_URL}/config`)
  return response.data
}

export default {
  fetchRoles,
  fetchRole,
  createRole,
  updateRole,
  deactivateRole,
  fetchChangeHistory,
  getStudioConfig
}
