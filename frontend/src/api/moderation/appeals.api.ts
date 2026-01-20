/**
 * Moderation Appeals API
 *
 * Handles user appeals of moderation decisions. Implements appeal workflow,
 * appeal review, and decision overturning when appropriate.
 *
 * Endpoints:
 * - POST /moderation/appeals - Submit appeal
 * - GET /moderation/appeals/{appealId} - Get appeal details
 * - GET /moderation/appeals/user/{userId} - Get user's appeals
 * - POST /moderation/appeals/{appealId}/review - Submit appeal review
 * - GET /moderation/appeals/stats - Appeal statistics
 */

import http from '../http'
import type {
  Appeal,
  AppealResponse,
  AppealListResponse,
  AppealSubmitRequest,
  AppealReviewRequest,
  AppealDecision,
} from './types'

/**
 * Submit appeal of moderation decision.
 *
 * User can appeal content removal or enforcement action. Appeal goes to specialized
 * appeal reviewers different from original moderator. Provides opportunity for
 * decision reconsideration with new evidence.
 *
 * @param request - Appeal submission (action_id, reason, evidence, new_evidence_urls)
 * @returns Appeal confirmation
 *
 * @example
 * const appeal = await submitAppeal({
 *   action_id: 'action-12345',
 *   reason: 'Removed content does not violate policy - political commentary',
 *   evidence: 'Full context shows satirical intent',
 *   new_evidence_urls: ['https://...original-post-full-context']
 * })
 * console.log('Appeal submitted:', appeal.appeal_id)
 * console.log('Status:', appeal.status)
 * console.log('Queue position:', appeal.queue_position)
 */
export const submitAppeal = async (request: AppealSubmitRequest): Promise<AppealResponse> => {
  const response = await http.post<{ success: boolean; data: AppealResponse }>(
    '/moderation/appeals',
    request
  )
  return response.data.data
}

/**
 * Get appeal details.
 *
 * Retrieve full details of an appeal including original decision context,
 * appeal reasoning, evidence, and current status.
 *
 * @param appealId - Appeal ID
 * @returns Appeal details
 *
 * @example
 * const appeal = await getAppeal('appeal-xyz789')
 * console.log('Original decision:', appeal.original_decision)
 * console.log('Appeal reason:', appeal.reason)
 * console.log('Status:', appeal.status)
 * if (appeal.decision_made) {
 *   console.log('Decision:', appeal.appeal_decision)
 *   console.log('Approved:', appeal.decision === 'upheld')
 * }
 */
export const getAppeal = async (appealId: string): Promise<Appeal> => {
  const response = await http.get<{ success: boolean; data: Appeal }>(
    `/moderation/appeals/${appealId}`
  )
  return response.data.data
}

/**
 * Get user's appeals.
 *
 * Get paginated list of appeals submitted by a user.
 * Shows appeal history and outcomes.
 *
 * @param userId - User ID
 * @param status - Filter by status (pending, approved, denied, partially_upheld)
 * @param limit - Max results (default 20, max 100)
 * @param offset - Skip N results (default 0)
 * @returns Paginated appeal list
 *
 * @example
 * const appeals = await getUserAppeals('user-789', 'pending')
 * console.log('Pending appeals:', appeals.data.length)
 * console.log('Total submitted:', appeals.total)
 * appeals.data.forEach(appeal => {
 *   console.log(`${appeal.appeal_id}: ${appeal.status} (${appeal.submitted_at})`)
 * })
 */
export const getUserAppeals = async (
  userId: string,
  status?: string,
  limit: number = 20,
  offset: number = 0
): Promise<AppealListResponse> => {
  const response = await http.get<{ success: boolean; data: AppealListResponse }>(
    `/moderation/appeals/user/${userId}`,
    {
      params: { status, limit: Math.min(limit, 100), offset },
    }
  )
  return response.data.data
}

/**
 * Submit appeal review decision.
 *
 * Appeal reviewer submits decision on appeal (approve/overturn, partially uphold, or deny).
 * If approved, original action may be reversed and content restored.
 *
 * @param appealId - Appeal ID
 * @param request - Review decision (decision, reason, actions_taken, reverse_original_action)
 * @returns Appeal decision
 *
 * @example
 * const decision = await submitAppealReview('appeal-xyz789', {
 *   decision: 'upheld',
 *   reason: 'Original decision was correct. Content violates policy on misinformation.',
 *   actions_taken: [],
 *   reverse_original_action: false
 * })
 * console.log('Appeal decision:', decision.decision)
 * console.log('Reasoning:', decision.appeal_reasoning)
 *
 * // Or to overturn original decision:
 * const overturn = await submitAppealReview('appeal-abc123', {
 *   decision: 'overturned',
 *   reason: 'Content removed in error. Does not violate policy.',
 *   actions_taken: ['restore_content'],
 *   reverse_original_action: true
 * })
 * console.log('Content restored:', overturn.actions_taken.includes('restore_content'))
 */
export const submitAppealReview = async (
  appealId: string,
  request: AppealReviewRequest
): Promise<AppealDecision> => {
  const response = await http.post<{ success: boolean; data: AppealDecision }>(
    `/moderation/appeals/${appealId}/review`,
    request
  )
  return response.data.data
}

/**
 * Get appeal statistics.
 *
 * Get aggregate statistics on appeal system (total appeals, approval rate,
 * average resolution time, overturned decision rate, etc).
 *
 * @param period - Time period (today, week, month, all)
 * @returns Appeal statistics
 *
 * @example
 * const stats = await getAppealStats('month')
 * console.log('Total appeals:', stats.total)
 * console.log('Approval rate:', stats.approval_rate_percent, '%')
 * console.log('Avg time to decide:', stats.avg_days_to_decision)
 * console.log('Overturned decisions:', stats.overturned_count, 'out of', stats.original_decisions)
 */
export const getAppealStats = async (period: string = 'month') => {
  const response = await http.get<{
    success: boolean
    data: {
      period: string
      total_appeals: number
      pending_appeals: number
      decided_appeals: number
      approved_percent: number
      denied_percent: number
      partially_upheld_percent: number
      avg_days_to_decision: number
      original_decisions_overturned: number
      appeal_reviewers: number
    }
  }>('/moderation/appeals/stats', { params: { period } })
  return response.data.data
}

/**
 * Get appeals awaiting review.
 *
 * Get list of appeals waiting for reviewer assignment/decision.
 * Used for appeal assignment dashboard.
 *
 * @param priority - Filter by priority (low, medium, high, critical)
 * @param limit - Max results (default 20)
 * @param offset - Skip N results (default 0)
 * @returns Pending appeals
 *
 * @example
 * const pending = await getPendingAppeals('high', 50)
 * console.log('High priority appeals:', pending.data.length)
 * console.log('Oldest appeal waiting:', pending.oldest_wait_time_hours, 'hours')
 */
export const getPendingAppeals = async (
  priority?: string,
  limit: number = 20,
  offset: number = 0
) => {
  const response = await http.get<{
    success: boolean
    data: {
      data: Array<{
        appeal_id: string
        original_action_id: string
        user_id: string
        reason: string
        submitted_at: string
        priority: string
        queue_position: number
      }>
      total: number
      oldest_wait_time_hours: number
    }
  }>('/moderation/appeals/pending', {
    params: { priority, limit: Math.min(limit, 100), offset },
  })
  return response.data.data
}

/**
 * Assign appeal to reviewer.
 *
 * Assign a pending appeal to a specific appeal reviewer.
 * Locks appeal from reassignment until decision is made.
 *
 * @param appealId - Appeal ID
 * @param reviewerId - Appeal reviewer ID
 * @returns Assignment confirmation
 *
 * @example
 * const assigned = await assignAppeal('appeal-xyz789', 'reviewer-555')
 * console.log('Appeal assigned to:', assigned.assigned_to)
 * console.log('Assignment time:', assigned.assigned_at)
 */
export const assignAppeal = async (appealId: string, reviewerId: string) => {
  const response = await http.post<{ success: boolean; data: { assigned_to: string } }>(
    `/moderation/appeals/${appealId}/assign`,
    { reviewer_id: reviewerId }
  )
  return response.data.data
}

/**
 * Get appeal reviewer's workload.
 *
 * Get statistics on appeal reviewer's current workload and performance.
 * Used for load balancing and performance monitoring.
 *
 * @param reviewerId - Appeal reviewer ID
 * @returns Reviewer workload stats
 *
 * @example
 * const workload = await getReviewerWorkload('reviewer-555')
 * console.log('Pending assignments:', workload.pending_count)
 * console.log('Avg resolution time:', workload.avg_days_to_decide)
 * console.log('Decision consistency:', workload.consistency_score, '/100')
 */
export const getReviewerWorkload = async (reviewerId: string) => {
  const response = await http.get<{
    success: boolean
    data: {
      reviewer_id: string
      pending_count: number
      completed_this_month: number
      avg_days_to_decide: number
      decision_consistency_score: number
      approved_percent: number
      overturned_percent: number
    }
  }>(`/moderation/appeals/reviewer/${reviewerId}/workload`)
  return response.data.data
}
