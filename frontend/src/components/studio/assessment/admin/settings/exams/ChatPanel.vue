<!--
  ChatPanel - Chat interface for exam generation
  Sub-component of ExamsTab
-->

<template>
  <div class="chat-panel">
    <div class="panel-header">
      <span class="panel-icon">💬</span>
      <span class="panel-title">{{ $t('windows.aiEditorExams.aiChat') }}</span>
      <span v-if="selectedFilesCount > 0" class="files-indicator">
        {{ $t('windows.aiEditorExams.filesAsContext', { count: selectedFilesCount }) }}
      </span>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="chatMessagesRef">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">🤖</div>
        <h4>{{ $t('windows.aiEditorExams.assistantTitle') }}</h4>
        <p>{{ $t('windows.aiEditorExams.assistantIntro') }}</p>

        <div v-if="selectedFilesCount > 0" class="selected-files-info">
          <strong>{{ $t('windows.aiEditorExams.filesSelected', { count: selectedFilesCount }) }}</strong>
          <ul>
            <li v-for="name in selectedFileNames.slice(0, 3)" :key="name">{{ name }}</li>
            <li v-if="selectedFilesCount > 3">{{ $t('windows.aiEditorExams.andMore', { count: selectedFilesCount - 3 }) }}</li>
          </ul>
        </div>

        <div class="welcome-hints">
          <p>{{ $t('windows.aiEditorExams.examples') }}</p>
          <ul>
            <li>{{ $t('windows.aiEditorExams.example1') }}</li>
            <li>{{ $t('windows.aiEditorExams.example2') }}</li>
            <li>{{ $t('windows.aiEditorExams.example3') }}</li>
          </ul>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(msg, idx) in messages" :key="idx" class="chat-message" :class="msg.role">
        <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(msg.content)"></div>
          <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isGenerating" class="typing-indicator">
        <div class="message-avatar">🤖</div>
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>

    <!-- Chat Input -->
    <div class="chat-input-area">
      <div class="input-wrapper">
        <textarea
          v-model="inputValue"
          @keydown.enter.exact.prevent="$emit('send', inputValue); inputValue = ''"
          :placeholder="$t('windows.aiEditorExams.inputPlaceholder')"
          rows="2"
          :disabled="isGenerating"
        ></textarea>
        <button @click="$emit('send', inputValue); inputValue = ''" class="send-btn" :disabled="!inputValue.trim() || isGenerating">
          <svg v-if="!isGenerating" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <span v-else class="loading-spinner"></span>
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-prompts">
        <button @click="$emit('quick-prompt', 'from_files')" class="quick-btn" :disabled="selectedFilesCount === 0">
          📄 {{ $t('windows.aiEditorExams.fromFiles') }}
        </button>
        <button @click="$emit('quick-prompt', 'exam_mc')" class="quick-btn">✅ {{ $t('windows.aiEditorExams.mcQuestions') }}</button>
        <button @click="$emit('quick-prompt', 'exam_ihk')" class="quick-btn">🎓 {{ $t('windows.aiEditorExams.ihkStyle') }}</button>
        <button @click="$emit('quick-prompt', 'exam_mixed')" class="quick-btn">🎯 {{ $t('windows.aiEditorExams.mixed') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const props = defineProps<{
  messages: ChatMessage[]
  isGenerating: boolean
  selectedFilesCount: number
  selectedFileNames: string[]
}>()

defineEmits<{
  (e: 'send', message: string): void
  (e: 'quick-prompt', type: string): void
}>()

const inputValue = ref('')
const chatMessagesRef = ref<HTMLElement | null>(null)

function formatMessage(content: string): string {
  return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

watch(() => props.messages.length, async () => {
  await nextTick()
  if (chatMessagesRef.value) chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
})
</script>

<style scoped>
.chat-panel { display: flex; flex-direction: column; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.75rem; overflow: hidden; }
.panel-header { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-border); background: var(--color-surface-secondary); }
.panel-icon { font-size: 1.125rem; }
.panel-title { font-weight: 600; color: var(--color-text-primary); flex: 1; }
.files-indicator { font-size: 0.75rem; padding: 0.25rem 0.5rem; background: rgba(99, 102, 241, 0.1); color: var(--color-primary); border-radius: 1rem; }

.chat-messages { flex: 1; overflow-y: auto; padding: 1rem; min-height: 300px; max-height: 400px; }

.welcome-message { text-align: center; padding: 1.5rem 1rem; }
.welcome-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.welcome-message h4 { color: var(--color-text-primary); margin: 0 0 0.5rem; }
.welcome-message p { color: var(--color-text-secondary); font-size: 0.875rem; margin: 0 0 1rem; }
.selected-files-info { text-align: left; padding: 0.75rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; margin-bottom: 1rem; font-size: 0.8125rem; }
.selected-files-info ul { margin: 0.5rem 0 0; padding-left: 1.25rem; color: var(--color-text-secondary); }
.welcome-hints { text-align: left; font-size: 0.8125rem; color: var(--color-text-tertiary); }
.welcome-hints ul { margin: 0.25rem 0 0; padding-left: 1.25rem; }

.chat-message { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.chat-message.user { flex-direction: row-reverse; }
.message-avatar { width: 32px; height: 32px; background: var(--color-surface-secondary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; flex-shrink: 0; }
.chat-message.user .message-avatar { background: var(--color-primary); }
.chat-message.assistant .message-avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.message-content { max-width: 80%; }
.message-text { padding: 0.625rem 0.875rem; border-radius: 1rem; font-size: 0.8125rem; line-height: 1.5; }
.chat-message.user .message-text { background: var(--color-primary); color: white; border-bottom-right-radius: 0.25rem; }
.chat-message.assistant .message-text { background: var(--color-surface-secondary); color: var(--color-text-primary); border-bottom-left-radius: 0.25rem; }
.message-time { font-size: 0.625rem; color: var(--color-text-tertiary); margin-top: 0.25rem; padding: 0 0.5rem; }
.chat-message.user .message-time { text-align: right; }

.typing-indicator { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.typing-dots { display: flex; align-items: center; gap: 0.25rem; padding: 0.625rem 0.875rem; background: var(--color-surface-secondary); border-radius: 1rem; }
.typing-dots span { width: 6px; height: 6px; background: var(--color-text-tertiary); border-radius: 50%; animation: typing 1.4s infinite; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-3px); opacity: 1; } }

.chat-input-area { padding: 0.75rem; border-top: 1px solid var(--color-border); }
.input-wrapper { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
.input-wrapper textarea { flex: 1; padding: 0.625rem; border: 1px solid var(--color-border); border-radius: 0.5rem; background: var(--color-surface); color: var(--color-text-primary); font-size: 0.8125rem; resize: none; }
.input-wrapper textarea:focus { outline: none; border-color: var(--color-primary); }
.send-btn { width: 40px; height: 40px; background: var(--color-primary); border: none; border-radius: 0.5rem; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.send-btn:hover:not(:disabled) { filter: brightness(1.1); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.send-btn svg { width: 18px; height: 18px; }
.loading-spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.quick-prompts { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.quick-btn { padding: 0.25rem 0.5rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 1rem; font-size: 0.6875rem; color: var(--color-text-secondary); cursor: pointer; }
.quick-btn:hover:not(:disabled) { background: var(--color-primary-subtle); border-color: var(--color-primary); color: var(--color-primary); }
.quick-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
