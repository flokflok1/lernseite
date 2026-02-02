/**
 * Compliance Domain Types
 *
 * TypeScript interfaces for all compliance-related API requests and responses.
 * Organized by compliance framework: GDPR, DSA, COPPA, Age Gate, Cookie Consent.
 */

// ============================================================================
// GDPR Types (General Data Protection Regulation)
// ============================================================================

export interface GDPRExportRequest {
  /** User email for confirmation */
  email: string
  /** Requested export format */
  format: 'json' | 'csv' | 'pdf'
  /** Optional: data categories to include (leave empty for all) */
  data_categories?: string[]
}

export interface GDPRExportResponse {
  /** Unique request ID for tracking */
  request_id: string
  /** Status of export request */
  status: 'pending' | 'processing' | 'ready' | 'expired'
  /** When export was requested */
  requested_at: string
  /** Estimated completion date (ISO format) */
  estimated_completion: string
}

export interface GDPRExportStatus {
  /** Current status of export */
  status: 'pending' | 'processing' | 'ready' | 'expired'
  /** Progress percentage (0-100) */
  progress_percent: number
  /** Size of export in MB (when ready) */
  file_size_mb?: number
  /** Download URL (when ready) */
  download_url?: string
  /** When export was created */
  created_at: string
  /** When export will expire (30 days after ready) */
  expires_at?: string
  /** Error message (if failed) */
  error?: string
}

export interface GDPRDeleteRequest {
  /** User email for confirmation */
  email: string
  /** Reason for deletion */
  reason:
    | 'account_not_needed'
    | 'privacy_concerns'
    | 'switching_services'
    | 'other'
  /** Current password confirmation */
  password: string
  /** Optional comment */
  comment?: string
}

export interface GDPRDeleteResponse {
  /** Unique request ID for tracking */
  request_id: string
  /** Status of deletion request */
  status: 'pending' | 'confirmed' | 'processing' | 'deleted'
  /** When deletion was requested */
  requested_at: string
  /** Grace period before permanent deletion (14 days) */
  grace_period_end: string
}

export interface GDPRDeleteStatus {
  /** Current deletion status */
  status: 'pending' | 'confirmed' | 'processing' | 'deleted'
  /** Scheduled deletion date (ISO format) */
  scheduled_deletion_date: string
  /** Confirmation deadline */
  confirmation_deadline?: string
  /** Whether deletion has been confirmed */
  confirmed: boolean
  /** Data being retained for legal reasons */
  retained_for_legal?: string[]
}

export interface GDPRConsentRequest {
  /** Consent for marketing communications */
  marketing?: boolean
  /** Consent for analytics and usage tracking */
  analytics?: boolean
  /** Consent for third-party data sharing */
  third_party_sharing?: boolean
  /** Consent for personalization and recommendations */
  personalization?: boolean
}

export interface GDPRConsent extends GDPRConsentRequest {
  /** Whether consents are essential (cannot be withdrawn) */
  essential: boolean
  /** When consent was last updated */
  last_updated: string
  /** IP address used for consent (hashed) */
  ip_address_hash: string
  /** Unique consent record ID */
  consent_record_id: string
}

// ============================================================================
// DSA Types (Digital Services Act)
// ============================================================================

export interface DSAReportRequest {
  /** ID of content being reported */
  content_id: string
  /** Type of content */
  content_type: 'post' | 'comment' | 'video' | 'image' | 'user' | 'other'
  /** Type of violation */
  violation_type:
    | 'harassment'
    | 'hate_speech'
    | 'misinformation'
    | 'illegal_content'
    | 'copyright'
    | 'spam'
    | 'nudity'
    | 'violence'
    | 'other'
  /** Detailed description of the violation */
  description: string
  /** Optional: supporting evidence URLs */
  evidence_urls?: string[]
}

export interface DSAReportResponse {
  /** Unique report ID for tracking */
  report_id: string
  /** When report was submitted */
  submitted_at: string
  /** Confirmation of submission */
  status: 'submitted' | 'under_review'
}

export interface DSAReport extends DSAReportResponse {
  /** Current status of report */
  status: 'pending' | 'under_review' | 'resolved' | 'dismissed'
  /** Moderator's decision (if resolved) */
  moderator_decision?: 'upheld' | 'dismissed' | 'partial'
  /** Reasoning for decision */
  moderator_reasoning?: string
  /** When decision was made */
  decision_date?: string
  /** Actions taken */
  actions_taken?: string[]
  /** Whether user can appeal */
  can_appeal: boolean
}

export interface DSAReportList {
  /** Array of reports */
  data: DSAReport[]
  /** Total number of user's reports */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
}

export interface DSAAppealRequest {
  /** ID of moderation decision being appealed */
  moderation_decision_id: string
  /** ID of content involved */
  content_id: string
  /** Reason for appealing */
  reason: string
  /** Supporting evidence or arguments */
  additional_evidence?: string
}

export interface DSAAppealResponse {
  /** Unique appeal ID for tracking */
  appeal_id: string
  /** Status of appeal */
  status: 'submitted' | 'under_review'
  /** When appeal was submitted */
  submitted_at: string
}

export interface DSAAppeal extends DSAAppealResponse {
  /** Current status of appeal */
  status: 'pending' | 'under_review' | 'upheld' | 'overturned'
  /** Appeal board's decision */
  decision_outcome?: 'upheld' | 'overturned' | 'partial'
  /** Reasoning for appeal decision */
  decision_reasoning?: string
  /** When decision was made */
  decision_date?: string
  /** Corrective actions if overturned */
  corrective_actions?: string[]
}

export interface DSAAppealList {
  /** Array of appeals */
  data: DSAAppeal[]
  /** Total number of user's appeals */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
}

// ============================================================================
// COPPA Types (Children's Online Privacy Protection Act)
// ============================================================================

export interface COPPAVerifyAgeRequest {
  /** Birth date for age verification */
  birth_date?: string // ISO format: YYYY-MM-DD
  /** Verification method used */
  verification_method: 'birth_date' | 'credit_card' | 'id_document'
}

export interface COPPAVerifyAgeResponse {
  /** Calculated age */
  age: number
  /** Whether user is age 13+ */
  age_13_or_older: boolean
  /** Next required action */
  required_action?: 'parental_consent_required' | 'none'
  /** If parental consent required, token for next step */
  consent_token?: string
}

export interface COPPAParentalConsentRequest {
  /** Child's account ID */
  child_account_id: string
  /** Parent's email for verification */
  parent_email: string
  /** Verification method */
  consent_method: 'email_verification' | 'credit_card' | 'id_verification'
  /** Parent's name */
  parent_name: string
  /** Optional relationship field */
  relationship?: 'parent' | 'guardian' | 'other'
}

export interface COPPAParentalConsentResponse {
  /** Consent submission ID */
  consent_id: string
  /** Status of consent verification */
  status: 'pending_verification' | 'verified' | 'rejected'
  /** Verification method */
  verification_method: string
  /** When consent was submitted */
  submitted_at: string
}

export interface COPPAConsentStatus {
  /** Current verification status */
  status: 'pending_parent_action' | 'pending_verification' | 'verified' | 'rejected'
  /** Parent email consent was sent to */
  parent_email: string
  /** Expiration of verification link (if pending) */
  verification_expires_at?: string
  /** Reason for rejection (if rejected) */
  rejection_reason?: string
}

export interface COPPAAccountStatus {
  /** Child account status */
  status: 'pending_consent' | 'consent_verified' | 'restricted' | 'deleted'
  /** Last login date */
  last_login?: string
  /** Features enabled for child account */
  enabled_features: string[]
  /** Data storage used in MB */
  data_storage_used_mb: number
  /** Data retention policy (days) */
  data_retention_days: number
}

export interface COPPALinkParentRequest {
  /** Child account ID to link parent to */
  child_account_id: string
  /** Parent email for verification */
  parent_email: string
  /** Relationship type */
  relationship: 'parent' | 'guardian'
}

export interface COPPAChildData {
  /** Child's profile information */
  profile: {
    account_id: string
    name: string
    email: string
    created_at: string
  }
  /** Learning progress summary */
  learning_progress: {
    courses_enrolled: number
    courses_completed: number
    average_score: number
    total_learning_hours: number
  }
  /** Last 30 days activity summary */
  activity_summary: {
    login_count: number
    last_login: string
    content_viewed: number
    assignments_completed: number
  }
}

// ============================================================================
// Age Gate Types
// ============================================================================

export interface AgeGateVerifyRequest {
  /** Content ID requiring age verification */
  content_id: string
  /** Age verification method */
  verification_method: 'birth_date' | 'credit_card' | 'id_document'
  /** Birth date if using that method */
  birth_date?: string
}

export interface AgeGateVerifyResponse {
  /** Verification ID for tracking */
  verification_id: string
  /** Whether age verification was successful */
  verified: boolean
  /** User's age (if verified) */
  age?: number
  /** Whether user meets minimum requirement */
  meets_requirement: boolean
}

export interface AgeGateVerificationStatus {
  /** Verification status */
  status: 'pending' | 'verified' | 'rejected' | 'expired'
  /** Reason for rejection (if rejected) */
  rejection_reason?: string
  /** When verification expires */
  expires_at?: string
}

export interface AgeGateRestrictedContent {
  /** Content ID */
  content_id: string
  /** Content title */
  content_title: string
  /** Minimum age required */
  minimum_age: number
  /** Reason for age restriction */
  restriction_reason: 'mature_content' | 'violence' | 'adult' | 'other'
  /** Detailed description */
  restriction_description: string
}

export interface AgeGateParentalOverrideRequest {
  /** Content ID */
  content_id: string
  /** Parent/guardian email */
  parent_email: string
  /** Reason for requesting override */
  reason: string
}

export interface AgeGateParentalOverrideResponse {
  /** Request ID for tracking */
  request_id: string
  /** Status of override request */
  status: 'pending' | 'approved' | 'rejected'
  /** Parent email override sent to */
  parent_email: string
  /** Decision deadline */
  decision_deadline: string
}

// ============================================================================
// Cookie Consent Types
// ============================================================================

export interface CookiePreferences {
  /** Essential cookies (always true) */
  essential: boolean
  /** Analytics cookies */
  analytics: boolean
  /** Marketing/advertising cookies */
  marketing: boolean
  /** Performance cookies */
  performance: boolean
  /** When preferences were last updated */
  last_updated: string
}

export interface CookiePreferencesUpdate {
  /** Essential cookies (always true, cannot change) */
  essential?: boolean
  /** Analytics cookies */
  analytics?: boolean
  /** Marketing cookies */
  marketing?: boolean
  /** Performance cookies */
  performance?: boolean
}

export interface CookieBannerStatus {
  /** Whether banner should be displayed */
  should_show_banner: boolean
  /** User's jurisdiction for cookie law */
  jurisdiction: 'EU' | 'CA' | 'US' | 'other'
  /** Banner display position */
  position: 'bottom' | 'top' | 'center'
  /** Whether user has already consented */
  user_has_consented: boolean
  /** When banner was last shown */
  last_shown?: string
}

export interface CookiePolicy {
  /** Policy version */
  policy_version: string
  /** When policy was last updated */
  last_updated: string
  /** Full text of cookie policy */
  policy_text: string
  /** Array of cookies used */
  cookies: Array<{
    name: string
    category: 'essential' | 'analytics' | 'marketing' | 'performance'
    purpose: string
    retention_days: number
    provider: string
  }>
}
