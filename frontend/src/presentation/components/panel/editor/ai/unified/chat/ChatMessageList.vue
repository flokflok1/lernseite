<!--
  ChatMessageList — Scrollable list of chat messages with auto-scroll
-->
<template>
  <div ref="containerRef" class="chat-message-list">
    <ChatMessage
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
      :disabled="disabled"
      @confirm="$emit('confirm', $event)"
    />
    <div v-if="isLoading" class="typing-indicator">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage as ChatMessageType, ChatConfirmation } from '../types'
import ChatMessage from './ChatMessage.vue'

const props = defineProps<{
  messages: ChatMessageType[]
  isLoading?: boolean
  disabled?: boolean
}>()

defineEmits<{
  confirm: [confirmation: ChatConfirmation]
}>()

const containerRef = ref<HTMLElement | null>(null)

function scrollToBottom(): void {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTo({
        top: containerRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.isLoading, scrollToBottom)

defineExpose({ scrollToBottom })
</script>

<style scoped>
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  align-self: flex-start;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-4px); }
}
</style>
