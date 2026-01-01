<!--
  CourseChatMessage.vue

  Einzelne Chat-Nachricht im Kurs-Builder.
  Zeigt User- und Assistant-Nachrichten unterschiedlich an.
  Zeigt angewendete Operationen bei Assistant-Nachrichten.
-->

<template>
  <div class="chat-message" :class="[message.role, { error: message.error }]">
    <!-- Avatar -->
    <div class="message-avatar">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </div>

    <!-- Content -->
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">{{ message.role === 'user' ? 'Du' : 'KI-Architekt' }}</span>
        <span v-if="message.timestamp" class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>

      <div class="message-text">{{ message.content }}</div>

      <!-- Operations Badge -->
      <div v-if="message.operations?.length" class="message-operations">
        <span class="ops-label">Änderungen:</span>
        <span
          v-for="(op, i) in message.operations"
          :key="i"
          class="op-badge"
          :class="getOpClass(op)"
        >
          {{ getOpIcon(op) }} {{ formatOp(op) }}
        </span>
      </div>

      <!-- Error Retry -->
      <button v-if="message.error && message.role === 'user'" @click="$emit('retry')" class="retry-btn">
        🔄 Erneut versuchen
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

defineProps<{
  message: ChatMessage
}>()

defineEmits<{
  (e: 'retry'): void
}>()

function formatTime(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

function formatOp(op: string): string {
  const names: Record<string, string> = {
    'add_chapter': 'Kapitel+',
    'update_chapter': 'Kapitel~',
    'delete_chapter': 'Kapitel-',
    'add_lesson': 'Lektion+',
    'update_lesson': 'Lektion~',
    'delete_lesson': 'Lektion-',
    'add_method': 'Methode+',
    'update_method': 'Methode~',
    'delete_method': 'Methode-'
  }
  return names[op] || op
}

function getOpIcon(op: string): string {
  if (op.startsWith('add_')) return '➕'
  if (op.startsWith('update_')) return '✏️'
  if (op.startsWith('delete_')) return '🗑️'
  return '🔧'
}

function getOpClass(op: string): string {
  if (op.startsWith('add_')) return 'op-add'
  if (op.startsWith('update_')) return 'op-update'
  if (op.startsWith('delete_')) return 'op-delete'
  return ''
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.chat-message.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.chat-message.assistant {
  margin-right: auto;
}

.chat-message.error .message-content {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.message-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  font-size: 1rem;
  flex-shrink: 0;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
}

.user .message-content {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  border-bottom-right-radius: 0.25rem;
}

.assistant .message-content {
  border-bottom-left-radius: 0.25rem;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.message-role {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.7;
}

.message-time {
  font-size: 0.625rem;
  opacity: 0.5;
}

.message-text {
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-operations {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.ops-label {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  margin-right: 0.25rem;
}

.op-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem;
  border-radius: 0.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.op-badge.op-add {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  color: #22c55e;
}

.op-badge.op-update {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
  color: #3b82f6;
}

.op-badge.op-delete {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}

.retry-btn {
  margin-top: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: transparent;
  border: 1px solid currentColor;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.15s;
}

.retry-btn:hover {
  opacity: 1;
}
</style>
