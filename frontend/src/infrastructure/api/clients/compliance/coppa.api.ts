/**
 * COPPA Compliance API (Children's Online Privacy Protection Act)
 *
 * Handles child account protection, parental consent, and age verification
 * for COPPA compliance in the United States and similar child protection laws
 * in other jurisdictions.
 *
 * COPPA Requirements:
 * - Age verification before account creation
 * - Parental consent for users under 13
 * - Limited data collection from child accounts
 * - Parental access to child account information
 * - Easy deletion of child account data
 *
 * Endpoints:
 * - POST /compliance/coppa/verify-age - Verify user age
 * - POST /compliance/coppa/parental-consent - Submit parental consent
 * - GET /compliance/coppa/parental-consent/:consentId - Check consent status
 * - GET /compliance/coppa/account-status - Get child account status (for parents)
 * - POST /compliance/coppa/linked-parent - Link parent to child account
 * - GET /compliance/coppa/child-data - Get child's data (for parents)
 */

import http from '@/infrastructure/api/http'
import type {
  COPPAVerifyAgeRequest,
  COPPAVerifyAgeResponse,
  COPPAParentalConsentRequest,
  COPPAParentalConsentResponse,
  COPPAConsentStatus,
  COPPAAccountStatus,
  COPPALinkParentRequest,
  COPPAChildData,
} from './types'

/**
 * Verify user's age during account creation.
 *
 * Age verification must be performed before account is activated.
 * Users under 13 require parental consent; older users can proceed independently.
 *
 * @param request - Age verification request with birth date or ID verification
 * @returns Age verification result and next steps
 *
 * @example
 * const result = await verifyAge({
 *   birth_date: '2012-03-15',
 *   verification_method: 'birth_date'
 * })
 * if (result.age < 13) {
 *   console.log('Parental consent required')
 *   window.location.href = '/coppa/parental-consent'
 * }
 */
export const verifyAge = async (request: COPPAVerifyAgeRequest): Promise<COPPAVerifyAgeResponse> => {
  const response = await http.post<{ success: boolean; data: COPPAVerifyAgeResponse }>(
    '/compliance/coppa/verify-age',
    request
  )
  return response.data.data
}

/**
 * Submit parental consent for child account.
 *
 * Parent must provide verifiable consent (email, credit card verification, etc.)
 * before child account can be fully activated.
 *
 * @param request - Parental consent submission with parent email and verification
 * @returns Consent submission confirmation and verification status
 *
 * @example
 * const consent = await submitParentalConsent({
 *   child_account_id: 'user-12345',
 *   parent_email: 'parent@example.com',
 *   consent_method: 'email_verification',
 *   parent_name: 'Jane Doe'
 * })
 * console.log('Consent status:', consent.status) // 'pending_verification'
 */
export const submitParentalConsent = async (
  request: COPPAParentalConsentRequest
): Promise<COPPAParentalConsentResponse> => {
  const response = await http.post<{ success: boolean; data: COPPAParentalConsentResponse }>(
    '/compliance/coppa/parental-consent',
    request
  )
  return response.data.data
}

/**
 * Check status of parental consent process.
 *
 * Monitor parental consent verification progress. Consent must be verified
 * before child account can access features.
 *
 * @param consentId - Consent submission ID from submitParentalConsent
 * @returns Current consent verification status
 *
 * @example
 * const status = await getConsentStatus('consent-67890')
 * if (status.status === 'verified') {
 *   console.log('Child account is now active')
 * } else if (status.status === 'pending_parent_action') {
 *   console.log('Parent verification email sent to:', status.parent_email)
 * }
 */
export const getConsentStatus = async (consentId: string): Promise<COPPAConsentStatus> => {
  const response = await http.get<{ success: boolean; data: COPPAConsentStatus }>(
    `/compliance/coppa/parental-consent/${consentId}`
  )
  return response.data.data
}

/**
 * Get child account status (for parents).
 *
 * Retrieve current status and restrictions for a child account linked to parent.
 * Shows activity level, data usage, and feature access.
 *
 * @returns Child account status information and restrictions
 *
 * @example
 * const status = await getChildAccountStatus()
 * console.log('Last login:', status.last_login)
 * console.log('Features enabled:', status.enabled_features)
 * console.log('Data collected (MB):', status.data_storage_used_mb)
 */
export const getChildAccountStatus = async (): Promise<COPPAAccountStatus> => {
  const response = await http.get<{ success: boolean; data: COPPAAccountStatus }>(
    '/compliance/coppa/account-status'
  )
  return response.data.data
}

/**
 * Link parent to child account for monitoring.
 *
 * Establish parent-child account relationship for parental controls and monitoring.
 * Parent will receive verification email to confirm linkage.
 *
 * @param request - Parent account linking request with verification
 * @returns Link confirmation and next steps for verification
 *
 * @example
 * const result = await linkParentToChild({
 *   child_account_id: 'user-12345',
 *   parent_email: 'parent@example.com',
 *   relationship: 'parent'
 * })
 * console.log('Verification email sent to:', result.verification_email)
 */
export const linkParentToChild = async (request: COPPALinkParentRequest) => {
  const response = await http.post<{ success: boolean; data: any }>(
    '/compliance/coppa/linked-parent',
    request
  )
  return response.data.data
}

/**
 * Get child account data (for parents).
 *
 * Download all data collected from child account including:
 * - Profile information
 * - Learning progress
 * - Activity logs
 * - Content interactions
 * - Performance metrics
 *
 * @returns Complete child account data
 *
 * @example
 * const data = await getChildAccountData()
 * console.log('Profile:', data.profile)
 * console.log('Learning progress:', data.learning_progress)
 * console.log('Last 30 days activity:', data.activity_summary)
 */
export const getChildAccountData = async (): Promise<COPPAChildData> => {
  const response = await http.get<{ success: boolean; data: COPPAChildData }>(
    '/compliance/coppa/child-data'
  )
  return response.data.data
}

/**
 * Request child account deletion (for parents).
 *
 * Parent can request permanent deletion of child account and all associated data.
 * This action cannot be undone.
 *
 * @param childAccountId - ID of child account to delete
 * @returns Deletion confirmation with timeline
 *
 * @example
 * const result = await requestChildAccountDeletion('user-12345')
 * console.log('Account will be deleted on:', result.deletion_date)
 */
export const requestChildAccountDeletion = async (childAccountId: string) => {
  const response = await http.post<{
    success: boolean
    data: {
      status: 'scheduled'
      deletion_date: string
      confirmation_email_sent: boolean
    }
  }>('/compliance/coppa/request-deletion', { child_account_id: childAccountId })
  return response.data.data
}

/**
 * Get list of COPPA-restricted features.
 *
 * Retrieve which features are limited or disabled for child accounts
 * under COPPA regulations.
 *
 * @returns List of restricted features with reasoning
 *
 * @example
 * const restrictions = await getCOPPARestrictions()
 * restrictions.forEach(restriction => {
 *   console.log(`Feature: ${restriction.feature_name}`)
 *   console.log(`Reason: ${restriction.reason}`)
 * })
 */
export const getCOPPARestrictions = async () => {
  const response = await http.get<{
    success: boolean
    data: Array<{
      feature_name: string
      reason: 'data_protection' | 'contact_safety' | 'content_safety'
      available_at_age: number
    }>
  }>('/compliance/coppa/restrictions')
  return response.data.data
}
