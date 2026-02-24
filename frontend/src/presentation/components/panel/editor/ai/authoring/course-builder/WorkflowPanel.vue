<!--
  WorkflowPanel - Context-aware workflow steps

  Displays the workflow when a chapter or lesson is selected:
  1. Analyze with materials
  2. Theory content (theories/explanations)
  3. LM Suggestions (for lessons)

  Refactored: extracted theory and LM sections into shared sub-components (2026-02-18)
-->

<template>
  <div v-if="context" class="workflow-panel">
    <!-- Context Header -->
    <div class="context-header">
      <span class="context-icon">{{ context.type === 'chapter' ? '\uD83D\uDCD6' : '\uD83D\uDCC4' }}</span>
      <div class="context-details">
        <span class="context-type">{{ context.type === 'chapter' ? $t('aiEditorWorkflow.chapter') : $t('aiEditorWorkflow.lesson') }}</span>
        <span class="context-title">{{ context.title }}</span>
      </div>
      <button @click="$emit('close')" class="context-close" :title="$t('aiEditorWorkflow.closeContext')">x</button>
    </div>

    <!-- Step 1: Analyze with Materials -->
    <div class="workflow-section analyze-section">
      <div class="workflow-header">
        <span class="workflow-icon">{{ searchIcon }}</span>
        <span class="workflow-title">{{ $t('aiEditorWorkflow.step1') }}</span>
        <span v-if="selectedFileCount" class="workflow-badge">{{ selectedFileCount }} {{ $t('aiEditorWorkflow.files') }}</span>
      </div>
      <button
        @click="$emit('analyze')"
        class="workflow-action-btn"
        :class="{ 'is-loading': isAnalyzing }"
        :disabled="isAnalyzing || disabled"
      >
        <span v-if="isAnalyzing">{{ $t('aiEditorWorkflow.analyzing') }}</span>
        <span v-else-if="selectedFileCount">{{ $t('aiEditorWorkflow.analyzeWithFiles', { count: selectedFileCount }) }}</span>
        <span v-else>{{ $t('aiEditorWorkflow.analyzeContext') }}</span>
      </button>
      <p v-if="!selectedFileCount" class="workflow-hint">
        {{ $t('aiEditorWorkflow.tipMaterials') }}
      </p>
    </div>

    <!-- Step 2: Theory Content -->
    <WorkflowTheorySection
      :context-type="context.type"
      :is-loading="isLoadingTheories"
      :is-generating="isGeneratingTheory"
      :theories="theories"
      :explanations="explanations"
      :selected-theory-id="selectedTheoryId"
      :disabled="disabled"
      @open-theory="$emit('open-theory', $event)"
      @open-explanation="$emit('open-explanation', $event)"
      @generate-theory="$emit('generate-theory')"
    />

    <!-- Step 3: LM Suggestions (for lessons only) -->
    <WorkflowLmSection
      v-if="context.type === 'lesson'"
      :suggestions="lmSuggestions"
      :is-loading="isLoadingLMSuggestions"
      :disabled="disabled"
      @create-lm="$emit('create-lm', $event)"
    />

    <!-- Context-specific Actions -->
    <div class="context-actions">
      <template v-if="isLoadingActions">
        <span class="loading-text">{{ $t('aiEditorWorkflow.loadingActions') }}</span>
      </template>
      <template v-else>
        <button
          v-for="action in contextActions"
          :key="action.action_id"
          @click="$emit('action', action)"
          class="context-action-btn"
          :disabled="disabled"
        >
          <span class="qa-icon">{{ action.icon }}</span>
          <span class="qa-label">{{ action.label }}</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
// TODO: These components were in the removed studio/ directory — needs migration to unified/
// import WorkflowTheorySection from '../../studio/workflow/WorkflowTheorySection.vue'
// import WorkflowLmSection from '../../studio/workflow/WorkflowLmSection.vue'

const searchIcon = '\uD83D\uDD0D'

// Types
interface SelectedContext {
  type: 'chapter' | 'lesson' | 'method'
  id: string
  title: string
}

interface Theory {
  theoryId: string
  title?: string
  style?: string
  createdAt?: string
  audioUrl?: string
}

interface Explanation {
  explanationId: string
  title?: string
  stepCount?: number
  createdAt?: string
}

interface LMSuggestion {
  lm_id: number
  name: string
  icon?: string
  group?: string
  reason: string
  description?: string
  confidence?: number
}

interface ContextAction {
  action_id: string
  action_key: string
  label: string
  icon: string
  prompt_template: string
  mode?: string
  color?: string
}

// Props
defineProps<{
  context: SelectedContext | null
  selectedFileCount?: number
  isAnalyzing?: boolean
  isLoadingTheories?: boolean
  isGeneratingTheory?: boolean
  isLoadingLMSuggestions?: boolean
  isLoadingActions?: boolean
  theories: Theory[]
  explanations: Explanation[]
  lmSuggestions: LMSuggestion[]
  contextActions: ContextAction[]
  selectedTheoryId?: string | null
  disabled?: boolean
}>()

// Emits
defineEmits<{
  (e: 'close'): void
  (e: 'analyze'): void
  (e: 'generate-theory'): void
  (e: 'open-theory', theory: Theory): void
  (e: 'open-explanation', explanation: Explanation): void
  (e: 'create-lm', suggestion: LMSuggestion): void
  (e: 'action', action: ContextAction): void
}>()
</script>

<style scoped>
.workflow-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

/* Context Header */
.context-header { display: flex; align-items: center; gap: 0.5rem; }
.context-icon { font-size: 1.25rem; }
.context-details { flex: 1; min-width: 0; }

.context-type {
  display: block;
  font-size: 0.625rem;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
  letter-spacing: 0.05em;
}

.context-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.context-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--color-text-tertiary);
  padding: 0.25rem;
  line-height: 1;
}

.context-close:hover { color: var(--color-text-primary); }

/* Workflow Sections */
.workflow-section {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
}

.workflow-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.workflow-icon { font-size: 1rem; }
.workflow-title { font-size: 0.75rem; font-weight: 600; flex: 1; }

.workflow-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
}

.workflow-action-btn {
  width: 100%;
  padding: 0.625rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.workflow-action-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.workflow-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.workflow-action-btn.is-loading { animation: pulse 1s infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.workflow-hint {
  margin: 0.5rem 0 0;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

/* Context Actions */
.context-actions { display: flex; flex-wrap: wrap; gap: 0.375rem; }

.context-action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.context-action-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.context-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.qa-icon { font-size: 0.875rem; }
.qa-label { white-space: nowrap; }
.loading-text { font-size: 0.75rem; color: var(--color-text-tertiary); }
</style>
