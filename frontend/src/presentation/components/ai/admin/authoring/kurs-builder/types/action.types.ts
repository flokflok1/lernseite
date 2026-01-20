/**
 * Action Types - Authoring Actions & Workflows
 *
 * Defines types for AI-assisted authoring actions, quick actions,
 * and workflow management.
 *
 * @module kurs-builder/types/action
 */

/**
 * Quick Action
 *
 * A quick action button in the chat interface (2x2 grid).
 */
export interface QuickAction {
  /** Unique action identifier */
  action_id: string

  /** Action key for backend */
  action_key: string

  /** Display label */
  label: string

  /** Icon emoji */
  icon: string

  /** AI prompt template */
  prompt_template: string

  /** Optional mode hint */
  mode?: string

  /** Optional color theme */
  color?: 'blue' | 'green' | 'purple' | 'orange'

  /** Category for grouping */
  category?: string

  /** Required context type */
  requires_context?: 'chapter' | 'lesson' | 'none'
}

/**
 * Context Action
 *
 * Context-sensitive action when a chapter/lesson is selected.
 */
export interface ContextAction {
  /** Unique action identifier */
  action_id: string

  /** Action key */
  action_key: string

  /** Display label */
  label: string

  /** Icon emoji */
  icon: string

  /** Action description */
  description?: string

  /** Target entity type */
  entity_type: 'chapter' | 'lesson'

  /** Required materials count */
  min_files?: number
}

/**
 * Pending Action
 *
 * An action waiting for user confirmation.
 */
export interface PendingAction {
  /** Action type */
  type: 'create' | 'update' | 'delete'

  /** Target entity */
  entity: 'chapter' | 'lesson' | 'method' | 'quiz' | 'theory'

  /** Action key from QuickAction */
  actionKey: string

  /** Generated data from AI */
  generatedData: any

  /** Preview text for user */
  previewText: string

  /** Parent chapter (if lesson/method) */
  parentChapter?: {
    id: string
    title: string
  }

  /** Session ID */
  session_id?: string

  /** Timestamp */
  created_at?: string
}

/**
 * Selected Context
 *
 * The currently selected chapter or lesson for context-aware actions.
 */
export interface SelectedContext {
  /** Context type */
  type: 'chapter' | 'lesson'

  /** Entity ID */
  id: string

  /** Entity title */
  title: string

  /** Chapter ID (if lesson) */
  chapter_id?: string

  /** Chapter title (if lesson) */
  chapter_title?: string
}

/**
 * Workflow State
 *
 * State of the authoring workflow process.
 */
export interface WorkflowState {
  /** Current step */
  step: 'analyze' | 'theory' | 'methods' | 'confirm' | 'complete'

  /** Step completion status */
  completed_steps: string[]

  /** Current pending action */
  pending_action?: PendingAction

  /** Loading states */
  loading: {
    analyze: boolean
    theory: boolean
    methods: boolean
    confirm: boolean
  }

  /** Error state */
  error?: string
}
