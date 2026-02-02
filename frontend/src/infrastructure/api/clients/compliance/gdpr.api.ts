/**
 * GDPR Compliance API (General Data Protection Regulation)
 *
 * Handles user data export, deletion requests, and consent management
 * for GDPR compliance across the EU and regions with similar regulations.
 *
 * Endpoints:
 * - POST /compliance/gdpr/export-request - Request personal data export
 * - GET /compliance/gdpr/export-status/:requestId - Check export status
 * - POST /compliance/gdpr/delete-request - Request account deletion
 * - GET /compliance/gdpr/delete-status/:requestId - Check deletion status
 * - GET /compliance/gdpr/consent - Get current consent status
 * - POST /compliance/gdpr/consent - Update consent preferences
 */

import http from '@/infrastructure/api/http'
import type {
  GDPRExportRequest,
  GDPRExportResponse,
  GDPRExportStatus,
  GDPRDeleteRequest,
  GDPRDeleteResponse,
  GDPRDeleteStatus,
  GDPRConsentRequest,
  GDPRConsent,
} from './types'

/**
 * Request personal data export (GDPR Article 15 - Right of Access).
 *
 * User can request a copy of all their personal data in machine-readable format.
 * Export is typically generated within 30 days.
 *
 * @param request - Export request with email confirmation
 * @returns Unique request ID for tracking export status
 *
 * @example
 * const { request_id } = await requestDataExport({
 *   email: 'user@example.com',
 *   format: 'json'
 * })
 * console.log('Export requested:', request_id)
 */
export const requestDataExport = async (request: GDPRExportRequest): Promise<GDPRExportResponse> => {
  const response = await http.post<{ success: boolean; data: GDPRExportResponse }>(
    '/compliance/gdpr/export-request',
    request
  )
  return response.data.data
}

/**
 * Get status of data export request.
 *
 * Check the current status and progress of a GDPR data export request.
 *
 * @param requestId - Export request ID from requestDataExport
 * @returns Export status (pending, processing, ready, expired)
 *
 * @example
 * const status = await getExportStatus('export-12345')
 * if (status.status === 'ready') {
 *   window.location.href = status.download_url
 * }
 */
export const getExportStatus = async (requestId: string): Promise<GDPRExportStatus> => {
  const response = await http.get<{ success: boolean; data: GDPRExportStatus }>(
    `/compliance/gdpr/export-status/${requestId}`
  )
  return response.data.data
}

/**
 * Request account deletion (GDPR Article 17 - Right to be Forgotten).
 *
 * Initiates the account deletion process. User must confirm via email.
 * Account is permanently deleted after confirmation and grace period.
 *
 * @param request - Deletion request with reason and email confirmation
 * @returns Unique request ID for tracking deletion status
 *
 * @example
 * const { request_id } = await requestAccountDeletion({
 *   email: 'user@example.com',
 *   reason: 'account_not_needed',
 *   password: 'currentPassword'
 * })
 */
export const requestAccountDeletion = async (request: GDPRDeleteRequest): Promise<GDPRDeleteResponse> => {
  const response = await http.post<{ success: boolean; data: GDPRDeleteResponse }>(
    '/compliance/gdpr/delete-request',
    request
  )
  return response.data.data
}

/**
 * Get status of account deletion request.
 *
 * Check the current status of a GDPR account deletion request.
 * Status progresses from pending → confirmed → processing → deleted.
 *
 * @param requestId - Deletion request ID from requestAccountDeletion
 * @returns Deletion status with timeline information
 *
 * @example
 * const status = await getDeletionStatus('delete-67890')
 * console.log(`Account will be deleted on: ${status.scheduled_deletion_date}`)
 */
export const getDeletionStatus = async (requestId: string): Promise<GDPRDeleteStatus> => {
  const response = await http.get<{ success: boolean; data: GDPRDeleteStatus }>(
    `/compliance/gdpr/delete-status/${requestId}`
  )
  return response.data.data
}

/**
 * Get current GDPR consent status.
 *
 * Retrieve user's current consent preferences for different data processing categories.
 *
 * @returns Current consent status for all categories
 *
 * @example
 * const consent = await getConsentStatus()
 * console.log('Marketing:', consent.marketing)
 * console.log('Analytics:', consent.analytics)
 */
export const getConsentStatus = async (): Promise<GDPRConsent> => {
  const response = await http.get<{ success: boolean; data: GDPRConsent }>(
    '/compliance/gdpr/consent'
  )
  return response.data.data
}

/**
 * Update GDPR consent preferences.
 *
 * Modify consent for different data processing purposes.
 * Essential consent cannot be changed (required for service).
 *
 * @param request - New consent preferences
 * @returns Updated consent status
 *
 * @example
 * const updated = await updateConsent({
 *   marketing: false,
 *   analytics: true,
 *   third_party_sharing: false
 * })
 */
export const updateConsent = async (request: GDPRConsentRequest): Promise<GDPRConsent> => {
  const response = await http.post<{ success: boolean; data: GDPRConsent }>(
    '/compliance/gdpr/consent',
    request
  )
  return response.data.data
}

/**
 * Withdraw all non-essential consents.
 *
 * Quickly withdraw all optional consents while keeping essential consent active.
 *
 * @returns Updated consent status with all non-essential consents withdrawn
 *
 * @example
 * const updated = await withdrawAllConsents()
 * console.log('All optional consents withdrawn')
 */
export const withdrawAllConsents = async (): Promise<GDPRConsent> => {
  return updateConsent({
    marketing: false,
    analytics: false,
    third_party_sharing: false,
    personalization: false,
  })
}
