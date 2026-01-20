/**
 * Moderation Domain Types
 *
 * TypeScript interfaces for all moderation-related APIs.
 * Organized by moderation concern: Queue, Reviews, Actions, Appeals.
 */

// ============================================================================
// Queue Management Types
// ============================================================================

export interface QueueItem {
  /** Unique queue item ID */
  queue_id: string
  /** Content being reviewed (post, comment, user profile, etc) */
  content_id: string
  /** Type of content (post, comment, user, video, image, other) */
  content_type: 'post' | 'comment' | 'user' | 'video' | 'image' | 'other'
  /** ID of user who created the content */
  created_by_user_id: string
  /** Current status in queue */
  status: 'pending' | 'assigned' | 'on_hold' | 'resolved'
  /** Priority level affecting review order */
  priority: 'low' | 'medium' | 'high' | 'critical'
  /** ID of assigned moderator (if assigned) */
  assigned_to?: string
  /** When item was added to queue */
  created_at: string
  /** When assigned (if applicable) */
  assigned_at?: string
  /** Content preview/snippet for quick review */
  content_preview: string
  /** Number of reports on this content */
  reported_by_count: number
}

export interface QueueItemResponse extends QueueItem {
  /** Full content object for review */
  content: {
    id: string
    text?: string
    title?: string
    type: string
    created_at: string
    created_by: {
      user_id: string
      username: string
      name: string
    }
  }
  /** Reports/flags on this content */
  reports: Array<{
    report_id: string
    reporter_id: string
    violation_type: string
    description: string
    created_at: string
  }>
  /** Previous moderation decisions on similar content */
  similar_decisions?: Array<{
    content_id: string
    decision: string
    reason: string
    decided_at: string
  }>
  /** User's moderation history */
  user_moderation_history?: {
    total_warnings: number
    total_removals: number
    current_restrictions: string[]
    last_action_date?: string
  }
}

export interface QueueListResponse {
  /** Array of queue items */
  data: QueueItem[]
  /** Total number of items in queue */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
}

export interface AssignmentRequest {
  /** ID of moderator to assign to */
  moderator_id: string
  /** Reason for assignment (specialist, workload, training, other) */
  reason?: string
}

export interface PriorityUpdateRequest {
  /** New priority level */
  new_priority: 'low' | 'medium' | 'high' | 'critical'
  /** Reason for priority change */
  reason?: string
}

// ============================================================================
// Review Workflow Types
// ============================================================================

export interface ReviewSession {
  /** Unique review session ID */
  review_id: string
  /** Queue item being reviewed */
  queue_id: string
  /** Moderator conducting review */
  moderator_id: string
  /** When review started */
  started_at: string
  /** When review ended (if finished) */
  ended_at?: string
  /** Current status of review */
  status: 'active' | 'submitted' | 'completed' | 'abandoned'
  /** Content to review */
  content_id: string
  /** Type of content */
  content_type: string
  /** Content details */
  content: {
    id: string
    text?: string
    title?: string
    created_by: string
    created_at: string
  }
  /** Reports on this content */
  reports: Array<{
    report_id: string
    violation_type: string
    description: string
  }>
  /** User moderation context */
  user_context: {
    user_id: string
    account_age_days: number
    total_warnings: number
    previous_removals: number
  }
}

export interface ReviewDecision {
  /** Decision ID */
  decision_id: string
  /** Review session ID */
  review_id: string
  /** Decision made (approve, remove, warn, restrict, etc) */
  decision: 'approve' | 'remove' | 'warn' | 'restrict' | 'escalate'
  /** Type of violation (if removing) */
  violation_type?: string
  /** Reasoning for decision */
  reason: string
  /** Moderator who made decision */
  moderator_id: string
  /** When decision was made and applied */
  applied_at: string
  /** Actions taken as result */
  actions_taken: Array<{
    type: string
    status: 'pending' | 'completed'
    result?: string
  }>
}

export interface ReviewHistory {
  /** Content ID reviewed */
  content_id: string
  /** All reviews on this content */
  reviews: Array<{
    review_id: string
    decision: string
    reason: string
    moderator_id: string
    created_at: string
    can_appeal: boolean
    appeal_submitted?: string
  }>
  /** Total number of reviews */
  total_reviews: number
  /** Current status of content */
  current_status: 'available' | 'removed' | 'restricted' | 'archived'
}

export interface ReviewListResponse {
  /** Review sessions */
  data: ReviewSession[]
  /** Total reviews */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
  /** Average time per review */
  avg_time_per_review_minutes?: number
}

export interface DecisionRequest {
  /** Decision to apply */
  decision: 'approve' | 'remove' | 'warn' | 'restrict' | 'escalate'
  /** Violation type if removing */
  violation_type?: string
  /** Detailed reasoning */
  reason: string
  /** Specific actions to take */
  actions: Array<{
    type: 'remove_content' | 'user_warning' | 'restrict_user' | 'notify_reporter'
    reason?: string
    duration_hours?: number
    message?: string
  }>
  /** Whether to notify user of decision */
  notify_user?: boolean
}

// ============================================================================
// Enforcement Actions Types
// ============================================================================

export interface EnforcementAction {
  /** Unique action ID */
  action_id: string
  /** Type of action (remove_content, warn_user, restrict_user) */
  action_type: 'remove_content' | 'warn_user' | 'restrict_user' | 'suspend_account'
  /** Related review decision */
  review_decision_id: string
  /** User affected */
  user_id: string
  /** Content affected (if applicable) */
  content_id?: string
  /** Reason for action */
  reason: string
  /** Who performed the action */
  moderator_id: string
  /** When action was applied */
  applied_at: string
  /** When action expires (if temporary) */
  expires_at?: string
  /** Whether action can be appealed */
  can_appeal: boolean
  /** Current status */
  is_active: boolean
}

export interface ActionResponse {
  /** Action ID */
  action_id: string
  /** Type of action */
  action_type: string
  /** Status of action */
  status: 'pending' | 'applied' | 'completed'
  /** When action was applied */
  applied_at: string
  /** When user was notified */
  user_notified_at?: string
  /** Duration of action (if applicable) */
  duration_days?: number
  /** When action expires */
  expires_at?: string
}

export interface ActionHistoryResponse {
  /** Actions on user */
  data: EnforcementAction[]
  /** Total actions */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
}

export interface RemoveContentRequest {
  /** ID of content to remove */
  content_id: string
  /** Type of content */
  content_type: string
  /** Reason for removal (policy_violation, copyright, spam, etc) */
  reason: string
  /** How to remove: soft_delete (visible to author), archive (hidden), or permanent */
  removal_method: 'soft_delete' | 'archive' | 'permanent'
  /** Whether to notify content creator */
  notify_user?: boolean
  /** Message to send to user */
  user_notification_message?: string
}

export interface WarnUserRequest {
  /** User ID to warn */
  user_id: string
  /** Reason for warning */
  reason: string
  /** Severity level */
  severity: 'low' | 'medium' | 'high'
  /** How long warning remains on record (days) */
  duration_days: number
  /** Whether warning is public (shown in user profile) */
  public: boolean
  /** Custom warning message */
  warning_message?: string
}

export interface RestrictUserRequest {
  /** User ID to restrict */
  user_id: string
  /** Type of restriction */
  restriction_type: 'mute' | 'shadow_ban' | 'rate_limit' | 'post_restrictions' | 'follower_disable'
  /** Reason for restriction */
  reason: string
  /** How long restriction lasts (days) */
  duration_days: number
  /** Custom message for user */
  restriction_message?: string
}

// ============================================================================
// Appeal System Types
// ============================================================================

export interface Appeal {
  /** Unique appeal ID */
  appeal_id: string
  /** Action being appealed */
  action_id: string
  /** User appealing */
  user_id: string
  /** Original decision (what was being appealed) */
  original_decision: string
  /** Reason user is appealing */
  reason: string
  /** Additional evidence provided */
  evidence?: string
  /** URLs to supporting evidence */
  evidence_urls?: string[]
  /** When appeal was submitted */
  submitted_at: string
  /** Current status */
  status: 'pending' | 'in_review' | 'decided'
  /** Whether decision has been made */
  decision_made: boolean
  /** Appeal outcome (if decided) */
  appeal_decision?: 'upheld' | 'overturned' | 'partially_upheld'
  /** Reasoning for appeal decision (if decided) */
  decision_reasoning?: string
  /** When decision was made (if decided) */
  decided_at?: string
  /** Review assigned to moderator */
  assigned_to?: string
  /** Position in appeal queue */
  queue_position?: number
  /** Can user submit another appeal */
  can_reappeal: boolean
}

export interface AppealResponse {
  /** Appeal ID */
  appeal_id: string
  /** Submission status */
  status: 'submitted' | 'queued' | 'in_review'
  /** When appeal was submitted */
  submitted_at: string
  /** Position in review queue */
  queue_position: number
  /** Estimated wait time (days) */
  estimated_wait_days: number
}

export interface AppealListResponse {
  /** Appeals submitted by user */
  data: Appeal[]
  /** Total appeals */
  total: number
  /** Pagination limit */
  limit: number
  /** Pagination offset */
  offset: number
}

export interface AppealSubmitRequest {
  /** Action ID being appealed */
  action_id: string
  /** User's reason for appeal */
  reason: string
  /** Additional evidence/explanation */
  evidence?: string
  /** URLs to supporting evidence */
  new_evidence_urls?: string[]
}

export interface AppealReviewRequest {
  /** Decision on appeal */
  decision: 'upheld' | 'overturned' | 'partially_upheld'
  /** Reasoning for decision */
  reason: string
  /** Actions to take based on decision */
  actions_taken: string[]
  /** Whether to reverse original action */
  reverse_original_action?: boolean
}

export interface AppealDecision {
  /** Appeal ID decided */
  appeal_id: string
  /** Original action ID */
  original_action_id: string
  /** Decision made */
  decision: 'upheld' | 'overturned' | 'partially_upheld'
  /** Reasoning for decision */
  appeal_reasoning: string
  /** When decision was made */
  decided_at: string
  /** Appeal reviewer who decided */
  decided_by: string
  /** Actions taken (if applicable) */
  actions_taken: string[]
  /** Whether original action was reversed */
  original_action_reversed: boolean
  /** Status */
  status: 'decided' | 'appealed_further'
}
