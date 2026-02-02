<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterForm } from '../types'

interface Props {
  form: ChapterForm
  isNewChapter: boolean
  isGenerating: boolean
  saveStatus: 'idle' | 'saving' | 'saved' | 'error'
  error: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:form': [value: ChapterForm]
  'generate-theory': []
  'save-chapter': []
}>()

const { t } = useI18n()

// Computed
const hasErrors = computed(() => !!props.error && props.error.length > 0)

const statusIcon = computed(() => {
  switch (props.saveStatus) {
    case 'saving':
      return '⏳'
    case 'saved':
      return '✅'
    case 'error':
      return '❌'
    default:
      return ''
  }
})

// Methods
const handleTitleChange = (newTitle: string) => {
  emit('update:form', {
    ...props.form,
    title: newTitle
  })
}

const handleDescriptionChange = (newDescription: string) => {
  emit('update:form', {
    ...props.form,
    description: newDescription
  })
}

const handleGenerateTheory = () => {
  emit('generate-theory')
}

const handleSave = () => {
  emit('save-chapter')
}
</script>

<template>
  <div class="info-tab">
    <!-- Error Alert -->
    <div v-if="hasErrors" class="alert alert-error mb-4">
      {{ error }}
    </div>

    <!-- Save Status -->
    <div v-if="saveStatus !== 'idle'" class="save-status mb-4">
      <span class="status-icon">{{ statusIcon }}</span>
      <span class="status-text">
        {{ $t(`features.chapterEditor.saveStatus.${saveStatus}`) }}
      </span>
    </div>

    <!-- Chapter Title -->
    <div class="form-group mb-6">
      <label class="form-label">{{ $t('features.chapterEditor.tabs.title') }}</label>
      <input
        type="text"
        class="form-input"
        :placeholder="$t('features.chapterEditor.placeholders.title')"
        :value="form.title"
        :disabled="isNewChapter"
        @input="handleTitleChange(($event.target as HTMLInputElement).value)"
      />
      <div v-if="!form.title" class="text-danger text-sm mt-1">
        {{ $t('features.chapterEditor.errors.titleRequired') }}
      </div>
    </div>

    <!-- Chapter Description -->
    <div class="form-group mb-6">
      <label class="form-label">{{ $t('features.chapterEditor.tabs.description') }}</label>
      <textarea
        class="form-textarea"
        rows="4"
        :placeholder="$t('features.chapterEditor.placeholders.description')"
        :value="form.description"
        @input="handleDescriptionChange(($event.target as HTMLTextAreaElement).value)"
      />
    </div>

    <!-- AI Generator Button -->
    <div class="form-group mb-6">
      <button
        class="btn btn-secondary"
        :disabled="isGenerating || isNewChapter || !form.title"
        @click="handleGenerateTheory"
      >
        <span v-if="isGenerating" class="spinner-icon">⏳</span>
        <span v-else class="icon">🤖</span>
        {{ $t('features.chapterEditor.buttons.generateTheory') }}
      </button>
    </div>

    <!-- Save Button (explicit for new chapters) -->
    <div v-if="isNewChapter" class="form-group">
      <button
        class="btn btn-primary"
        :disabled="!form.title"
        @click="handleSave"
      >
        {{ $t('features.chapterEditor.buttons.saveAndEnable') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.info-tab {
  padding: 1rem;
  max-width: 600px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-family: inherit;
  font-size: 1rem;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.form-input:disabled,
.form-textarea:disabled {
  background-color: var(--color-bg-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.status-icon {
  font-size: 1.25rem;
}

.status-text {
  color: var(--color-text-secondary);
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-secondary-dark);
}

.spinner-icon,
.icon {
  font-size: 1.25rem;
}

.alert {
  padding: 0.75rem;
  border-radius: 0.25rem;
}

.alert-error {
  background-color: var(--color-error-bg);
  color: var(--color-error-text);
  border: 1px solid var(--color-error);
}

.text-danger {
  color: var(--color-error);
}

.text-sm {
  font-size: 0.875rem;
}

.mt-1 {
  margin-top: 0.25rem;
}
</style>
