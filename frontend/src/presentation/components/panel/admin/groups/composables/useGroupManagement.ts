/**
 * useGroupManagement Composable
 *
 * Manages group CRUD operations and permissions (Group-Based Access Control)
 */

import { ref } from 'vue'
import {
  fetchGroups as fetchGroupsAPI,
  createGroup as createGroupAPI,
  updateGroup as updateGroupAPI,
  deleteGroup as deleteGroupAPI
} from '@/application/services/api/panel-admin'
import type { Group } from '../types'

export function useGroupManagement() {
  const groups = ref<Group[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(0)
  const pageSize = ref(20)

  /**
   * Load groups from API
   */
  const loadGroups = async (page: number = 0, limit: number = 20) => {
    isLoading.value = true
    error.value = null
    try {
      const result = await fetchGroupsAPI(limit, page * limit)
      groups.value = result.data
      currentPage.value = page
      pageSize.value = limit
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load groups'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create new group
   */
  const createNew = async (groupData: {
    name: string
    slug: string
    type: 'system_admin' | 'org_admin' | 'custom'
    description?: string
  }) => {
    try {
      error.value = null
      const newGroup = await createGroupAPI(groupData)
      groups.value.push(newGroup)
      return newGroup
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create group'
      throw err
    }
  }

  /**
   * Update existing group
   */
  const update = async (
    groupId: string,
    updates: Partial<{
      name: string
      type: 'system_admin' | 'org_admin' | 'custom'
      description?: string
    }>
  ) => {
    try {
      error.value = null
      const updated = await updateGroupAPI(groupId, updates)
      const index = groups.value.findIndex(g => g.id === groupId)
      if (index >= 0) {
        groups.value[index] = updated
      }
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update group'
      throw err
    }
  }

  /**
   * Delete group
   */
  const remove = async (groupId: string) => {
    try {
      error.value = null
      await deleteGroupAPI(groupId)
      groups.value = groups.value.filter(g => g.id !== groupId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete group'
      throw err
    }
  }

  return {
    // State
    groups,
    isLoading,
    error,
    currentPage,
    pageSize,

    // Methods
    loadGroups,
    createNew,
    update,
    remove
  }
}
