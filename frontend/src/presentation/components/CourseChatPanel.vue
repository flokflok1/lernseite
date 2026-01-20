<!--
  CourseChatPanel.vue

  Chat-Panel für KI-Kurs-Builder.
  Zeigt Chat-Verlauf und ermöglicht Nachrichten-Eingabe.
  Quick-Actions für häufige Operationen.
-->

<template>
  <div class="course-chat-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">💬</span>
      <span class="panel-title">Chat</span>
      <button @click="clearChat" class="clear-btn" :title="$t('admin.actions.clearChat')">🗑️</button>
    </div>

    <!-- Chat Messages -->
    <div ref="chatContainer" class="chat-messages">
      <div v-if="messages.length === 0" class="chat-empty">
        <span class="empty-icon">👋</span>
        <p>Starte den Kurs-Builder!</p>
        <p class="hint">Nutze die Quick-Actions oder schreibe eine Nachricht.</p>
      </div>

      <CourseChatMessage
        v-for="(msg, index) in messages"
        :key="index"
        :message="msg"
        @retry="retryMessage(index)"
      />

      <!-- Typing Indicator -->
      <div v-if="isLoading" class="typing-indicator">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="typing-text">KI denkt...</span>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button
        v-for="action in quickActions"
        :key="action.id"
        @click="sendQuickAction(action)"
        class="quick-action-btn"
        :disabled="isLoading"
      >
        <span class="action-icon">{{ action.icon }}</span>
        <span class="action-label">{{ action.label }}</span>
      </button>
    </div>

    <!-- Input Area -->
    <div class="chat-input-area">
      <textarea
        ref="inputField"
        v-model="inputMessage"
        @keydown.enter.ctrl="sendMessage"
        @keydown.enter.meta="sendMessage"
        placeholder="Nachricht eingeben... (Strg+Enter zum Senden)"
        :disabled="isLoading"
        rows="2"
      ></textarea>
      <button
        @click="sendMessage"
        class="send-btn"
        :disabled="!inputMessage.trim() || isLoading"
      >
        {{ isLoading ? '⏳' : '➤' }}
      </button>
    </div>

    <!-- Mode Selector -->
    <div class="mode-selector">
      <label>Modus:</label>
      <select v-model="selectedMode">
        <option value="">Auto</option>
        <option value="structure">Struktur</option>
        <option value="lesson">Lektionen</option>
        <option value="method">Methoden</option>
        <option value="exam">Prüfung</option>
        <option value="calculator">Taschenrechner</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CourseChatMessage from './CourseChatMessage.vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

interface QuickAction {
  id: string
  label: string
  icon: string
  prompt: string
  mode?: string
}

const props = defineProps<{
  messages: ChatMessage[]
  isLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'send', payload: { message: string; mode?: string }): void
  (e: 'clear'): void
}>()

const { t } = useI18n()

const inputMessage = ref('')
const selectedMode = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const inputField = ref<HTMLTextAreaElement | null>(null)

const quickActions = computed<QuickAction[]>(() => [
  {
    id: 'structure',
    label: t('admin.courseChat.suggestStructure'),
    icon: '📋',
    prompt: 'Analysiere das Kursmaterial und schlage eine passende Kapitelstruktur vor.',
    mode: 'structure'
  },
  {
    id: 'chapters',
    label: t('admin.courseChat.createChapters'),
    icon: '📚',
    prompt: 'Erstelle 3 Kapitel mit je 3-5 Lektionen basierend auf dem Kursmaterial.',
    mode: 'structure'
  },
  {
    id: 'calculator',
    label: t('admin.courseChat.calculatorTutorial'),
    icon: '🧮',
    prompt: 'Erstelle ein Taschenrechner-Tutorial für das aktuelle Thema mit Casio fx-991.',
    mode: 'calculator'
  },
  {
    id: 'exam',
    label: t('admin.courseChat.generateExam'),
    icon: '🎓',
    prompt: 'Generiere IHK-Stil Prüfungsfragen basierend auf den vorhandenen Kapiteln.',
    mode: 'exam'
  }
])

function sendMessage() {
  if (!inputMessage.value.trim() || props.isLoading) return

  emit('send', {
    message: inputMessage.value.trim(),
    mode: selectedMode.value || undefined
  })

  inputMessage.value = ''
}

function sendQuickAction(action: QuickAction) {
  emit('send', {
    message: action.prompt,
    mode: action.mode
  })
}

function clearChat() {
  if (confirm('Chat-Verlauf wirklich leeren?')) {
    emit('clear')
  }
}

function retryMessage(index: number) {
  const msg = props.messages[index]
  if (msg && msg.role === 'user') {
    emit('send', { message: msg.content, mode: selectedMode.value || undefined })
  }
}

// Auto-scroll to bottom when new messages arrive
watch(() => props.messages.length, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
})

onMounted(() => {
  inputField.value?.focus()
})
</script>

<style scoped>
.course-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }
.panel-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.clear-btn:hover { opacity: 1; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-secondary);
}

.chat-empty .empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.chat-empty p { margin: 0.25rem 0; }
.chat-empty .hint { font-size: 0.75rem; opacity: 0.7; }

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
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
  animation: typing 1.4s infinite ease-in-out;
}
.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }
.typing-text {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  overflow-x: auto;
  border-top: 1px solid var(--color-border);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.75rem;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s;
}

.quick-action-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-icon { font-size: 0.875rem; }
.action-label { color: inherit; }

.chat-input-area {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
}

.chat-input-area textarea {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  resize: none;
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.send-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mode-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  border-top: 1px solid var(--color-border);
}

.mode-selector select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.75rem;
}
</style>
