/**
 * Groups API Service (Group-Based Access Control)
 *
 * Manages groups and group-based permissions (replaces legacy RBAC)
 *
 * Endpoints:
 * - GET /api/v1/admin/groups - List all groups
 * - POST /api/v1/admin/groups - Create new group
 * - GET /api/v1/admin/groups/<id> - Get group details
 * - PUT /api/v1/admin/groups/<id> - Update group
 * - DELETE /api/v1/admin/groups/<id> - Delete group
 * - GET /api/v1/admin/groups/<id>/members - List group members
 * - POST /api/v1/admin/groups/<id>/members - Add member to group
 * - DELETE /api/v1/admin/groups/<id>/members/<user_id> - Remove member
 * - GET /api/v1/admin/groups/<id>/permissions - List group permissions
 * - POST /api/v1/admin/groups/<id>/permissions - Grant permission to group
 * - DELETE /api/v1/admin/groups/<id>/permissions/<perm_id> - Revoke permission
 */

import api from '@/infrastructure/api/http'
import type {
  Group,
  GroupMember,
  GroupPermission
} from '@/presentation/components/admin/groups/types'

const BASE_URL = '/api/v1/admin/groups'

/**
 * Fetch all groups with pagination
 * @param limit - Max results (default: 20, max: 100)
 * @param offset - Skip N results (default: 0)
 * @returns Promise with groups array and total count
 */
export async function fetchGroups(
  limit: number = 20,
  offset: number = 0
): Promise<{ data: Group[]; total: number }> {
  const params = new URLSearchParams({
    limit: Math.min(limit, 100).toString(),
    offset: offset.toString()
  })

  const response = await api.get(`${BASE_URL}?${params.toString()}`)
  return response.data
}

/**
 * Fetch single group by ID
 * @param groupId - The group ID
 * @returns Promise with group data
 */
export async function fetchGroup(groupId: string): Promise<Group> {
  const response = await api.get(`${BASE_URL}/${groupId}`)
  return response.data.data
}

/**
 * Create new group
 * @param data - Group creation data
 * @returns Promise with created group
 */
export async function createGroup(data: {
  name: string
  slug: string
  type: 'system_admin' | 'org_admin' | 'custom'
  description?: string
}): Promise<Group> {
  const response = await api.post(BASE_URL, data)
  return response.data.data
}

/**
 * Update group
 * @param groupId - The group ID
 * @param data - Updated group data
 * @returns Promise with updated group
 */
export async function updateGroup(
  groupId: string,
  data: Partial<{
    name: string
    type: 'system_admin' | 'org_admin' | 'custom'
    description?: string
  }>
): Promise<Group> {
  const response = await api.put(`${BASE_URL}/${groupId}`, data)
  return response.data.data
}

/**
 * Delete group
 * @param groupId - The group ID
 * @returns Promise<void>
 */
export async function deleteGroup(groupId: string): Promise<void> {
  await api.delete(`${BASE_URL}/${groupId}`)
}

/**
 * Fetch group members
 * @param groupId - The group ID
 * @param limit - Max results (default: 50)
 * @param offset - Skip N results (default: 0)
 * @returns Promise with members array and total count
 */
export async function fetchGroupMembers(
  groupId: string,
  limit: number = 50,
  offset: number = 0
): Promise<{ data: GroupMember[]; total: number }> {
  const params = new URLSearchParams({
    limit: Math.min(limit, 100).toString(),
    offset: offset.toString()
  })

  const response = await api.get(
    `${BASE_URL}/${groupId}/members?${params.toString()}`
  )
  return response.data
}

/**
 * Add member to group
 * @param groupId - The group ID
 * @param userId - The user ID
 * @param role - Member role (owner, member, viewer)
 * @returns Promise with member data
 */
export async function addGroupMember(
  groupId: string,
  userId: string,
  role: 'owner' | 'member' | 'viewer' = 'member'
): Promise<GroupMember> {
  const response = await api.post(
    `${BASE_URL}/${groupId}/members`,
    { user_id: userId, role }
  )
  return response.data.data
}

/**
 * Remove member from group
 * @param groupId - The group ID
 * @param userId - The user ID
 * @returns Promise<void>
 */
export async function removeGroupMember(
  groupId: string,
  userId: string
): Promise<void> {
  await api.delete(`${BASE_URL}/${groupId}/members/${userId}`)
}

/**
 * Fetch group permissions
 * @param groupId - The group ID
 * @param limit - Max results (default: 50)
 * @param offset - Skip N results (default: 0)
 * @returns Promise with permissions array and total count
 */
export async function fetchGroupPermissions(
  groupId: string,
  limit: number = 50,
  offset: number = 0
): Promise<{ data: GroupPermission[]; total: number }> {
  const params = new URLSearchParams({
    limit: Math.min(limit, 100).toString(),
    offset: offset.toString()
  })

  const response = await api.get(
    `${BASE_URL}/${groupId}/permissions?${params.toString()}`
  )
  return response.data
}

/**
 * Grant permission to group
 * @param groupId - The group ID
 * @param permission - The permission code
 * @returns Promise with permission data
 */
export async function grantGroupPermission(
  groupId: string,
  permission: string
): Promise<GroupPermission> {
  const response = await api.post(
    `${BASE_URL}/${groupId}/permissions`,
    { permission }
  )
  return response.data.data
}

/**
 * Revoke permission from group
 * @param groupId - The group ID
 * @param permissionId - The permission ID
 * @returns Promise<void>
 */
export async function revokeGroupPermission(
  groupId: string,
  permissionId: string
): Promise<void> {
  await api.delete(`${BASE_URL}/${groupId}/permissions/${permissionId}`)
}

export default {
  fetchGroups,
  fetchGroup,
  createGroup,
  updateGroup,
  deleteGroup,
  fetchGroupMembers,
  addGroupMember,
  removeGroupMember,
  fetchGroupPermissions,
  grantGroupPermission,
  revokeGroupPermission
}
