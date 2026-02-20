<!--
  LessonExplanationView - Orchestrator for Lesson Explanation Management
  Coordinates ExplanationList, ExplanationViewer, and ExplanationSettings
-->

<template>
  <div class="lesson-explanation-view">
    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span class="error-icon">⚠️</span>
      <span class="error-message">{{ error }}</span>
      <button @click="clearError" class="error-close">×</button>
    </div>

    <!-- Three Column Layout -->
    <div class="explanation-layout">
      <!-- LEFT: Explanation List -->
      <ExplanationList
        :explanations="explanations"
        :is-loading="isLoading"
        :selected-id="selectedExplanationId"
        @select="handleSelectExplanation"
        @delete="handleDeleteExplanation"
        @create="handleShowCreateForm"
        @refresh="handleRefresh"
      />

      <!-- MIDDLE: Viewer -->
      <ExplanationViewer
        :show-create-form="showCreateForm"
        :is-generating="isGenerating"
        :explanation="currentExplanation"
        :current-step-data="currentStepData"
        :current-step="currentStep"
        :steps-count="stepsCount"
        :progress-percent="progressPercent"
        :can-go-prev="canGoPrev"
        :can-go-next="canGoNext"
        :is-speaking="isSpeaking"
        :is-animating="isAnimating"
        :tts-enabled="ttsEnabled"
        :voices="availableVoices"
        :selected-voice="selectedVoice"
        :selected-model="selectedModel"
        :style="explanationStyle"
        :generate-with-audio="generateWithAudio"
        @generate="handleGenerate"
        @cancel-create="showCreateForm = false"
        @start="handleStart"
        @next="handleNext"
        @prev="handlePrev"
        @goto="handleGoToStep"
        @toggle-tts="handleToggleTTS"
        @update:selected-voice="selectedVoice = $event"
        @update:selected-model="selectedModel = $event"
      >
        <!-- Whiteboard Slot -->
        <template #whiteboard>
          <InteractiveWhiteboard
            v-if="currentStepData && currentStepData.whiteboard_data"
            :whiteboard-data="currentStepData.whiteboard_data"
            :is-animating="isAnimating"
            @animation-complete="isAnimating = false"
          />
        </template>
      </ExplanationViewer>

      <!-- RIGHT: Settings -->
      <ExplanationSettings
        :auto-play="autoPlay"
        :playback-speed="playbackSpeed"
        :explanation="currentExplanation"
        :steps-count="stepsCount"
        @update:auto-play="autoPlay = $event"
        @update:playback-speed="playbackSpeed = $event"
        @regenerate="handleRegenerate"
        @download-pdf="handleDownloadPDF"
        @share="handleShare"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * LessonExplanationView - Main orchestrator component
 * Manages lesson explanations with step-by-step teaching
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTTS } from '@/application/composables/system/useTTS'
import type { Course, Lesson } from '@/presentation/components/panel/editor/ai/explanation-generation/types/explanation.types'
import type { LessonExplanation as _LessonExplanation } from '@/application/composables/learning/useTheoryManagement'
import InteractiveWhiteboard from '@/presentation/components/public/system-features/tutor/user/InteractiveWhiteboard.vue'
import {
  ExplanationList,
  ExplanationViewer,
  ExplanationSettings,
  useExplanationManager,
  type GenerateOptions
} from './index'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  course: Course
  lesson: Lesson
}

const props = defineProps<Props>()

// =============================================================================
// Composables
// =============================================================================

const explanationMgr = useExplanationManager()
const tts = useTTS()

// =============================================================================
// Local State
// =============================================================================

// UI State
const showCreateForm = ref(false)
const isAnimating = ref(false)

// TTS Settings
const autoPlay = ref(false)
const playbackSpeed = ref('1')
const selectedVoice = ref('default')
const selectedModel = ref('browser')

// Generation Options
const explanationStyle = ref('detailed')
const generateWithAudio = ref(true)

// =============================================================================
// Computed - From Manager
// =============================================================================

const explanations = computed(() => explanationMgr.explanations.value)
const isLoading = computed(() => explanationMgr.isLoading.value)
const isGenerating = computed(() => explanationMgr.isGenerating.value)
const error = computed(() => explanationMgr.error.value)

const selectedExplanationId = computed(() => explanationMgr.selectedExplanationId.value)
const currentExplanation = computed(() => explanationMgr.currentExplanation.value)
const currentStepData = computed(() => explanationMgr.currentStepData.value)
const currentStep = computed(() => explanationMgr.currentStep.value)
const stepsCount = computed(() => explanationMgr.steps.value.length)
const progressPercent = computed(() => explanationMgr.progressPercent.value)
const canGoPrev = computed(() => explanationMgr.canGoPrev.value)
const canGoNext = computed(() => explanationMgr.canGoNext.value)

// =============================================================================
// Computed - TTS
// =============================================================================

const availableVoices = computed(() => tts.availableVoices.value)
const isSpeaking = computed(() => tts.isSpeaking.value)
const ttsEnabled = computed(() => tts.isEnabled.value)

// =============================================================================
// Methods - Event Handlers
// =============================================================================

async function handleSelectExplanation(explanationId: string): Promise<void> {
  try {
    await explanationMgr.selectExplanation(explanationId)
    showCreateForm.value = false
  } catch (err) {
    console.error('Failed to select explanation:', err)
  }
}

async function handleDeleteExplanation(explanationId: string): Promise<void> {
  await explanationMgr.deleteExplanation(explanationId)
}

async function handleRefresh(): Promise<void> {
  if (props.lesson?.lesson_id) {
    await explanationMgr.loadExplanations(props.lesson.lesson_id)
  }
}

function handleShowCreateForm(): void {
  showCreateForm.value = true
}

async function handleGenerate(options: { style: string; voice: string; generateWithAudio: boolean }): Promise<void> {
  if (!props.lesson?.lesson_id) return

  try {
    const generateOpts: GenerateOptions = {
      lessonId: props.lesson.lesson_id,
      style: options.style,
      generateTTS: options.generateWithAudio,
      voice: options.voice
    }

    const explanationId = await explanationMgr.generateExplanation(generateOpts)

    if (explanationId) {
      showCreateForm.value = false
      await explanationMgr.selectExplanation(explanationId)
    }
  } catch (err) {
    console.error('Generation failed:', err)
  }
}

async function handleRegenerate(): Promise<void> {
  if (!currentExplanation.value || !props.lesson?.lesson_id) return

  const confirmed = confirm(t('lessonExplanationView.confirmRegenerate'))
  if (!confirmed) return

  try {
    await explanationMgr.deleteExplanation(currentExplanation.value.explanationId)
    handleShowCreateForm()
  } catch (err) {
    console.error('Regenerate failed:', err)
  }
}

async function handleDownloadPDF(): Promise<void> {
  if (!currentExplanation.value) return
  console.log('Download PDF:', currentExplanation.value.explanationId)
  // TODO: Implement PDF download
}

async function handleShare(): Promise<void> {
  if (!currentExplanation.value) return
  console.log('Share:', currentExplanation.value.explanationId)
  // TODO: Implement share functionality
}

// =============================================================================
// Methods - Navigation
// =============================================================================

function handleStart(): void {
  explanationMgr.resetStep()
  if (autoPlay.value && currentStepData.value?.speech) {
    handleToggleTTS(currentStepData.value.speech)
  }
  if (currentStepData.value?.whiteboard_data) {
    isAnimating.value = true
  }
}

function handleNext(): void {
  explanationMgr.nextStep()
}

function handlePrev(): void {
  explanationMgr.prevStep()
}

function handleGoToStep(index: number): void {
  explanationMgr.goToStep(index)
}

// =============================================================================
// Methods - TTS
// =============================================================================

function handleToggleTTS(speech?: string): void {
  if (isSpeaking.value) {
    tts.stop()
  } else if (speech) {
    tts.speak(speech, {
      rate: parseFloat(playbackSpeed.value),
      voice: selectedVoice.value
    })
  }
}

function clearError(): void {
  explanationMgr.clearError()
}

// =============================================================================
// Watchers
// =============================================================================

// Auto-play TTS when step changes
watch(currentStep, (newStep, oldStep) => {
  if (newStep !== oldStep && autoPlay.value && currentStepData.value?.speech) {
    handleToggleTTS(currentStepData.value.speech)
  }
  if (currentStepData.value?.whiteboard_data) {
    isAnimating.value = true
  }
})

// Stop TTS when leaving component
watch(() => showCreateForm.value, (newVal) => {
  if (newVal && isSpeaking.value) {
    tts.stop()
  }
})

// =============================================================================
// Lifecycle
// =============================================================================

onMounted(async () => {
  if (props.lesson?.lesson_id) {
    await explanationMgr.loadExplanations(props.lesson.lesson_id)
  }
})
</script>

<style scoped>
.lesson-explanation-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-background);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--color-error-light);
  border-bottom: 1px solid var(--color-error);
  color: var(--color-error-dark);
}

.error-icon {
  font-size: 1.25rem;
}

.error-message {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-error-dark);
  opacity: 0.7;
  transition: opacity 0.15s;
}

.error-close:hover {
  opacity: 1;
}

/* Three Column Layout */
.explanation-layout {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 0;
  flex: 1;
  min-height: 0;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 1400px) {
  .explanation-layout {
    grid-template-columns: 260px 1fr 300px;
  }
}

@media (max-width: 1200px) {
  .explanation-layout {
    grid-template-columns: 240px 1fr;
  }
}

@media (max-width: 768px) {
  .explanation-layout {
    grid-template-columns: 1fr;
  }
}
</style>
