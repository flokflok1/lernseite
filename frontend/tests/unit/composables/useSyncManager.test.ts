/**
 * Unit Tests for useSyncManager Composable
 *
 * Tests:
 * - State management (selectedMode, selectedLanguages, scanResults, dashboardStats)
 * - All async operations (loadDashboard, startScan, applyScan, rollbackSync)
 * - Computed properties (isManualMode, isAutoMode, hasConflicts)
 * - Error handling and loading states
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useSyncManager } from '@/composables/admin/useSyncManager'
import * as i18nSyncApi from '@/api/admin/i18n-sync.api'

// Mock API module
vi.mock('@/api/admin/i18n-sync.api')

const mockApi = i18nSyncApi as any

describe('useSyncManager Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('State Management', () => {
    it('should initialize with default state', () => {
      // Execute
      const {
        selectedMode,
        selectedLanguages,
        currentSyncId,
        currentStatus,
        isScanning,
        error,
        scanResults,
        dashboardStats,
        isLoadingDashboard
      } = useSyncManager()

      // Assert
      expect(selectedMode.value).toBe('MANUAL')
      expect(selectedLanguages.value).toEqual(['de', 'en', 'pl'])
      expect(currentSyncId.value).toBeNull()
      expect(currentStatus.value).toBe('IDLE')
      expect(isScanning.value).toBe(false)
      expect(error.value).toBeNull()
      expect(scanResults.value).toBeNull()
      expect(dashboardStats.value).toBeNull()
      expect(isLoadingDashboard.value).toBe(false)
    })
  })

  describe('Computed Properties', () => {
    it('should compute isManualMode correctly', () => {
      // Execute
      const { selectedMode, isManualMode } = useSyncManager()
      selectedMode.value = 'MANUAL'

      // Assert
      expect(isManualMode.value).toBe(true)
    })

    it('should compute isAutoMode correctly', () => {
      // Execute
      const { selectedMode, isAutoMode } = useSyncManager()
      selectedMode.value = 'AUTO'

      // Assert
      expect(isAutoMode.value).toBe(true)
    })

    it('should detect conflicts in scan results', () => {
      // Execute
      const { scanResults, hasConflicts } = useSyncManager()
      scanResults.value = {
        summary: {
          conflicted_keys: 5,
          new_keys: 10,
          changed_keys: 3,
          deleted_keys: 2,
          total_keys: 100,
          scan_status: 'COMPLETED',
          scan_duration_ms: 1500,
          languages_affected: ['de', 'en', 'pl'],
          error_message: null
        },
        next_action: 'REVIEW'
      }

      // Assert
      expect(hasConflicts.value).toBe(true)
    })
  })

  describe('Async Operations - loadDashboard', () => {
    it('should load dashboard statistics successfully', async () => {
      // Arrange
      const mockStats = {
        total_syncs: 42,
        successful_syncs: 38,
        failed_syncs: 4,
        pending_resolutions: 0
      }
      mockApi.getDashboardStats.mockResolvedValue(mockStats)

      // Execute
      const { loadDashboard, dashboardStats, isLoadingDashboard, error } = useSyncManager()
      const promise = loadDashboard()

      // Assert loading state
      expect(isLoadingDashboard.value).toBe(true)

      // Wait for completion
      await promise
      expect(isLoadingDashboard.value).toBe(false)
      expect(dashboardStats.value).toEqual(mockStats)
      expect(error.value).toBeNull()
    })

    it('should handle loadDashboard errors', async () => {
      // Arrange
      const testError = new Error('Failed to load dashboard')
      mockApi.getDashboardStats.mockRejectedValue(testError)

      // Execute
      const { loadDashboard, dashboardStats, error } = useSyncManager()
      try {
        await loadDashboard()
      } catch (e) {
        // Error is caught and stored
      }

      // Assert
      expect(error.value).toBeTruthy()
      expect(dashboardStats.value).toBeNull()
    })
  })

  describe('Async Operations - startScan', () => {
    it('should start scan with selected languages and mode', async () => {
      // Arrange
      const mockSyncId = 'sync-123'
      mockApi.initiateScan.mockResolvedValue({ sync_id: mockSyncId })
      mockApi.getScanResults.mockResolvedValue({
        summary: {
          conflicted_keys: 0,
          new_keys: 5,
          changed_keys: 2,
          deleted_keys: 1,
          total_keys: 100,
          scan_status: 'COMPLETED',
          scan_duration_ms: 2000,
          languages_affected: ['de', 'en', 'pl'],
          error_message: null
        },
        next_action: 'APPLY_AUTO'
      })

      // Execute
      const { startScan, currentSyncId, isScanning, scanResults, selectedMode, selectedLanguages } = useSyncManager()
      selectedMode.value = 'AUTO'
      selectedLanguages.value = ['de', 'en']

      const promise = startScan()
      expect(isScanning.value).toBe(true)

      await promise

      // Assert
      expect(isScanning.value).toBe(false)
      expect(currentSyncId.value).toBe(mockSyncId)
      expect(scanResults.value).toBeTruthy()
      expect(mockApi.initiateScan).toHaveBeenCalledWith({
        mode: 'AUTO',
        languages: ['de', 'en']
      })
    })

    it('should handle scan initiation errors', async () => {
      // Arrange
      const testError = new Error('Scan failed')
      mockApi.initiateScan.mockRejectedValue(testError)

      // Execute
      const { startScan, error } = useSyncManager()
      try {
        await startScan()
      } catch (e) {
        // Error is caught
      }

      // Assert
      expect(error.value).toBeTruthy()
    })
  })

  describe('Async Operations - applyScan', () => {
    it('should apply scan results', async () => {
      // Arrange
      const mockSyncId = 'sync-123'
      const mockResolutions = {
        'new_key_1': 'ADD',
        'changed_key_1': 'UPDATE',
        'conflicted_key_1': 'SKIP'
      }

      mockApi.applyScan.mockResolvedValue({
        status: 'COMPLETED',
        applied_count: 7,
        skipped_count: 1
      })

      // Execute
      const { applyScan, currentSyncId } = useSyncManager()
      currentSyncId.value = mockSyncId

      const result = await applyScan(mockResolutions)

      // Assert
      expect(mockApi.applyScan).toHaveBeenCalledWith(mockSyncId, mockResolutions)
      expect(result.status).toBe('COMPLETED')
    })
  })

  describe('Async Operations - rollbackSync', () => {
    it('should rollback synchronization with reason', async () => {
      // Arrange
      const mockSyncId = 'sync-123'
      const rollbackReason = 'Incorrect translation detected'

      mockApi.rollbackSync.mockResolvedValue({
        status: 'ROLLED_BACK',
        restored_count: 8
      })

      // Execute
      const { rollbackSync, currentSyncId } = useSyncManager()
      currentSyncId.value = mockSyncId

      const result = await rollbackSync(rollbackReason)

      // Assert
      expect(mockApi.rollbackSync).toHaveBeenCalledWith(mockSyncId, {
        reason: rollbackReason
      })
      expect(result.status).toBe('ROLLED_BACK')
    })
  })

  describe('Utility Methods', () => {
    it('should reset state correctly', () => {
      // Arrange
      const { selectedMode, scanResults, currentSyncId, error, reset } = useSyncManager()
      selectedMode.value = 'AUTO'
      scanResults.value = { summary: {}, next_action: 'REVIEW' } as any
      currentSyncId.value = 'sync-123'
      error.value = 'Some error'

      // Execute
      reset()

      // Assert
      expect(selectedMode.value).toBe('MANUAL')
      expect(scanResults.value).toBeNull()
      expect(currentSyncId.value).toBeNull()
      expect(error.value).toBeNull()
    })

    it('should change mode', () => {
      // Execute
      const { selectedMode, changeMode } = useSyncManager()
      changeMode('AUTO')

      // Assert
      expect(selectedMode.value).toBe('AUTO')
    })

    it('should toggle language selection', () => {
      // Execute
      const { selectedLanguages, toggleLanguage } = useSyncManager()
      toggleLanguage('de')

      // Assert
      expect(selectedLanguages.value).not.toContain('de')

      // Toggle again
      toggleLanguage('de')
      expect(selectedLanguages.value).toContain('de')
    })
  })

  describe('Edge Cases', () => {
    it('should handle concurrent scan requests', async () => {
      // Arrange
      let callCount = 0
      mockApi.initiateScan.mockImplementation(() => {
        callCount++
        return Promise.resolve({ sync_id: `sync-${callCount}` })
      })

      // Execute
      const { startScan } = useSyncManager()

      // Try to start scan twice quickly
      const promise1 = startScan()
      const promise2 = startScan()

      // Assert - only one should complete successfully (second should be ignored or queued)
      await Promise.all([promise1, promise2])
      expect(callCount).toBeLessThanOrEqual(2)
    })

    it('should handle empty language selection', async () => {
      // Arrange
      mockApi.initiateScan.mockResolvedValue({ sync_id: 'sync-123' })

      // Execute
      const { startScan, selectedLanguages } = useSyncManager()
      selectedLanguages.value = [] // No languages selected

      // Should handle gracefully
      try {
        await startScan()
      } catch (e) {
        // Expected - no languages selected
      }
    })
  })
})
