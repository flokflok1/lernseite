<template>
  <div class="chat-input">
    <div v-if="contextLabel" class="context-badge">
      <span class="context-text">{{ contextLabel }}</span>
      <button class="context-clear" @click="$emit('clearContext')">&times;</button>
    </div>
    <div class="input-row">
      <button
        class="attach-btn"
        :title="$t('aiEditor.chat.attachFile')"
        @click="$emit('attachFile')"
      >
        <span>+</span>
      </button>
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="$t('aiEditor.chat.placeholder')"
        :disabled="disabled"
        rows="1"
        class="message-textarea"
        @keydown.enter.exact.prevent="handleSend"
      />
      <button class="send-btn" :disabled="!canSend" @click="handleSend">&rarr;</button>
    </div>
    <div v-if="fileCount && fileCount > 0" class="file-indicator">
      {{ fileCount }} {{ $t('aiEditor.chat.filesAttached') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  disabled?: boolean
  contextLabel?: string | null
  fileCount?: number
}>()

const emit = defineEmits<{
  send: [content: string]
  attachFile: []
  clearContext: []
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed((): boolean =>
  inputText.value.trim().length > 0 && !props.disabled
)

function handleSend(): void {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}
</script>

<style scoped>
.chat-input {
  border-top: 1px solid var(--color-border);
  padding: 0.5rem;
  background: var(--color-surface);
}

.context-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.375rem;
  padding: 0.25rem 0.5rem;
  background: var(--color-primary-subtle);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.context-text {
  flex: 1;
}

.context-clear {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: var(--color-primary);
  padding: 0;
  line-height: 1;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.375rem;
}

.attach-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 1.125rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.attach-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.message-textarea {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  resize: none;
  font-size: 0.875rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text-primary);
  min-height: 2rem;
  max-height: 8rem;
  overflow-y: auto;
}

.message-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.message-textarea:disabled {
  opacity: 0.5;
}

.send-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
  flex-shrink: 0;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.file-indicator {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
  padding-left: 2.375rem;
}
</style>
