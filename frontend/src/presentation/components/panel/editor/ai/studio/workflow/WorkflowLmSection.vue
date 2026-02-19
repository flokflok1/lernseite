<!--
  WorkflowLmSection - Learning Method suggestions for workflow

  Displays AI-generated LM suggestions for lessons with a grid
  of suggestion buttons grouped by learning method type.
-->

<template>
  <div class="workflow-section lm-section">
    <div class="workflow-header">
      <span class="workflow-icon">{{ brainIcon }}</span>
      <span class="workflow-title">{{ $t('aiEditorWorkflow.step3') }}</span>
      <span v-if="isLoading" class="workflow-badge">{{ $t('aiEditorWorkflow.analyzing') }}</span>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="lm-suggestions-loading">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="loading-text">{{ $t('aiEditorWorkflow.aiAnalyzing') }}</span>
    </div>

    <!-- Suggestions Grid -->
    <div v-else-if="suggestions.length > 0" class="lm-suggestions-grid">
      <button
        v-for="lm in suggestions"
        :key="lm.lm_id"
        @click="$emit('create-lm', lm)"
        class="lm-suggestion-btn"
        :class="`lm-group-${lm.group?.toLowerCase() || 'b'}`"
        :disabled="disabled"
        :title="lm.reason"
      >
        <div class="lm-btn-top">
          <span class="lm-icon">{{ lm.icon }}</span>
          <span class="lm-name">{{ lm.name }}</span>
        </div>
        <div class="lm-btn-bottom">
          <span class="lm-reason">{{ lm.reason }}</span>
        </div>
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="lm-no-suggestions">
      <span>{{ $t('aiEditorWorkflow.analyzeFirst') }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface LMSuggestion {
  lm_id: number
  name: string
  icon?: string
  group?: string
  reason: string
  description?: string
  confidence?: number
}

interface Props {
  suggestions: LMSuggestion[]
  isLoading: boolean
  disabled?: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'create-lm', suggestion: LMSuggestion): void
}>()

const brainIcon = '\uD83E\uDDE0'
</script>

<style scoped>
.workflow-section {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
}

.workflow-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.workflow-icon { font-size: 1rem; }
.workflow-title { font-size: 0.75rem; font-weight: 600; flex: 1; }

.workflow-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
}

.lm-suggestions-loading {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem;
  color: var(--color-text-tertiary);
  font-size: 0.75rem;
}

.dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce { to { transform: translateY(-4px); } }

.lm-suggestions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.lm-suggestion-btn {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
}

.lm-suggestion-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.lm-suggestion-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.lm-group-a { border-left: 3px solid #3b82f6; }
.lm-group-b { border-left: 3px solid #22c55e; }
.lm-group-c { border-left: 3px solid #f59e0b; }

.lm-btn-top { display: flex; align-items: center; gap: 0.375rem; margin-bottom: 0.25rem; }
.lm-icon { font-size: 0.875rem; }
.lm-name { font-size: 0.75rem; font-weight: 500; }

.lm-btn-bottom { font-size: 0.625rem; color: var(--color-text-tertiary); line-height: 1.3; }

.lm-reason {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.lm-no-suggestions {
  padding: 0.75rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.loading-text { font-size: 0.75rem; color: var(--color-text-tertiary); }
</style>
