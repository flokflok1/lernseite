/**
 * useChatManager - Chat & Messaging Management
 *
 * Manages chat messages, sending, and UI interactions for course authoring.
 *
 * @module kurs-builder/composables/useChatManager
 */

import { ref, nextTick, watch, type Ref } from 'vue'
import http from '@/application/services/api/system'
import type { ChatMessage, Session } from '../types'

/**
 * Chat Manager Composable
 *
 * Provides reactive chat message management with auto-scroll,
 * message sending, and loading states.
 *
 * @param session - Reactive session reference
 * @param selectedFileIds - Optional selected file IDs for context
 * @returns Chat management state and methods
 *
 * @example
 * ```typescript
 * const chatMgr = useChatManager(
 *   computed(() => sessionMgr.session.value),
 *   selectedFileIds
 * )
 *
 * // Send message
 * await chatMgr.sendMessage('Generate a chapter about React')
 *
 * // Auto-scroll is handled automatically
 * ```
 */
export function useChatManager(
  session: Ref<Session | null>,
  selectedFileIds?: Ref<string[]>
) {
  // State
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const chatContainer = ref<HTMLElement | null>(null)

  /**
   * Send a chat message to AI
   *
   * Sends a message to the AI assistant and updates the chat history.
   * Creates a session automatically if none exists.
   *
   * @param content - Message content
   * @param mode - Optional mode hint (structure/lesson/exam)
   * @param onCreateSession - Callback to create session if needed
   * @returns AI response data or null if failed
   */
  async function sendMessage(
    content: string,
    mode?: string,
    onCreateSession?: () => Promise<void>
  ): Promise<any | null> {
    if (!content.trim() || loading.value) {
      return null
    }

    // Create session if needed
    if (!session.value && onCreateSession) {
      await onCreateSession()
      if (!session.value) {
        error.value = 'Keine Session verfügbar'
        return null
      }
    }

    if (!session.value) {
      error.value = 'Keine aktive Session'
      return null
    }

    // Add user message
    const userMessage: ChatMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)
    scrollToBottom()

    loading.value = true
    error.value = null

    try {
      const res = await http.post(
        `/admin/course-authoring/sessions/${session.value.session_id}/chat`,
        {
          message: content,
          mode: mode || undefined,
          file_ids: selectedFileIds?.value || []
        }
      )

      if (res.data.success) {
        const responseData = res.data.data

        // Add assistant message
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: responseData.assistant_message,
          operations: responseData.operations_applied,
          timestamp: new Date().toISOString()
        }
        messages.value.push(assistantMessage)

        scrollToBottom()

        return responseData
      } else {
        error.value = res.data.error || 'Chat-Fehler'
        addErrorMessage(error.value)
        return null
      }
    } catch (err: any) {
      error.value = 'Chat-Fehler: ' + (err.message || 'Unbekannt')
      addErrorMessage(error.value)
      console.error('Chat error:', err)
      return null
    } finally {
      loading.value = false
      scrollToBottom()
    }
  }

  /**
   * Add a system message to chat
   *
   * Adds an assistant message without making an API call.
   * Useful for local notifications and status updates.
   *
   * @param content - Message content (markdown supported)
   */
  function addSystemMessage(content: string): void {
    const message: ChatMessage = {
      role: 'assistant',
      content,
      timestamp: new Date().toISOString()
    }
    messages.value.push(message)
    scrollToBottom()
  }

  /**
   * Add an error message to chat
   *
   * @param errorText - Error message text
   */
  function addErrorMessage(errorText: string): void {
    const message: ChatMessage = {
      role: 'assistant',
      content: `❌ **Fehler:** ${errorText}`,
      error: true,
      timestamp: new Date().toISOString()
    }
    messages.value.push(message)
    scrollToBottom()
  }

  /**
   * Scroll chat container to bottom
   *
   * Scrolls the chat container to show the latest message.
   * Uses smooth scrolling and nextTick for proper DOM updates.
   */
  function scrollToBottom(): void {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTo({
          top: chatContainer.value.scrollHeight,
          behavior: 'smooth'
        })
      }
    })
  }

  /**
   * Clear all chat messages
   *
   * Removes all messages from chat history.
   * Does not affect backend session data.
   */
  function clearMessages(): void {
    messages.value = []
    error.value = null
  }

  /**
   * Load chat history from session
   *
   * Loads message history from the current session.
   *
   * @param chatHistory - Array of chat messages
   */
  function loadChatHistory(chatHistory: ChatMessage[]): void {
    messages.value = chatHistory || []
    scrollToBottom()
  }

  /**
   * Set chat container reference
   *
   * @param container - HTMLElement reference to chat container
   */
  function setChatContainer(container: HTMLElement | null): void {
    chatContainer.value = container
  }

  // Auto-scroll when messages change
  watch(
    () => messages.value.length,
    () => {
      scrollToBottom()
    }
  )

  // Auto-scroll when loading state changes
  watch(loading, () => {
    scrollToBottom()
  })

  return {
    // State
    messages,
    loading,
    error,
    chatContainer,

    // Methods
    sendMessage,
    addSystemMessage,
    addErrorMessage,
    scrollToBottom,
    clearMessages,
    loadChatHistory,
    setChatContainer
  }
}
