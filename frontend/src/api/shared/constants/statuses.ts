/**
 * Shared Status Constants
 *
 * Central location for all status value constants used across domains.
 * Provides both string values and object-based lookups.
 *
 * Usage:
 * import { MODERATION_STATUS, USER_STATUS } from '@/api/shared/constants'
 *
 * // Use in conditions:
 * if (item.status === MODERATION_STATUS.PENDING) { }
 *
 * // Use in dropdowns:
 * const options = Object.entries(USER_STATUS).map(([key, value]) => ({
 *   label: key,
 *   value
 * }))
 */

/**
 * Moderation queue item statuses.
 * Lifecycle states: pending → assigned → on_hold/resolved
 */
export const MODERATION_STATUS = {
  PENDING: 'pending',
  ASSIGNED: 'assigned',
  ON_HOLD: 'on_hold',
  RESOLVED: 'resolved',
} as const

/**
 * Review session statuses.
 * States during active content review process.
 */
export const REVIEW_STATUS = {
  ACTIVE: 'active',
  SUBMITTED: 'submitted',
  COMPLETED: 'completed',
  ABANDONED: 'abandoned',
} as const

/**
 * Appeal statuses.
 * Lifecycle of user appeals against moderation decisions.
 */
export const APPEAL_STATUS = {
  PENDING: 'pending',
  IN_REVIEW: 'in_review',
  DECIDED: 'decided',
} as const

/**
 * Approval workflow statuses.
 * Generic states for items requiring approval.
 */
export const APPROVAL_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  NEEDS_REVIEW: 'needs_review',
} as const

/**
 * Async processing statuses.
 * States of background jobs and async operations.
 */
export const PROCESSING_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

/**
 * Compliance request statuses.
 * Lifecycle of GDPR/DSA/COPPA compliance requests.
 */
export const COMPLIANCE_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  READY: 'ready',
  EXPIRED: 'expired',
} as const

/**
 * Content availability statuses.
 * Visibility and accessibility states of content.
 */
export const CONTENT_STATUS = {
  AVAILABLE: 'available',
  REMOVED: 'removed',
  RESTRICTED: 'restricted',
  ARCHIVED: 'archived',
} as const

/**
 * User account statuses.
 * States of user accounts.
 */
export const USER_STATUS = {
  ACTIVE: 'active',
  SUSPENDED: 'suspended',
  BANNED: 'banned',
  PENDING_VERIFICATION: 'pending_verification',
  INACTIVE: 'inactive',
} as const

/**
 * Enforcement action statuses.
 * States of moderation enforcement (warn, restrict, remove, suspend).
 */
export const ACTION_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

/**
 * Notification delivery statuses.
 * States of notification messages.
 */
export const NOTIFICATION_STATUS = {
  SENT: 'sent',
  DELIVERED: 'delivered',
  READ: 'read',
  FAILED: 'failed',
  BOUNCED: 'bounced',
} as const

/**
 * User consent statuses (GDPR, COPPA).
 * User data processing consent state.
 */
export const CONSENT_STATUS = {
  NOT_GIVEN: 'not_given',
  GIVEN: 'given',
  WITHDRAWN: 'withdrawn',
  EXPIRED: 'expired',
} as const

/**
 * Feature flag statuses.
 * Rollout states of feature flags.
 */
export const FEATURE_FLAG_STATUS = {
  DISABLED: 'disabled',
  ENABLED: 'enabled',
  ROLLING_OUT: 'rolling_out',
  ROLLED_BACK: 'rolled_back',
} as const

/**
 * Terminal statuses (no further state changes possible).
 * Useful for checking if an entity is in a final state.
 */
export const TERMINAL_STATUSES = {
  MODERATION: [MODERATION_STATUS.RESOLVED],
  REVIEW: [REVIEW_STATUS.COMPLETED, REVIEW_STATUS.ABANDONED],
  APPEAL: [APPEAL_STATUS.DECIDED],
  PROCESSING: [PROCESSING_STATUS.COMPLETED, PROCESSING_STATUS.FAILED],
  COMPLIANCE: [COMPLIANCE_STATUS.READY, COMPLIANCE_STATUS.EXPIRED],
  ACTION: [ACTION_STATUS.COMPLETED, ACTION_STATUS.FAILED],
} as const

/**
 * Status groups for filtering and display.
 * Groups related statuses for UI purposes.
 */
export const STATUS_GROUPS = {
  MODERATION: {
    PENDING: [MODERATION_STATUS.PENDING, MODERATION_STATUS.ASSIGNED],
    COMPLETED: [MODERATION_STATUS.ON_HOLD, MODERATION_STATUS.RESOLVED],
  },
  USER: {
    ACTIVE: [USER_STATUS.ACTIVE],
    INACTIVE: [USER_STATUS.INACTIVE, USER_STATUS.SUSPENDED, USER_STATUS.BANNED],
    PENDING: [USER_STATUS.PENDING_VERIFICATION],
  },
  CONTENT: {
    VISIBLE: [CONTENT_STATUS.AVAILABLE],
    HIDDEN: [CONTENT_STATUS.REMOVED, CONTENT_STATUS.RESTRICTED, CONTENT_STATUS.ARCHIVED],
  },
  PROCESSING: {
    IN_PROGRESS: [PROCESSING_STATUS.PENDING, PROCESSING_STATUS.PROCESSING],
    FINISHED: [PROCESSING_STATUS.COMPLETED, PROCESSING_STATUS.FAILED],
  },
} as const

/**
 * Get all values for a status enum.
 *
 * @param statusObj - Status constant object
 * @returns Array of status values
 *
 * @example
 * const values = getStatusValues(MODERATION_STATUS)
 * // Returns: ['pending', 'assigned', 'on_hold', 'resolved']
 */
export function getStatusValues<T extends Record<string, string>>(
  statusObj: T
): Array<T[keyof T]> {
  return Object.values(statusObj) as Array<T[keyof T]>
}

/**
 * Get human-readable label for status value.
 *
 * Converts snake_case values to Title Case.
 *
 * @param status - Status value
 * @returns Human-readable label
 *
 * @example
 * getStatusLabel('pending_verification')  // Returns: 'Pending Verification'
 * getStatusLabel('active')                // Returns: 'Active'
 */
export function getStatusLabel(status: string): string {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Check if status is terminal (no further changes).
 *
 * @param status - Status value to check
 * @param terminalList - List of terminal statuses
 * @returns true if status is terminal
 *
 * @example
 * if (isTerminalStatus(review.status, TERMINAL_STATUSES.REVIEW)) {
 *   // Cannot modify review
 * }
 */
export function isTerminalStatus(status: string, terminalList: readonly string[]): boolean {
  return terminalList.includes(status)
}

/**
 * Get status color for UI display.
 *
 * @param status - Status value
 * @returns Color code (success, warning, error, info, default)
 *
 * @example
 * const color = getStatusColor(MODERATION_STATUS.RESOLVED)
 * // Returns: 'success'
 */
export function getStatusColor(status: string): string {
  // Terminal/resolved statuses
  if (
    status === MODERATION_STATUS.RESOLVED ||
    status === REVIEW_STATUS.COMPLETED ||
    status === APPEAL_STATUS.DECIDED ||
    status === PROCESSING_STATUS.COMPLETED ||
    status === COMPLIANCE_STATUS.READY
  ) {
    return 'success'
  }

  // Failed/error statuses
  if (
    status === PROCESSING_STATUS.FAILED ||
    status === ACTION_STATUS.FAILED ||
    status === COMPLIANCE_STATUS.EXPIRED ||
    status === USER_STATUS.BANNED
  ) {
    return 'error'
  }

  // In-progress statuses
  if (
    status === MODERATION_STATUS.ASSIGNED ||
    status === REVIEW_STATUS.ACTIVE ||
    status === APPEAL_STATUS.IN_REVIEW ||
    status === PROCESSING_STATUS.PROCESSING ||
    status === ACTION_STATUS.IN_PROGRESS ||
    status === COMPLIANCE_STATUS.PROCESSING
  ) {
    return 'warning'
  }

  // Pending/waiting statuses
  if (
    status === MODERATION_STATUS.PENDING ||
    status === APPEAL_STATUS.PENDING ||
    status === PROCESSING_STATUS.PENDING ||
    status === COMPLIANCE_STATUS.PENDING ||
    status === USER_STATUS.PENDING_VERIFICATION
  ) {
    return 'info'
  }

  // On-hold/suspended statuses
  if (
    status === MODERATION_STATUS.ON_HOLD ||
    status === USER_STATUS.SUSPENDED ||
    status === REVIEW_STATUS.ABANDONED
  ) {
    return 'warning'
  }

  return 'default'
}

/**
 * Get icon for status display.
 *
 * @param status - Status value
 * @returns Icon name (e.g., 'CheckCircle', 'Clock', 'AlertCircle')
 *
 * @example
 * const icon = getStatusIcon(MODERATION_STATUS.RESOLVED)
 * // Returns: 'CheckCircle'
 */
export function getStatusIcon(status: string): string {
  // Resolved/completed
  if (
    status === MODERATION_STATUS.RESOLVED ||
    status === REVIEW_STATUS.COMPLETED ||
    status === APPEAL_STATUS.DECIDED ||
    status === PROCESSING_STATUS.COMPLETED ||
    status === COMPLIANCE_STATUS.READY
  ) {
    return 'CheckCircle'
  }

  // Failed/error
  if (
    status === PROCESSING_STATUS.FAILED ||
    status === ACTION_STATUS.FAILED ||
    status === COMPLIANCE_STATUS.EXPIRED ||
    status === USER_STATUS.BANNED
  ) {
    return 'XCircle'
  }

  // In-progress
  if (
    status === REVIEW_STATUS.ACTIVE ||
    status === PROCESSING_STATUS.PROCESSING ||
    status === ACTION_STATUS.IN_PROGRESS ||
    status === COMPLIANCE_STATUS.PROCESSING
  ) {
    return 'Loader'
  }

  // Pending/waiting
  if (
    status === MODERATION_STATUS.PENDING ||
    status === APPEAL_STATUS.PENDING ||
    status === PROCESSING_STATUS.PENDING ||
    status === COMPLIANCE_STATUS.PENDING ||
    status === USER_STATUS.PENDING_VERIFICATION
  ) {
    return 'Clock'
  }

  // Suspended/on-hold
  if (status === MODERATION_STATUS.ON_HOLD || status === USER_STATUS.SUSPENDED) {
    return 'PauseCircle'
  }

  // Abandoned
  if (status === REVIEW_STATUS.ABANDONED) {
    return 'AlertCircle'
  }

  // On hold / restricted
  if (status === CONTENT_STATUS.RESTRICTED || status === CONTENT_STATUS.REMOVED) {
    return 'Lock'
  }

  return 'Circle'
}
