<!--
  ResultView — Shown after generation completes.
  Displays generated content preview with accept/reject/revise actions.
-->
<template>
  <div class="result-view">
    <div class="result-header">
      <h3>{{ $t('aiEditor.result.title') }}</h3>
      <span v-if="result" class="result-meta">
        {{ result.modelName }} · {{ (result.tokensOutput ?? 0).toLocaleString() }} tokens
      </span>
    </div>
    <div v-if="result" class="result-content">
      <div v-if="result.targetTitle" class="result-target">
        {{ result.targetTitle }}
      </div>
      <div class="result-preview">
        <pre class="result-json">{{ JSON.stringify(result.content, null, 2) }}</pre>
      </div>
    </div>
    <div v-if="result" class="result-actions">
      <button class="action-btn accept" :disabled="disabled" @click="$emit('accept')">
        {{ $t('aiEditor.result.accept') }}
      </button>
      <button class="action-btn revise" :disabled="disabled" @click="$emit('revise')">
        {{ $t('aiEditor.result.revise') }}
      </button>
      <button class="action-btn reject" :disabled="disabled" @click="$emit('reject')">
        {{ $t('aiEditor.result.reject') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerateResult } from '../types'

defineProps<{
  result: GenerateResult | null
  disabled?: boolean
}>()

defineEmits<{
  accept: []
  reject: []
  revise: []
}>()
</script>

<style scoped>
.result-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.result-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.result-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}
.result-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}
.result-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}
.result-target {
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}
.result-preview {
  background: var(--color-surface-secondary);
  border-radius: 0.375rem;
  padding: 0.75rem;
}
.result-json {
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  color: var(--color-text-secondary);
}
.result-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
}
.action-btn.accept { background: var(--color-success, #22c55e); color: white; }
.action-btn.revise { background: var(--color-warning, #f59e0b); color: white; }
.action-btn.reject { background: var(--color-surface-secondary); color: var(--color-text-primary); border: 1px solid var(--color-border); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn:hover:not(:disabled) { filter: brightness(0.9); }
</style>
