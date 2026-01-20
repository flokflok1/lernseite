<!--
  WorkflowPanel - Context-aware workflow steps

  Displays the workflow when a chapter or lesson is selected:
  1. Analyze with materials
  2. Theory content (theories/explanations)
  3. LM Suggestions (for lessons)
-->

<template>
  <div v-if="context" class="workflow-panel">
    <!-- Context Header -->
    <div class="context-header">
      <span class="context-icon">{{ context.type === 'chapter' ? '📖' : '📄' }}</span>
      <div class="context-details">
        <span class="context-type">{{ context.type === 'chapter' ? $t('features.aiEditorWorkflow.chapter') : $t('features.aiEditorWorkflow.lesson') }}</span>
        <span class="context-title">{{ context.title }}</span>
      </div>
      <button @click="$emit('close')" class="context-close" :title="$t('features.aiEditorWorkflow.closeContext')">×</button>
    </div>

    <!-- Step 1: Analyze with Materials -->
    <div class="workflow-section analyze-section">
      <div class="workflow-header">
        <span class="workflow-icon">🔍</span>
        <span class="workflow-title">{{ $t('features.aiEditorWorkflow.step1') }}</span>
        <span v-if="selectedFileCount" class="workflow-badge">{{ selectedFileCount }} {{ $t('features.aiEditorWorkflow.files') }}</span>
      </div>
      <button
        @click="$emit('analyze')"
        class="workflow-action-btn"
        :class="{ 'is-loading': isAnalyzing }"
        :disabled="isAnalyzing || disabled"
      >
        <span v-if="isAnalyzing">⏳ {{ $t('features.aiEditorWorkflow.analyzing') }}</span>
        <span v-else-if="selectedFileCount">🔍 {{ $t('features.aiEditorWorkflow.analyzeWithFiles', { count: selectedFileCount }) }}</span>
        <span v-else>🔍 {{ $t('features.aiEditorWorkflow.analyzeContext') }}</span>
      </button>
      <p v-if="!selectedFileCount" class="workflow-hint">
        💡 {{ $t('features.aiEditorWorkflow.tipMaterials') }}
      </p>
    </div>

    <!-- Step 2: Theory Content -->
    <div class="workflow-section theory-section">
      <div class="workflow-header">
        <span class="workflow-icon">📖</span>
        <span class="workflow-title">{{ $t('features.aiEditorWorkflow.step2') }}</span>
        <span v-if="isLoadingTheories" class="workflow-badge">{{ $t('features.aiEditorWorkflow.loading') }}</span>
        <span v-else-if="context.type === 'chapter' && theories.length" class="workflow-badge">
          {{ theories.length }} {{ $t('features.aiEditorWorkflow.available') }}
        </span>
        <span v-else-if="context.type === 'lesson' && explanations.length" class="workflow-badge">
          {{ explanations.length }} {{ $t('features.aiEditorWorkflow.available') }}
        </span>
        <span v-else class="workflow-badge workflow-badge--empty">{{ $t('features.aiEditorWorkflow.none') }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="isLoadingTheories" class="theory-loading">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        <span class="loading-text">{{ $t('features.aiEditorWorkflow.loadingContent') }}</span>
      </div>

      <!-- Chapter: Existing Theories List -->
      <div v-else-if="context.type === 'chapter'" class="theory-content-list">
        <div v-if="theories.length > 0" class="existing-items">
          <div
            v-for="theory in theories"
            :key="theory.theoryId"
            class="theory-item"
            :class="{ selected: selectedTheoryId === theory.theoryId }"
            @click="$emit('open-theory', theory)"
          >
            <span class="theory-item-icon">📄</span>
            <div class="theory-item-info">
              <span class="theory-item-title">{{ theory.title }}</span>
              <span class="theory-item-meta">{{ theory.style }} · {{ formatDate(theory.createdAt) }}</span>
            </div>
            <span v-if="theory.audioUrl" class="theory-item-audio" :title="$t('features.aiEditorWorkflow.withAudio')">🔊</span>
          </div>
        </div>
        <div v-else class="no-content-hint">
          <span>📋</span>
          <p>{{ $t('features.aiEditorWorkflow.noSummary') }}</p>
        </div>
        <button
          @click="$emit('generate-theory')"
          class="workflow-action-btn workflow-action-btn--theory"
          :disabled="isGeneratingTheory || disabled"
        >
          <span v-if="isGeneratingTheory">⏳ {{ $t('features.aiEditorWorkflow.generating') }}</span>
          <span v-else>{{ theories.length ? '➕ ' + $t('features.aiEditorWorkflow.addSummary') : '📚 ' + $t('features.aiEditorWorkflow.createSummary') }}</span>
        </button>
      </div>

      <!-- Lesson: Existing Explanations List -->
      <div v-else class="theory-content-list">
        <div v-if="explanations.length > 0" class="existing-items">
          <div
            v-for="expl in explanations"
            :key="expl.explanationId"
            class="theory-item"
            @click="$emit('open-explanation', expl)"
          >
            <span class="theory-item-icon">📝</span>
            <div class="theory-item-info">
              <span class="theory-item-title">{{ expl.title }}</span>
              <span class="theory-item-meta">{{ expl.stepCount }} {{ $t('features.aiEditorWorkflow.steps') }} · {{ formatDate(expl.createdAt) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-content-hint">
          <span>📝</span>
          <p>{{ $t('features.aiEditorWorkflow.noTheory') }}</p>
        </div>
        <button
          @click="$emit('generate-theory')"
          class="workflow-action-btn workflow-action-btn--theory"
          :disabled="isGeneratingTheory || disabled"
        >
          <span v-if="isGeneratingTheory">⏳ {{ $t('features.aiEditorWorkflow.generating') }}</span>
          <span v-else>{{ explanations.length ? '➕ ' + $t('features.aiEditorWorkflow.addTheory') : '📖 ' + $t('features.aiEditorWorkflow.createTheory') }}</span>
        </button>
      </div>
    </div>

    <!-- Step 3: LM Suggestions (for lessons only) -->
    <div v-if="context.type === 'lesson'" class="workflow-section lm-section">
      <div class="workflow-header">
        <span class="workflow-icon">🧠</span>
        <span class="workflow-title">{{ $t('features.aiEditorWorkflow.step3') }}</span>
        <span v-if="isLoadingLMSuggestions" class="workflow-badge">{{ $t('features.aiEditorWorkflow.analyzing') }}</span>
      </div>
      <div v-if="isLoadingLMSuggestions" class="lm-suggestions-loading">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="loading-text">{{ $t('features.aiEditorWorkflow.aiAnalyzing') }}</span>
      </div>
      <div v-else-if="lmSuggestions.length > 0" class="lm-suggestions-grid">
        <button
          v-for="lm in lmSuggestions"
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
      <div v-else class="lm-no-suggestions">
        <span>{{ $t('features.aiEditorWorkflow.analyzeFirst') }}</span>
      </div>
    </div>

    <!-- Context-specific Actions -->
    <div class="context-actions">
      <template v-if="isLoadingActions">
        <span class="loading-text">{{ $t('features.aiEditorWorkflow.loadingActions') }}</span>
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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

// Helpers
function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    })
  } catch {
    return dateStr
  }
}
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
.context-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.context-icon {
  font-size: 1.25rem;
}

.context-details {
  flex: 1;
  min-width: 0;
}

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

.context-close:hover {
  color: var(--color-text-primary);
}

/* Workflow Sections */
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

.workflow-icon {
  font-size: 1rem;
}

.workflow-title {
  font-size: 0.75rem;
  font-weight: 600;
  flex: 1;
}

.workflow-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
}

.workflow-badge--empty {
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
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

.workflow-action-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.workflow-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.workflow-action-btn.is-loading {
  animation: pulse 1s infinite;
}

.workflow-action-btn--theory {
  background: #8b5cf6;
}

.workflow-action-btn--theory:hover:not(:disabled) {
  background: #7c3aed;
}

.workflow-hint {
  margin: 0.5rem 0 0;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

/* Loading States */
.theory-loading,
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

@keyframes bounce {
  to { transform: translateY(-4px); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Theory Items */
.theory-content-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.existing-items {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-height: 150px;
  overflow-y: auto;
}

.theory-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.15s;
}

.theory-item:hover {
  background: var(--color-primary-subtle);
}

.theory-item.selected {
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary);
}

.theory-item-icon {
  font-size: 1rem;
}

.theory-item-info {
  flex: 1;
  min-width: 0;
}

.theory-item-title {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theory-item-meta {
  display: block;
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

.theory-item-audio {
  font-size: 0.75rem;
}

.no-content-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.no-content-hint span {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.no-content-hint p {
  margin: 0;
  font-size: 0.75rem;
}

/* LM Suggestions */
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

.lm-suggestion-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* LM Group Colors */
.lm-group-a { border-left: 3px solid #3b82f6; }
.lm-group-b { border-left: 3px solid #22c55e; }
.lm-group-c { border-left: 3px solid #f59e0b; }

.lm-btn-top {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.25rem;
}

.lm-icon {
  font-size: 0.875rem;
}

.lm-name {
  font-size: 0.75rem;
  font-weight: 500;
}

.lm-btn-bottom {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  line-height: 1.3;
}

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

/* Context Actions */
.context-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

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

.context-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qa-icon {
  font-size: 0.875rem;
}

.qa-label {
  white-space: nowrap;
}

.loading-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}
</style>
