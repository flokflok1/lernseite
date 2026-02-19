<!--
  ExplanationViewer - Main viewer for lesson explanation steps
-->

<template>
  <div class="explanation-viewer">
    <!-- Create Form -->
    <ExplanationCreateForm
      v-if="showCreateForm"
      :is-generating="isGenerating"
      :voices="voices"
      :selected-voice="selectedVoice"
      :style="style"
      :generate-with-audio="generateWithAudio"
      @generate="$emit('generate', $event)"
      @cancel-create="$emit('cancel-create')"
    />

    <!-- Explanation View -->
    <div v-else-if="hasExplanation && hasSteps" class="explanation-view">
      <!-- Tutor Header -->
      <div class="tutor-header">
        <div class="tutor-avatar">
          <span class="avatar-emoji">&#x1F468;&#x200D;&#x1F3EB;</span>
        </div>
        <div class="tutor-info">
          <span class="tutor-name">
            {{ explanation.title || $t('lessonExplanationView.tutorExplains') }}
          </span>
          <span class="tutor-status" :class="{ speaking: isSpeaking }">
            {{ isSpeaking
                ? $t('lessonExplanationView.speaking')
                : $t('lessonExplanationView.ready')
            }}
          </span>
        </div>
        <div class="tutor-controls">
          <select v-model="localSelectedVoice" class="tts-select" :title="$t('lessonExplanationView.voiceLabel')">
            <option v-for="voice in voices" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
          <select v-model="localSelectedModel" class="tts-select" :title="$t('lessonExplanationView.ttsModel')">
            <option value="browser">{{ $t('lessonExplanationView.browserFree') }}</option>
            <option value="tts-1">TTS-1</option>
            <option value="tts-1-hd">TTS-1-HD</option>
          </select>
          <button @click="$emit('toggle-tts', currentStepData?.speech)" class="tts-btn" :class="{ active: ttsEnabled }">
            {{ ttsEnabled ? '&#x1F50A;' : '&#x1F507;' }}
          </button>
        </div>
      </div>

      <!-- Progress -->
      <div class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
        <span class="progress-text">
          {{ $t('lessonExplanationView.stepProgress', { current: currentStep + 1, total: stepsCount }) }}
        </span>
        <button
          v-if="currentStep === 0 && !isSpeaking && !isAnimating"
          @click="$emit('start')"
          class="start-btn"
        >
          {{ $t('lessonExplanationView.start') }}
        </button>
        <div v-if="isAnimating" class="animating-indicator">
          <span class="spinner-small"></span>
          <span>{{ $t('lessonExplanationView.drawing') }}</span>
        </div>
      </div>

      <!-- Main Area: Whiteboard + Step Card -->
      <div class="tutor-main-area">
        <!-- Whiteboard (if step has whiteboard actions) -->
        <div v-if="currentStepData?.whiteboardActions?.length" class="whiteboard-container" :class="{ animating: isAnimating }">
          <slot name="whiteboard"></slot>
        </div>

        <!-- Step Card -->
        <ExplanationStepCard
          :step="currentStepData"
          :step-number="currentStep + 1"
        />
      </div>

      <!-- Navigation -->
      <div class="step-navigation">
        <button @click="$emit('prev')" :disabled="!canGoPrev" class="nav-btn">
          {{ $t('lessonExplanationView.back') }}
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
          {{ $t('lessonExplanationView.next') }}
        </button>
      </div>
    </div>

    <!-- No Selection -->
    <div v-else class="no-selection">
      <span class="empty-icon">&#x1F4DD;</span>
      <p>{{ $t('lessonExplanationView.noSelection') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationViewer - Main view for explanation steps.
 * Orchestrates create form, step display, and navigation.
 */
import { ref, computed, watch } from 'vue'
import type { LessonExplanation, TeachingStep } from '@/application/composables/learning/useTheoryManagement'
import ExplanationCreateForm from './ExplanationCreateForm.vue'
import ExplanationStepCard from './ExplanationStepCard.vue'

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

// Local state for TTS controls
const localSelectedVoice = ref(props.selectedVoice)
const localSelectedModel = ref(props.selectedModel)

// Computed
const hasExplanation = computed(() => props.explanation !== null)
const hasSteps = computed(() => props.stepsCount > 0)

// Watchers - sync props to local state
watch(() => props.selectedVoice, (val) => {
  localSelectedVoice.value = val
})

watch(() => props.selectedModel, (val) => {
  localSelectedModel.value = val
})

// Watchers - emit changes from local state
watch(localSelectedVoice, (val) => {
  emit('update:selectedVoice', val)
})

watch(localSelectedModel, (val) => {
  emit('update:selectedModel', val)
})
</script>

<style scoped>
.explanation-viewer {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
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
