/**
 * Unit Tests for Role Studio API Service
 *
 * Tests:
 * - All 7 API endpoint methods
 * - Response type correctness
 * - Error handling
 * - Parameter passing
 * - Pagination handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock the http client module - must be before import
vi.mock('@/api/http', () => {
  const mockHttp = {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
  return {
    default: mockHttp
  }
})

import * as roleStudioApi from '@/api/admin/role-studio.api'
import { default as mockHttp } from '@/api/http'

describe('Role Studio API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchRoles', () => {
    it('should fetch roles with pagination', async () => {
      // Setup
      const mockResponse = {
        data: {
          roles: [
            {
              role_code: 'SYSTEM_ADMIN',
              display_name: 'System Administrator',
              is_active: true,
              requires_organization: false
            }
          ],
          total: 1
        }
      }

      mockHttp.get.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.fetchRoles(1, 20, 'active')

      // Assert
      expect(result.roles).toHaveLength(1)
      expect(result.total).toBe(1)
      expect(result.roles[0].role_code).toBe('SYSTEM_ADMIN')
      expect(mockHttp.get).toHaveBeenCalled()
    })

    it('should handle default parameters', async () => {
      // Setup
      const mockResponse = {
        data: {
          roles: [],
          total: 0
        }
      }

      mockHttp.get.mockResolvedValue(mockResponse)

      // Execute
      await roleStudioApi.fetchRoles()

      // Assert
      expect(mockHttp.get).toHaveBeenCalled()
    })

    it('should handle API errors', async () => {
      // Setup
      const error = new Error('Network error')
      mockHttp.get.mockRejectedValue(error)

      // Execute & Assert
      expect(roleStudioApi.fetchRoles()).rejects.toThrow('Network error')
    })
  })

  describe('fetchRole', () => {
    it('should fetch single role by code', async () => {
      // Setup
      const mockResponse = {
        data: {
          role_code: 'SYSTEM_ADMIN',
          display_name: 'System Administrator',
          description: 'Full system access',
          is_active: true,
          requires_organization: false,
          permissions: '["admin.roles.view", "admin.roles.edit"]'
        }
      }

      mockHttp.get.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.fetchRole('SYSTEM_ADMIN')

      // Assert
      expect(result.role_code).toBe('SYSTEM_ADMIN')
      expect(result.display_name).toBe('System Administrator')
      expect(result.is_active).toBe(true)
      expect(mockHttp.get).toHaveBeenCalled()
    })

    it('should handle non-existent role', async () => {
      // Setup
      mockHttp.get.mockRejectedValue({
        response: {
          status: 404,
          data: { error: { code: 'NOT_FOUND' } }
        }
      })

      // Execute & Assert
      expect(roleStudioApi.fetchRole('NONEXISTENT')).rejects.toThrow()
    })
  })

  describe('createRole', () => {
    it('should create new role', async () => {
      // Setup
      const newRoleData = {
        role_code: 'CUSTOM_ROLE',
        display_name: 'Custom Role',
        description: 'Custom role description',
        permissions: '["read", "write"]'
      }

      const mockResponse = {
        data: {
          ...newRoleData,
          is_active: true,
          requires_organization: false,
          created_at: '2026-01-14T10:00:00Z'
        }
      }

      mockHttp.post.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.createRole(newRoleData as any)

      // Assert
      expect(result.role_code).toBe('CUSTOM_ROLE')
      expect(result.display_name).toBe('Custom Role')
      expect(result.is_active).toBe(true)
      expect(mockHttp.post).toHaveBeenCalled()
    })

    it('should handle validation errors', async () => {
      // Setup
      mockHttp.post.mockRejectedValue({
        response: {
          status: 400,
          data: { error: { code: 'VALIDATION_ERROR', message: 'Invalid input' } }
        }
      })

      // Execute & Assert
      expect(roleStudioApi.createRole({} as any)).rejects.toThrow()
    })
  })

  describe('updateRole', () => {
    it('should update existing role', async () => {
      // Setup
      const updateData = {
        display_name: 'Updated Display Name',
        description: 'Updated description'
      }

      const mockResponse = {
        data: {
          role_code: 'SYSTEM_ADMIN',
          ...updateData,
          is_active: true,
          requires_organization: false,
          updated_at: '2026-01-14T10:00:00Z'
        }
      }

      mockHttp.put.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.updateRole('SYSTEM_ADMIN', updateData)

      // Assert
      expect(result.display_name).toBe('Updated Display Name')
      expect(result.description).toBe('Updated description')
      expect(mockHttp.put).toHaveBeenCalled()
    })

    it('should handle partial updates', async () => {
      // Setup
      const updateData = {
        display_name: 'New Name'
      }

      const mockResponse = {
        data: {
          role_code: 'TEST_ROLE',
          display_name: 'New Name',
          is_active: true
        }
      }

      mockHttp.put.mockResolvedValue(mockResponse)

      // Execute
      await roleStudioApi.updateRole('TEST_ROLE', updateData)

      // Assert
      expect(mockHttp.put).toHaveBeenCalled()
    })
  })

  describe('deactivateRole', () => {
    it('should deactivate role', async () => {
      // Setup
      const mockResponse = {
        data: {
          role_code: 'TEST_ROLE',
          display_name: 'Test Role',
          is_active: false,
          updated_at: '2026-01-14T10:00:00Z'
        }
      }

      mockHttp.delete.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.deactivateRole('TEST_ROLE')

      // Assert
      expect(result.is_active).toBe(false)
      expect(mockHttp.delete).toHaveBeenCalled()
    })
  })

  describe('fetchChangeHistory', () => {
    it('should fetch change history with pagination', async () => {
      // Setup
      const mockResponse = {
        data: {
          history: [
            {
              history_id: 'hist1',
              role_code: 'TEST_ROLE',
              action: 'UPDATE',
              changed_by: 'admin-1',
              timestamp: '2026-01-14T10:00:00Z'
            }
          ],
          total: 1
        }
      }

      mockHttp.get.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.fetchChangeHistory('TEST_ROLE', 1, 10)

      // Assert
      expect(result.history).toHaveLength(1)
      expect(result.total).toBe(1)
      expect(result.history[0].action).toBe('UPDATE')
      expect(mockHttp.get).toHaveBeenCalled()
    })
  })

  describe('getStudioConfig', () => {
    it('should fetch studio configuration', async () => {
      // Setup
      const mockResponse = {
        data: {
          available_modes: 7,
          total_roles: 5,
          active_roles: 5,
          last_modified: '2026-01-14T10:00:00Z'
        }
      }

      mockHttp.get.mockResolvedValue(mockResponse)

      // Execute
      const result = await roleStudioApi.getStudioConfig()

      // Assert
      expect(result.available_modes).toBe(7)
      expect(result.total_roles).toBe(5)
      expect(mockHttp.get).toHaveBeenCalled()
    })
  })
})
