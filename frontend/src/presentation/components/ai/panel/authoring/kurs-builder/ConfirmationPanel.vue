<!--
  ConfirmationPanel - Confirmation dialog for generated content

  Displays a preview of AI-generated content and allows
  the user to confirm, modify, or reject the changes.
-->

<template>
  <div v-if="pendingAction" class="confirmation-panel">
    <div class="confirm-header">
      <span class="confirm-icon">✨</span>
      <span class="confirm-title">Inhalt generiert - Bestätigung erforderlich</span>
    </div>

    <div class="confirm-preview">
      <pre class="preview-text">{{ pendingAction.previewText }}</pre>
    </div>

    <div class="confirm-actions">
      <button
        @click="$emit('confirm')"
        class="confirm-btn confirm-btn--accept"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Speichere...' : '✓ Bestätigen' }}
      </button>
      <button
        @click="$emit('modify')"
        class="confirm-btn confirm-btn--modify"
        :disabled="isLoading"
      >
        ✏️ Ändern
      </button>
      <button
        @click="$emit('reject')"
        class="confirm-btn confirm-btn--reject"
        :disabled="isLoading"
      >
        ✗ Verwerfen
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Types
interface PendingAction {
  type: 'create' | 'update' | 'delete'
  entity: 'chapter' | 'lesson' | 'method' | 'quiz'
  actionKey: string
  generatedData: any
  previewText: string
  parentChapter?: any
  session_id?: string
}

// Props
defineProps<{
  pendingAction: PendingAction | null
  isLoading?: boolean
}>()

// Emits
defineEmits<{
  (e: 'confirm'): void
  (e: 'modify'): void
  (e: 'reject'): void
}>()
</script>

<style scoped>
.confirmation-panel {
  margin: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #f59e0b;
  border-radius: 0.75rem;
}

.confirm-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.confirm-icon {
  font-size: 1.25rem;
}

.confirm-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #92400e;
}

.confirm-preview {
  background: white;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  max-height: 200px;
  overflow-y: auto;
}

.preview-text {
  margin: 0;
  font-size: 0.8125rem;
  font-family: inherit;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-primary);
}

.confirm-actions {
  display: flex;
  gap: 0.5rem;
}

.confirm-btn {
  flex: 1;
  padding: 0.625rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-btn--accept {
  background: #22c55e;
  color: white;
}

.confirm-btn--accept:hover:not(:disabled) {
  background: #16a34a;
}

.confirm-btn--modify {
  background: #6366f1;
  color: white;
}

.confirm-btn--modify:hover:not(:disabled) {
  background: #4f46e5;
}

.confirm-btn--reject {
  background: #ef4444;
  color: white;
}

.confirm-btn--reject:hover:not(:disabled) {
  background: #dc2626;
}
</style>
