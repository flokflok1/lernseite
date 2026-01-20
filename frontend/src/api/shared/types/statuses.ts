/**
 * Shared Status & Priority Types
 *
 * Standardized type definitions for all status and priority enums used across API domains.
 * Single source of truth for status values.
 *
 * Usage:
 * import type {
 *   ModerationStatus,
 *   ComplianceStatus,
 *   PriorityLevel,
 *   ActionStatus
 * } from '@/api/shared'
 */

/**
 * Moderation queue item status.
 *
 * Represents lifecycle states of content in moderation queue.
 * - `pending` - Awaiting assignment to moderator
 * - `assigned` - Assigned to moderator, in review
 * - `on_hold` - Held for additional context/legal review
 * - `resolved` - Decision made and enforcement complete
 */
export type ModerationStatus = 'pending' | 'assigned' | 'on_hold' | 'resolved'

/**
 * Review session status.
 *
 * Represents states of active content review.
 * - `active` - Review in progress
 * - `submitted` - Moderator submitted decision, awaiting approval
 * - `completed` - Review finished, decision applied
 * - `abandoned` - Review abandoned (timeout, moderator reassignment, etc)
 */
export type ReviewStatus = 'active' | 'submitted' | 'completed' | 'abandoned'

/**
 * Appeal status.
 *
 * Represents lifecycle of user appeal to moderation decision.
 * - `pending` - Appeal queued, awaiting review
 * - `in_review` - Appeal reviewer assigned, in review
 * - `decided` - Appeal decision made
 */
export type AppealStatus = 'pending' | 'in_review' | 'decided'

/**
 * Approval/decision status.
 *
 * Generic status for items requiring approval workflow.
 * - `pending` - Awaiting decision
 * - `approved` - Approved
 * - `rejected` - Rejected
 * - `needs_review` - Requires additional review (conditional)
 */
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'needs_review'

/**
 * General processing status.
 *
 * Represents async operation states.
 * - `pending` - Queued, awaiting processing
 * - `processing` - Currently being processed
 * - `completed` - Successfully completed
 * - `failed` - Processing failed
 */
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed'

/**
 * Compliance/request status.
 *
 * Represents lifecycle of compliance requests (GDPR, DSA, COPPA).
 * - `pending` - Request submitted, queued
 * - `processing` - Request being processed
 * - `ready` - Ready for delivery/collection
 * - `expired` - Request expired (TTL exceeded)
 */
export type ComplianceStatus = 'pending' | 'processing' | 'ready' | 'expired'

/**
 * Content availability status.
 *
 * Represents current state/visibility of content.
 * - `available` - Content visible and accessible
 * - `removed` - Soft-deleted (visible to author only)
 * - `restricted` - Visible with restrictions/warnings
 * - `archived` - Hard-deleted (not visible, may be recoverable)
 */
export type ContentStatus = 'available' | 'removed' | 'restricted' | 'archived'

/**
 * User account status.
 *
 * Represents user account state.
 * - `active` - Account active and in use
 * - `suspended` - Account temporarily suspended
 * - `banned` - Account permanently banned
 * - `pending_verification` - Email/phone verification pending
 * - `inactive` - Account inactive (no logins for extended period)
 */
export type UserStatus = 'active' | 'suspended' | 'banned' | 'pending_verification' | 'inactive'

/**
 * Enforcement action status.
 *
 * Represents state of moderation action (warn, restrict, remove, suspend).
 * - `pending` - Action queued, awaiting application
 * - `in_progress` - Action being applied
 * - `completed` - Action successfully applied
 * - `failed` - Action failed to apply (retry needed)
 */
export type ActionStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

/**
 * Priority level for items needing triage.
 *
 * Used in moderation queues, support tickets, alerts.
 * - `low` - Non-urgent, can wait
 * - `medium` - Standard priority
 * - `high` - Time-sensitive, handle soon
 * - `critical` - Urgent, handle immediately
 * - `urgent` - Alias for critical (for backward compatibility)
 */
export type PriorityLevel = 'low' | 'medium' | 'high' | 'critical' | 'urgent'

/**
 * Violation type / policy violation classification.
 *
 * Represents type of policy violation (used in DSA, moderation).
 */
export type ViolationType =
  | 'harassment'
  | 'hate_speech'
  | 'misinformation'
  | 'illegal_content'
  | 'copyright'
  | 'spam'
  | 'nudity'
  | 'violence'
  | 'other'

/**
 * Moderation decision outcome.
 *
 * Result of moderation review.
 * - `approve` - Content approved, no action taken
 * - `remove` - Content removed
 * - `warn` - User warned
 * - `restrict` - User restricted (mute, shadow-ban, rate-limit)
 * - `escalate` - Escalated to human review or other team
 */
export type ModerationDecision = 'approve' | 'remove' | 'warn' | 'restrict' | 'escalate'

/**
 * Appeal decision outcome.
 *
 * Result of appeal review.
 * - `upheld` - Original decision upheld, appeal denied
 * - `overturned` - Original decision overturned, action reversed
 * - `partially_upheld` - Partial decision (e.g., reduce suspension length)
 */
export type AppealDecision = 'upheld' | 'overturned' | 'partially_upheld'

/**
 * Restriction type.
 *
 * Different ways to restrict user account.
 */
export type RestrictionType =
  | 'mute' // Cannot post
  | 'shadow_ban' // Posts hidden from others
  | 'rate_limit' // Limited posts per period
  | 'post_restrictions' // Only text posts (no media/links)
  | 'follower_disable' // Cannot gain followers

/**
 * Content removal method.
 *
 * Different ways to remove content.
 */
export type RemovalMethod =
  | 'soft_delete' // Visible to author only
  | 'archive' // Hidden from others
  | 'permanent' // Permanently deleted

/**
 * Enforcement action type.
 *
 * Different types of moderation enforcement.
 */
export type EnforcementActionType =
  | 'remove_content'
  | 'warn_user'
  | 'restrict_user'
  | 'suspend_account'

/**
 * Content type classification.
 *
 * Different types of content that can be moderated.
 */
export type ContentType =
  | 'post'
  | 'comment'
  | 'user_profile'
  | 'video'
  | 'image'
  | 'audio'
  | 'other'

/**
 * Notification status.
 *
 * State of notification delivery/read status.
 */
export type NotificationStatus = 'sent' | 'delivered' | 'read' | 'failed' | 'bounced'

/**
 * Consent status (GDPR, COPPA).
 *
 * User consent state for data processing.
 */
export type ConsentStatus = 'not_given' | 'given' | 'withdrawn' | 'expired'

/**
 * Feature flag status.
 *
 * State of feature flag rollout.
 */
export type FeatureFlagStatus = 'disabled' | 'enabled' | 'rolling_out' | 'rolled_back'

/**
 * Generic status helper to check if status is terminal (no further changes).
 *
 * @param status - Status to check
 * @param terminalStatuses - Array of terminal status values
 * @returns true if status is terminal
 *
 * @example
 * if (isTerminalStatus(reviewStatus, ['completed', 'abandoned'])) {
 *   // Cannot modify review
 * }
 */
export function isTerminalStatus(
  status: string,
  terminalStatuses: string[]
): boolean {
  return terminalStatuses.includes(status)
}

/**
 * Generic status helper to check if status transition is valid.
 *
 * @param from - Current status
 * @param to - Target status
 * @param validTransitions - Map of valid transitions
 * @returns true if transition is valid
 *
 * @example
 * const transitions: Record<ModerationStatus, ModerationStatus[]> = {
 *   pending: ['assigned', 'resolved'],
 *   assigned: ['on_hold', 'resolved'],
 *   on_hold: ['assigned', 'resolved'],
 *   resolved: []
 * }
 *
 * if (isValidStatusTransition('pending', 'resolved', transitions)) {
 *   // Valid transition
 * }
 */
export function isValidStatusTransition(
  from: string,
  to: string,
  validTransitions: Record<string, string[]>
): boolean {
  if (from === to) return true // No change is always valid
  return validTransitions[from]?.includes(to) ?? false
}

/**
 * Get human-readable status label.
 *
 * @param status - Status value
 * @returns Display label for status
 *
 * @example
 * const label = getStatusLabel('pending')  // "Pending"
 * const label = getStatusLabel('in_review')  // "In Review"
 */
export function getStatusLabel(status: string): string {
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Get priority level severity.
 *
 * @param priority - Priority level
 * @returns Numeric severity (higher = more urgent)
 *
 * @example
 * const severity = getPrioritySeverity('critical')  // 4
 * const severity = getPrioritySeverity('low')  // 1
 */
export function getPrioritySeverity(priority: PriorityLevel): number {
  const severityMap: Record<PriorityLevel, number> = {
    low: 1,
    medium: 2,
    high: 3,
    critical: 4,
    urgent: 4
  }
  return severityMap[priority] ?? 0
}

/**
 * Compare two priority levels.
 *
 * @param p1 - First priority
 * @param p2 - Second priority
 * @returns -1 if p1 < p2, 0 if equal, 1 if p1 > p2
 *
 * @example
 * comparePriorities('critical', 'medium')  // 1 (critical is higher)
 * comparePriorities('low', 'high')  // -1 (low is lower)
 */
export function comparePriorities(
  p1: PriorityLevel,
  p2: PriorityLevel
): -1 | 0 | 1 {
  const s1 = getPrioritySeverity(p1)
  const s2 = getPrioritySeverity(p2)
  return s1 > s2 ? 1 : s1 < s2 ? -1 : 0
}
