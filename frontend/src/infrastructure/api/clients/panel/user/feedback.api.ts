/**
 * Feedback API - API functions for user feedback system
 */

import http from '@/infrastructure/api/http'

// Types
export interface FeedbackContext {
  course_id?: string | null
  lesson_id?: string | null
  page_context?: string | null
  url?: string
  user_agent?: string
  timestamp?: string
}

export interface SubmitFeedbackRequest {
  type: 'question' | 'bug' | 'suggestion' | 'praise' | 'other'
  message: string
  title?: string
  email?: string
  is_anonymous?: boolean
  context?: FeedbackContext
}

export interface FeedbackItem {
  feedback_id: string
  feedback_type: string
  title: string | null
  message: string
  status: string
  priority: string
  created_at: string
  ai_summary?: string
  ai_sentiment?: string
  admin_response?: string
  admin_responded_at?: string
}

export interface FeedbackListResponse {
  feedbacks: FeedbackItem[]
  page: number
  per_page: number
  has_more: boolean
}

export interface FeedbackDashboardStats {
  total_feedbacks: number
  new_count: number
  in_progress_count: number
  resolved_count: number
  questions: number
  bugs: number
  suggestions: number
  praise: number
  urgent_count: number
  high_priority_count: number
  last_24h: number
  last_7d: number
  last_30d: number
  positive_sentiment: number
  negative_sentiment: number
  response_rate_percent: number
  avg_resolution_hours: number
}

export interface FeedbackDashboardResponse {
  stats: FeedbackDashboardStats
  trending_topics: Array<{ tag: string; count: number }>
  by_course: Array<{
    course_id: string
    course_title: string
    feedback_count: number
    bugs: number
    questions: number
  }>
  new_count: number
  recent_summaries: Array<{
    batch_id: string
    period_start: string
    period_end: string
    total_feedbacks: number
    ai_executive_summary: string
  }>
}

/**
 * Submit user feedback (works with or without auth)
 */
export const submitFeedback = async (request: SubmitFeedbackRequest): Promise<{ feedback_id: string }> => {
  const response = await http.post<{
    success: boolean
    data: { feedback_id: string; message: string }
  }>('/feedback/submit', request)
  return response.data.data
}

/**
 * Get current user's feedback history
 */
export const getMyFeedback = async (): Promise<FeedbackItem[]> => {
  const response = await http.get<{
    success: boolean
    data: { feedbacks: FeedbackItem[] }
  }>('/feedback/my')
  return response.data.data.feedbacks
}

/**
 * Get all feedback (admin only)
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
 * Get single feedback details (admin only)
 */
export const getFeedback = async (feedbackId: string): Promise<FeedbackItem> => {
  const response = await http.get<{
    success: boolean
    data: FeedbackItem
  }>(`/feedback/${feedbackId}`)
  return response.data.data
}

/**
 * Update feedback status (admin only)
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
 * Update feedback priority (admin only)
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
 * Add admin response to feedback
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
 * Add internal note to feedback (admin only)
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

/**
 * Get feedback dashboard data (admin only)
 */
export const getFeedbackDashboard = async (): Promise<FeedbackDashboardResponse> => {
  const response = await http.get<{
    success: boolean
    data: FeedbackDashboardResponse
  }>('/feedback/dashboard')
  return response.data.data
}

/**
 * Generate AI summary batch (admin only)
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
 * Get summary batches (admin only)
 */
export const getFeedbackSummaries = async (limit: number = 10): Promise<unknown[]> => {
  const response = await http.get<{
    success: boolean
    data: { batches: unknown[] }
  }>('/feedback/summaries', { params: { limit } })
  return response.data.data.batches
}
