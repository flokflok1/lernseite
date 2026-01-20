/**
 * Moderation Queue Management API
 *
 * Handles moderation queue operations, content triage, and workflow management.
 * Manages items awaiting review, assignment, and status tracking.
 *
 * Endpoints:
 * - GET /moderation/queue - Get queue items with filters
 * - GET /moderation/queue/{id} - Get queue item details
 * - POST /moderation/queue/{id}/assign - Assign item to moderator
 * - POST /moderation/queue/{id}/prioritize - Change priority level
 * - POST /moderation/queue/{id}/hold - Place item on hold
 * - DELETE /moderation/queue/{id} - Remove from queue (resolved/dismissed)
 */

import http from '@/infrastructure/api/http'
import type {
  QueueItem,
  QueueItemResponse,
  QueueListResponse,
  AssignmentRequest,
  PriorityUpdateRequest,
} from './types'

/**
 * Get moderation queue items.
 *
 * Retrieve paginated list of items awaiting moderation with optional filtering.
 * Queue supports filtering by status, priority, type, and assigned moderator.
 *
 * @param status - Filter by status (pending, assigned, on_hold, resolved)
 * @param priority - Filter by priority (low, medium, high, critical)
 * @param content_type - Filter by content type (post, comment, user, video, image)
 * @param assigned_to - Filter by moderator ID
 * @param limit - Max items to return (default 20, max 100)
 * @param offset - Items to skip for pagination (default 0)
 * @returns Queue items with pagination info
 *
 * @example
 * const queue = await getQueueItems({
 *   status: 'pending',
 *   priority: 'high',
 *   limit: 50
 * })
 * console.log(`${queue.data.length} items pending review`)
 */
export const getQueueItems = async (filters: {
  status?: string
  priority?: string
  content_type?: string
  assigned_to?: string
  limit?: number
  offset?: number
} = {}): Promise<QueueListResponse> => {
  const response = await http.get<{ success: boolean; data: QueueListResponse }>(
    '/moderation/queue',
    { params: filters }
  )
  return response.data.data
}

/**
 * Get queue item details.
 *
 * Retrieve full details of a specific queue item including flagged content,
 * report information, history, and previous decisions on similar content.
 *
 * @param queueId - Queue item ID
 * @returns Full queue item details
 *
 * @example
 * const item = await getQueueItem('queue-12345')
 * console.log('Content:', item.content.text)
 * console.log('Flagged by:', item.reported_by_count, 'users')
 * console.log('Previous decisions on similar:', item.similar_decisions?.length)
 */
export const getQueueItem = async (queueId: string): Promise<QueueItemResponse> => {
  const response = await http.get<{ success: boolean; data: QueueItemResponse }>(
    `/moderation/queue/${queueId}`
  )
  return response.data.data
}

/**
 * Assign queue item to moderator.
 *
 * Assign a pending queue item to a specific moderator or to current user.
 * Updates item status to 'assigned' and records assignment timestamp.
 *
 * @param queueId - Queue item ID
 * @param request - Assignment request (moderator_id, reason)
 * @returns Updated queue item
 *
 * @example
 * await assignQueueItem('queue-12345', {
 *   moderator_id: 'mod-user-789',
 *   reason: 'Assigned to specialist for hateful content review'
 * })
 * // Item now shows assigned_to: 'mod-user-789', status: 'assigned'
 */
export const assignQueueItem = async (
  queueId: string,
  request: AssignmentRequest
): Promise<QueueItemResponse> => {
  const response = await http.post<{ success: boolean; data: QueueItemResponse }>(
    `/moderation/queue/${queueId}/assign`,
    request
  )
  return response.data.data
}

/**
 * Update queue item priority.
 *
 * Change the priority level of a queue item. Affects review order and routing.
 * Critical items bypass queue and go to specialized reviewers.
 *
 * @param queueId - Queue item ID
 * @param request - Priority update request (new_priority, reason)
 * @returns Updated queue item
 *
 * @example
 * await updateQueuePriority('queue-12345', {
 *   new_priority: 'critical',
 *   reason: 'Illegal content - escalating to law enforcement liaison'
 * })
 * // Item now has priority: 'critical', escalated: true
 */
export const updateQueuePriority = async (
  queueId: string,
  request: PriorityUpdateRequest
): Promise<QueueItemResponse> => {
  const response = await http.post<{ success: boolean; data: QueueItemResponse }>(
    `/moderation/queue/${queueId}/prioritize`,
    request
  )
  return response.data.data
}

/**
 * Place queue item on hold.
 *
 * Temporarily place item on hold (waiting for additional context, legal review, etc).
 * Removes from active queue but keeps history for future reference.
 *
 * @param queueId - Queue item ID
 * @param reason - Reason for hold (legal_review, missing_context, escalation, other)
 * @param hold_until - Optional: ISO datetime when hold expires
 * @returns Updated queue item
 *
 * @example
 * await holdQueueItem('queue-12345', 'legal_review', '2026-02-20T00:00:00Z')
 * // Item status: 'on_hold', hold_reason: 'legal_review', hold_until: '2026-02-20T00:00:00Z'
 */
export const holdQueueItem = async (
  queueId: string,
  reason: string,
  hold_until?: string
) => {
  const response = await http.post<{ success: boolean; data: QueueItemResponse }>(
    `/moderation/queue/${queueId}/hold`,
    { reason, hold_until }
  )
  return response.data.data
}

/**
 * Remove item from queue.
 *
 * Remove item from queue after resolution (content removed, user warned/banned, etc).
 * Item moved to completed queue for analytics and audit purposes.
 *
 * @param queueId - Queue item ID
 * @returns Success status
 *
 * @example
 * await removeFromQueue('queue-12345')
 * // Item moved to completed queue, no longer in active queue
 */
export const removeFromQueue = async (queueId: string) => {
  const response = await http.delete<{ success: boolean; data: { status: 'removed' } }>(
    `/moderation/queue/${queueId}`
  )
  return response.data.data
}

/**
 * Get queue statistics.
 *
 * Get real-time statistics about queue state (total items, by priority, by type, etc).
 * Used for dashboard and performance monitoring.
 *
 * @returns Queue statistics
 *
 * @example
 * const stats = await getQueueStats()
 * console.log('Total pending:', stats.total)
 * console.log('Critical items:', stats.by_priority.critical)
 * console.log('Avg time in queue:', stats.avg_wait_time_minutes, 'minutes')
 */
export const getQueueStats = async () => {
  const response = await http.get<{
    success: boolean
    data: {
      total: number
      by_status: { [key: string]: number }
      by_priority: { [key: string]: number }
      by_content_type: { [key: string]: number }
      avg_wait_time_minutes: number
      oldest_item_age_minutes: number
    }
  }>('/moderation/queue/stats')
  return response.data.data
}
