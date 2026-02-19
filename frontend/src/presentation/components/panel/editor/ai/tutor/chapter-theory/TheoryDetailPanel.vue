<!--
  TheoryDetailPanel - Middle column displaying the create form or theory detail.

  Shows one of three states:
  1. Create form (when showCreateForm is true)
  2. Theory detail view (when a theory is selected)
  3. Empty state (no selection)
-->

<template>
  <div class="detail-panel">
    <div class="panel-header">
      <span class="panel-icon">{{ showCreateForm ? '✨' : '📄' }}</span>
      <span class="panel-title">{{ showCreateForm ? $t('chapterTheoryView.newTheory') : $t('chapterTheoryView.preview') }}</span>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="create-form">
      <div class="form-section">
        <label>{{ $t('chapterTheoryView.titleLabel') }}</label>
        <input
          :value="newTitle"
          @input="$emit('update:newTitle', ($event.target as HTMLInputElement).value)"
          type="text"
          class="form-input"
          :placeholder="$t('chapterTheoryView.titlePlaceholder')"
        />
      </div>

      <div class="form-section">
        <label>{{ $t('chapterTheoryView.styleLabel') }}</label>
        <select
          :value="selectedStyle"
          @change="$emit('update:selectedStyle', ($event.target as HTMLSelectElement).value)"
          class="form-select"
        >
          <option value="standard">{{ $t('chapterTheoryView.styles.standard') }}</option>
          <option value="compact">{{ $t('chapterTheoryView.styles.compact') }}</option>
          <option value="detailed">{{ $t('chapterTheoryView.styles.detailed') }}</option>
          <option value="visual">{{ $t('chapterTheoryView.styles.visual') }}</option>
          <option value="exam">{{ $t('chapterTheoryView.styles.exam') }}</option>
        </select>
      </div>

      <div class="form-section">
        <label class="checkbox-label">
          <input
            type="checkbox"
            :checked="generateWithAudio"
            @change="$emit('update:generateWithAudio', ($event.target as HTMLInputElement).checked)"
          />
          {{ $t('chapterTheoryView.generateWithAudio') }}
        </label>
      </div>

      <button
        @click="$emit('generate')"
        class="generate-btn"
        :disabled="isGenerating"
      >
        <span v-if="isGenerating">{{ $t('chapterTheoryView.generating') }}</span>
        <span v-else>{{ $t('chapterTheoryView.generate') }}</span>
      </button>

      <button @click="$emit('cancelCreate')" class="cancel-btn">
        {{ $t('chapterTheoryView.cancel') }}
      </button>
    </div>

    <!-- Theory Detail View -->
    <div v-else-if="selectedTheory" class="theory-detail">
      <div class="theory-header">
        <h3>{{ theoryTitle }}</h3>
        <span class="style-badge">{{ getStyleEmoji(theoryStyle) }} {{ getStyleName(theoryStyle) }}</span>
      </div>

      <div class="theory-content">
        <div v-if="selectedTheory.overview" class="theory-section">
          <h4>{{ $t('chapterTheoryView.sections.overview') }}</h4>
          <p>{{ selectedTheory.overview }}</p>
        </div>

        <div v-if="selectedTheory.learningGoals?.length" class="theory-section">
          <h4>{{ $t('chapterTheoryView.sections.learningGoals') }}</h4>
          <ul>
            <li v-for="(goal, i) in selectedTheory.learningGoals" :key="i">{{ goal }}</li>
          </ul>
        </div>

        <div v-if="selectedTheory.concepts?.length" class="theory-section">
          <h4>{{ $t('chapterTheoryView.sections.concepts') }}</h4>
          <div v-for="(concept, i) in selectedTheory.concepts" :key="i" class="concept-item">
            <strong>{{ concept.name }}</strong>
            <p>{{ concept.description }}</p>
          </div>
        </div>

        <div v-if="selectedTheory.terms?.length" class="theory-section">
          <h4>{{ $t('chapterTheoryView.sections.terms') }}</h4>
          <dl class="terms-list">
            <template v-for="(term, i) in selectedTheory.terms" :key="i">
              <dt>{{ term.term }}</dt>
              <dd>{{ term.definition }}</dd>
            </template>
          </dl>
        </div>

        <div v-if="selectedTheory.examRelevance" class="theory-section exam-section">
          <h4>{{ $t('chapterTheoryView.sections.examRelevance') }}</h4>
          <p>{{ selectedTheory.examRelevance }}</p>
        </div>

        <div v-if="selectedTheory.examTips?.length" class="theory-section">
          <h4>{{ $t('chapterTheoryView.sections.examTips') }}</h4>
          <ul>
            <li v-for="(tip, i) in selectedTheory.examTips" :key="i">{{ tip }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- No Selection -->
    <div v-else class="no-selection">
      <span class="empty-icon">📄</span>
      <p>{{ $t('chapterTheoryView.noSelection') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChapterTheory, TheoryStyle } from './chapter-theory.types'

interface Props {
  showCreateForm: boolean
  newTitle: string
  selectedStyle: TheoryStyle
  generateWithAudio: boolean
  isGenerating: boolean
  selectedTheory: ChapterTheory | null
  theoryTitle: string
  theoryStyle: string
  getStyleEmoji: (style: string) => string
  getStyleName: (style: string) => string
}

defineProps<Props>()

defineEmits<{
  (e: 'update:newTitle', value: string): void
  (e: 'update:selectedStyle', value: string): void
  (e: 'update:generateWithAudio', value: boolean): void
  (e: 'generate'): void
  (e: 'cancelCreate'): void
}>()
</script>

<style scoped>
.detail-panel {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-weight: 600;
  font-size: 0.875rem;
  flex: 1;
}

/* Create Form */
.create-form {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-section label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input,
.form-select {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.generate-btn {
  padding: 0.875rem;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.15s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 0.625rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

/* Theory Detail */
.theory-detail {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.theory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.theory-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.style-badge {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 1rem;
  font-size: 0.75rem;
}

.theory-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.theory-section h4 {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
  color: var(--color-text-primary);
}

.theory-section p {
  margin: 0;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.theory-section ul {
  margin: 0;
  padding-left: 1.25rem;
}

.theory-section li {
  margin-bottom: 0.375rem;
  color: var(--color-text-secondary);
}

.concept-item {
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.concept-item strong {
  color: var(--color-primary);
}

.concept-item p {
  margin-top: 0.25rem;
}

.terms-list {
  margin: 0;
}

.terms-list dt {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-top: 0.5rem;
}

.terms-list dd {
  margin: 0.25rem 0 0 0;
  color: var(--color-text-secondary);
}

.exam-section {
  padding: 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
  border-radius: 0.5rem;
  border-left: 3px solid #f59e0b;
}

/* No Selection */
.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}
</style>
