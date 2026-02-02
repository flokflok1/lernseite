/**
 * Social Domain - Feedback API
 * ==============================
 *
 * User feedback collection and management system.
 * Part of the DDD Architecture - Infrastructure Layer (API Clients).
 *
 * Handles:
 * - User feedback submission (questions, bugs, suggestions, praise)
 * - Feedback list management and filtering (admin)
 * - Feedback status and priority tracking (admin)
 * - Admin responses and internal notes (admin)
 * - Feedback analytics dashboard (admin)
 * - AI-powered feedback summarization
 *
 * Usage:
 * import { submitFeedback, getMyFeedback, listFeedback } from '@/infrastructure/api/clients/social'
 * import type { FeedbackItem, SubmitFeedbackRequest } from '@/infrastructure/api/clients/social'
 */

import http from '@/infrastructure/api/http'

// ============================================================================
// Feedback Management API Functions
// ============================================================================

/**
 * Submit user feedback (works with or without authentication).
 *
 * Collects feedback from users in various categories (question, bug, suggestion, praise, other).
 * Captures context information like course/lesson IDs and user agent for better tracking.
 *
 * @param request - Feedback submission request data
 * @returns Feedback ID of the submitted feedback
 *
 * @example
 * const { feedback_id } = await submitFeedback({
 *   type: 'bug',
 *   message: 'Button not working in course editor',
 *   title: 'Course Editor Bug',
 *   context: { course_id: '123' }
 * })
 */
export const submitFeedback = async (request: SubmitFeedbackRequest): Promise<{ feedback_id: string }> => {
  const response = await http.post<{
    success: boolean
    data: { feedback_id: string; message: string }
  }>('/feedback/submit', request)
  return response.data.data
}

/**
 * Get current user's feedback history.
 *
 * Retrieves all feedback items submitted by the authenticated user.
 * Returns feedback sorted by creation date (newest first).
 *
 * @returns Array of user's feedback items
 *
 * @example
 * const myFeedback = await getMyFeedback()
 * console.log(`You submitted ${myFeedback.length} feedback items`)
 */
export const getMyFeedback = async (): Promise<FeedbackItem[]> => {
  const response = await http.get<{
    success: boolean
    data: { feedbacks: FeedbackItem[] }
  }>('/feedback/my')
  return response.data.data.feedbacks
}

/**
 * Get paginated list of all feedback (admin only).
 *
 * Retrieves feedback with optional filtering by type, status, priority, or course.
 * Results are paginated for performance.
 *
 * @param params - Query parameters for filtering and pagination
 * @returns Paginated feedback list with total count and pagination info
 *
 * @example
 * const results = await listFeedback({
 *   status: 'new',
 *   type: 'bug',
 *   page: 1,
 *   per_page: 20
 * })
 */
export const listFeedback = async (params?: {
  type?: string
  status?: string
  priority?: string
  course_id?: string
  search?: string
  page?: number
  per_page?: number
}): Promise<FeedbackListResponse> => {
  const response = await http.get<{
    success: boolean
    data: FeedbackListResponse
  }>('/feedback', { params })
  return response.data.data
}

/**
 * Get single feedback details (admin only).
 *
 * Retrieves complete details for a specific feedback item.
 * Includes AI analysis, admin responses, and internal notes.
 *
 * @param feedbackId - The feedback item ID
 * @returns Complete feedback item with all details
 *
 * @example
 * const feedback = await getFeedback('fb-123')
 * console.log(feedback.ai_summary)
 */
export const getFeedback = async (feedbackId: string): Promise<FeedbackItem> => {
  const response = await http.get<{
    success: boolean
    data: FeedbackItem
  }>(`/feedback/${feedbackId}`)
  return response.data.data
}

/**
 * Update feedback status (admin only).
 *
 * Changes the status of a feedback item in the workflow.
 * Statuses: new → read → in_progress → resolved → closed
 *
 * @param feedbackId - The feedback item ID
 * @param status - New status for the feedback
 * @returns Updated feedback item
 *
 * @example
 * const updated = await updateFeedbackStatus('fb-123', 'in_progress')
 */
export const updateFeedbackStatus = async (
  feedbackId: string,
  status: 'new' | 'read' | 'in_progress' | 'resolved' | 'closed'
): Promise<FeedbackItem> => {
  const response = await http.patch<{
    success: boolean
    data: FeedbackItem
  }>(`/feedback/${feedbackId}/status`, { status })
  return response.data.data
}

/**
 * Update feedback priority (admin only).
 *
 * Sets the priority level for a feedback item for better triage.
 * Helps organize response efforts.
 *
 * @param feedbackId - The feedback item ID
 * @param priority - New priority level
 * @returns Updated feedback item
 *
 * @example
 * const updated = await updateFeedbackPriority('fb-123', 'high')
 */
export const updateFeedbackPriority = async (
  feedbackId: string,
  priority: 'low' | 'normal' | 'high' | 'urgent'
): Promise<FeedbackItem> => {
  const response = await http.patch<{
    success: boolean
    data: FeedbackItem
  }>(`/feedback/${feedbackId}/priority`, { priority })
  return response.data.data
}

/**
 * Add admin response to feedback.
 *
 * Posts a response message to a feedback item that will be visible to the feedback author.
 * Marks the feedback as responded to.
 *
 * @param feedbackId - The feedback item ID
 * @param response - Admin response message
 * @returns Updated feedback item
 *
 * @example
 * const updated = await respondToFeedback('fb-123', 'Thank you for reporting this bug!')
 */
export const respondToFeedback = async (
  feedbackId: string,
  response: string
): Promise<FeedbackItem> => {
  const res = await http.post<{
    success: boolean
    data: FeedbackItem
  }>(`/feedback/${feedbackId}/respond`, { response })
  return res.data.data
}

/**
 * Add internal note to feedback (admin only).
 *
 * Creates an internal note on a feedback item for team discussion.
 * Internal notes are not visible to the feedback author.
 *
 * @param feedbackId - The feedback item ID
 * @param note - Note content
 * @param isInternal - Whether note is internal (default: true)
 * @returns Note data
 *
 * @example
 * await addFeedbackNote('fb-123', 'Duplicate of fb-120', true)
 */
export const addFeedbackNote = async (
  feedbackId: string,
  note: string,
  isInternal: boolean = true
): Promise<unknown> => {
  const response = await http.post<{
    success: boolean
    data: unknown
  }>(`/feedback/${feedbackId}/notes`, { note, is_internal: isInternal })
  return response.data.data
}

// ============================================================================
// Feedback Analytics & Dashboard API Functions
// ============================================================================

/**
 * Get feedback dashboard data (admin only).
 *
 * Retrieves comprehensive feedback analytics including:
 * - Feedback statistics (total, by status, by type)
 * - Trending topics and keywords
 * - Feedback distribution by course
 * - Recent AI-generated summaries
 *
 * @returns Dashboard data with stats, trending topics, and course breakdown
 *
 * @example
 * const dashboard = await getFeedbackDashboard()
 * console.log(`Total feedback: ${dashboard.stats.total_feedbacks}`)
 * console.log(`Response rate: ${dashboard.stats.response_rate_percent}%`)
 */
export const getFeedbackDashboard = async (): Promise<FeedbackDashboardResponse> => {
  const response = await http.get<{
    success: boolean
    data: FeedbackDashboardResponse
  }>('/feedback/dashboard')
  return response.data.data
}

/**
 * Generate AI summary batch (admin only).
 *
 * Triggers AI analysis of feedback items in a time period.
 * Generates executive summary and key insights from collected feedback.
 *
 * @param params - Period for summary generation
 * @returns Batch processing result
 *
 * @example
 * const result = await generateFeedbackSummary({
 *   period_start: '2026-01-01',
 *   period_end: '2026-01-07'
 * })
 */
export const generateFeedbackSummary = async (params?: {
  period_start?: string
  period_end?: string
}): Promise<unknown> => {
  const response = await http.post<{
    success: boolean
    data: unknown
  }>('/feedback/generate-summary', params)
  return response.data.data
}

/**
 * Get summary batches (admin only).
 *
 * Retrieves previously generated feedback summary batches.
 * Used for reviewing historical feedback analysis.
 *
 * @param limit - Maximum number of summaries to return (default: 10)
 * @returns Array of feedback summary batches
 *
 * @example
 * const summaries = await getFeedbackSummaries(5)
 * summaries.forEach(s => console.log(s.ai_executive_summary))
 */
export const getFeedbackSummaries = async (limit: number = 10): Promise<unknown[]> => {
  const response = await http.get<{
    success: boolean
    data: { batches: unknown[] }
  }>('/feedback/summaries', { params: { limit } })
  return response.data.data.batches
}
