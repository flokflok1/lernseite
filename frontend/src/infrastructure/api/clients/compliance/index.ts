/**
 * Compliance Domain Barrel Export
 * ====================================================
 *
 * Clean interface for all compliance-related APIs.
 * Consolidates GDPR, DSA, COPPA, Age Gate, and Cookie Consent endpoints.
 *
 * Usage:
 * import { requestDataExport, getConsentStatus } from '@/infrastructure/api/compliance'
 * import type { GDPRExportResponse, CookiePreferences } from '@/infrastructure/api/compliance'
 */

// ============================================================================
// Types Export (Consolidated)
// ============================================================================

export type {
  // GDPR Types
  GDPRExportRequest,
  GDPRExportResponse,
  GDPRExportStatus,
  GDPRDeleteRequest,
  GDPRDeleteResponse,
  GDPRDeleteStatus,
  GDPRConsentRequest,
  GDPRConsent,
  // DSA Types
  DSAReportRequest,
  DSAReportResponse,
  DSAReport,
  DSAReportList,
  DSAAppealRequest,
  DSAAppealResponse,
  DSAAppeal,
  DSAAppealList,
  // COPPA Types
  COPPAVerifyAgeRequest,
  COPPAVerifyAgeResponse,
  COPPAParentalConsentRequest,
  COPPAParentalConsentResponse,
  COPPAConsentStatus,
  COPPAAccountStatus,
  COPPALinkParentRequest,
  COPPAChildData,
  // Age Gate Types
  AgeGateVerifyRequest,
  AgeGateVerifyResponse,
  AgeGateVerificationStatus,
  AgeGateRestrictedContent,
  AgeGateParentalOverrideRequest,
  AgeGateParentalOverrideResponse,
  // Cookie Consent Types
  CookiePreferences,
  CookiePreferencesUpdate,
  CookieBannerStatus,
  CookiePolicy,
} from './types'

// ============================================================================
// GDPR API Export
// ============================================================================

export {
  requestDataExport,
  getExportStatus,
  requestAccountDeletion,
  getDeletionStatus,
  getConsentStatus as getGDPRConsentStatus,
  updateConsent as updateGDPRConsent,
  withdrawAllConsents,
} from './gdpr.api'

// ============================================================================
// DSA API Export (Digital Services Act)
// ============================================================================

export {
  reportContent,
  getMyReports,
  getReportDetails,
  appealModerationDecision,
  getMyAppeals,
  getAppealDetails,
  getDSATransparencyReport,
} from './dsa.api'

// ============================================================================
// COPPA API Export (Children's Online Privacy Protection)
// ============================================================================

export {
  verifyAge as coppaVerifyAge,
  submitParentalConsent,
  getConsentStatus as getCOPPAConsentStatus,
  getChildAccountStatus,
  linkParentToChild,
  getChildAccountData,
  requestChildAccountDeletion,
  getCOPPARestrictions,
} from './coppa.api'

// ============================================================================
// Age Gate API Export
// ============================================================================

export {
  verifyAge as verifyAgeGate,
  getVerificationStatus as getAgeVerificationStatus,
  getContentAgeRestriction,
  requestParentalOverride,
  getVerifiedContent,
  clearVerification,
  isAgeVerifiedFor,
} from './age-gate.api'

// ============================================================================
// Cookie Consent API Export
// ============================================================================

export {
  getCookiePreferences,
  updateCookiePreferences,
  getCookieBannerStatus,
  dismissCookieBanner,
  getCookiePolicy,
  acceptAllCookies,
  rejectAllCookies,
  getActiveCookies,
  clearCookieCategory,
  getConsentHistory,
} from './cookie-consent.api'
