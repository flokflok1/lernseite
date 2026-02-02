/**
 * Course Editor WebSocket Handlers
 *
 * Handles real-time WebSocket events for AI-powered course editor:
 * - AI message streaming
 * - Generation progress
 * - Content completion
 * - Variant creation
 * - Session updates
 *
 * Events namespace: course-editor/*
 */

import { Socket } from 'socket.io-client'
import type { ChatMessage, Variant, GeneratedContentResponse } from '../api/clients/course-editor/courseEditor.client'

// ============================================================================
// Event Types
// ============================================================================

/**
 * AI Message Received Event
 */
export interface AIMessageReceivedEvent {
  sessionId: string
  message: ChatMessage
  isComplete: boolean
}

/**
 * Generation Started Event
 */
export interface AIGenerationStartedEvent {
  contentId: string
  projectId: string
  contentType: 'explanation' | 'example' | 'exercise' | 'quiz'
  estimatedDuration: number // in seconds
}

/**
 * Generation Complete Event
 */
export interface AIGenerationCompleteEvent {
  contentId: string
  content: GeneratedContentResponse
  variants: Variant[]
}

/**
 * Variant Created Event
 */
export interface AIVariantCreatedEvent {
  contentId: string
  variant: Variant
  index: number // Position in variants array
}

/**
 * Session Updated Event
 */
export interface AISessionUpdatedEvent {
  sessionId: string
  updatedAt: Date
  messageCount: number
  status: 'active' | 'paused' | 'completed'
}

// ============================================================================
// Handler Definitions
// ============================================================================

export type AIMessageReceivedHandler = (event: AIMessageReceivedEvent) => void
export type AIGenerationStartedHandler = (event: AIGenerationStartedEvent) => void
export type AIGenerationCompleteHandler = (event: AIGenerationCompleteEvent) => void
export type AIVariantCreatedHandler = (event: AIVariantCreatedEvent) => void
export type AISessionUpdatedHandler = (event: AISessionUpdatedEvent) => void

// ============================================================================
// Course Editor WebSocket Manager
// ============================================================================

export class CourseEditorWebSocketManager {
  private socket: Socket | null = null
  private handlers: Map<string, Set<Function>> = new Map()

  constructor(socket: Socket) {
    this.socket = socket
    this.setupEventListeners()
  }

  /**
   * Setup WebSocket event listeners
   */
  private setupEventListeners(): void {
    if (!this.socket) return

    // AI Message Received
    this.socket.on('course-editor/ai-message-received', (event: AIMessageReceivedEvent) => {
      this.emit('ai-message-received', event)
    })

    // AI Generation Started
    this.socket.on('course-editor/ai-generation-started', (event: AIGenerationStartedEvent) => {
      this.emit('ai-generation-started', event)
    })

    // AI Generation Complete
    this.socket.on('course-editor/ai-generation-complete', (event: AIGenerationCompleteEvent) => {
      this.emit('ai-generation-complete', event)
    })

    // AI Variant Created
    this.socket.on('course-editor/ai-variant-created', (event: AIVariantCreatedEvent) => {
      this.emit('ai-variant-created', event)
    })

    // Session Updated
    this.socket.on('course-editor/ai-session-updated', (event: AISessionUpdatedEvent) => {
      this.emit('ai-session-updated', event)
    })

    // Error handling
    this.socket.on('course-editor/error', (error: { message: string; code?: string }) => {
      this.emit('error', error)
    })
  }

  /**
   * Register event handler
   */
  on<T extends keyof CourseEditorEvents>(
    event: T,
    handler: CourseEditorEvents[T]
  ): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set())
    }

    this.handlers.get(event)!.add(handler)

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(event)
      if (handlers) {
        handlers.delete(handler)
      }
    }
  }

  /**
   * Remove event handler
   */
  off<T extends keyof CourseEditorEvents>(
    event: T,
    handler: CourseEditorEvents[T]
  ): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  /**
   * Emit event to all registered handlers
   */
  private emit<T extends keyof CourseEditorEvents>(
    event: T,
    data: any
  ): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          (handler as Function)(data)
        } catch (error) {
          console.error(`Error in ${event} handler:`, error)
        }
      })
    }
  }

  /**
   * Subscribe to AI message stream
   *
   * @param sessionId - Chat session ID
   * @param handler - Callback for each message
   * @returns Unsubscribe function
   */
  onAIMessage(sessionId: string, handler: AIMessageReceivedHandler): () => void {
    return this.on('ai-message-received', (event) => {
      if (event.sessionId === sessionId) {
        handler(event)
      }
    })
  }

  /**
   * Subscribe to generation progress
   *
   * @param contentId - Generated content ID
   * @param handler - Callback on generation start
   * @returns Unsubscribe function
   */
  onGenerationStart(contentId: string, handler: AIGenerationStartedHandler): () => void {
    return this.on('ai-generation-started', (event) => {
      if (event.contentId === contentId) {
        handler(event)
      }
    })
  }

  /**
   * Subscribe to generation completion
   *
   * @param contentId - Generated content ID
   * @param handler - Callback on generation complete
   * @returns Unsubscribe function
   */
  onGenerationComplete(contentId: string, handler: AIGenerationCompleteHandler): () => void {
    return this.on('ai-generation-complete', (event) => {
      if (event.contentId === contentId) {
        handler(event)
      }
    })
  }

  /**
   * Subscribe to variant creation
   *
   * @param contentId - Generated content ID
   * @param handler - Callback for each variant
   * @returns Unsubscribe function
   */
  onVariantCreated(contentId: string, handler: AIVariantCreatedHandler): () => void {
    return this.on('ai-variant-created', (event) => {
      if (event.contentId === contentId) {
        handler(event)
      }
    })
  }

  /**
   * Subscribe to session updates
   *
   * @param sessionId - Chat session ID
   * @param handler - Callback on session update
   * @returns Unsubscribe function
   */
  onSessionUpdate(sessionId: string, handler: AISessionUpdatedHandler): () => void {
    return this.on('ai-session-updated', (event) => {
      if (event.sessionId === sessionId) {
        handler(event)
      }
    })
  }

  /**
   * Subscribe to errors
   */
  onError(handler: (error: { message: string; code?: string }) => void): () => void {
    return this.on('error', handler as any)
  }

  /**
   * Emit socket event
   */
  emit<T>(event: string, data: T): void {
    if (this.socket) {
      this.socket.emit(event, data)
    }
  }

  /**
   * Cleanup and disconnect
   */
  disconnect(): void {
    this.handlers.clear()
    this.socket = null
  }
}

// ============================================================================
// Event Map
// ============================================================================

export interface CourseEditorEvents {
  'ai-message-received': AIMessageReceivedHandler
  'ai-generation-started': AIGenerationStartedHandler
  'ai-generation-complete': AIGenerationCompleteHandler
  'ai-variant-created': AIVariantCreatedHandler
  'ai-session-updated': AISessionUpdatedHandler
  error: (error: { message: string; code?: string }) => void
}

// ============================================================================
// Socket IO Event Emitters
// ============================================================================

/**
 * Emit request to start generation
 */
export const emitStartGeneration = (
  socket: Socket,
  payload: {
    projectId: string
    contentType: string
    templateId?: string
    customPrompt?: string
  }
): void => {
  socket.emit('course-editor/start-generation', payload)
}

/**
 * Emit request to generate variants
 */
export const emitGenerateVariants = (
  socket: Socket,
  payload: {
    contentId: string
    count: number
  }
): void => {
  socket.emit('course-editor/generate-variants', payload)
}

/**
 * Emit chat message
 */
export const emitChatMessage = (
  socket: Socket,
  payload: {
    sessionId: string
    message: string
  }
): void => {
  socket.emit('course-editor/chat-message', payload)
}

/**
 * Emit session join
 */
export const emitJoinSession = (
  socket: Socket,
  sessionId: string
): void => {
  socket.emit('course-editor/join-session', { sessionId })
}

/**
 * Emit session leave
 */
export const emitLeaveSession = (
  socket: Socket,
  sessionId: string
): void => {
  socket.emit('course-editor/leave-session', { sessionId })
}

// ============================================================================
// Singleton Instance
// ============================================================================

let courseEditorManager: CourseEditorWebSocketManager | null = null

/**
 * Initialize course editor WebSocket manager
 */
export const initializeCourseEditorWebSocket = (
  socket: Socket
): CourseEditorWebSocketManager => {
  courseEditorManager = new CourseEditorWebSocketManager(socket)
  return courseEditorManager
}

/**
 * Get course editor WebSocket manager instance
 */
export const getCourseEditorWebSocket = (): CourseEditorWebSocketManager | null => {
  return courseEditorManager
}

/**
 * Cleanup course editor WebSocket
 */
export const cleanupCourseEditorWebSocket = (): void => {
  if (courseEditorManager) {
    courseEditorManager.disconnect()
    courseEditorManager = null
  }
}
