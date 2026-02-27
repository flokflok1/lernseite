<template>
  <div class="chat-message" :class="[`role-${message.role}`]">
    <div class="message-header">
      <span class="message-role">{{ roleLabel }}</span>
      <span class="message-time">{{ formattedTime }}</span>
    </div>
    <div class="message-content" v-html="sanitizedContent" />
    <div v-if="message.confirmation" class="message-confirmation">
      <button
        class="confirm-btn"
        :disabled="disabled"
        @click="$emit('confirm', message.confirmation!)"
      >
        {{ message.confirmation.label }}
      </button>
    </div>
    <div v-if="message.operations?.length" class="message-operations">
      <div class="ops-header">
        <span class="ops-icon">&#x2713;</span>
        <span class="ops-count">{{ message.operations.length }} {{ message.operations.length === 1 ? 'Aktion' : 'Aktionen' }} ausgeführt</span>
      </div>
      <div class="ops-badges">
        <span
          v-for="op in message.operations"
          :key="op.type + (op.target_id || '')"
          class="operation-badge"
        >
          {{ op.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import type { ChatMessage, ChatConfirmation } from '../types'

const { t } = useI18n()

const props = defineProps<{
  message: ChatMessage
  disabled?: boolean
}>()

defineEmits<{
  confirm: [confirmation: ChatConfirmation]
}>()

const roleLabel = computed((): string => {
  const key = `aiEditor.chat.roles.${props.message.role}`
  const translated = t(key)
  // Fall back to raw role name if key is missing
  return translated !== key ? translated : props.message.role
})

const formattedTime = computed((): string => {
  try {
    return new Date(props.message.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
})

const sanitizedContent = computed((): string =>
  DOMPurify.sanitize(props.message.content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre', 'h3', 'h4'],
    ALLOWED_ATTR: ['href', 'title'],
  })
)
</script>

<style scoped>
.chat-message {
  padding: 0.75rem;
  border-radius: 0.5rem;
  max-width: 90%;
}

.chat-message.role-user {
  background: var(--color-primary-subtle);
  align-self: flex-end;
  margin-left: auto;
}

.chat-message.role-assistant {
  background: var(--color-surface-secondary);
  align-self: flex-start;
}

.chat-message.role-system {
  background: rgba(255, 200, 0, 0.1);
  align-self: center;
  font-size: 0.8125rem;
  text-align: center;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}

.message-role {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.message-time {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

.message-content {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-primary);
  word-break: break-word;
}

.message-content :deep(code) {
  background: var(--color-surface);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
}

.message-content :deep(pre) {
  background: var(--color-surface);
  padding: 0.5rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.message-confirmation {
  margin-top: 0.5rem;
}

.confirm-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: background 0.15s;
}

.confirm-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.message-operations {
  margin-top: 0.5rem;
  padding: 0.5rem 0.625rem;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.375rem;
}

.ops-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.375rem;
}

.ops-icon {
  color: #10b981;
  font-weight: 700;
  font-size: 0.8125rem;
}

.ops-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: #10b981;
}

.ops-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.operation-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
}
</style>
