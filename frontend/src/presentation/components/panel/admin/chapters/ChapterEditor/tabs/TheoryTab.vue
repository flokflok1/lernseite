<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  content: string
  isLoading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:content': [value: string]
}>()

const { t } = useI18n()

const handleContentChange = (newContent: string) => {
  emit('update:content', newContent)
}
</script>

<template>
  <div class="theory-tab">
    <div class="editor-container">
      <label class="editor-label">{{ $t('features.chapterEditor.tabs.theory') }}</label>

      <textarea
        class="editor-textarea"
        :placeholder="$t('features.chapterEditor.placeholders.theory')"
        :value="content"
        :disabled="isLoading"
        @input="handleContentChange(($event.target as HTMLTextAreaElement).value)"
      />

      <div class="editor-info">
        <p class="text-sm">
          {{ $t('features.chapterEditor.info.theoryTip') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theory-tab {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 1rem;
}

.editor-label {
  display: block;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.editor-textarea {
  flex: 1;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.95rem;
  line-height: 1.5;
  resize: none;
}

.editor-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.editor-textarea:disabled {
  background-color: var(--color-bg-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}

.editor-info {
  padding: 0.75rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.25rem;
  border-left: 3px solid var(--color-info);
}

.text-sm {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}
</style>
