/**
 * chat.store.ts
 *
 * Chat history state management.
 * Tracks conversation history with AI assistant.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export const useChatStore = defineStore('courseEditor/chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)

  const addMessage = (message: ChatMessage) => {
    messages.value.push(message)
  }

  const clearHistory = () => {
    messages.value = []
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  return {
    messages,
    isLoading,
    addMessage,
    clearHistory,
    setLoading
  }
})
