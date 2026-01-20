/**
 * Shared Violation & Enforcement Constants
 *
 * Centralized definitions for policy violations, enforcement actions,
 * and restriction types used in moderation and compliance systems.
 *
 * Usage:
 * import {
 *   VIOLATION_TYPES,
 *   ENFORCEMENT_ACTIONS,
 *   RESTRICTION_TYPES,
 *   MODERATION_DECISIONS
 * } from '@/infrastructure/api/shared/constants'
 */

/**
 * Policy violation classifications.
 * Types of content violations that can be reported or detected.
 */
export const VIOLATION_TYPES = {
  HARASSMENT: 'harassment',
  HATE_SPEECH: 'hate_speech',
  MISINFORMATION: 'misinformation',
  ILLEGAL_CONTENT: 'illegal_content',
  COPYRIGHT: 'copyright',
  SPAM: 'spam',
  NUDITY: 'nudity',
  VIOLENCE: 'violence',
  OTHER: 'other',
} as const

/**
 * Categories of violation types for grouping/filtering.
 */
export const VIOLATION_CATEGORIES = {
  HARMFUL_BEHAVIOR: [
    VIOLATION_TYPES.HARASSMENT,
    VIOLATION_TYPES.HATE_SPEECH,
    VIOLATION_TYPES.VIOLENCE,
  ],
  MISINFORMATION: [VIOLATION_TYPES.MISINFORMATION],
  ILLEGAL: [VIOLATION_TYPES.ILLEGAL_CONTENT, VIOLATION_TYPES.COPYRIGHT],
  SPAM: [VIOLATION_TYPES.SPAM],
  ADULT: [VIOLATION_TYPES.NUDITY],
  UNCATEGORIZED: [VIOLATION_TYPES.OTHER],
} as const

/**
 * Moderation enforcement actions.
 * Actions taken against users after moderation decision.
 */
export const ENFORCEMENT_ACTIONS = {
  REMOVE_CONTENT: 'remove_content',
  WARN_USER: 'warn_user',
  RESTRICT_USER: 'restrict_user',
  SUSPEND_ACCOUNT: 'suspend_account',
} as const

/**
 * Severity ranking of enforcement actions.
 * Higher = more severe.
 */
export const ENFORCEMENT_SEVERITY = {
  [ENFORCEMENT_ACTIONS.REMOVE_CONTENT]: 1,
  [ENFORCEMENT_ACTIONS.WARN_USER]: 2,
  [ENFORCEMENT_ACTIONS.RESTRICT_USER]: 3,
  [ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT]: 4,
} as const

/**
 * User restriction types.
 * Different ways to restrict user account behavior.
 */
export const RESTRICTION_TYPES = {
  MUTE: 'mute', // Cannot post
  SHADOW_BAN: 'shadow_ban', // Posts hidden from others
  RATE_LIMIT: 'rate_limit', // Limited posts per period
  POST_RESTRICTIONS: 'post_restrictions', // Only text posts
  FOLLOWER_DISABLE: 'follower_disable', // Cannot gain followers
} as const

/**
 * Restriction impact levels.
 */
export const RESTRICTION_IMPACT = {
  [RESTRICTION_TYPES.MUTE]: 'high', // Cannot post at all
  [RESTRICTION_TYPES.SHADOW_BAN]: 'high', // Hidden from others
  [RESTRICTION_TYPES.RATE_LIMIT]: 'medium', // Can still post, but limited
  [RESTRICTION_TYPES.POST_RESTRICTIONS]: 'medium', // Limited content types
  [RESTRICTION_TYPES.FOLLOWER_DISABLE]: 'low', // Cannot gain followers
} as const

/**
 * Content removal/deletion methods.
 */
export const REMOVAL_METHODS = {
  SOFT_DELETE: 'soft_delete', // Visible to author only
  ARCHIVE: 'archive', // Hidden from others
  PERMANENT: 'permanent', // Permanently deleted
} as const

/**
 * Data retention periods for removed content.
 * Days before permanent deletion.
 */
export const REMOVAL_RETENTION = {
  [REMOVAL_METHODS.SOFT_DELETE]: 90, // 3 months
  [REMOVAL_METHODS.ARCHIVE]: 365, // 1 year
  [REMOVAL_METHODS.PERMANENT]: 0, // Immediately
} as const

/**
 * Moderation decisions for content review.
 */
export const MODERATION_DECISIONS = {
  APPROVE: 'approve', // Content approved, no action
  REMOVE: 'remove', // Content removed
  WARN: 'warn', // User warned
  RESTRICT: 'restrict', // User restricted
  ESCALATE: 'escalate', // Escalated to specialized team
} as const

/**
 * Appeal decisions for user appeals.
 */
export const APPEAL_DECISIONS = {
  UPHELD: 'upheld', // Original decision upheld
  OVERTURNED: 'overturned', // Decision reversed
  PARTIALLY_UPHELD: 'partially_upheld', // Partial reversal (e.g., reduced ban)
} as const

/**
 * Get human-readable label for violation type.
 *
 * @param violation - Violation type code
 * @returns Display label
 *
 * @example
 * getViolationLabel(VIOLATION_TYPES.HATE_SPEECH)  // Returns: 'Hate Speech'
 */
export function getViolationLabel(violation: string): string {
  const labels: Record<string, string> = {
    [VIOLATION_TYPES.HARASSMENT]: 'Harassment',
    [VIOLATION_TYPES.HATE_SPEECH]: 'Hate Speech',
    [VIOLATION_TYPES.MISINFORMATION]: 'Misinformation',
    [VIOLATION_TYPES.ILLEGAL_CONTENT]: 'Illegal Content',
    [VIOLATION_TYPES.COPYRIGHT]: 'Copyright Infringement',
    [VIOLATION_TYPES.SPAM]: 'Spam',
    [VIOLATION_TYPES.NUDITY]: 'Nudity',
    [VIOLATION_TYPES.VIOLENCE]: 'Violence',
    [VIOLATION_TYPES.OTHER]: 'Other',
  }
  return labels[violation] || violation
}

/**
 * Get violation category for a violation type.
 *
 * @param violation - Violation type code
 * @returns Category name
 *
 * @example
 * getViolationCategory(VIOLATION_TYPES.HATE_SPEECH)  // Returns: 'harmful_behavior'
 */
export function getViolationCategory(violation: string): string {
  for (const [category, types] of Object.entries(VIOLATION_CATEGORIES)) {
    if (types.includes(violation as typeof VIOLATION_TYPES[keyof typeof VIOLATION_TYPES])) {
      return category.toLowerCase()
    }
  }
  return 'uncategorized'
}

/**
 * Get color for violation display.
 *
 * @param violation - Violation type code
 * @returns Color code
 *
 * @example
 * getViolationColor(VIOLATION_TYPES.HATE_SPEECH)  // Returns: 'error'
 */
export function getViolationColor(violation: string): string {
  const category = getViolationCategory(violation)

  if (category === 'harmful_behavior' || category === 'illegal') {
    return 'error'
  }
  if (category === 'misinformation' || category === 'spam') {
    return 'warning'
  }
  if (category === 'adult') {
    return 'warning'
  }
  return 'info'
}

/**
 * Get icon for violation display.
 *
 * @param violation - Violation type code
 * @returns Icon name
 *
 * @example
 * getViolationIcon(VIOLATION_TYPES.HATE_SPEECH)  // Returns: 'AlertTriangle'
 */
export function getViolationIcon(violation: string): string {
  const category = getViolationCategory(violation)

  if (category === 'harmful_behavior') {
    return 'AlertTriangle'
  }
  if (category === 'illegal') {
    return 'Lock'
  }
  if (category === 'misinformation' || category === 'spam') {
    return 'AlertCircle'
  }
  if (category === 'adult') {
    return 'Eye'
  }
  return 'Info'
}

/**
 * Get label for enforcement action.
 *
 * @param action - Enforcement action code
 * @returns Display label
 *
 * @example
 * getEnforcementLabel(ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT)  // Returns: 'Suspend Account'
 */
export function getEnforcementLabel(action: string): string {
  const labels: Record<string, string> = {
    [ENFORCEMENT_ACTIONS.REMOVE_CONTENT]: 'Remove Content',
    [ENFORCEMENT_ACTIONS.WARN_USER]: 'Warn User',
    [ENFORCEMENT_ACTIONS.RESTRICT_USER]: 'Restrict User',
    [ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT]: 'Suspend Account',
  }
  return labels[action] || action
}

/**
 * Get severity value for enforcement action.
 *
 * @param action - Enforcement action code
 * @returns Severity value (1-4)
 *
 * @example
 * getEnforcementSeverity(ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT)  // Returns: 4
 */
export function getEnforcementSeverity(action: string): number {
  return ENFORCEMENT_SEVERITY[action as keyof typeof ENFORCEMENT_SEVERITY] || 0
}

/**
 * Get label for restriction type.
 *
 * @param restriction - Restriction type code
 * @returns Display label
 *
 * @example
 * getRestrictionLabel(RESTRICTION_TYPES.SHADOW_BAN)  // Returns: 'Shadow Ban'
 */
export function getRestrictionLabel(restriction: string): string {
  const labels: Record<string, string> = {
    [RESTRICTION_TYPES.MUTE]: 'Muted',
    [RESTRICTION_TYPES.SHADOW_BAN]: 'Shadow Banned',
    [RESTRICTION_TYPES.RATE_LIMIT]: 'Rate Limited',
    [RESTRICTION_TYPES.POST_RESTRICTIONS]: 'Post Restricted',
    [RESTRICTION_TYPES.FOLLOWER_DISABLE]: 'Follower Disabled',
  }
  return labels[restriction] || restriction
}

/**
 * Get label for removal method.
 *
 * @param method - Removal method code
 * @returns Display label
 *
 * @example
 * getRemovalLabel(REMOVAL_METHODS.SOFT_DELETE)  // Returns: 'Soft Delete'
 */
export function getRemovalLabel(method: string): string {
  const labels: Record<string, string> = {
    [REMOVAL_METHODS.SOFT_DELETE]: 'Soft Delete',
    [REMOVAL_METHODS.ARCHIVE]: 'Archive',
    [REMOVAL_METHODS.PERMANENT]: 'Permanent Delete',
  }
  return labels[method] || method
}

/**
 * Get description for removal method.
 *
 * @param method - Removal method code
 * @returns Description
 *
 * @example
 * getRemovalDescription(REMOVAL_METHODS.SOFT_DELETE)
 * // Returns: 'Content hidden from public, visible to author only'
 */
export function getRemovalDescription(method: string): string {
  const descriptions: Record<string, string> = {
    [REMOVAL_METHODS.SOFT_DELETE]:
      'Content hidden from public, visible to author only',
    [REMOVAL_METHODS.ARCHIVE]:
      'Content hidden from others, archived for record-keeping',
    [REMOVAL_METHODS.PERMANENT]:
      'Content permanently deleted, cannot be recovered',
  }
  return descriptions[method] || ''
}

/**
 * Get label for moderation decision.
 *
 * @param decision - Moderation decision code
 * @returns Display label
 *
 * @example
 * getModerationLabel(MODERATION_DECISIONS.APPROVE)  // Returns: 'Approve'
 */
export function getModerationLabel(decision: string): string {
  const labels: Record<string, string> = {
    [MODERATION_DECISIONS.APPROVE]: 'Approve',
    [MODERATION_DECISIONS.REMOVE]: 'Remove',
    [MODERATION_DECISIONS.WARN]: 'Warn',
    [MODERATION_DECISIONS.RESTRICT]: 'Restrict',
    [MODERATION_DECISIONS.ESCALATE]: 'Escalate',
  }
  return labels[decision] || decision
}

/**
 * Get label for appeal decision.
 *
 * @param decision - Appeal decision code
 * @returns Display label
 *
 * @example
 * getAppealLabel(APPEAL_DECISIONS.OVERTURNED)  // Returns: 'Overturned'
 */
export function getAppealLabel(decision: string): string {
  const labels: Record<string, string> = {
    [APPEAL_DECISIONS.UPHELD]: 'Upheld',
    [APPEAL_DECISIONS.OVERTURNED]: 'Overturned',
    [APPEAL_DECISIONS.PARTIALLY_UPHELD]: 'Partially Upheld',
  }
  return labels[decision] || decision
}

/**
 * Check if enforcement action is reversible.
 *
 * @param action - Enforcement action code
 * @returns true if action can be reversed/appealed
 *
 * @example
 * if (isReversible(ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT)) {
 *   // Show appeal button
 * }
 */
export function isReversible(action: string): boolean {
  // Most enforcement actions can potentially be appealed
  return [
    ENFORCEMENT_ACTIONS.RESTRICT_USER,
    ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT,
    ENFORCEMENT_ACTIONS.WARN_USER,
  ].includes(action as typeof ENFORCEMENT_ACTIONS[keyof typeof ENFORCEMENT_ACTIONS])
}

/**
 * Get recommended enforcement action for violation type.
 *
 * @param violation - Violation type code
 * @returns Recommended enforcement action
 *
 * @example
 * getRecommendedAction(VIOLATION_TYPES.SPAM)
 * // Returns: 'remove_content'
 */
export function getRecommendedAction(
  violation: string
): typeof ENFORCEMENT_ACTIONS[keyof typeof ENFORCEMENT_ACTIONS] | null {
  const recommendations: Record<string, typeof ENFORCEMENT_ACTIONS[keyof typeof ENFORCEMENT_ACTIONS]> = {
    [VIOLATION_TYPES.HARASSMENT]: ENFORCEMENT_ACTIONS.WARN_USER,
    [VIOLATION_TYPES.HATE_SPEECH]: ENFORCEMENT_ACTIONS.WARN_USER,
    [VIOLATION_TYPES.MISINFORMATION]: ENFORCEMENT_ACTIONS.REMOVE_CONTENT,
    [VIOLATION_TYPES.ILLEGAL_CONTENT]: ENFORCEMENT_ACTIONS.SUSPEND_ACCOUNT,
    [VIOLATION_TYPES.COPYRIGHT]: ENFORCEMENT_ACTIONS.REMOVE_CONTENT,
    [VIOLATION_TYPES.SPAM]: ENFORCEMENT_ACTIONS.REMOVE_CONTENT,
    [VIOLATION_TYPES.NUDITY]: ENFORCEMENT_ACTIONS.REMOVE_CONTENT,
    [VIOLATION_TYPES.VIOLENCE]: ENFORCEMENT_ACTIONS.WARN_USER,
    [VIOLATION_TYPES.OTHER]: ENFORCEMENT_ACTIONS.REMOVE_CONTENT,
  }

  return recommendations[violation] || null
}
