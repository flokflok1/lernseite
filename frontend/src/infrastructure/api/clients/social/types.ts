/**
 * Social Domain - TypeScript Types & Interfaces
 * ===============================================
 *
 * Consolidated type definitions for all social domain APIs:
 * - User feedback (submission, management, analytics)
 * - Future: Posts, comments, reactions, connections
 */

// ============================================================================
// Feedback Types
// ============================================================================

/**
 * Context information for feedback submission.
 * Helps track where feedback was submitted from.
 */
export interface FeedbackContext {
  /** Course ID where feedback was submitted (if applicable) */
  course_id?: string | null
  /** Lesson ID where feedback was submitted (if applicable) */
  lesson_id?: string | null
  /** Page or feature context (e.g., 'course-editor', 'dashboard') */
  page_context?: string | null
  /** Page URL where feedback was submitted */
  url?: string
  /** User agent for debugging */
  user_agent?: string
  /** Timestamp when feedback was submitted */
  timestamp?: string
}

/**
 * Request body for submitting feedback.
 * Supports anonymous feedback and multiple feedback types.
 */
export interface SubmitFeedbackRequest {
  /** Type of feedback: question, bug, suggestion, praise, or other */
  type: 'question' | 'bug' | 'suggestion' | 'praise' | 'other'
  /** Main feedback message/content (required) */
  message: string
  /** Optional subject/title for the feedback */
  title?: string
  /** Optional email for follow-up (not required if authenticated) */
  email?: string
  /** Whether feedback should be marked as anonymous */
  is_anonymous?: boolean
  /** Context information about where feedback was submitted */
  context?: FeedbackContext
}

/**
 * Single feedback item with full details.
 * Includes status, priority, admin response, and AI analysis.
 */
export interface FeedbackItem {
  /** Unique feedback identifier */
  feedback_id: string
  /** Type of feedback: question, bug, suggestion, praise, other */
  feedback_type: string
  /** Subject/title of the feedback */
  title: string | null
  /** Main feedback message content */
  message: string
  /** Current status: new, read, in_progress, resolved, closed */
  status: string
  /** Priority level: low, normal, high, urgent */
  priority: string
  /** Timestamp when feedback was created */
  created_at: string
  /** AI-generated summary of the feedback */
  ai_summary?: string
  /** AI sentiment analysis result */
  ai_sentiment?: string
  /** Admin response message to the feedback author */
  admin_response?: string
  /** Timestamp of admin response */
  admin_responded_at?: string
}

/**
 * Paginated response for listing feedback items.
 */
export interface FeedbackListResponse {
  /** Array of feedback items on this page */
  feedbacks: FeedbackItem[]
  /** Current page number (1-indexed) */
  page: number
  /** Items per page */
  per_page: number
  /** Whether more pages exist */
  has_more: boolean
}

/**
 * Comprehensive feedback statistics for dashboard.
 * Includes counts by status, type, priority, and sentiment.
 */
export interface FeedbackDashboardStats {
  /** Total number of feedback items */
  total_feedbacks: number
  /** Count of new/unread feedback */
  new_count: number
  /** Count of feedback in progress */
  in_progress_count: number
  /** Count of resolved feedback */
  resolved_count: number
  /** Count of question-type feedback */
  questions: number
  /** Count of bug-type feedback */
  bugs: number
  /** Count of suggestion-type feedback */
  suggestions: number
  /** Count of praise-type feedback */
  praise: number
  /** Count of urgent priority feedback */
  urgent_count: number
  /** Count of high priority feedback */
  high_priority_count: number
  /** Feedback received in last 24 hours */
  last_24h: number
  /** Feedback received in last 7 days */
  last_7d: number
  /** Feedback received in last 30 days */
  last_30d: number
  /** Count of positive sentiment feedback (AI-analyzed) */
  positive_sentiment: number
  /** Count of negative sentiment feedback (AI-analyzed) */
  negative_sentiment: number
  /** Percentage of feedback that received admin response */
  response_rate_percent: number
  /** Average time in hours from submission to resolution */
  avg_resolution_hours: number
}

/**
 * Complete feedback dashboard response with analytics.
 * Provides overview of all feedback metrics and trends.
 */
export interface FeedbackDashboardResponse {
  /** Statistical summary of all feedback */
  stats: FeedbackDashboardStats
  /** Top trending topics/keywords in feedback */
  trending_topics: Array<{ tag: string; count: number }>
  /** Feedback distribution broken down by course */
  by_course: Array<{
    /** Course identifier */
    course_id: string
    /** Course title */
    course_title: string
    /** Total feedback for this course */
    feedback_count: number
    /** Bug reports for this course */
    bugs: number
    /** Questions for this course */
    questions: number
  }>
  /** Count of new feedback items */
  new_count: number
  /** Recent AI-generated feedback summaries */
  recent_summaries: Array<{
    /** Batch identifier */
    batch_id: string
    /** Period start date for this summary */
    period_start: string
    /** Period end date for this summary */
    period_end: string
    /** Total feedback items in this summary */
    total_feedbacks: number
    /** AI-generated executive summary */
    ai_executive_summary: string
  }>
}
