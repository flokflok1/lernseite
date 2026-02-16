<!--
  ActionsBar - Token Summary and Actions
  Sub-component of SystemFeaturesTab
-->

<template>
  <div class="actions-bar">
    <div class="token-summary">
      <span class="summary-label">{{ $t('aiEditorFeatures.estimatedTokens') }}:</span>
      <span class="summary-value">{{ estimatedTokens.toLocaleString() }}</span>
      <span class="summary-cost">(~{{ (estimatedTokens * 0.00002).toFixed(4) }}€)</span>
    </div>
    <div class="action-buttons">
      <button @click="$emit('reset')" class="btn-secondary">
        {{ $t('aiEditorFeatures.reset') }}
      </button>
      <button @click="$emit('save')" :disabled="isSaving" class="btn-primary">
        <span v-if="isSaving" class="spinner-small"></span>
        {{ $t('aiEditorFeatures.save') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  estimatedTokens: number
  isSaving: boolean
}>()

defineEmits<{
  (e: 'reset'): void
  (e: 'save'): void
}>()
</script>

<style scoped>
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.token-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.summary-cost {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--color-primary);
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
