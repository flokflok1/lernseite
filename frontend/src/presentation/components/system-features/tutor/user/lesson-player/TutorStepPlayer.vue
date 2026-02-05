<template>
  <div class="step-player">
    <!-- Tutor Header -->
    <div class="tutor-header">
      <div class="tutor-avatar">
        <span class="avatar-emoji">{{ $t('lesson.tutorPlayer.teacherIcon') }}</span>
      </div>
      <div class="tutor-info">
        <span class="tutor-name">{{ $t('lesson.tutorPlayer.tutorExplains', { lesson: lessonTitle }) }}</span>
        <span class="tutor-status" :class="{ speaking: isSpeaking }">
          {{ isSpeaking ? $t('lesson.tutorPlayer.speaking') : $t('lesson.tutorPlayer.ready') }}
        </span>
      </div>
      <div class="tutor-controls">
        <!-- Voice Select -->
        <select v-model="selectedVoiceLocal" class="tts-select voice-select" :title="$t('lesson.tutorPlayer.voice')">
          <option value="nova">{{ $t('lesson.tutorPlayer.voices.nova') }}</option>
          <option value="alloy">{{ $t('lesson.tutorPlayer.voices.alloy') }}</option>
          <option value="echo">{{ $t('lesson.tutorPlayer.voices.echo') }}</option>
          <option value="onyx">{{ $t('lesson.tutorPlayer.voices.onyx') }}</option>
          <option value="shimmer">{{ $t('lesson.tutorPlayer.voices.shimmer') }}</option>
        </select>
        <!-- Model Select -->
        <select v-model="selectedTTSModelLocal" class="tts-select model-select" :title="$t('lesson.tutorPlayer.ttsModel')">
          <option value="browser">{{ $t('lesson.tutorPlayer.browserFree') }}</option>
          <option value="tts-1">{{ $t('lesson.tutorPlayer.tts1Standard') }}</option>
          <option value="tts-1-hd">{{ $t('lesson.tutorPlayer.tts1HD') }}</option>
        </select>
        <button @click="$emit('toggle-tts')" class="tts-btn" :class="{ active: ttsEnabled }" :title="$t('lesson.tutorPlayer.speechOutput')">
          {{ ttsEnabled ? $t('lesson.tutorPlayer.audioOn') : $t('lesson.tutorPlayer.audioOff') }}
        </button>
      </div>
    </div>

    <!-- Progress -->
    <div class="progress-section">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"></div>
      </div>
      <span class="progress-text">{{ $t('lesson.tutorPlayer.stepProgress', { current: currentStep + 1, total: totalSteps }) }}</span>
      <button
        v-if="currentStep === 0 && !isSpeaking && !isAnimatingWhiteboard"
        @click="$emit('start')"
        class="start-explanation-btn"
      >
        {{ $t('lesson.tutorPlayer.startExplanation') }}
      </button>
      <div v-if="isAnimatingWhiteboard" class="animating-indicator">
        <span class="spinner"></span>
        <span>{{ $t('lesson.tutorPlayer.drawingOnWhiteboard') }}</span>
      </div>
    </div>

    <!-- Whiteboard + Step Card Layout -->
    <div class="tutor-main-area">
      <!-- Interactive Whiteboard -->
      <div v-if="hasWhiteboardActions" class="whiteboard-container" :class="{ animating: isAnimatingWhiteboard }">
        <div class="whiteboard-label">{{ $t('lesson.tutorPlayer.whiteboard') }}</div>
        <InteractiveWhiteboard
          :ref="(el: any) => $emit('whiteboard-ref', el)"
          :width="480"
          :height="320"
          :show-controls="true"
          background-color="#1e293b"
          text-color="#f1f5f9"
          title=""
          @action-complete="$emit('whiteboard-action-complete', $event)"
        />
      </div>

      <!-- Current Step Card -->
      <div class="step-card" v-if="currentStepData">
        <div class="step-header">
          <span class="step-badge">{{ $t('lesson.tutorPlayer.step', { number: currentStep + 1 }) }}</span>
          <h3 class="step-title">{{ currentStepData.title }}</h3>
        </div>

        <!-- Speech Bubble -->
        <div class="speech-bubble">
          <p>{{ currentStepData.speech }}</p>
        </div>

        <!-- Calculator Hint -->
        <div v-if="currentStepData.calculator" class="calculator-box">
          <div class="calc-header">
            <span class="calc-icon">{{ $t('lesson.tutorPlayer.calculatorIcon') }}</span>
            <span class="calc-label">{{ $t('lesson.tutorPlayer.calculatorHint') }}</span>
          </div>
          <div class="calc-input">
            <code>{{ currentStepData.calculator }}</code>
          </div>
          <div v-if="currentStepData.result" class="calc-result">
            <span class="equals">=</span>
            <span class="result-value">{{ currentStepData.result }}</span>
          </div>
        </div>

        <!-- Schema Preview -->
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
    <div class="nav-buttons">
      <button @click="$emit('prev')" class="nav-btn nav-prev" :disabled="currentStep === 0">
        {{ $t('lesson.tutorPlayer.back') }}
      </button>
      <button v-if="currentStep < totalSteps - 1" @click="$emit('next')" class="nav-btn nav-next">
        {{ $t('lesson.tutorPlayer.next') }}
      </button>
      <button v-else @click="$emit('finish')" class="nav-btn nav-finish">
        {{ $t('lesson.tutorPlayer.done') }}
      </button>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button @click="$emit('back-to-theory')" class="action-btn">
        {{ $t('lesson.tutorPlayer.backToTheory') }}
      </button>
      <button @click="$emit('restart')" class="action-btn">
        {{ $t('lesson.tutorPlayer.restart') }}
      </button>
      <button @click="$emit('practice')" class="action-btn primary">
        {{ $t('lesson.tutorPlayer.practiceNow') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorStepPlayer Component
 * ==========================
 * Main player for tutor explanations (header, whiteboard, step card, navigation)
 */
import { ref, watch } from 'vue'
import InteractiveWhiteboard from '../InteractiveWhiteboard.vue'
import type { TutorialStep } from './composables/useTutorPlayer'

interface Props {
  lessonTitle: string
  currentStep: number
  totalSteps: number
  currentStepData: TutorialStep | undefined
  hasWhiteboardActions: boolean
  ttsEnabled: boolean
  isSpeaking: boolean
  selectedVoice: string
  selectedTTSModel: string
  isAnimatingWhiteboard: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'toggle-tts': []
  'start': []
  'prev': []
  'next': []
  'finish': []
  'restart': []
  'back-to-theory': []
  'practice': []
  'whiteboard-ref': [ref: any]
  'whiteboard-action-complete': [action: any]
}>()

// Local state synced with props for controls
const selectedVoiceLocal = ref(props.selectedVoice)
const selectedTTSModelLocal = ref(props.selectedTTSModel)

// Watch for external changes
watch(() => props.selectedVoice, (newVal) => {
  selectedVoiceLocal.value = newVal
})

watch(() => props.selectedTTSModel, (newVal) => {
  selectedTTSModelLocal.value = newVal
})

// Emit changes to parent
watch(selectedVoiceLocal, (_newVal) => {
  // Parent will handle this via v-model in orchestrator
})

watch(selectedTTSModelLocal, (_newVal) => {
  // Parent will handle this via v-model in orchestrator
})
</script>

<style scoped>
/* Step Player Container */
.step-player {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Tutor Header */
.tutor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
}

.tutor-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: white;
  flex-shrink: 0;
}

.tutor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tutor-name {
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.9375rem;
}

.tutor-status {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  margin-top: 0.25rem;
}

.tutor-status.speaking {
  color: #10b981;
}

.tutor-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tts-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tts-select:hover {
  border-color: var(--color-primary, #6366f1);
}

.tts-select:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
}

.voice-select {
  min-width: 90px;
}

.model-select {
  min-width: 140px;
}

.tts-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: transparent;
  font-size: 0.75rem;
  cursor: pointer;
  color: var(--color-text-secondary, #94a3b8);
  transition: all 0.2s;
}

.tts-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-text-primary, #f1f5f9);
}

.tts-btn.active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #10b981;
}

/* Progress */
.progress-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface-secondary, #0f172a);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  white-space: nowrap;
}

.start-explanation-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.start-explanation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.animating-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: #8b5cf6;
}

.animating-indicator .spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Tutor Main Area */
.tutor-main-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 900px) {
  .tutor-main-area {
    flex-direction: row;
    align-items: flex-start;
  }

  .tutor-main-area .whiteboard-container {
    flex: 0 0 500px;
  }

  .tutor-main-area .step-card {
    flex: 1;
  }
}

/* Whiteboard Container */
.whiteboard-container {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.whiteboard-container.animating {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

.whiteboard-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Step Card */
.step-card {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  overflow: hidden;
}

.step-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #334155);
  background: var(--color-surface-secondary, #0f172a);
}

.step-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.step-title {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary, #f1f5f9);
}

/* Speech Bubble */
.speech-bubble {
  padding: 1.25rem;
  background: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366f1;
  margin: 1rem;
  border-radius: 0 0.5rem 0.5rem 0;
}

.speech-bubble p {
  margin: 0;
  color: var(--color-text-primary, #f1f5f9);
  line-height: 1.6;
}

/* Calculator Box */
.calculator-box {
  margin: 0 1rem 1rem;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.5rem;
}

.calc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.calc-icon {
  font-size: 1rem;
}

.calc-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.calc-input {
  background: rgba(0, 0, 0, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

.calc-input code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 1.125rem;
  color: #10b981;
}

.calc-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-left: 0.5rem;
}

.equals {
  color: var(--color-text-tertiary, #64748b);
  font-size: 1.25rem;
}

.result-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #10b981;
}

/* Schema Preview */
.schema-preview {
  margin: 0 1rem 1rem;
  overflow-x: auto;
}

.schema-preview table {
  width: 100%;
  border-collapse: collapse;
}

.schema-preview tr {
  border-bottom: 1px solid var(--color-border, #334155);
}

.schema-preview tr.highlighted {
  background: rgba(139, 92, 246, 0.1);
}

.schema-preview tr.highlighted td {
  color: #8b5cf6;
  font-weight: 600;
}

.schema-preview td {
  padding: 0.5rem 0.75rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
}

.schema-name {
  text-align: left;
}

.schema-op {
  text-align: center;
  width: 30px;
}

.schema-value {
  text-align: right;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* Navigation */
.nav-buttons {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
}

.nav-btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-prev {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  color: var(--color-text-secondary, #94a3b8);
}

.nav-prev:hover:not(:disabled) {
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
}

.nav-prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-next {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.nav-next:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.nav-finish {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.nav-finish:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  padding-top: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
  border-color: var(--color-primary, #6366f1);
}

.action-btn.primary {
  background: var(--color-primary, #6366f1);
  border-color: var(--color-primary, #6366f1);
  color: white;
}

.action-btn.primary:hover {
  filter: brightness(1.1);
}
</style>
