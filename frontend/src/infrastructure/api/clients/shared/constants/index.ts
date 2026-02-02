/**
 * Shared Constants - Barrel Export
 *
 * Central export point for all shared constant definitions.
 * Eliminates scattered hardcoded string values across codebase.
 *
 * Usage:
 * import {
 *   PRIORITY_LEVELS,
 *   VIOLATION_TYPES,
 *   MODERATION_STATUS,
 *   ENFORCEMENT_ACTIONS
 * } from '@/infrastructure/api/shared/constants'
 *
 * // Instead of:
 * if (status === 'critical') { }
 *
 * // Use:
 * if (priority === PRIORITY_LEVELS.CRITICAL) { }
 */

// ============================================
// Status Constants
// ============================================

export {
  MODERATION_STATUS,
  REVIEW_STATUS,
  APPEAL_STATUS,
  APPROVAL_STATUS,
  PROCESSING_STATUS,
  COMPLIANCE_STATUS,
  CONTENT_STATUS,
  USER_STATUS,
  ACTION_STATUS,
  NOTIFICATION_STATUS,
  CONSENT_STATUS,
  FEATURE_FLAG_STATUS,
  TERMINAL_STATUSES,
  STATUS_GROUPS,
  getStatusValues,
  getStatusLabel,
  isTerminalStatus,
  getStatusColor,
  getStatusIcon,
} from './statuses'

// ============================================
// Priority Constants
// ============================================

export {
  PRIORITY_LEVELS,
  SEVERITY_RATINGS,
  PRIORITY_ORDER,
  PRIORITY_SLA,
  PRIORITY_RESPONSE_TIME,
  PRIORITY_QUEUE_POSITION,
  getSeverityValue,
  comparePriorities,
  getPriorityLabel,
  getPriorityColor,
  getPriorityIcon,
  getSLADeadline,
  isUrgent,
  isHighSeverity,
  sortByPriority,
} from './priorities'

// ============================================
// Violation & Enforcement Constants
// ============================================

export {
  VIOLATION_TYPES,
  VIOLATION_CATEGORIES,
  ENFORCEMENT_ACTIONS,
  ENFORCEMENT_SEVERITY,
  RESTRICTION_TYPES,
  RESTRICTION_IMPACT,
  REMOVAL_METHODS,
  REMOVAL_RETENTION,
  MODERATION_DECISIONS,
  APPEAL_DECISIONS,
  getViolationLabel,
  getViolationCategory,
  getViolationColor,
  getViolationIcon,
  getEnforcementLabel,
  getEnforcementSeverity,
  getRestrictionLabel,
  getRemovalLabel,
  getRemovalDescription,
  getModerationLabel,
  getAppealLabel,
  isReversible,
  getRecommendedAction,
} from './violations'
