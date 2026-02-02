/**
 * Age Gate Verification API
 *
 * Handles age verification for age-restricted content and features.
 * Implements multiple verification methods for comprehensive age confirmation.
 *
 * Endpoints:
 * - POST /compliance/age-gate/verify - Submit age verification
 * - GET /compliance/age-gate/verification/:verificationId - Check verification status
 * - GET /compliance/age-gate/restricted-content/:contentId - Get age restriction info
 * - POST /compliance/age-gate/parental-override - Request parental override
 */

import http from '@/infrastructure/api/http'
import type {
  AgeGateVerifyRequest,
  AgeGateVerifyResponse,
  AgeGateVerificationStatus,
  AgeGateRestrictedContent,
  AgeGateParentalOverrideRequest,
  AgeGateParentalOverrideResponse,
} from './types'

/**
 * Verify user's age for restricted content.
 *
 * Submit age verification to access age-restricted features or content.
 * Supports multiple verification methods for different confidence levels.
 *
 * Methods:
 * - `birth_date`: User enters their birth date
 * - `credit_card`: Credit card verification (age confirmation via cardholder age)
 * - `id_document`: Government ID upload and verification
 *
 * @param request - Age verification request with chosen verification method
 * @returns Verification result and content access status
 *
 * @example
 * const result = await verifyAge({
 *   content_id: 'course-mature-12345',
 *   verification_method: 'birth_date',
 *   birth_date: '1995-06-20'
 * })
 * if (result.verified) {
 *   console.log('Access granted to age-restricted content')
 * }
 */
export const verifyAge = async (request: AgeGateVerifyRequest): Promise<AgeGateVerifyResponse> => {
  const response = await http.post<{ success: boolean; data: AgeGateVerifyResponse }>(
    '/compliance/age-gate/verify',
    request
  )
  return response.data.data
}

/**
 * Check status of age verification.
 *
 * Track verification progress, especially for verification methods that
 * require manual review (ID documents).
 *
 * @param verificationId - ID from verifyAge response
 * @returns Verification status (pending, verified, rejected, expired)
 *
 * @example
 * const status = await getVerificationStatus('verify-99999')
 * if (status.status === 'verified') {
 *   console.log('Age verified successfully')
 * } else if (status.status === 'rejected') {
 *   console.log('Age verification rejected:', status.rejection_reason)
 * }
 */
export const getVerificationStatus = async (
  verificationId: string
): Promise<AgeGateVerificationStatus> => {
  const response = await http.get<{ success: boolean; data: AgeGateVerificationStatus }>(
    `/compliance/age-gate/verification/${verificationId}`
  )
  return response.data.data
}

/**
 * Get age restriction information for content.
 *
 * Retrieve minimum age requirement and restriction reason for a specific content item.
 * Used to show age gate before accessing restricted content.
 *
 * @param contentId - ID of content to check age restrictions
 * @returns Age restriction details
 *
 * @example
 * const restriction = await getContentAgeRestriction('course-mature-12345')
 * console.log(`Minimum age: ${restriction.minimum_age}`)
 * console.log(`Reason: ${restriction.restriction_reason}`)
 */
export const getContentAgeRestriction = async (contentId: string): Promise<AgeGateRestrictedContent> => {
  const response = await http.get<{ success: boolean; data: AgeGateRestrictedContent }>(
    `/compliance/age-gate/restricted-content/${contentId}`
  )
  return response.data.data
}

/**
 * Request parental override for age-restricted content.
 *
 * For users under the minimum age, request parent/guardian permission to access content.
 * Parent receives email with content details and age gap information.
 *
 * @param request - Override request with parent email and content context
 * @returns Request confirmation and status
 *
 * @example
 * const result = await requestParentalOverride({
 *   content_id: 'course-mature-12345',
 *   parent_email: 'parent@example.com',
 *   reason: 'I need this content for school assignment'
 * })
 * console.log('Request sent to:', result.parent_email)
 * console.log('Decision pending:', result.decision_pending)
 */
export const requestParentalOverride = async (
  request: AgeGateParentalOverrideRequest
): Promise<AgeGateParentalOverrideResponse> => {
  const response = await http.post<{ success: boolean; data: AgeGateParentalOverrideResponse }>(
    '/compliance/age-gate/parental-override',
    request
  )
  return response.data.data
}

/**
 * Get list of age-gated content user has already verified for.
 *
 * Retrieve list of all age-restricted content the user has been verified to access.
 * Used to avoid repeated age verifications.
 *
 * @returns List of verified age-restricted content
 *
 * @example
 * const verified = await getVerifiedContent()
 * console.log('You have access to', verified.length, 'age-restricted items')
 */
export const getVerifiedContent = async () => {
  const response = await http.get<{
    success: boolean
    data: Array<{
      content_id: string
      content_title: string
      minimum_age: number
      verified_date: string
      verification_method: string
    }>
  }>('/compliance/age-gate/verified-content')
  return response.data.data
}

/**
 * Clear age verification for specific content.
 *
 * Remove access to previously verified age-restricted content.
 * User will need to reverify age if they want to access it again.
 *
 * @param contentId - ID of content to clear verification for
 * @returns Confirmation of verification removal
 *
 * @example
 * await clearVerification('course-mature-12345')
 * console.log('Access removed from age-restricted content')
 */
export const clearVerification = async (contentId: string) => {
  const response = await http.post<{ success: boolean; data: { status: 'cleared' } }>(
    '/compliance/age-gate/clear-verification',
    { content_id: contentId }
  )
  return response.data.data
}

/**
 * Check if user is age-verified for specific content.
 *
 * Quick check to determine if user has already been age-verified for content.
 * Used before showing age gate dialog.
 *
 * @param contentId - ID of content to check
 * @returns Whether user is verified for this content
 *
 * @example
 * const isVerified = await isAgeVerifiedFor('course-mature-12345')
 * if (!isVerified) {
 *   // Show age gate
 * }
 */
export const isAgeVerifiedFor = async (contentId: string): Promise<boolean> => {
  try {
    const response = await http.get<{ success: boolean; data: { verified: boolean } }>(
      `/compliance/age-gate/is-verified/${contentId}`
    )
    return response.data.data.verified
  } catch {
    return false
  }
}
