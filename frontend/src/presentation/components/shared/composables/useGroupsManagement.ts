/**
 * useGroupsManagement Composable (GBA - Group-Based Access)
 * =========================================================
 *
 * Shared logic for groups management.
 * Replaces the legacy role-based system with GBA.
 *
 * GBA Architecture:
 * - Users belong to Groups
 * - Groups have Permissions
 * - No hierarchy_level or role-based checks
 */
import { ref, computed } from 'vue'
import {
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
  revokeGroupPermission,
  type Group,
  type GroupMember,
  type GroupPermission
} from '@/infrastructure/api/clients/admin/groups.api'

export function useGroupsManagement() {
  // State
  const groups = ref<Group[]>([])
  const selectedGroup = ref<Group | null>(null)
  const groupMembers = ref<GroupMember[]>([])
  const groupPermissions = ref<GroupPermission[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalGroups = ref(0)

  // Computed
  const systemGroups = computed(() =>
    groups.value.filter(g => g.type === 'system_admin')
  )
  const orgGroups = computed(() =>
    groups.value.filter(g => g.type === 'org_admin')
  )
  const customGroups = computed(() =>
    groups.value.filter(g => g.type === 'custom')
  )

  // Load all groups
  async function loadGroups(limit = 100, offset = 0) {
    loading.value = true
    error.value = null
    try {
      const result = await fetchGroups(limit, offset)
      groups.value = result.data
      totalGroups.value = result.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load groups'
      console.error('[GBA] Failed to load groups:', e)
    } finally {
      loading.value = false
    }
  }

  // Select a group and load its details
  async function selectGroup(group: Group) {
    selectedGroup.value = group
    error.value = null

    try {
      const [fullGroup, members, permissions] = await Promise.all([
        fetchGroup(group.id),
        fetchGroupMembers(group.id),
        fetchGroupPermissions(group.id)
      ])
      selectedGroup.value = fullGroup
      groupMembers.value = members.data
      groupPermissions.value = permissions.data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load group details'
      console.error('[GBA] Failed to load group details:', e)
    }
  }

  // Create new group
  async function handleCreateGroup(data: {
    name: string
    slug: string
    type: 'system_admin' | 'org_admin' | 'custom'
    description?: string
  }) {
    error.value = null
    try {
      await createGroup(data)
      await loadGroups()
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create group'
      console.error('[GBA] Failed to create group:', e)
      return false
    }
  }

  // Update group
  async function handleUpdateGroup(
    groupId: string,
    data: Partial<{
      name: string
      type: 'system_admin' | 'org_admin' | 'custom'
      description?: string
    }>
  ) {
    error.value = null
    try {
      await updateGroup(groupId, data)
      await loadGroups()
      if (selectedGroup.value?.id === groupId) {
        await selectGroup({ ...selectedGroup.value, ...data } as Group)
      }
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update group'
      console.error('[GBA] Failed to update group:', e)
      return false
    }
  }

  // Delete group
  async function handleDeleteGroup(group: Group) {
    // System groups cannot be deleted
    if (group.type === 'system_admin') {
      error.value = 'System groups cannot be deleted'
      return false
    }

    error.value = null
    try {
      await deleteGroup(group.id)
      if (selectedGroup.value?.id === group.id) {
        selectedGroup.value = null
        groupMembers.value = []
        groupPermissions.value = []
      }
      await loadGroups()
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete group'
      console.error('[GBA] Failed to delete group:', e)
      return false
    }
  }

  // Member management
  async function handleAddMember(
    groupId: string,
    userId: string,
    role: 'owner' | 'member' | 'viewer' = 'member'
  ) {
    error.value = null
    try {
      await addGroupMember(groupId, userId, role)
      if (selectedGroup.value?.id === groupId) {
        const members = await fetchGroupMembers(groupId)
        groupMembers.value = members.data
      }
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add member'
      console.error('[GBA] Failed to add member:', e)
      return false
    }
  }

  async function handleRemoveMember(groupId: string, userId: string) {
    error.value = null
    try {
      await removeGroupMember(groupId, userId)
      if (selectedGroup.value?.id === groupId) {
        groupMembers.value = groupMembers.value.filter(m => m.user_id !== userId)
      }
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to remove member'
      console.error('[GBA] Failed to remove member:', e)
      return false
    }
  }

  // Permission management
  async function handleGrantPermission(groupId: string, permission: string) {
    error.value = null
    try {
      await grantGroupPermission(groupId, permission)
      if (selectedGroup.value?.id === groupId) {
        const permissions = await fetchGroupPermissions(groupId)
        groupPermissions.value = permissions.data
      }
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to grant permission'
      console.error('[GBA] Failed to grant permission:', e)
      return false
    }
  }

  async function handleRevokePermission(groupId: string, permissionId: string) {
    error.value = null
    try {
      await revokeGroupPermission(groupId, permissionId)
      if (selectedGroup.value?.id === groupId) {
        groupPermissions.value = groupPermissions.value.filter(
          p => p.id !== permissionId
        )
      }
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to revoke permission'
      console.error('[GBA] Failed to revoke permission:', e)
      return false
    }
  }

  // Initialize
  async function initialize() {
    await loadGroups()
  }

  return {
    // State
    groups,
    selectedGroup,
    groupMembers,
    groupPermissions,
    loading,
    error,
    totalGroups,
    // Computed
    systemGroups,
    orgGroups,
    customGroups,
    // Methods
    loadGroups,
    selectGroup,
    createGroup: handleCreateGroup,
    updateGroup: handleUpdateGroup,
    deleteGroup: handleDeleteGroup,
    addMember: handleAddMember,
    removeMember: handleRemoveMember,
    grantPermission: handleGrantPermission,
    revokePermission: handleRevokePermission,
    initialize
  }
}

