/**
 * useChatManagement - Chat Panel State Management
 * =================================================
 * Simple composable for managing chat panel expand/collapse state
 */
import { ref, readonly } from 'vue'

export function useChatManagement() {
  // State
  const chatExpanded = ref(false)

  // Methods
  function toggleChat(): void {
    chatExpanded.value = !chatExpanded.value
  }

  function openChat(): void {
    chatExpanded.value = true
  }

  function closeChat(): void {
    chatExpanded.value = false
  }

  // Expose
  return {
    chatExpanded: readonly(chatExpanded),
    toggleChat,
    openChat,
    closeChat
  }
}
