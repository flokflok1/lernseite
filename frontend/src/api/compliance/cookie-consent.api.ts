/**
 * Cookie Consent Management API
 *
 * Handles cookie consent preferences, banner management, and tracking consent.
 * Ensures compliance with GDPR, CCPA, and ePrivacy regulations for cookie usage.
 *
 * Cookie Categories:
 * - Essential: Required for site functionality (never requires consent)
 * - Analytics: Tracking user behavior and site improvements
 * - Marketing: Targeted advertising and retargeting
 * - Performance: Site performance optimization
 *
 * Endpoints:
 * - GET /compliance/cookies/preferences - Get current cookie preferences
 * - POST /compliance/cookies/preferences - Update cookie preferences
 * - GET /compliance/cookies/banner-status - Check if banner should be shown
 * - POST /compliance/cookies/banner-dismissed - Mark banner as dismissed
 * - GET /compliance/cookies/policy - Get full cookie policy
 */

import http from '../http'
import type {
  CookiePreferences,
  CookiePreferencesUpdate,
  CookieBannerStatus,
  CookiePolicy,
} from './types'

/**
 * Get current cookie preferences.
 *
 * Retrieve the user's current cookie consent settings.
 * Essential cookies are always enabled.
 *
 * @returns Current cookie preferences for all categories
 *
 * @example
 * const prefs = await getCookiePreferences()
 * console.log('Analytics enabled:', prefs.analytics)
 * console.log('Marketing enabled:', prefs.marketing)
 */
export const getCookiePreferences = async (): Promise<CookiePreferences> => {
  const response = await http.get<{ success: boolean; data: CookiePreferences }>(
    '/compliance/cookies/preferences'
  )
  return response.data.data
}

/**
 * Update cookie preferences.
 *
 * Modify consent for different cookie categories. User can enable/disable
 * analytics, marketing, and performance cookies independently.
 * Essential cookies cannot be disabled.
 *
 * @param preferences - Updated cookie preferences
 * @returns Confirmation of preferences saved
 *
 * @example
 * const updated = await updateCookiePreferences({
 *   essential: true,  // Always true, cannot change
 *   analytics: true,
 *   marketing: false,
 *   performance: true
 * })
 * console.log('Preferences saved')
 * // Tracking scripts will be updated accordingly
 */
export const updateCookiePreferences = async (
  preferences: CookiePreferencesUpdate
): Promise<CookiePreferences> => {
  const response = await http.post<{ success: boolean; data: CookiePreferences }>(
    '/compliance/cookies/preferences',
    preferences
  )
  return response.data.data
}

/**
 * Check if cookie banner should be displayed.
 *
 * Determine whether to show the cookie consent banner based on:
 * - User's jurisdiction (GDPR, CCPA, ePrivacy)
 * - Whether user has already consented
 * - Banner dismissal history
 *
 * @returns Banner display status and configuration
 *
 * @example
 * const status = await getCookieBannerStatus()
 * if (status.should_show_banner) {
 *   // Display cookie consent banner
 *   console.log('Jurisdiction:', status.jurisdiction) // 'EU', 'CA', 'US'
 *   console.log('Banner position:', status.position) // 'bottom', 'top'
 * }
 */
export const getCookieBannerStatus = async (): Promise<CookieBannerStatus> => {
  const response = await http.get<{ success: boolean; data: CookieBannerStatus }>(
    '/compliance/cookies/banner-status'
  )
  return response.data.data
}

/**
 * Mark cookie banner as dismissed.
 *
 * Record that user has seen and dismissed the cookie banner.
 * Banner will not reappear unless preferences change.
 *
 * @param preferences - Preferences selected when dismissing banner
 * @returns Confirmation of dismissal recorded
 *
 * @example
 * await dismissCookieBanner({
 *   essential: true,
 *   analytics: true,
 *   marketing: false,
 *   performance: true
 * })
 * // Banner hidden, tracking updated based on selections
 */
export const dismissCookieBanner = async (preferences: CookiePreferencesUpdate) => {
  const response = await http.post<{
    success: boolean
    data: { status: 'dismissed'; tracked_preferences: CookiePreferences }
  }>('/compliance/cookies/banner-dismissed', preferences)
  return response.data.data
}

/**
 * Get full cookie policy document.
 *
 * Retrieve detailed explanation of all cookies used, their purpose,
 * retention period, and how user data is handled.
 *
 * @returns Complete cookie policy information
 *
 * @example
 * const policy = await getCookiePolicy()
 * console.log('Policy version:', policy.policy_version)
 * console.log('Total cookies used:', policy.cookies.length)
 * policy.cookies.forEach(cookie => {
 *   console.log(`${cookie.name}: ${cookie.purpose}`)
 *   console.log(`Duration: ${cookie.retention_days} days`)
 * })
 */
export const getCookiePolicy = async (): Promise<CookiePolicy> => {
  const response = await http.get<{ success: boolean; data: CookiePolicy }>(
    '/compliance/cookies/policy'
  )
  return response.data.data
}

/**
 * Accept all cookies (for quick consent).
 *
 * Quickly enable all non-essential cookies without visiting preferences page.
 * Useful for "Accept All" button in cookie banner.
 *
 * @returns Updated preferences with all cookies enabled
 *
 * @example
 * await acceptAllCookies()
 * console.log('All cookies enabled')
 */
export const acceptAllCookies = async (): Promise<CookiePreferences> => {
  return updateCookiePreferences({
    essential: true,
    analytics: true,
    marketing: true,
    performance: true,
  })
}

/**
 * Reject all non-essential cookies.
 *
 * Quickly disable all non-essential cookies without visiting preferences page.
 * Useful for "Reject All" button in cookie banner (where available by law).
 *
 * @returns Updated preferences with only essential cookies enabled
 *
 * @example
 * await rejectAllCookies()
 * console.log('All optional cookies disabled')
 */
export const rejectAllCookies = async (): Promise<CookiePreferences> => {
  return updateCookiePreferences({
    essential: true,
    analytics: false,
    marketing: false,
    performance: false,
  })
}

/**
 * Get list of all active cookies on this device.
 *
 * Retrieve detailed information about all cookies currently stored,
 * including values, expiration, and purpose.
 *
 * @returns List of active cookies with metadata
 *
 * @example
 * const cookies = await getActiveCookies()
 * cookies.forEach(cookie => {
 *   console.log(`${cookie.name} (${cookie.category})`)
 *   console.log(`Expires: ${cookie.expires_date}`)
 * })
 */
export const getActiveCookies = async () => {
  const response = await http.get<{
    success: boolean
    data: Array<{
      name: string
      category: string
      purpose: string
      expires_date: string
      value_preview?: string
    }>
  }>('/compliance/cookies/active-cookies')
  return response.data.data
}

/**
 * Clear cookies from specific category.
 *
 * Manually delete all cookies from a specific category (except essential).
 * Useful when user wants to withdraw consent for specific category.
 *
 * @param category - Cookie category to clear ('analytics', 'marketing', 'performance')
 * @returns Confirmation of cookies cleared
 *
 * @example
 * await clearCookieCategory('marketing')
 * console.log('Marketing cookies cleared')
 */
export const clearCookieCategory = async (
  category: 'analytics' | 'marketing' | 'performance'
) => {
  const response = await http.post<{
    success: boolean
    data: {
      status: 'cleared'
      cookies_removed: number
      category: string
    }
  }>('/compliance/cookies/clear-category', { category })
  return response.data.data
}

/**
 * Get user's consent history.
 *
 * View timeline of all cookie preference changes made by user,
 * including timestamps and IP addresses (for dispute resolution).
 *
 * @returns Chronological list of consent changes
 *
 * @example
 * const history = await getConsentHistory()
 * history.forEach(entry => {
 *   console.log(`${entry.timestamp}: ${entry.action}`)
 *   console.log(`Preferences: ${JSON.stringify(entry.preferences)}`)
 * })
 */
export const getConsentHistory = async () => {
  const response = await http.get<{
    success: boolean
    data: Array<{
      timestamp: string
      action: 'banner_dismissed' | 'preferences_updated' | 'all_accepted' | 'all_rejected'
      preferences: CookiePreferences
      ip_address_hash: string
    }>
  }>('/compliance/cookies/consent-history')
  return response.data.data
}
