<!--
  ChatPanel — Left side of split-view. Persistent chat interface.
  Shows welcome state if no session, otherwise message list + input.
-->
<template>
  <div class="chat-panel">
    <!-- Token budget bar -->
    <div v-if="hasSession" class="token-bar">
      <div class="token-bar-fill" :style="{ width: `${usagePercent}%` }" :class="tokenBarClass" />
      <span class="token-label">{{ tokensUsed.toLocaleString() }} / {{ tokenBudget.toLocaleString() }}</span>
    </div>

    <!-- Welcome or Messages -->
    <ChatWelcome
      v-if="!hasSession"
      @new-course="$emit('newCourse')"
      @load-course="$emit('loadCourse')"
    />
    <ChatMessageList
      v-else
      ref="messageListRef"
      :messages="messages"
      :is-loading="isLoading"
      :disabled="isLoading"
      @confirm="$emit('confirm', $event)"
    />

    <!-- Input -->
    <ChatInput
      v-if="hasSession"
      :disabled="isLoading"
      :context-label="contextLabel"
      :file-count="fileCount"
      @send="$emit('send', $event)"
      @attach-file="$emit('attachFile')"
      @clear-context="$emit('clearContext')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ChatMessage as ChatMessageType, ChatConfirmation } from '../types'
import ChatWelcome from './ChatWelcome.vue'
import ChatMessageList from './ChatMessageList.vue'
import ChatInput from './ChatInput.vue'

const props = defineProps<{
  hasSession: boolean
  messages: ChatMessageType[]
  isLoading: boolean
  tokensUsed: number
  tokenBudget: number
  usagePercent: number
  contextLabel?: string | null
  fileCount?: number
}>()

defineEmits<{
  newCourse: []
  loadCourse: []
  send: [content: string]
  attachFile: []
  clearContext: []
  confirm: [confirmation: ChatConfirmation]
}>()

const messageListRef = ref<InstanceType<typeof ChatMessageList> | null>(null)

const tokenBarClass = computed(() => ({
  'is-warning': props.usagePercent >= 80 && props.usagePercent < 100,
  'is-over': props.usagePercent >= 100,
}))
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  min-width: 320px;
}
.token-bar {
  height: 3px;
  background: var(--color-surface-secondary);
  position: relative;
  flex-shrink: 0;
}
.token-bar-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s;
}
.token-bar-fill.is-warning { background: var(--color-warning, #f59e0b); }
.token-bar-fill.is-over { background: var(--color-danger, #ef4444); }
.token-label {
  position: absolute;
  right: 0.5rem;
  top: 4px;
  font-size: 0.5625rem;
  color: var(--color-text-tertiary);
}
</style>
