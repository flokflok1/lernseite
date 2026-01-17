<!--
  ExplanationViewer - Main viewer for lesson explanation steps
-->

<template>
  <div class="explanation-viewer">
    <!-- Create Form -->
    <div v-if="showCreateForm" class="create-form">
      <div class="panel-header">
        <span class="panel-icon">✨</span>
        <span class="panel-title">{{ $t('features.lessonExplanationView.newExplanation') }}</span>
      </div>

      <div class="form-content">
        <div class="form-section">
          <label>{{ $t('features.lessonExplanationView.styleLabel') }}</label>
          <select v-model="localStyle" class="form-select">
            <option value="adhs">{{ $t('features.lessonExplanationView.styles.adhs') }}</option>
            <option value="detailed">{{ $t('features.lessonExplanationView.styles.detailed') }}</option>
            <option value="short">{{ $t('features.lessonExplanationView.styles.short') }}</option>
            <option value="exam_focus">{{ $t('features.lessonExplanationView.styles.examFocus') }}</option>
          </select>
        </div>

        <div class="form-section">
          <label>{{ $t('features.lessonExplanationView.voiceLabel') }}</label>
          <select v-model="localVoice" class="form-select">
            <option v-for="voice in voices" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
        </div>

        <div class="form-section">
          <label class="checkbox-label">
            <input type="checkbox" v-model="localGenerateWithAudio" />
            {{ $t('features.lessonExplanationView.generateWithAudio') }}
          </label>
        </div>

        <button
          @click="handleGenerate"
          class="generate-btn"
          :disabled="isGenerating"
        >
          <span v-if="isGenerating">{{ $t('features.lessonExplanationView.generating') }}</span>
          <span v-else>{{ $t('features.lessonExplanationView.generate') }}</span>
        </button>

        <button @click="$emit('cancel-create')" class="cancel-btn">
          {{ $t('features.lessonExplanationView.cancel') }}
        </button>
      </div>
    </div>

    <!-- Explanation View -->
    <div v-else-if="hasExplanation && hasSteps" class="explanation-view">
      <!-- Tutor Header -->
      <div class="tutor-header">
        <div class="tutor-avatar">
          <span class="avatar-emoji">👨‍🏫</span>
        </div>
        <div class="tutor-info">
          <span class="tutor-name">
            {{ explanation.title || $t('features.lessonExplanationView.tutorExplains') }}
          </span>
          <span class="tutor-status" :class="{ speaking: isSpeaking }">
            {{ isSpeaking
                ? $t('features.lessonExplanationView.speaking')
                : $t('features.lessonExplanationView.ready')
            }}
          </span>
        </div>
        <div class="tutor-controls">
          <select v-model="localSelectedVoice" class="tts-select" :title="$t('features.lessonExplanationView.voiceLabel')">
            <option v-for="voice in voices" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
          <select v-model="localSelectedModel" class="tts-select" :title="$t('features.lessonExplanationView.ttsModel')">
            <option value="browser">{{ $t('features.lessonExplanationView.browserFree') }}</option>
            <option value="tts-1">TTS-1</option>
            <option value="tts-1-hd">TTS-1-HD</option>
          </select>
          <button @click="$emit('toggle-tts', currentStepData?.speech)" class="tts-btn" :class="{ active: ttsEnabled }">
            {{ ttsEnabled ? '🔊' : '🔇' }}
          </button>
        </div>
      </div>

      <!-- Progress -->
      <div class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
        <span class="progress-text">
          {{ $t('features.lessonExplanationView.stepProgress', { current: currentStep + 1, total: stepsCount }) }}
        </span>
        <button
          v-if="currentStep === 0 && !isSpeaking && !isAnimating"
          @click="$emit('start')"
          class="start-btn"
        >
          {{ $t('features.lessonExplanationView.start') }}
        </button>
        <div v-if="isAnimating" class="animating-indicator">
          <span class="spinner-small"></span>
          <span>{{ $t('features.lessonExplanationView.drawing') }}</span>
        </div>
      </div>

      <!-- Main Area: Whiteboard + Step Card -->
      <div class="tutor-main-area">
        <!-- Whiteboard (if step has whiteboard actions) -->
        <div v-if="currentStepData?.whiteboardActions?.length" class="whiteboard-container" :class="{ animating: isAnimating }">
          <slot name="whiteboard"></slot>
        </div>

        <!-- Step Card -->
        <div class="step-card" v-if="currentStepData">
          <div class="step-header">
            <span class="step-badge">
              {{ $t('features.lessonExplanationView.stepBadge', { n: currentStep + 1 }) }}
            </span>
            <h3 class="step-title">
              {{ currentStepData.title || $t('features.lessonExplanationView.stepTitle', { n: currentStep + 1 }) }}
            </h3>
          </div>

          <!-- Speech Bubble -->
          <div class="speech-bubble">
            <p>{{ currentStepData.speech }}</p>
          </div>

          <!-- Calculator Hint -->
          <div v-if="currentStepData.calculator" class="calculator-box">
            <div class="calc-header">
              <span class="calc-icon">🔢</span>
              <span class="calc-label">{{ $t('features.lessonExplanationView.calculatorInput') }}</span>
            </div>
            <div class="calc-input">
              <code>{{ currentStepData.calculator }}</code>
            </div>
            <div v-if="currentStepData.result" class="calc-result">
              <span class="equals">{{ $t('features.lessonExplanationView.equals') }}</span>
              <span class="result-value">{{ currentStepData.result }}</span>
            </div>
          </div>

          <!-- Schema Preview (fallback) -->
          <div v-if="currentStepData.schema && !currentStepData.whiteboardActions?.length" class="schema-preview">
            <table>
              <tr v-for="(row, idx) in currentStepData.schema" :key="idx" :class="{ highlighted: row.highlight }">
                <td class="schema-name">{{ row.name }}</td>
                <td class="schema-op">{{ row.operator }}</td>
                <td class="schema-value">{{ row.value }}</td>
              </tr>
            </table>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="step-navigation">
        <button @click="$emit('prev')" :disabled="!canGoPrev" class="nav-btn">
          {{ $t('features.lessonExplanationView.back') }}
        </button>
        <div class="step-dots">
          <span
            v-for="(_, idx) in stepsCount"
            :key="idx"
            class="step-dot"
            :class="{ active: idx === currentStep, completed: idx < currentStep }"
            @click="$emit('goto', idx)"
          ></span>
        </div>
        <button @click="$emit('next')" :disabled="!canGoNext" class="nav-btn">
          {{ $t('features.lessonExplanationView.next') }}
        </button>
      </div>
    </div>

    <!-- No Selection -->
    <div v-else class="no-selection">
      <span class="empty-icon">📝</span>
      <p>{{ $t('features.lessonExplanationView.noSelection') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationViewer - Main view for explanation steps
 */
import { ref, watch } from 'vue'
import type { LessonExplanation, TeachingStep } from '@/composables/useTheoryManagement'

// Props
interface Voice {
  id: string
  name: string
}

interface Props {
  showCreateForm: boolean
  isGenerating: boolean
  explanation: LessonExplanation | null
  currentStepData: TeachingStep | null
  currentStep: number
  stepsCount: number
  progressPercent: number
  canGoPrev: boolean
  canGoNext: boolean
  isSpeaking: boolean
  isAnimating: boolean
  ttsEnabled: boolean
  voices: Voice[]
  selectedVoice: string
  selectedModel: string
  style: string
  generateWithAudio: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showCreateForm: false,
  isGenerating: false,
  stepsCount: 0,
  progressPercent: 0,
  canGoPrev: false,
  canGoNext: false,
  isSpeaking: false,
  isAnimating: false,
  ttsEnabled: false,
  voices: () => [],
  selectedVoice: '',
  selectedModel: 'browser',
  style: 'adhs',
  generateWithAudio: false
})

// Emits
const emit = defineEmits<{
  (e: 'generate', options: { style: string; voice: string; generateWithAudio: boolean }): void
  (e: 'cancel-create'): void
  (e: 'start'): void
  (e: 'next'): void
  (e: 'prev'): void
  (e: 'goto', index: number): void
  (e: 'toggle-tts', speech?: string): void
  (e: 'update:selectedVoice', value: string): void
  (e: 'update:selectedModel', value: string): void
}>()

// Local state for create form
const localStyle = ref(props.style)
const localVoice = ref(props.selectedVoice)
const localGenerateWithAudio = ref(props.generateWithAudio)

// Local state for TTS controls
const localSelectedVoice = ref(props.selectedVoice)
const localSelectedModel = ref(props.selectedModel)

// Computed
const hasExplanation = computed(() => props.explanation !== null)
const hasSteps = computed(() => props.stepsCount > 0)

// Methods
function handleGenerate(): void {
  emit('generate', {
    style: localStyle.value,
    voice: localVoice.value,
    generateWithAudio: localGenerateWithAudio.value
  })
}

// Watchers
watch(() => props.selectedVoice, (val) => {
  localVoice.value = val
  localSelectedVoice.value = val
})

watch(() => props.selectedModel, (val) => {
  localSelectedModel.value = val
})

watch(localSelectedVoice, (val) => {
  emit('update:selectedVoice', val)
})

watch(localSelectedModel, (val) => {
  emit('update:selectedModel', val)
})
</script>

<script lang="ts">
import { computed } from 'vue'
</script>

<style scoped>
.explanation-viewer {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Create Form */
.create-form {
  display: flex;
  flex-direction: column;
  height: 100%;
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

.form-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 1.25rem;
}

.form-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-select {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.generate-btn {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.generate-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

/* Explanation View */
.explanation-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Tutor Header */
.tutor-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.tutor-avatar {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  font-size: 1.5rem;
}

.tutor-info {
  flex: 1;
}

.tutor-name {
  display: block;
  font-weight: 600;
  font-size: 0.9375rem;
  margin-bottom: 0.25rem;
}

.tutor-status {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.tutor-status.speaking {
  color: var(--color-primary);
}

.tutor-controls {
  display: flex;
  gap: 0.5rem;
}

.tts-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  background: var(--color-surface);
}

.tts-btn {
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 1.125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.tts-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* Progress */
.progress-section {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.progress-bar {
  height: 6px;
  background: var(--color-surface-secondary);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.75rem;
}

.start-btn {
  display: block;
  width: 100%;
  padding: 0.75rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
}

.animating-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(var(--color-primary-rgb), 0.1);
  border-radius: 0.375rem;
  color: var(--color-primary);
  font-size: 0.875rem;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(var(--color-primary-rgb), 0.3);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Main Area */
.tutor-main-area {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.whiteboard-container {
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  overflow: hidden;
}

.whiteboard-container.animating {
  border: 2px solid var(--color-primary);
}

/* Step Card */
.step-card {
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.step-badge {
  padding: 0.25rem 0.625rem;
  background: var(--color-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.step-title {
  margin: 0;
  font-size: 1rem;
}

.speech-bubble {
  background: white;
  color: #1a202c;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  position: relative;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.speech-bubble p {
  margin: 0;
  line-height: 1.6;
}

/* Calculator */
.calculator-box {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.calc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #3b82f6;
}

.calc-input code {
  display: block;
  background: rgba(0,0,0,0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 0.5rem;
}

.calc-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.equals {
  color: #3b82f6;
}

.result-value {
  font-size: 1.125rem;
}

/* Schema */
.schema-preview table {
  width: 100%;
  border-collapse: collapse;
}

.schema-preview tr {
  border-bottom: 1px solid var(--color-border);
}

.schema-preview tr.highlighted {
  background: rgba(var(--color-primary-rgb), 0.1);
}

.schema-preview td {
  padding: 0.5rem;
  font-size: 0.875rem;
}

.schema-op {
  text-align: center;
  color: var(--color-text-tertiary);
}

.schema-value {
  text-align: right;
  font-weight: 500;
}

/* Navigation */
.step-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}

.nav-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: var(--color-border);
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.step-dots {
  display: flex;
  gap: 0.5rem;
}

.step-dot {
  width: 10px;
  height: 10px;
  background: var(--color-border);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s;
}

.step-dot:hover {
  background: var(--color-text-tertiary);
}

.step-dot.active {
  background: var(--color-primary);
  transform: scale(1.3);
}

.step-dot.completed {
  background: var(--color-success);
}

/* No Selection */
.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-tertiary);
  padding: 3rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-selection p {
  margin: 0;
  font-size: 0.9375rem;
}
</style>
