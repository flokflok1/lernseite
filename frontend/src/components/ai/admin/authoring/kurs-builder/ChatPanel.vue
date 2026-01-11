<!--
  ChatPanel - Chat messages and input for KI-Kurs-Builder

  Displays chat messages with the AI assistant,
  input field with mode selector, and quick actions grid.
-->

<template>
  <div class="chat-panel">
    <!-- Chat Messages -->
    <div ref="chatContainer" class="chat-messages">
      <div v-if="messages.length === 0" class="chat-welcome">
        <div class="welcome-icon">🤖</div>
        <h4>KI-Kurs-Builder bereit</h4>
        <p>Nutze die Quick-Actions oder schreibe eine Nachricht.</p>
        <p class="welcome-hint" v-if="selectedFileCount > 0">
          📎 {{ selectedFileCount }} Datei(en) als Kontext ausgewählt
        </p>
      </div>

      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="chat-message"
        :class="msg.role"
      >
        <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-content">
          <div class="message-text">{{ msg.content }}</div>
          <div v-if="msg.operations?.length" class="message-ops">
            <span v-for="op in msg.operations" :key="op" class="op-badge">{{ op }}</span>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isLoading" class="typing-indicator">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="typing-text">KI denkt...</span>
      </div>
    </div>

    <!-- Quick Actions (2x2 Grid) -->
    <div v-if="showQuickActions && !hasContext" class="quick-actions-grid">
      <template v-if="actionsLoading">
        <div class="actions-loading">Lade Actions...</div>
      </template>
      <button
        v-else
        v-for="action in quickActions"
        :key="action.action_id"
        @click="$emit('quick-action', action)"
        class="quick-action-btn"
        :class="action.color ? `action-${action.color}` : ''"
        :disabled="isLoading"
      >
        <span class="qa-icon">{{ action.icon }}</span>
        <span class="qa-label">{{ action.label }}</span>
      </button>
    </div>

    <!-- Chat Input -->
    <div class="chat-input-wrapper">
      <div class="input-row">
        <textarea
          ref="inputField"
          v-model="localMessage"
          @keydown.enter.ctrl="handleSend"
          @keydown.enter.meta="handleSend"
          placeholder="Nachricht eingeben... (Strg+Enter)"
          :disabled="isLoading"
          rows="2"
        ></textarea>
        <button
          @click="handleSend"
          class="send-btn"
          :disabled="!localMessage.trim() || isLoading"
        >
          {{ isLoading ? '⏳' : '➤' }}
        </button>
      </div>
      <div class="input-footer">
        <select v-model="localMode" class="mode-select">
          <option value="">Auto</option>
          <option value="structure">📋 Struktur</option>
          <option value="lesson">📄 Lektionen</option>
          <option value="exam">🎓 Prüfung</option>
        </select>
        <span v-if="selectedFileCount > 0" class="context-info">
          📎 {{ selectedFileCount }} Datei(en) im Kontext
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

// Types
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

interface QuickAction {
  action_id: string
  action_key: string
  label: string
  icon: string
  prompt_template: string
  mode?: string
  color?: string
}

// Props
const props = defineProps<{
  messages: ChatMessage[]
  isLoading: boolean
  quickActions: QuickAction[]
  actionsLoading: boolean
  selectedFileCount: number
  hasContext: boolean
  showQuickActions?: boolean
  modelValue?: string
  mode?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'send', message: string, mode: string): void
  (e: 'quick-action', action: QuickAction): void
  (e: 'update:modelValue', value: string): void
  (e: 'update:mode', value: string): void
}>()

// Local state
const chatContainer = ref<HTMLElement | null>(null)
const inputField = ref<HTMLTextAreaElement | null>(null)
const localMessage = ref(props.modelValue || '')
const localMode = ref(props.mode || '')

// Sync with v-model
watch(() => props.modelValue, (val) => {
  if (val !== undefined) localMessage.value = val
})

watch(localMessage, (val) => {
  emit('update:modelValue', val)
})

watch(() => props.mode, (val) => {
  if (val !== undefined) localMode.value = val
})

watch(localMode, (val) => {
  emit('update:mode', val)
})

// Auto-scroll when messages change
watch(() => props.messages.length, () => {
  scrollToBottom()
})

watch(() => props.isLoading, () => {
  scrollToBottom()
})

// Methods
function handleSend() {
  if (!localMessage.value.trim() || props.isLoading) return
  emit('send', localMessage.value.trim(), localMode.value)
  localMessage.value = ''
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// Expose for parent
defineExpose({
  focus() {
    inputField.value?.focus()
  },
  scrollToBottom
})
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-welcome {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.chat-welcome h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.chat-welcome p {
  margin: 0;
  font-size: 0.875rem;
}

.welcome-hint {
  margin-top: 0.75rem !important;
  padding: 0.5rem;
  background: var(--color-primary-subtle);
  border-radius: 0.375rem;
  display: inline-block;
}

/* Messages */
.chat-message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.chat-message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-message.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  flex-shrink: 0;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  max-width: 100%;
}

.chat-message.user .message-content {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.chat-message.assistant .message-content {
  background: var(--color-surface-secondary);
  border-bottom-left-radius: 0.25rem;
}

.message-text {
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-ops {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.op-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
}

.chat-message.assistant .op-badge {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-radius: 1rem;
  width: fit-content;
}

.typing-indicator .dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
}

.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

.typing-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-left: 0.25rem;
}

@keyframes bounce {
  to { transform: translateY(-4px); }
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 0 1rem 0.5rem;
}

.actions-loading {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  padding: 1rem;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
}

.quick-action-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-action-btn .qa-icon {
  font-size: 1.25rem;
}

.quick-action-btn .qa-label {
  font-size: 0.8125rem;
  font-weight: 500;
}

/* Action Colors */
.action-blue { border-left: 3px solid #3b82f6; }
.action-green { border-left: 3px solid #22c55e; }
.action-purple { border-left: 3px solid #8b5cf6; }
.action-orange { border-left: 3px solid #f59e0b; }

/* Chat Input */
.chat-input-wrapper {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.input-row {
  display: flex;
  gap: 0.5rem;
}

.input-row textarea {
  flex: 1;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  resize: none;
  font-family: inherit;
  background: var(--color-bg);
}

.input-row textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.input-row textarea:disabled {
  opacity: 0.5;
}

.send-btn {
  padding: 0 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.15s;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.mode-select {
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: var(--color-bg);
}

.context-info {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
</style>
