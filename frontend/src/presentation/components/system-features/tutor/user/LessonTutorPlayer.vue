<template>
  <div class="lesson-tutor-player">
    <!-- TTS Error Banner -->
    <div v-if="ttsError" class="tts-error-banner">
      <span class="error-icon">!</span>
      <span class="error-text">{{ ttsError }}</span>
      <button @click="ttsError = null" class="error-close">×</button>
    </div>

    <!-- Two Column Layout: List + Content -->
    <div class="tutor-layout">
      <!-- Left: Explanation List -->
      <TutorExplanationList
        :explanations="explanationList"
        :selected-id="selectedExplanationId"
        :is-loading="isLoadingList"
        :editing-explanation="editingExplanation"
        :edit-title="editTitle"
        @new-explanation="showNewForm = true"
        @select="selectExplanation"
        @edit="startEditTitle"
        @delete="confirmDelete"
        @save-title="saveTitle"
        @cancel-edit="cancelEdit"
      />

      <!-- Right: Content Area -->
      <div class="content-panel">
        <!-- Loading State -->
        <div v-if="isGenerating" class="generating-state">
          <div class="generating-spinner"></div>
          <p>{{ $t('lesson.tutorPlayer.generatingExplanation') }}</p>
          <p class="generating-hint">{{ $t('lesson.tutorPlayer.generationTime') }}</p>
        </div>

        <!-- New Explanation Form -->
        <TutorGenerationForm
          v-else-if="showNewForm"
          :selected-style="selectedStyle"
          :selected-voice="selectedVoice"
          :generate-with-tts="generateWithTTS"
          :has-explanations="explanationList.length > 0"
          @generate="handleGenerate"
          @cancel="showNewForm = false"
        />

        <!-- No Selection (has list but nothing selected) -->
        <div v-else-if="!hasContent && explanationList.length > 0" class="select-prompt">
          <p>{{ $t('lesson.tutorPlayer.selectExplanation') }}</p>
          <p class="or-text">{{ $t('common.or') }}</p>
          <button @click="showNewForm = true" class="new-explanation-btn">
            {{ $t('lesson.tutorPlayer.createNew') }}
          </button>
        </div>

        <!-- Explanation View -->
        <TutorStepPlayer
          v-else-if="hasContent"
          :lesson-title="lessonTitle"
          :current-step="currentStep"
          :total-steps="steps.length"
          :current-step-data="currentStepData"
          :has-whiteboard-actions="hasWhiteboardActions"
          :tts-enabled="ttsEnabled"
          :is-speaking="isSpeaking"
          :selected-voice="selectedVoice"
          :selected-tts-model="selectedTTSModel"
          :is-animating-whiteboard="isAnimatingWhiteboard"
          @toggle-tts="toggleTTS"
          @start="startExplanation"
          @prev="prevStep"
          @next="nextStep"
          @finish="finishTutorial"
          @restart="restartTutorial"
          @back-to-theory="$emit('back-to-theory')"
          @practice="$emit('practice')"
          @whiteboard-ref="whiteboardRef = $event"
          @whiteboard-action-complete="() => {}"
        />

        <!-- Delete Confirmation Modal -->
        <div v-if="deleteConfirm" class="delete-modal">
          <div class="delete-modal-content">
            <h4>{{ $t('lesson.tutorPlayer.deleteConfirmTitle') }}</h4>
            <p>{{ deleteConfirm.title }}</p>
            <div class="modal-buttons">
              <button @click="executeDelete" class="confirm-delete-btn">
                {{ $t('common.delete') }}
              </button>
              <button @click="cancelDelete" class="cancel-delete-btn">
                {{ $t('common.cancel') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * LessonTutorPlayer (Orchestrator)
 * =================================
 * Coordinates sub-components for interactive tutor explanations
 * Refactored from 1692 LOC to ~230 LOC (-86%)
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  TutorExplanationList,
  TutorGenerationForm,
  TutorStepPlayer,
  useTutorPlayer
} from './lesson-player'

const { t } = useI18n()

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  lessonId: string
  lessonTitle: string
  chapterTitle?: string
  courseTitle?: string
  lmType?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'completed'): void
  (e: 'back-to-theory'): void
  (e: 'practice'): void
}>()

// ============================================================================
// Composable
// ============================================================================

const {
  // State - Steps & Navigation
  currentStep,
  hasContent,
  steps,
  currentStepData,
  hasWhiteboardActions,

  // State - Explanation List
  explanationList,
  selectedExplanationId,
  isLoadingList,
  showNewForm,

  // State - Generation
  isGenerating,
  selectedStyle,
  selectedVoice,
  generateWithTTS,

  // State - Edit/Delete
  editingExplanation,
  editTitle,
  deleteConfirm,

  // State - TTS
  ttsEnabled,
  isSpeaking,
  selectedTTSModel,
  ttsError,

  // State - Whiteboard
  whiteboardRef,
  isAnimatingWhiteboard,

  // Methods - Explanation List
  loadExplanationList,
  selectExplanation,
  generateSteps,

  // Methods - Edit/Delete
  startEditTitle,
  cancelEdit,
  saveTitle,
  confirmDelete,
  executeDelete,
  cancelDelete,

  // Methods - Navigation
  nextStep,
  prevStep,
  restartTutorial,

  // Methods - TTS
  toggleTTS,
  startExplanation
} = useTutorPlayer(props.lessonId, {
  lessonTitle: props.lessonTitle,
  chapterTitle: props.chapterTitle,
  courseTitle: props.courseTitle,
  lmType: props.lmType
})

// ============================================================================
// Event Handlers
// ============================================================================

function finishTutorial() {
  emit('completed')
}

function handleGenerate(options: { style: string; voice: string; generateWithTTS: boolean }) {
  selectedStyle.value = options.style
  selectedVoice.value = options.voice
  generateWithTTS.value = options.generateWithTTS
  generateSteps()
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await loadExplanationList()
})
</script>

<style scoped>
/* Lesson Tutor Player Container */
.lesson-tutor-player {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  height: 100%;
  overflow: hidden;
}

/* Two Column Layout */
.tutor-layout {
  display: flex;
  gap: 1rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Right Panel - Content */
.content-panel {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}

/* TTS Error Banner */
.tts-error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
}

.tts-error-banner .error-icon {
  font-size: 1.25rem;
  color: #ef4444;
  font-weight: bold;
}

.tts-error-banner .error-text {
  flex: 1;
  color: #ef4444;
  font-size: 0.875rem;
}

.tts-error-banner .error-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #ef4444;
  font-size: 1.5rem;
  cursor: pointer;
  border-radius: 4px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tts-error-banner .error-close:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Generating State */
.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.generating-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border, #334155);
  border-top-color: var(--color-primary, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generating-hint {
  color: var(--color-text-tertiary, #64748b);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* Select Prompt */
.select-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-tertiary, #64748b);
}

.select-prompt p {
  margin: 0;
  font-size: 0.9375rem;
}

.or-text {
  margin: 0.75rem 0 !important;
  font-size: 0.75rem;
}

.new-explanation-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px dashed var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
  transition: all 0.2s;
}

.new-explanation-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-primary, #6366f1);
}

/* Delete Modal */
.delete-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.delete-modal-content {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}

.delete-modal-content h4 {
  margin: 0 0 0.5rem;
  color: var(--color-text-primary, #f1f5f9);
}

.delete-modal-content p {
  margin: 0 0 1.5rem;
  color: var(--color-text-secondary, #94a3b8);
}

.modal-buttons {
  display: flex;
  gap: 0.75rem;
}

.confirm-delete-btn {
  flex: 1;
  padding: 0.75rem;
  background: #ef4444;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-delete-btn:hover {
  background: #dc2626;
}

.cancel-delete-btn {
  flex: 1;
  padding: 0.75rem;
  background: var(--color-surface-secondary, #0f172a);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-delete-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-text-primary, #f1f5f9);
}
</style>
