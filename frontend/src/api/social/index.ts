/**
 * Social Domain - Barrel Export
 * ==============================
 *
 * This file provides a clean interface for importing all social-related APIs and types.
 * Part of the DDD Architecture - Infrastructure Layer (API Clients).
 *
 * Usage:
 * import { submitFeedback, getFeedbackDashboard } from '@/api/social'
 * import type { FeedbackItem, SubmitFeedbackRequest } from '@/api/social'
 *
 * Future APIs (planned):
 * - Feed management (getFeed, getFeedItem, etc.)
 * - Posts (createPost, updatePost, deletePost, etc.)
 * - Comments (addComment, updateComment, deleteComment, etc.)
 * - Reactions (likePost, unlikePost, etc.)
 * - Social connections (follow, unfollow, getConnections, etc.)
 */

// ============================================================================
// Types Export (Consolidated from all social API modules)
// ============================================================================

export type {
  // Feedback Types
  FeedbackContext,
  FeedbackDashboardResponse,
  FeedbackDashboardStats,
  FeedbackItem,
  FeedbackListResponse,
  SubmitFeedbackRequest,
} from './types'

// ============================================================================
// Feedback API Export
// ============================================================================

export {
  addFeedbackNote,
  generateFeedbackSummary,
  getFeedback,
  getFeedbackDashboard,
  getFeedbackSummaries,
  getMyFeedback,
  listFeedback,
  respondToFeedback,
  submitFeedback,
  updateFeedbackPriority,
  updateFeedbackStatus,
} from './feedback.api'

// ============================================================================
// Future API Placeholders
// ============================================================================

// Feed API (planned)
// export { ... } from './feed.api'

// Posts API (planned)
// export { ... } from './posts.api'

// Comments API (planned)
// export { ... } from './comments.api'

// Reactions API (planned)
// export { ... } from './reactions.api'

// Connections API (planned)
// export { ... } from './connections.api'
