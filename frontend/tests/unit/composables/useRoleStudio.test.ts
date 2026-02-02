/**
 * Unit Tests for useRoleStudio Composable
 *
 * Tests:
 * - State management (roles, selectedRole, loading, error, pagination)
 * - All async operations (fetch, create, update, deactivate)
 * - Computed properties (sortedRoles, activeRoles, organizationRoles)
 * - Error handling and edge cases
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useRoleStudio } from '@/components/admin/role-studio/composables/useRoleStudio'
import * as roleStudioApi from '@/api/admin/role-studio.api'

// Mock API module
vi.mock('@/api/admin/role-studio.api')

const mockApi = roleStudioApi as any

describe('useRoleStudio Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('State Management', () => {
    it('should initialize with default state', () => {
      // Execute
      const { roles, selectedRole, loading, error, totalRoles, currentPage, pageSize } =
        useRoleStudio()

      // Assert
      expect(roles.value).toEqual([])
      expect(selectedRole.value).toBeNull()
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(totalRoles.value).toBe(0)
      expect(currentPage.value).toBe(1)
      expect(pageSize.value).toBe(10)
    })
  })

  describe('Computed Properties', () => {
    it('should compute sortedRoles', () => {
      // Execute
      const { sortedRoles } = useRoleStudio()

      // Mock roles after initialization
      const composable = useRoleStudio()
      ;(composable as any).roles.value = [
        { role_code: 'C', display_name: 'Zebra Role', is_active: true },
        { role_code: 'A', display_name: 'Admin Role', is_active: true },
        { role_code: 'B', display_name: 'Teacher Role', is_active: true }
      ]

      // Assert - should be sorted by display_name
      expect(composable.sortedRoles.value[0].display_name).toBe('Admin Role')
      expect(composable.sortedRoles.value[1].display_name).toBe('Teacher Role')
      expect(composable.sortedRoles.value[2].display_name).toBe('Zebra Role')
    })

    it('should compute activeRoles', () => {
      // Execute
      const composable = useRoleStudio()

      ;(composable as any).roles.value = [
        { role_code: 'A', display_name: 'Role A', is_active: true },
        { role_code: 'B', display_name: 'Role B', is_active: false },
        { role_code: 'C', display_name: 'Role C', is_active: true }
      ]

      // Assert
      expect(composable.activeRoles.value).toHaveLength(2)
      expect(composable.activeRoles.value.every((r: any) => r.is_active)).toBe(true)
    })

    it('should compute organizationRoles', () => {
      // Execute
      const composable = useRoleStudio()

      ;(composable as any).roles.value = [
        { role_code: 'A', display_name: 'Role A', requires_organization: true },
        { role_code: 'B', display_name: 'Role B', requires_organization: false },
        { role_code: 'C', display_name: 'Role C', requires_organization: true }
      ]

      // Assert
      expect(composable.organizationRoles.value).toHaveLength(2)
      expect(composable.organizationRoles.value.every((r: any) => r.requires_organization)).toBe(
        true
      )
    })
  })

  describe('fetchRoles', () => {
    it('should fetch roles successfully', async () => {
      // Setup
      const mockRoles = [
        {
          role_code: 'ROLE1',
          display_name: 'Role 1',
          is_active: true,
          requires_organization: false
        },
        {
          role_code: 'ROLE2',
          display_name: 'Role 2',
          is_active: true,
          requires_organization: true
        }
      ]

      mockApi.fetchRoles.mockResolvedValue({
        roles: mockRoles,
        total: 2
      })

      const composable = useRoleStudio()

      // Execute
      await composable.fetchRoles()

      // Assert
      expect(composable.roles.value).toEqual(mockRoles)
      expect(composable.totalRoles.value).toBe(2)
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
    })

    it('should handle filter parameter', async () => {
      // Setup
      mockApi.fetchRoles.mockResolvedValue({
        roles: [],
        total: 0
      })

      const composable = useRoleStudio()

      // Execute
      await composable.fetchRoles('active')

      // Assert
      expect(mockApi.fetchRoles).toHaveBeenCalledWith(1, 10, 'active')
    })

    it('should handle errors during fetch', async () => {
      // Setup
      const error = new Error('Network error')
      mockApi.fetchRoles.mockRejectedValue(error)

      const composable = useRoleStudio()

      // Execute
      await composable.fetchRoles()

      // Assert
      expect(composable.error.value).toBe('Network error')
      expect(composable.roles.value).toEqual([])
      expect(composable.loading.value).toBe(false)
    })

    it('should set loading state during fetch', async () => {
      // Setup
      mockApi.fetchRoles.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve({ roles: [], total: 0 }), 100)
          })
      )

      const composable = useRoleStudio()

      // Execute
      const fetchPromise = composable.fetchRoles()
      expect(composable.loading.value).toBe(true)

      await fetchPromise
      expect(composable.loading.value).toBe(false)
    })
  })

  describe('fetchRole', () => {
    it('should fetch single role by code', async () => {
      // Setup
      const mockRole = {
        role_code: 'SYSTEM_ADMIN',
        display_name: 'System Administrator',
        description: 'Full system access',
        is_active: true,
        requires_organization: false
      }

      mockApi.fetchRole.mockResolvedValue(mockRole)

      const composable = useRoleStudio()

      // Execute
      const result = await composable.fetchRole('SYSTEM_ADMIN')

      // Assert
      expect(result).toEqual(mockRole)
      expect(composable.selectedRole.value).toEqual(mockRole)
      expect(mockApi.fetchRole).toHaveBeenCalledWith('SYSTEM_ADMIN')
    })

    it('should return null for non-existent role', async () => {
      // Setup
      mockApi.fetchRole.mockRejectedValue(new Error('Not found'))

      const composable = useRoleStudio()

      // Execute
      const result = await composable.fetchRole('NONEXISTENT')

      // Assert
      expect(result).toBeNull()
      expect(composable.error.value).toBe('Not found')
    })
  })

  describe('createRole', () => {
    it('should create new role', async () => {
      // Setup
      const newRoleData = {
        role_code: 'NEW_ROLE',
        display_name: 'New Role',
        description: 'New role description',
        permissions: '["read"]'
      }

      const createdRole = {
        ...newRoleData,
        is_active: true,
        requires_organization: false,
        created_at: '2026-01-14T10:00:00Z'
      }

      mockApi.createRole.mockResolvedValue(createdRole)

      const composable = useRoleStudio()
      ;(composable as any).roles.value = []

      // Execute
      const result = await composable.createRole(newRoleData as any)

      // Assert
      expect(result).toEqual(createdRole)
      expect(composable.roles.value).toContain(createdRole)
      expect(mockApi.createRole).toHaveBeenCalledWith(newRoleData)
    })

    it('should handle creation errors', async () => {
      // Setup
      mockApi.createRole.mockRejectedValue(new Error('Validation error'))

      const composable = useRoleStudio()

      // Execute & Assert
      expect(composable.createRole({} as any)).rejects.toThrow('Validation error')
    })
  })

  describe('updateRole', () => {
    it('should update existing role', async () => {
      // Setup
      const roleCode = 'TEST_ROLE'
      const updates = { display_name: 'Updated Name' }

      const updatedRole = {
        role_code: roleCode,
        display_name: 'Updated Name',
        is_active: true
      }

      mockApi.updateRole.mockResolvedValue(updatedRole)

      const composable = useRoleStudio()
      ;(composable as any).roles.value = [
        {
          role_code: roleCode,
          display_name: 'Old Name',
          is_active: true
        }
      ]

      // Execute
      const result = await composable.updateRole(roleCode, updates)

      // Assert
      expect(result).toEqual(updatedRole)
      expect(composable.roles.value[0].display_name).toBe('Updated Name')
      expect(mockApi.updateRole).toHaveBeenCalledWith(roleCode, updates)
    })

    it('should update selectedRole if it matches', async () => {
      // Setup
      const roleCode = 'TEST_ROLE'
      const updatedRole = {
        role_code: roleCode,
        display_name: 'Updated',
        is_active: true
      }

      mockApi.updateRole.mockResolvedValue(updatedRole)

      const composable = useRoleStudio()
      ;(composable as any).selectedRole.value = {
        role_code: roleCode,
        display_name: 'Old',
        is_active: true
      }

      // Execute
      await composable.updateRole(roleCode, { display_name: 'Updated' })

      // Assert
      expect(composable.selectedRole.value).toEqual(updatedRole)
    })
  })

  describe('deactivateRole', () => {
    it('should deactivate role', async () => {
      // Setup
      const roleCode = 'TEST_ROLE'
      const deactivatedRole = {
        role_code: roleCode,
        display_name: 'Test Role',
        is_active: false
      }

      mockApi.deactivateRole.mockResolvedValue(deactivatedRole)

      const composable = useRoleStudio()
      ;(composable as any).roles.value = [
        {
          role_code: roleCode,
          display_name: 'Test Role',
          is_active: true
        }
      ]

      // Execute
      await composable.deactivateRole(roleCode)

      // Assert
      expect(composable.roles.value[0].is_active).toBe(false)
      expect(mockApi.deactivateRole).toHaveBeenCalledWith(roleCode)
    })
  })

  describe('fetchChangeHistory', () => {
    it('should fetch change history', async () => {
      // Setup
      const mockHistory = [
        {
          history_id: 'hist1',
          role_code: 'TEST_ROLE',
          action: 'UPDATE',
          changed_by: 'admin-1',
          timestamp: '2026-01-14T10:00:00Z'
        }
      ]

      mockApi.fetchChangeHistory.mockResolvedValue({
        history: mockHistory,
        total: 1
      })

      const composable = useRoleStudio()

      // Execute
      const result = await composable.fetchChangeHistory('TEST_ROLE', 1)

      // Assert
      expect(result).toEqual(mockHistory)
      expect(composable.changeHistory.value).toEqual(mockHistory)
      expect(mockApi.fetchChangeHistory).toHaveBeenCalledWith('TEST_ROLE', 1, 10)
    })
  })

  describe('Selection Management', () => {
    it('should select role', () => {
      // Setup
      const role = {
        role_code: 'TEST_ROLE',
        display_name: 'Test Role',
        is_active: true
      }

      const composable = useRoleStudio()

      // Execute
      composable.selectRole(role as any)

      // Assert
      expect(composable.selectedRole.value).toEqual(role)
    })

    it('should clear selection', () => {
      // Setup
      const composable = useRoleStudio()
      ;(composable as any).selectedRole.value = { role_code: 'TEST' }

      // Execute
      composable.clearSelection()

      // Assert
      expect(composable.selectedRole.value).toBeNull()
    })

    it('should clear error', () => {
      // Setup
      const composable = useRoleStudio()
      ;(composable as any).error.value = 'Some error'

      // Execute
      composable.clearError()

      // Assert
      expect(composable.error.value).toBeNull()
    })
  })

  describe('Pagination', () => {
    it('should set current page', () => {
      // Setup
      const composable = useRoleStudio()

      // Execute
      ;(composable as any).setCurrentPage(5)

      // Assert
      expect(composable.currentPage.value).toBe(5)
    })

    it('should set page size', () => {
      // Setup
      const composable = useRoleStudio()

      // Execute
      ;(composable as any).setPageSize(50)

      // Assert
      expect(composable.pageSize.value).toBe(50)
    })
  })
})
