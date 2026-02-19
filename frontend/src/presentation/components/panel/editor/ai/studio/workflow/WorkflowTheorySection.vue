<!--
  WorkflowTheorySection - Theory content display for workflow

  Handles both chapter theories and lesson explanations with
  loading states, empty states, and generation actions.
-->

<template>
  <div class="workflow-section theory-section">
    <div class="workflow-header">
      <span class="workflow-icon">{{ headerIcon }}</span>
      <span class="workflow-title">{{ $t('aiEditorWorkflow.step2') }}</span>
      <span v-if="isLoading" class="workflow-badge">{{ $t('aiEditorWorkflow.loading') }}</span>
      <span v-else-if="contextType === 'chapter' && theories.length" class="workflow-badge">
        {{ theories.length }} {{ $t('aiEditorWorkflow.available') }}
      </span>
      <span v-else-if="contextType === 'lesson' && explanations.length" class="workflow-badge">
        {{ explanations.length }} {{ $t('aiEditorWorkflow.available') }}
      </span>
      <span v-else class="workflow-badge workflow-badge--empty">{{ $t('aiEditorWorkflow.none') }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="theory-loading">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      <span class="loading-text">{{ $t('aiEditorWorkflow.loadingContent') }}</span>
    </div>

    <!-- Chapter: Existing Theories List -->
    <div v-else-if="contextType === 'chapter'" class="theory-content-list">
      <div v-if="theories.length > 0" class="existing-items">
        <div
          v-for="theory in theories"
          :key="theory.theoryId"
          class="theory-item"
          :class="{ selected: selectedTheoryId === theory.theoryId }"
          @click="$emit('open-theory', theory)"
        >
          <span class="theory-item-icon">{{ theoryIcon }}</span>
          <div class="theory-item-info">
            <span class="theory-item-title">{{ theory.title }}</span>
            <span class="theory-item-meta">{{ theory.style }} · {{ formatDate(theory.createdAt) }}</span>
          </div>
          <span v-if="theory.audioUrl" class="theory-item-audio" :title="$t('aiEditorWorkflow.withAudio')">{{ audioIcon }}</span>
        </div>
      </div>
      <div v-else class="no-content-hint">
        <span>{{ summaryIcon }}</span>
        <p>{{ $t('aiEditorWorkflow.noSummary') }}</p>
      </div>
      <button
        @click="$emit('generate-theory')"
        class="workflow-action-btn workflow-action-btn--theory"
        :disabled="isGenerating || disabled"
      >
        <span v-if="isGenerating">{{ $t('aiEditorWorkflow.generating') }}</span>
        <span v-else>{{ theories.length ? $t('aiEditorWorkflow.addSummary') : $t('aiEditorWorkflow.createSummary') }}</span>
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
          <span class="theory-item-icon">{{ explanationIcon }}</span>
          <div class="theory-item-info">
            <span class="theory-item-title">{{ expl.title }}</span>
            <span class="theory-item-meta">{{ expl.stepCount }} {{ $t('aiEditorWorkflow.steps') }} · {{ formatDate(expl.createdAt) }}</span>
          </div>
        </div>
      </div>
      <div v-else class="no-content-hint">
        <span>{{ explanationIcon }}</span>
        <p>{{ $t('aiEditorWorkflow.noTheory') }}</p>
      </div>
      <button
        @click="$emit('generate-theory')"
        class="workflow-action-btn workflow-action-btn--theory"
        :disabled="isGenerating || disabled"
      >
        <span v-if="isGenerating">{{ $t('aiEditorWorkflow.generating') }}</span>
        <span v-else>{{ explanations.length ? $t('aiEditorWorkflow.addTheory') : $t('aiEditorWorkflow.createTheory') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
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

interface Props {
  contextType: 'chapter' | 'lesson' | 'method'
  isLoading: boolean
  isGenerating: boolean
  theories: Theory[]
  explanations: Explanation[]
  selectedTheoryId?: string | null
  disabled?: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'open-theory', theory: Theory): void
  (e: 'open-explanation', explanation: Explanation): void
  (e: 'generate-theory'): void
}>()

const headerIcon = '\uD83D\uDCD6'
const theoryIcon = '\uD83D\uDCC4'
const audioIcon = '\uD83D\uDD0A'
const summaryIcon = '\uD83D\uDCCB'
const explanationIcon = '\uD83D\uDCDD'

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

.workflow-action-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.workflow-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.workflow-action-btn--theory { background: #8b5cf6; }
.workflow-action-btn--theory:hover:not(:disabled) { background: #7c3aed; }

.theory-loading {
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

.theory-content-list { display: flex; flex-direction: column; gap: 0.5rem; }

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

.theory-item:hover { background: var(--color-primary-subtle); }

.theory-item.selected {
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary);
}

.theory-item-icon { font-size: 1rem; }
.theory-item-info { flex: 1; min-width: 0; }

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

.theory-item-audio { font-size: 0.75rem; }

.no-content-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.no-content-hint span { font-size: 1.5rem; margin-bottom: 0.25rem; }
.no-content-hint p { margin: 0; font-size: 0.75rem; }

.loading-text { font-size: 0.75rem; color: var(--color-text-tertiary); }
</style>
