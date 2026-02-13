<!--
  ModelConfigCard - Model Configuration per Category
  Sub-component of SettingsTab
-->

<template>
  <div class="settings-card">
    <div class="card-header">
      <span class="card-icon">🤖</span>
      <span class="card-title">{{ $t('aiEditorSettings.modelConfig') }}</span>
      <span v-if="isCustom" class="custom-badge">{{ $t('aiEditorSettings.custom') }}</span>
    </div>
    <div class="model-list">
      <div v-for="cat in modelCategories" :key="cat.key" class="model-item">
        <div class="model-label">
          <span class="model-icon">{{ cat.icon }}</span>
          <span>{{ cat.label }}</span>
        </div>
        <select
          :value="formData[cat.key]"
          @change="updateModel(cat.key, ($event.target as HTMLSelectElement).value)"
          class="model-select"
        >
          <option value="">{{ $t('aiEditorSettings.profileDefault') }}</option>
          <option
            v-for="model in modelsByCategory[cat.key]"
            :key="model.model_id"
            :value="model.model_id"
          >
            {{ model.display_name || model.model_id }}
          </option>
        </select>
      </div>
    </div>
    <div class="card-footer">
      <button @click="$emit('reset')" class="reset-btn" :disabled="!isCustom">
        {{ $t('aiEditorSettings.resetToDefaults') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface AIModel {
  model_id: string
  display_name?: string
}

interface ModelsByCategory {
  chat: AIModel[]
  reasoning: AIModel[]
  image: AIModel[]
  audio: AIModel[]
  realtime: AIModel[]
  embedding: AIModel[]
}

interface FormData {
  chat_model_id: string
  reasoning_model_id: string
  image_model_id: string
  audio_model_id: string
  realtime_model_id: string
  embedding_model_id: string
  [key: string]: string
}

const props = defineProps<{
  formData: FormData
  modelsByCategory: ModelsByCategory
  isCustom: boolean
}>()

const emit = defineEmits<{
  (e: 'update', key: string, value: string): void
  (e: 'reset'): void
}>()

const modelCategories = computed(() => [
  { key: 'chat_model_id', icon: '💬', label: t('aiEditorSettings.catChat') },
  { key: 'reasoning_model_id', icon: '🧠', label: t('aiEditorSettings.catReasoning') },
  { key: 'image_model_id', icon: '🖼️', label: t('aiEditorSettings.catImage') },
  { key: 'audio_model_id', icon: '🔊', label: t('aiEditorSettings.catAudio') },
  { key: 'realtime_model_id', icon: '⚡', label: t('aiEditorSettings.catRealtime') },
  { key: 'embedding_model_id', icon: '🔗', label: t('aiEditorSettings.catEmbedding') }
])

function updateModel(key: string, value: string) {
  emit('update', key, value)
}
</script>

<style scoped>
.settings-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.card-icon { font-size: 1.25rem; }

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.custom-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.model-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.model-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 160px;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.model-icon { font-size: 1rem; }

.model-select {
  flex: 1;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.model-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.reset-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.reset-btn:hover:not(:disabled) {
  border-color: var(--color-error);
  color: var(--color-error);
}

.reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
