/**
 * Content Review Workflow API
 *
 * Handles the content review workflow including submission, decision recording,
 * and review history tracking. Implements moderation decision workflows.
 *
 * Endpoints:
 * - GET /moderation/reviews/{reviewId} - Get review details
 * - POST /moderation/reviews/{queueId}/start - Start reviewing item
 * - POST /moderation/reviews/{queueId}/submit-decision - Submit review decision
 * - GET /moderation/reviews/moderator/{moderatorId} - Get moderator's reviews
 * - GET /moderation/reviews/item/{contentId} - Get review history for content
 */

import http from '@/infrastructure/api/http'
import type {
  ReviewSession,
  ReviewDecision,
  ReviewHistory,
  ReviewListResponse,
  DecisionRequest,
} from './types'

/**
 * Get review session details.
 *
 * Retrieve details of a moderation review session including content, evidence,
 * previous decisions on similar content, and user context.
 *
 * @param reviewId - Review session ID
 * @returns Review session details
 *
 * @example
 * const review = await getReviewSession('review-xyz789')
 * console.log('Content:', review.content)
 * console.log('Reports:', review.reports.length)
 * console.log('User history:', review.user_moderation_history)
 */
export const getReviewSession = async (reviewId: string): Promise<ReviewSession> => {
  const response = await http.get<{ success: boolean; data: ReviewSession }>(
    `/moderation/reviews/${reviewId}`
  )
  return response.data.data
}

/**
 * Start content review session.
 *
 * Create a new review session for a queue item. Locks item from reassignment,
 * records start time, and initializes review context.
 *
 * @param queueId - Queue item ID to review
 * @returns Review session details
 *
 * @example
 * const review = await startReview('queue-12345')
 * console.log('Review session created:', review.review_id)
 * console.log('Content to review:', review.content_id)
 * // Start reviewing content, can now submit decision
 */
export const startReview = async (queueId: string): Promise<ReviewSession> => {
  const response = await http.post<{ success: boolean; data: ReviewSession }>(
    `/moderation/reviews/${queueId}/start`
  )
  return response.data.data
}

/**
 * Submit moderation decision for content.
 *
 * Submit the moderation decision (approve, remove, warn user, etc) with detailed
 * reasoning. Decision is immediately applied and recorded in review history.
 *
 * @param queueId - Queue item ID
 * @param request - Decision details (decision, reason, actions, violation_type)
 * @returns Review decision confirmation
 *
 * @example
 * const decision = await submitDecision('queue-12345', {
 *   decision: 'remove',
 *   violation_type: 'hate_speech',
 *   reason: 'Content violates community standards on hate speech',
 *   actions: [
 *     { type: 'remove_content', reason: 'policy_violation' },
 *     { type: 'user_warning', duration_hours: 0 },
 *     { type: 'notify_reporter', message: 'Action taken' }
 *   ]
 * })
 * console.log('Decision applied:', decision.applied_at)
 * console.log('Content removed, user warned')
 */
export const submitDecision = async (
  queueId: string,
  request: DecisionRequest
): Promise<ReviewDecision> => {
  const response = await http.post<{ success: boolean; data: ReviewDecision }>(
    `/moderation/reviews/${queueId}/submit-decision`,
    request
  )
  return response.data.data
}

/**
 * Get moderator's review sessions.
 *
 * Get paginated list of review sessions completed by a moderator.
 * Used for performance tracking and quality assurance.
 *
 * @param moderatorId - Moderator user ID
 * @param status - Filter by status (active, completed, abandoned)
 * @param limit - Max results (default 20, max 100)
 * @param offset - Skip N results (default 0)
 * @returns Paginated list of review sessions
 *
 * @example
 * const reviews = await getModeratorReviews('mod-123', 'completed', 50)
 * console.log('Total reviews:', reviews.total)
 * console.log('Avg decision time:', reviews.avg_time_per_review_minutes, 'min')
 */
export const getModeratorReviews = async (
  moderatorId: string,
  status?: string,
  limit: number = 20,
  offset: number = 0
): Promise<ReviewListResponse> => {
  const response = await http.get<{ success: boolean; data: ReviewListResponse }>(
    `/moderation/reviews/moderator/${moderatorId}`,
    {
      params: { status, limit: Math.min(limit, 100), offset },
    }
  )
  return response.data.data
}

/**
 * Get review history for content.
 *
 * Get complete review history for a content item including all moderation decisions,
 * appeals, and enforcement actions taken on that content.
 *
 * @param contentId - Content ID (post, comment, user, etc)
 * @returns Review history timeline
 *
 * @example
 * const history = await getContentReviewHistory('post-5678')
 * history.reviews.forEach(review => {
 *   console.log(`${review.decision} by ${review.moderator_id} on ${review.created_at}`)
 *   console.log(`Reason: ${review.reason}`)
 * })
 */
export const getContentReviewHistory = async (contentId: string): Promise<ReviewHistory> => {
  const response = await http.get<{ success: boolean; data: ReviewHistory }>(
    `/moderation/reviews/item/${contentId}`
  )
  return response.data.data
}

/**
 * Get review guidelines for violation type.
 *
 * Get moderation guidelines and precedent decisions for specific violation type.
 * Helps moderators make consistent decisions aligned with platform policy.
 *
 * @param violationType - Type of violation (hate_speech, violence, nudity, etc)
 * @returns Guidelines and precedent decisions
 *
 * @example
 * const guidelines = await getReviewGuidelines('hate_speech')
 * console.log('Policy:', guidelines.policy_text)
 * console.log('Recent decisions:', guidelines.precedent_decisions.length)
 * console.log('Recommended actions:', guidelines.recommended_actions)
 */
export const getReviewGuidelines = async (violationType: string) => {
  const response = await http.get<{
    success: boolean
    data: {
      violation_type: string
      policy_text: string
      examples: string[]
      recommended_actions: string[]
      precedent_decisions: Array<{
        decision: string
        reason: string
        appeal_rate: number
      }>
    }
  }>(`/moderation/reviews/guidelines/${violationType}`)
  return response.data.data
}

/**
 * Get review performance metrics.
 *
 * Get aggregate performance metrics for review process (average decision time,
 * appeal rate, consistency score, etc).
 *
 * @param period - Time period (today, week, month, all)
 * @returns Performance metrics
 *
 * @example
 * const metrics = await getReviewMetrics('week')
 * console.log('Avg review time:', metrics.avg_time_minutes, 'min')
 * console.log('Items reviewed:', metrics.total_reviews)
 * console.log('Appeal rate:', metrics.appeal_rate_percent, '%')
 */
export const getReviewMetrics = async (period: string = 'month') => {
  const response = await http.get<{
    success: boolean
    data: {
      period: string
      total_reviews: number
      avg_time_minutes: number
      approval_rate_percent: number
      removal_rate_percent: number
      appeal_rate_percent: number
      consistency_score: number
      moderators: Array<{
        moderator_id: string
        reviews: number
        avg_time: number
        appeal_rate: number
      }>
    }
  }>('/moderation/reviews/metrics', { params: { period } })
  return response.data.data
}
