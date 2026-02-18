<!--
  ExplanationViewPanel - Explanation detail or creation form

  Middle panel displaying explanation details with step navigation,
  or showing creation form for new explanations.
-->

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LessonExplanation, ExplanationStyle } from '../types/explanation.types'

const { t } = useI18n()

interface Props {
  explanation: LessonExplanation | null
  showCreateForm: boolean
  isGenerating: boolean
  currentStep: number
  stepsCount: number
}

interface Emits {
  (e: 'generate', style: ExplanationStyle, withAudio: boolean): void
  (e: 'cancel-create'): void
  (e: 'start'): void
  (e: 'next'): void
  (e: 'prev'): void
  (e: 'goto', index: number): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// Local state
const selectedStyle = ref<ExplanationStyle>('standard')
const generateWithAudio = ref(true)

// Computed
const canGoNext = computed(() => props.currentStep < props.stepsCount - 1)
const canGoPrev = computed(() => props.currentStep > 0)
const progressPercent = computed(() => {
  if (props.stepsCount === 0) return 0
  return Math.round(((props.currentStep + 1) / props.stepsCount) * 100)
})

const currentStepData = computed(() => {
  if (!props.explanation || props.currentStep >= props.explanation.steps.length) return null
  return props.explanation.steps[props.currentStep]
})

// Methods
const handleGenerate = () => {
  emit('generate', selectedStyle.value, generateWithAudio.value)
}

const handleCancel = () => {
  emit('cancel-create')
}

const handleStart = () => {
  emit('start')
}

const handleNext = () => {
  if (canGoNext.value) {
    emit('next')
  }
}

const handlePrev = () => {
  if (canGoPrev.value) {
    emit('prev')
  }
}

const handleGoToStep = (index: number) => {
  emit('goto', index)
}

// Reset form when create mode closes
watch(() => props.showCreateForm, (isShow) => {
  if (!isShow) {
    selectedStyle.value = 'standard'
    generateWithAudio.value = true
  }
})
</script>

<template>
  <div class="explanation-view-panel">
    <!-- Create Form -->
    <div v-if="showCreateForm" class="create-form">
      <h3>{{ $t('course-editor.explanation.create.title') }}</h3>

      <!-- Style Selection -->
      <div class="form-group">
        <label>{{ $t('course-editor.explanation.create.style') }}</label>
        <select v-model="selectedStyle" class="form-control">
          <option value="brief">{{ $t('course-editor.explanation.styles.brief') }}</option>
          <option value="standard">{{ $t('course-editor.explanation.styles.standard') }}</option>
          <option value="detailed">{{ $t('course-editor.explanation.styles.detailed') }}</option>
          <option value="visual">{{ $t('course-editor.explanation.styles.visual') }}</option>
          <option value="interactive">{{ $t('course-editor.explanation.styles.interactive') }}</option>
        </select>
      </div>

      <!-- Audio Generation -->
      <div class="form-group checkbox">
        <input
          id="generate-audio"
          v-model="generateWithAudio"
          type="checkbox"
        />
        <label for="generate-audio">
          {{ $t('course-editor.explanation.create.withAudio') }}
        </label>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button
          class="btn btn-primary"
          @click="handleGenerate"
          :disabled="isGenerating"
        >
          {{ isGenerating ? $t('common.generating') : $t('course-editor.explanation.create.generate') }}
        </button>
        <button
          class="btn btn-secondary"
          @click="handleCancel"
          :disabled="isGenerating"
        >
          {{ $t('common.cancel') }}
        </button>
      </div>

      <!-- Progress -->
      <div v-if="isGenerating" class="progress-section">
        <div class="spinner"></div>
        <p>{{ $t('course-editor.explanation.create.generating') }}</p>
      </div>
    </div>

    <!-- Explanation Detail -->
    <div v-else-if="explanation" class="explanation-detail">
      <!-- Title -->
      <h3>{{ explanation.title }}</h3>

      <!-- Meta -->
      <div class="meta-info">
        <span class="badge">{{ explanation.style }}</span>
        <span class="meta">{{ explanation.steps.length }} {{ $t('course-editor.explanation.list.steps') }}</span>
      </div>

      <!-- Step Navigation -->
      <div v-if="stepsCount > 0" class="step-navigation">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <div class="step-info">
          {{ currentStep + 1 }} / {{ stepsCount }} ({{ progressPercent }}%)
        </div>

        <!-- Step Thumbnails -->
        <div class="step-thumbnails">
          <button
            v-for="(step, index) in explanation.steps"
            :key="step.stepId"
            :class="['step-thumb', { active: currentStep === index }]"
            @click="handleGoToStep(index)"
            :title="step.title"
          >
            {{ index + 1 }}
          </button>
        </div>
      </div>

      <!-- Current Step Content -->
      <div v-if="currentStepData" class="step-content">
        <h4>{{ currentStepData.title }}</h4>
        <div class="content">{{ currentStepData.content }}</div>

        <!-- Whiteboard Slot -->
        <div v-if="currentStepData.whiteboard_data" class="whiteboard-container">
          <slot name="whiteboard"></slot>
        </div>
      </div>

      <!-- Step Controls -->
      <div class="step-controls">
        <button class="btn btn-sm" @click="handleStart">
          🎬 {{ $t('course-editor.explanation.view.start') }}
        </button>
        <button
          class="btn btn-sm"
          @click="handlePrev"
          :disabled="!canGoPrev"
        >
          ← {{ $t('course-editor.explanation.view.prev') }}
        </button>
        <button
          class="btn btn-sm"
          @click="handleNext"
          :disabled="!canGoNext"
        >
          {{ $t('course-editor.explanation.view.next') }} →
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('course-editor.explanation.view.empty') }}</p>
    </div>
  </div>
</template>

<style scoped>
.explanation-view-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  background: var(--color-surface);
  overflow-y: auto;
}

/* Create Form */
.create-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 2px dashed var(--color-primary);
  border-radius: 8px;
  background: var(--color-primary-light);
}

.create-form h3 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1.125rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-control {
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.875rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.form-group.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.form-group.checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-group.checkbox label {
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-secondary {
  border-color: var(--color-border);
  background: var(--color-surface);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-surface-hover);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
}

.progress-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Explanation Detail */
.explanation-detail {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.explanation-detail h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.badge {
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}

/* Step Navigation */
.step-navigation {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-bar {
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.step-info {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  text-align: center;
}

.step-thumbnails {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 0.5rem 0;
}

.step-thumb {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 2px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface-secondary);
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.step-thumb:hover {
  border-color: var(--color-primary);
}

.step-thumb.active {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
}

/* Step Content */
.step-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.step-content h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.content {
  padding: 0.75rem;
  border-radius: 4px;
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.whiteboard-container {
  height: 300px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: white;
  overflow: hidden;
}

/* Step Controls */
.step-controls {
  display: flex;
  gap: 0.75rem;
  margin-top: auto;
}

.step-controls .btn {
  flex: 1;
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  text-align: center;
}
</style>
