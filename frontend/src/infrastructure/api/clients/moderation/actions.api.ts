/**
 * Moderation Actions API
 *
 * Handles enforcement actions taken as a result of moderation decisions.
 * Implements content removal, user restrictions, and enforcement workflows.
 *
 * Actions:
 * - Content removal (soft delete, archive, or permanent)
 * - User warnings and restrictions
 * - Temporary or permanent suspensions
 * - Appeal mechanism implementation
 *
 * Endpoints:
 * - POST /moderation/actions/remove-content - Remove content
 * - POST /moderation/actions/warn-user - Issue user warning
 * - POST /moderation/actions/restrict-user - Restrict user (mute, shadow-ban, etc)
 * - GET /moderation/actions/{actionId} - Get action details
 * - POST /moderation/actions/{actionId}/undo - Reverse an action (requires approval)
 */

import http from '@/infrastructure/api/http'
import type {
  EnforcementAction,
  ActionResponse,
  ActionHistoryResponse,
  RemoveContentRequest,
  WarnUserRequest,
  RestrictUserRequest,
} from './types'

/**
 * Remove content from platform.
 *
 * Remove flagged or policy-violating content. Can be soft-deleted (visible to author),
 * archived (hidden from others), or permanently removed with no recovery.
 *
 * @param request - Removal request (content_id, type, reason, removal_method, notify_user)
 * @returns Action confirmation
 *
 * @example
 * const action = await removeContent({
 *   content_id: 'post-12345',
 *   content_type: 'post',
 *   reason: 'hate_speech',
 *   removal_method: 'soft_delete',
 *   notify_user: true
 * })
 * console.log('Content removed:', action.action_id)
 * console.log('User notified:', action.user_notified_at)
 */
export const removeContent = async (request: RemoveContentRequest): Promise<ActionResponse> => {
  const response = await http.post<{ success: boolean; data: ActionResponse }>(
    '/moderation/actions/remove-content',
    request
  )
  return response.data.data
}

/**
 * Issue user warning.
 *
 * Issue warning to user for policy violation. Can be visible in user history
 * and may lead to escalation if user accumulates multiple warnings.
 *
 * @param request - Warning request (user_id, reason, severity, duration_days, public)
 * @returns Action confirmation
 *
 * @example
 * const action = await warnUser({
 *   user_id: 'user-789',
 *   reason: 'harassment',
 *   severity: 'medium',
 *   duration_days: 30,
 *   public: false
 * })
 * console.log('Warning issued:', action.action_id)
 * console.log('User warned:', action.user_notified_at)
 * console.log('Warning expires:', action.expires_at)
 */
export const warnUser = async (request: WarnUserRequest): Promise<ActionResponse> => {
  const response = await http.post<{ success: boolean; data: ActionResponse }>(
    '/moderation/actions/warn-user',
    request
  )
  return response.data.data
}

/**
 * Restrict user account.
 *
 * Apply restrictions to user account (mute, shadow-ban, rate limit, post restrictions, etc).
 * Different restriction types for different severity levels.
 *
 * @param request - Restriction request (user_id, restriction_type, reason, duration_days)
 * @returns Action confirmation
 *
 * @example
 * const action = await restrictUser({
 *   user_id: 'user-789',
 *   restriction_type: 'rate_limit',
 *   reason: 'spam_posts',
 *   duration_days: 7
 * })
 * console.log('User restricted:', action.action_id)
 * console.log('Restriction type:', action.restriction_type)
 * console.log('Expires:', action.expires_at)
 *
 * // Other restriction types:
 * // 'mute' - Cannot post (all platforms)
 * // 'shadow_ban' - Posts hidden from others but visible to author
 * // 'rate_limit' - Limited posts per day
 * // 'post_restrictions' - Only text posts (no media/links)
 * // 'follower_disable' - Cannot gain followers temporarily
 */
export const restrictUser = async (request: RestrictUserRequest): Promise<ActionResponse> => {
  const response = await http.post<{ success: boolean; data: ActionResponse }>(
    '/moderation/actions/restrict-user',
    request
  )
  return response.data.data
}

/**
 * Get action details.
 *
 * Retrieve details of a specific enforcement action including original reason,
 * applied restrictions, and appeal information.
 *
 * @param actionId - Enforcement action ID
 * @returns Action details
 *
 * @example
 * const action = await getAction('action-xyz999')
 * console.log('Type:', action.action_type)
 * console.log('Reason:', action.reason)
 * console.log('Applied by:', action.moderator_id)
 * console.log('Can appeal:', action.can_appeal)
 */
export const getAction = async (actionId: string): Promise<EnforcementAction> => {
  const response = await http.get<{ success: boolean; data: EnforcementAction }>(
    `/moderation/actions/${actionId}`
  )
  return response.data.data
}

/**
 * Get user's enforcement action history.
 *
 * Get history of all enforcement actions taken against a user
 * (warnings, restrictions, suspensions, etc).
 *
 * @param userId - User ID
 * @param limit - Max results (default 20, max 100)
 * @param offset - Skip N results (default 0)
 * @returns Paginated action history
 *
 * @example
 * const history = await getUserActions('user-789', 50)
 * console.log('Total actions:', history.total)
 * history.data.forEach(action => {
 *   console.log(`${action.action_type}: ${action.reason} (${action.created_at})`)
 * })
 */
export const getUserActions = async (
  userId: string,
  limit: number = 20,
  offset: number = 0
): Promise<ActionHistoryResponse> => {
  const response = await http.get<{ success: boolean; data: ActionHistoryResponse }>(
    `/moderation/actions/user/${userId}`,
    {
      params: { limit: Math.min(limit, 100), offset },
    }
  )
  return response.data.data
}

/**
 * Undo/reverse an enforcement action.
 *
 * Reverse a previous enforcement action (restore content, lift restriction, etc).
 * Requires override approval and creates audit trail.
 *
 * @param actionId - Action ID to reverse
 * @param reason - Reason for reversal (mistake, appeal_upheld, other)
 * @returns Reversal action confirmation
 *
 * @example
 * const reversal = await undoAction('action-xyz999', 'appeal_upheld')
 * console.log('Action reversed:', reversal.reversal_id)
 * console.log('Original action:', reversal.original_action_id)
 * console.log('Content restored:', reversal.content_restored)
 */
export const undoAction = async (actionId: string, reason: string) => {
  const response = await http.post<{ success: boolean; data: { reversal_id: string } }>(
    `/moderation/actions/${actionId}/undo`,
    { reason }
  )
  return response.data.data
}

/**
 * Get enforcement action statistics.
 *
 * Get aggregate statistics on enforcement actions (most common reasons,
 * reversal rates, user distribution, etc).
 *
 * @param period - Time period (today, week, month, all)
 * @returns Enforcement statistics
 *
 * @example
 * const stats = await getActionStats('month')
 * console.log('Total actions:', stats.total)
 * console.log('Most common reason:', stats.top_reasons[0])
 * console.log('Reversal rate:', stats.reversal_rate_percent, '%')
 */
export const getActionStats = async (period: string = 'month') => {
  const response = await http.get<{
    success: boolean
    data: {
      period: string
      total_actions: number
      by_type: { [key: string]: number }
      by_reason: { [key: string]: number }
      reversal_rate_percent: number
      avg_duration_days: number
      users_affected: number
      content_removed: number
    }
  }>('/moderation/actions/stats', { params: { period } })
  return response.data.data
}

/**
 * Get active restrictions for user.
 *
 * Get all currently active restrictions/actions on a specific user account.
 * Used to enforce restrictions in real-time across platform.
 *
 * @param userId - User ID
 * @returns List of active restrictions
 *
 * @example
 * const restrictions = await getActiveRestrictions('user-789')
 * restrictions.forEach(r => {
 *   console.log(`${r.restriction_type} (expires ${r.expires_at})`)
 * })
 * if (restrictions.some(r => r.restriction_type === 'mute')) {
 *   // Block user from posting
 * }
 */
export const getActiveRestrictions = async (userId: string) => {
  const response = await http.get<{
    success: boolean
    data: Array<{
      action_id: string
      restriction_type: string
      reason: string
      applied_at: string
      expires_at?: string
      is_active: boolean
    }>
  }>(`/moderation/actions/user/${userId}/active`)
  return response.data.data
}
