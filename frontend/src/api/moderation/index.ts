/**
 * Moderation Domain Barrel Export
 * ====================================================
 *
 * Clean interface for all moderation-related APIs.
 * Consolidates Queue Management, Content Reviews, Enforcement Actions, and Appeal System.
 *
 * Usage:
 * import { getQueueItems, submitDecision, submitAppeal } from '@/api/moderation'
 * import type { QueueItem, ReviewDecision, Appeal } from '@/api/moderation'
 */

// ============================================================================
// Types Export (Consolidated)
// ============================================================================

export type {
  // Queue Management Types
  QueueItem,
  QueueItemResponse,
  QueueListResponse,
  AssignmentRequest,
  PriorityUpdateRequest,
  // Review Workflow Types
  ReviewSession,
  ReviewDecision,
  ReviewHistory,
  ReviewListResponse,
  DecisionRequest,
  // Enforcement Actions Types
  EnforcementAction,
  ActionResponse,
  ActionHistoryResponse,
  RemoveContentRequest,
  WarnUserRequest,
  RestrictUserRequest,
  // Appeal System Types
  Appeal,
  AppealResponse,
  AppealListResponse,
  AppealSubmitRequest,
  AppealReviewRequest,
  AppealDecision,
} from './types'

// ============================================================================
// Queue Management API Export
// ============================================================================

export {
  getQueueItems,
  getQueueItem,
  assignQueueItem,
  updateQueuePriority,
  holdQueueItem,
  removeFromQueue,
  getQueueStats,
} from './queue.api'

// ============================================================================
// Content Review Workflow API Export
// ============================================================================

export {
  getReviewSession,
  startReview,
  submitDecision,
  getModeratorReviews,
  getContentReviewHistory,
  getReviewGuidelines,
  getReviewMetrics,
} from './reviews.api'

// ============================================================================
// Enforcement Actions API Export
// ============================================================================

export {
  removeContent,
  warnUser,
  restrictUser,
  getAction,
  getUserActions,
  undoAction,
  getActionStats,
  getActiveRestrictions,
} from './actions.api'

// ============================================================================
// Appeal System API Export
// ============================================================================

export {
  submitAppeal,
  getAppeal,
  getUserAppeals,
  submitAppealReview,
  getAppealStats,
  getPendingAppeals,
  assignAppeal,
  getReviewerWorkload,
} from './appeals.api'
