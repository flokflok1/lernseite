/**
 * Compliance Components
 *
 * GDPR, COPPA, DSA compliance features
 *
 * Structure:
 * - admin/ - Admin compliance dashboards and controls
 * - user/ - User-facing compliance UIs (consent, reports, privacy)
 */

// Admin exports
export { default as ParentalControls } from './admin/ParentalControls.vue'
export { default as PrivacyDashboard } from './admin/PrivacyDashboard.vue'
export { default as TransparencyReport } from './admin/TransparencyReport.vue'

// User exports
export { default as AgeGate } from './user/AgeGate.vue'
export { default as ConsentManager } from './user/ConsentManager.vue'
export { default as ContentWarning } from './user/ContentWarning.vue'
export { default as CookieConsent } from './user/CookieConsent.vue'
export { default as CookieSettings } from './user/CookieSettings.vue'
export { default as DataDeletion } from './user/DataDeletion.vue'
export { default as DataExport } from './user/DataExport.vue'
export { default as ParentalConsent } from './user/ParentalConsent.vue'
export { default as ReportContent } from './user/ReportContent.vue'
export { default as ReportStatus } from './user/ReportStatus.vue'
export { default as SafeMode } from './user/SafeMode.vue'
export { default as ScreenTimeWidget } from './user/ScreenTimeWidget.vue'
