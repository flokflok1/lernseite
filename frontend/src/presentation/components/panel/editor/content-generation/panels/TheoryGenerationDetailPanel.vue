<!--
  TheoryGenerationDetailPanel - Theory detail or creation (middle panel)

  Displays theory content or creation form.
  Handles generation of new theories with AI.
  Max 350 lines = modular detail handling.
-->

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterTheory, TheoryStyle } from '../types/theory.types'

interface Props {
  selectedTheory: ChapterTheory | null
  isGenerating: boolean
  showCreateForm: boolean
}

interface Emits {
  (e: 'generate', style: TheoryStyle, title: string, withAudio: boolean): void
  (e: 'cancel-create'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Local state
const newTitle = ref('')
const selectedStyle = ref<TheoryStyle>('standard')
const generateWithAudio = ref(false)

// Computed
const currentTheoryTitle = computed(() => props.selectedTheory?.title || '')
const currentTheoryStyle = computed(() => props.selectedTheory?.style || 'standard')

// Methods
const handleGenerate = () => {
  emit('generate', selectedStyle.value, newTitle.value, generateWithAudio.value)
  newTitle.value = ''
}

const handleCancel = () => {
  emit('cancel-create')
  newTitle.value = ''
  selectedStyle.value = 'standard'
  generateWithAudio.value = false
}

const getStyleEmoji = (style: string): string => {
  const emojis: Record<string, string> = {
    standard: '📚',
    compact: '📋',
    detailed: '📖',
    visual: '🎨',
    exam: '📝'
  }
  return emojis[style] || '📚'
}

const getStyleName = (style: string): string => {
  const names: Record<string, string> = {
    standard: t('course-editor.theory.styles.standard'),
    compact: t('course-editor.theory.styles.compact'),
    detailed: t('course-editor.theory.styles.detailed'),
    visual: t('course-editor.theory.styles.visual'),
    exam: t('course-editor.theory.styles.exam')
  }
  return names[style] || style
}
</script>

<template>
  <div class="theory-detail-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">{{ showCreateForm ? '✨' : '📄' }}</span>
      <span class="panel-title">
        {{ showCreateForm ? $t('course-editor.theory.detail.createNew') : $t('course-editor.theory.detail.preview') }}
      </span>
    </div>

    <!-- Content -->
    <div class="panel-content">
      <!-- Create Form -->
      <div v-if="showCreateForm" class="create-form">
        <div class="form-section">
          <label>{{ $t('course-editor.theory.detail.titleLabel') }}</label>
          <input
            v-model="newTitle"
            type="text"
            class="form-input"
            :placeholder="$t('course-editor.theory.detail.titlePlaceholder')"
          />
        </div>

        <div class="form-section">
          <label>{{ $t('course-editor.theory.detail.styleLabel') }}</label>
          <select v-model="selectedStyle" class="form-select">
            <option value="standard">{{ getStyleName('standard') }}</option>
            <option value="compact">{{ getStyleName('compact') }}</option>
            <option value="detailed">{{ getStyleName('detailed') }}</option>
            <option value="visual">{{ getStyleName('visual') }}</option>
            <option value="exam">{{ getStyleName('exam') }}</option>
          </select>
        </div>

        <div class="form-section">
          <label class="checkbox-label">
            <input type="checkbox" v-model="generateWithAudio" />
            {{ $t('course-editor.theory.detail.generateWithAudio') }}
          </label>
        </div>

        <div class="form-actions">
          <button
            @click="handleGenerate"
            class="generate-btn"
            :disabled="isGenerating || !newTitle.trim()"
          >
            <span v-if="isGenerating">{{ $t('course-editor.theory.detail.generating') }}</span>
            <span v-else>{{ $t('course-editor.theory.detail.generate') }}</span>
          </button>
          <button @click="handleCancel" class="cancel-btn">
            {{ $t('course-editor.theory.detail.cancel') }}
          </button>
        </div>
      </div>

      <!-- Theory Detail View -->
      <div v-else-if="selectedTheory" class="theory-detail">
        <div class="theory-header">
          <h3>{{ currentTheoryTitle }}</h3>
          <span class="style-badge">{{ getStyleEmoji(currentTheoryStyle) }} {{ getStyleName(currentTheoryStyle) }}</span>
        </div>

        <div class="theory-content">
          <!-- Overview -->
          <div v-if="selectedTheory.overview" class="theory-section">
            <h4>{{ $t('course-editor.theory.detail.sections.overview') }}</h4>
            <p>{{ selectedTheory.overview }}</p>
          </div>

          <!-- Learning Goals -->
          <div v-if="selectedTheory.learningGoals?.length" class="theory-section">
            <h4>{{ $t('course-editor.theory.detail.sections.learningGoals') }}</h4>
            <ul>
              <li v-for="(goal, i) in selectedTheory.learningGoals" :key="i">{{ goal }}</li>
            </ul>
          </div>

          <!-- Concepts -->
          <div v-if="selectedTheory.concepts?.length" class="theory-section">
            <h4>{{ $t('course-editor.theory.detail.sections.concepts') }}</h4>
            <div v-for="(concept, i) in selectedTheory.concepts" :key="i" class="concept-item">
              <strong>{{ concept.name }}</strong>
              <p>{{ concept.description }}</p>
            </div>
          </div>

          <!-- Terms -->
          <div v-if="selectedTheory.terms?.length" class="theory-section">
            <h4>{{ $t('course-editor.theory.detail.sections.terms') }}</h4>
            <dl class="terms-list">
              <template v-for="(term, i) in selectedTheory.terms" :key="i">
                <dt>{{ term.term }}</dt>
                <dd>{{ term.definition }}</dd>
              </template>
            </dl>
          </div>

          <!-- Exam Relevance -->
          <div v-if="selectedTheory.examRelevance" class="theory-section exam-section">
            <h4>{{ $t('course-editor.theory.detail.sections.examRelevance') }}</h4>
            <p>{{ selectedTheory.examRelevance }}</p>
          </div>

          <!-- Exam Tips -->
          <div v-if="selectedTheory.examTips?.length" class="theory-section">
            <h4>{{ $t('course-editor.theory.detail.sections.examTips') }}</h4>
            <ul>
              <li v-for="(tip, i) in selectedTheory.examTips" :key="i">{{ tip }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- No Selection -->
      <div v-else class="no-selection">
        <span class="empty-icon">📄</span>
        <p>{{ $t('course-editor.theory.detail.noSelection') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theory-detail-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
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
}

.panel-content {
  flex: 1;
  overflow-y: auto;
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
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.generate-btn {
  flex: 1;
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
  flex: 1;
  padding: 0.875rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.15s;
}

.cancel-btn:hover {
  background: var(--color-surface-secondary);
}

/* Theory Detail */
.theory-detail {
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
  white-space: nowrap;
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
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
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
  height: 100%;
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
