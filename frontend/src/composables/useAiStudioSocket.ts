/**
 * AI Studio WebSocket Composable
 *
 * Provides real-time connection to AI Studio backend for:
 * - Generation progress updates
 * - Session status changes
 * - Variant generation notifications
 *
 * Phase D4 - KI-Authoring-Studio WebSocket Integration
 */

import { ref, onUnmounted, watch } from 'vue'
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/store/modules/core'

// Event types
export interface GenerationProgressEvent {
  session_id: string
  event_type: 'progress'
  step: string
  progress: number
  message: string
  data?: Record<string, unknown>
}

export interface GenerationCompleteEvent {
  session_id: string
  event_type: 'complete'
  step: string
  progress: 100
  message: string
  data: Record<string, unknown>
}

export interface GenerationErrorEvent {
  session_id: string
  event_type: 'error'
  step: string
  progress: 0
  message: string
  data?: Record<string, unknown>
}

export interface SessionStatusEvent {
  session_id: string
  event_type: 'status_changed'
  old_status: string
  new_status: string
  message: string
}

export interface VariantGeneratedEvent {
  session_id: string
  event_type: 'variant_generated'
  variant_type: string
  variant_index: number
  variant_id: string
  message: string
}

export type AIStudioEvent =
  | GenerationProgressEvent
  | GenerationCompleteEvent
  | GenerationErrorEvent
  | SessionStatusEvent
  | VariantGeneratedEvent

// Callbacks type
export interface AIStudioSocketCallbacks {
  onProgress?: (event: GenerationProgressEvent) => void
  onComplete?: (event: GenerationCompleteEvent) => void
  onError?: (event: GenerationErrorEvent) => void
  onStatusChange?: (event: SessionStatusEvent) => void
  onVariantGenerated?: (event: VariantGeneratedEvent) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useAiStudioSocket(callbacks: AIStudioSocketCallbacks = {}) {
  const authStore = useAuthStore()

  // State
  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const currentSessionId = ref<string | null>(null)
  const connectionError = ref<string | null>(null)
  const lastEvent = ref<AIStudioEvent | null>(null)

  /**
   * Connect to AI Studio WebSocket namespace
   */
  function connect() {
    if (socket.value?.connected) {
      console.log('[AI Studio Socket] Already connected')
      return
    }

    const token = authStore.accessToken
    if (!token) {
      connectionError.value = 'No authentication token available'
      console.error('[AI Studio Socket] No auth token')
      return
    }

    // Determine WebSocket URL (same host as API)
    const wsUrl = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL || 'http://localhost:5000'

    console.log('[AI Studio Socket] Connecting to:', wsUrl)

    socket.value = io(`${wsUrl}/ai-studio`, {
      auth: { token },
      query: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000
    })

    // Connection events
    socket.value.on('connect', () => {
      isConnected.value = true
      connectionError.value = null
      console.log('[AI Studio Socket] Connected')
      callbacks.onConnect?.()
    })

    socket.value.on('disconnect', (reason) => {
      isConnected.value = false
      console.log('[AI Studio Socket] Disconnected:', reason)
      callbacks.onDisconnect?.()
    })

    socket.value.on('connect_error', (error) => {
      connectionError.value = error.message
      console.error('[AI Studio Socket] Connection error:', error)
    })

    socket.value.on('connected', (data) => {
      console.log('[AI Studio Socket] Server acknowledged connection:', data)
    })

    // Generation events
    socket.value.on('generation_progress', (event: GenerationProgressEvent) => {
      lastEvent.value = event
      console.log('[AI Studio Socket] Progress:', event.progress, event.message)
      callbacks.onProgress?.(event)
    })

    socket.value.on('generation_complete', (event: GenerationCompleteEvent) => {
      lastEvent.value = event
      console.log('[AI Studio Socket] Complete:', event.step)
      callbacks.onComplete?.(event)
    })

    socket.value.on('generation_error', (event: GenerationErrorEvent) => {
      lastEvent.value = event
      console.error('[AI Studio Socket] Error:', event.message)
      callbacks.onError?.(event)
    })

    socket.value.on('session_status', (event: SessionStatusEvent) => {
      lastEvent.value = event
      console.log('[AI Studio Socket] Status changed:', event.old_status, '->', event.new_status)
      callbacks.onStatusChange?.(event)
    })

    socket.value.on('variant_generated', (event: VariantGeneratedEvent) => {
      lastEvent.value = event
      console.log('[AI Studio Socket] Variant generated:', event.variant_type, event.variant_index)
      callbacks.onVariantGenerated?.(event)
    })

    // Session room events
    socket.value.on('joined_session', (data) => {
      console.log('[AI Studio Socket] Joined session:', data.session_id)
    })

    socket.value.on('left_session', (data) => {
      console.log('[AI Studio Socket] Left session:', data.session_id)
    })

    socket.value.on('error', (data) => {
      console.error('[AI Studio Socket] Server error:', data.message)
      connectionError.value = data.message
    })
  }

  /**
   * Disconnect from WebSocket
   */
  function disconnect() {
    if (socket.value) {
      if (currentSessionId.value) {
        leaveSession(currentSessionId.value)
      }
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
      console.log('[AI Studio Socket] Manually disconnected')
    }
  }

  /**
   * Join a session room to receive updates
   */
  function joinSession(sessionId: string) {
    if (!socket.value?.connected) {
      console.warn('[AI Studio Socket] Not connected, cannot join session')
      return
    }

    // Leave current session if any
    if (currentSessionId.value && currentSessionId.value !== sessionId) {
      leaveSession(currentSessionId.value)
    }

    socket.value.emit('join_session', { session_id: sessionId })
    currentSessionId.value = sessionId
  }

  /**
   * Leave a session room
   */
  function leaveSession(sessionId: string) {
    if (!socket.value?.connected) return

    socket.value.emit('leave_session', { session_id: sessionId })
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
    }
  }

  /**
   * Send ping for keepalive
   */
  function ping() {
    if (!socket.value?.connected) return
    socket.value.emit('ping', { timestamp: Date.now() })
  }

  // Auto-disconnect on unmount
  onUnmounted(() => {
    disconnect()
  })

  // Watch for auth changes - reconnect if token changes
  watch(() => authStore.accessToken, (newToken, oldToken) => {
    if (newToken !== oldToken && socket.value?.connected) {
      console.log('[AI Studio Socket] Auth token changed, reconnecting...')
      disconnect()
      if (newToken) {
        setTimeout(connect, 100)
      }
    }
  })

  return {
    // State
    socket,
    isConnected,
    currentSessionId,
    connectionError,
    lastEvent,

    // Actions
    connect,
    disconnect,
    joinSession,
    leaveSession,
    ping
  }
}
