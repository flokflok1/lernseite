<!--
  PromptTemplatesList - Prompt Templates Section
  Sub-component of SettingsTab
-->

<template>
  <div class="settings-card lg:col-span-2">
    <div class="card-header">
      <span class="card-icon">📝</span>
      <span class="card-title">{{ $t('features.aiEditorSettings.promptTemplates') }}</span>
      <button @click="$emit('addNew')" class="add-btn">
        + {{ $t('features.aiEditorSettings.newTemplate') }}
      </button>
    </div>
    <div class="prompt-list">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner small"></div>
      </div>
      <div v-else-if="!prompts.length" class="text-center py-4 text-[var(--color-text-tertiary)]">
        {{ $t('features.aiEditorSettings.noTemplates') }}
      </div>
      <div
        v-else
        v-for="prompt in prompts"
        :key="prompt.template_key"
        class="prompt-item"
      >
        <div class="prompt-info">
          <span class="prompt-key">{{ prompt.template_key }}</span>
          <span class="prompt-name">{{ prompt.template_name }}</span>
        </div>
        <div class="prompt-category">{{ prompt.category }}</div>
        <button @click="$emit('edit', prompt)" class="edit-btn">
          {{ $t('features.aiEditorSettings.edit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface PromptTemplate {
  template_key: string
  template_name: string
  category: string
}

defineProps<{
  prompts: PromptTemplate[]
  loading: boolean
}>()

defineEmits<{
  (e: 'addNew'): void
  (e: 'edit', prompt: PromptTemplate): void
}>()
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

.add-btn {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
}

.add-btn:hover { opacity: 0.9; }

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.prompt-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.prompt-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.prompt-key {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.prompt-name {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
}

.prompt-category {
  padding: 0.125rem 0.5rem;
  background: var(--color-surface);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.edit-btn {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.edit-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
