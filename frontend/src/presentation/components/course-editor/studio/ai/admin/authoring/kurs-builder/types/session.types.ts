/**
 * Session Types - KI-Kurs-Builder Session Management
 *
 * Defines types for authoring sessions and chat interactions.
 *
 * @module kurs-builder/types/session
 */

/**
 * Authoring Session
 *
 * Represents an active course authoring session with AI assistance.
 */
export interface Session {
  /** Unique session identifier */
  session_id: string

  /** Course being authored */
  course_id: string

  /** Session status */
  status: 'active' | 'paused' | 'completed' | 'finalized'

  /** Session creation timestamp */
  created_at: string

  /** Last activity timestamp */
  updated_at: string

  /** Session metadata */
  metadata?: {
    /** Total AI requests made */
    ai_requests?: number

    /** Tokens consumed */
    tokens_used?: number

    /** Draft structure version */
    draft_version?: number
  }
}

/**
 * Chat Message
 *
 * Represents a message in the authoring chat interface.
 */
export interface ChatMessage {
  /** Message sender role */
  role: 'user' | 'assistant'

  /** Message content (markdown supported) */
  content: string

  /** Optional timestamp */
  timestamp?: string

  /** Operations performed (for assistant messages) */
  operations?: string[]

  /** Error indicator */
  error?: boolean

  /** Loading indicator for streaming */
  loading?: boolean
}

/**
 * Session Statistics
 *
 * Aggregated statistics for a session.
 */
export interface SessionStats {
  /** Total messages exchanged */
  message_count: number

  /** Chapters created/modified */
  chapters_count: number

  /** Lessons created/modified */
  lessons_count: number

  /** Learning methods created */
  methods_count: number

  /** Total tokens consumed */
  tokens_used: number

  /** Session duration in seconds */
  duration_seconds: number
}
