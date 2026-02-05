<!--
  ExplanationGenerationContainer - Lesson Explanation Management System

  Main orchestrator for explanation generation and management.
  Coordinates 3-column layout: list | view/create | settings.
  Integrated into course-editor system (both manual and AI editors).
-->

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useExplanationGeneration } from './composables/useExplanationGeneration'
import ExplanationListPanel from './panels/ExplanationListPanel.vue'
import ExplanationViewPanel from './panels/ExplanationViewPanel.vue'
import ExplanationSettingsPanel from './panels/ExplanationSettingsPanel.vue'
import type { Lesson, Course, ExplanationStyle } from './types/explanation.types'

interface Props {
  lesson: Lesson | null
  course: Course | null
}

interface Emits {
  (e: 'generated', explanationId: string): void
  (e: 'deleted', explanationId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Composables
const explanationMgr = useExplanationGeneration()

// Local state
const showCreateForm = ref(false)
const localError = ref<string | null>(null)
const currentStep = ref(0)
const autoPlay = ref(false)
const playbackSpeed = ref('1')

// Computed shortcuts
const {
  explanations,
  selectedExplanationId,
  selectedExplanation,
  isLoading,
  isGenerating,
  error,
  currentExplanationTitle: _currentExplanationTitle,
  currentExplanationStyle: _currentExplanationStyle
} = explanationMgr

// Combined error (local + from composable)
const displayError = ref('')

// Step-related computed
const stepsCount = ref(0)
const progressPercent = ref(0)
const canGoPrev = ref(false)
const canGoNext = ref(false)
const currentStepData = ref<any>(null)

// Methods
const loadExplanations = async () => {
  if (props.lesson?.lesson_id) {
    await explanationMgr.loadExplanations(props.lesson.lesson_id)
  }
}

const onSelectExplanation = async (explanationId: string) => {
  await explanationMgr.selectExplanation(explanationId)
  showCreateForm.value = false
  currentStep.value = 0
}

const onDeleteExplanation = async (explanationId: string) => {
  const success = await explanationMgr.deleteExplanation(explanationId)
  if (success) {
    emit('deleted', explanationId)
  }
}

const handleGenerateExplanation = async (
  style: ExplanationStyle,
  withAudio: boolean
) => {
  if (!props.lesson?.lesson_id) return

  const newExplanationId = await explanationMgr.generateExplanation(
    props.lesson.lesson_id,
    style,
    withAudio
  )

  if (newExplanationId) {
    showCreateForm.value = false
    await explanationMgr.selectExplanation(newExplanationId)
    emit('generated', newExplanationId)
  }
}

const handleRegenerateExplanation = () => {
  if (selectedExplanationId.value) {
    showCreateForm.value = true
  }
}

const handleStart = () => {
  currentStep.value = 0
}

const handleNext = () => {
  if (canGoNext.value) {
    currentStep.value++
  }
}

const handlePrev = () => {
  if (canGoPrev.value) {
    currentStep.value--
  }
}

const handleGoToStep = (index: number) => {
  currentStep.value = index
}

const handleDownloadPDF = () => {
  console.log('Download PDF:', selectedExplanationId.value)
  // TODO: Implement PDF download
}

const handleShare = () => {
  console.log('Share:', selectedExplanationId.value)
  // TODO: Implement share functionality
}

const clearError = () => {
  displayError.value = ''
  localError.value = null
}

// Update step data when explanation or step changes
const updateStepData = () => {
  if (!selectedExplanation.value) {
    stepsCount.value = 0
    currentStepData.value = null
    canGoPrev.value = false
    canGoNext.value = false
    progressPercent.value = 0
    return
  }

  const steps = selectedExplanation.value.steps
  stepsCount.value = steps.length

  if (currentStep.value < steps.length) {
    currentStepData.value = steps[currentStep.value]
  } else {
    currentStepData.value = null
  }

  progressPercent.value = steps.length > 0 ? Math.round(((currentStep.value + 1) / steps.length) * 100) : 0
  canGoPrev.value = currentStep.value > 0
  canGoNext.value = currentStep.value < steps.length - 1
}

// Watchers
watch(() => props.lesson, async (newLesson) => {
  explanationMgr.reset()
  showCreateForm.value = false
  currentStep.value = 0

  if (newLesson?.lesson_id) {
    await loadExplanations()
  }
}, { immediate: true })

watch(() => error.value, (newError) => {
  displayError.value = newError || ''
})

watch(() => selectedExplanation.value, () => {
  currentStep.value = 0
  updateStepData()
})

watch(() => currentStep.value, () => {
  updateStepData()
})

// Lifecycle
onMounted(() => {
  loadExplanations()
})
</script>

<template>
  <div class="explanation-generation-container">
    <!-- Header with Lesson/Course Info -->
    <div class="container-header">
      <div class="header-icon">📚</div>
      <div class="header-info">
        <h2>{{ $t('course-editor.explanation.container.title') }}</h2>
        <p v-if="course && lesson">{{ course.title }} • {{ lesson.title }}</p>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ explanations.length }}</span>
          <span class="stat-label">{{ $t('course-editor.explanation.container.available') }}</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ selectedExplanationId ? 1 : 0 }}</span>
          <span class="stat-label">{{ $t('course-editor.explanation.container.selected') }}</span>
        </div>
      </div>
    </div>

    <!-- Main 3-Column Layout -->
    <div class="main-layout">
      <!-- Left: Explanation List -->
      <ExplanationListPanel
        :explanations="explanations"
        :is-loading="isLoading"
        :selected-id="selectedExplanationId"
        @select="onSelectExplanation"
        @delete="onDeleteExplanation"
        @refresh="loadExplanations"
        @create="showCreateForm = true"
      />

      <!-- Middle: View/Generator Panel -->
      <ExplanationViewPanel
        :explanation="selectedExplanation"
        :show-create-form="showCreateForm"
        :is-generating="isGenerating"
        :current-step="currentStep"
        :steps-count="stepsCount"
        @generate="handleGenerateExplanation"
        @cancel-create="showCreateForm = false"
        @start="handleStart"
        @next="handleNext"
        @prev="handlePrev"
        @goto="handleGoToStep"
      >
        <!-- Whiteboard Slot - Future Enhancement -->
        <template #whiteboard>
          <!-- Interactive Whiteboard Component -->
        </template>
      </ExplanationViewPanel>

      <!-- Right: Settings Panel -->
      <ExplanationSettingsPanel
        :explanation="selectedExplanation"
        :auto-play="autoPlay"
        :playback-speed="playbackSpeed"
        @update:auto-play="autoPlay = $event"
        @update:playback-speed="playbackSpeed = $event"
        @regenerate="handleRegenerateExplanation"
        @download-pdf="handleDownloadPDF"
        @share="handleShare"
      />
    </div>

    <!-- Error Banner -->
    <div v-if="displayError" class="error-banner">
      <span>⚠️ {{ displayError }}</span>
      <button @click="clearError">×</button>
    </div>
  </div>
</template>

<style scoped>
.explanation-generation-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

/* Header */
.container-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header-icon {
  font-size: 2rem;
}

.header-info {
  flex: 1;
}

.header-info h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.header-info p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Main Layout - 3 Columns */
.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 0;
  flex: 1;
  min-height: 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-size: 0.875rem;
}

.error-banner button {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
}

.error-banner button:hover {
  opacity: 0.7;
}

/* Responsive */
@media (max-width: 1400px) {
  .main-layout {
    grid-template-columns: 240px 1fr 240px;
  }
}

@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 220px 1fr;
  }
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
}
</style>
