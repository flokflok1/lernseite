/**
 * SourceSelectionContainer.vue
 *
 * PHASE 1a: Source Selection & PDF Upload
 *
 * 3-step wizard:
 * 1. Source Type Selection (PDF, Manual, Template)
 * 2. PDF Upload & Analysis (if PDF selected)
 * 3. Summary & Confirmation
 *
 * Emits:
 * - complete: session created and ready for Phase 2
 * - cancel: user cancelled the process
 */

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSourceSelection } from './composables/useSourceSelection'
import SourceTypeSelector from './steps/SourceTypeSelector.vue'
import PDFUploadPanel from './steps/PDFUploadPanel.vue'
import SessionSummaryPanel from './steps/SessionSummaryPanel.vue'

interface Props {
  courseId: string
}

interface Emits {
  (e: 'complete', sessionId: string): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const {
  state,
  currentStep,
  isLoading,
  error,
  sourceType,
  uploadedFile,
  pdfAnalysis,
  sessionData,
  canProceedToUpload,
  canProceedToSummary,
  canFinalize,
  selectSourceType,
  uploadPDFFile,
  createManualSession,
  goToPreviousStep,
  reset
} = useSourceSelection(ref(props.courseId))

// Handle completion
const handleComplete = async () => {
  if (sessionData.value?.session_id) {
    emit('complete', sessionData.value.session_id)
  }
}

// Handle cancel
const handleCancel = () => {
  reset()
  emit('cancel')
}

// Clear error
const clearError = () => {
  // error is a ref from composable, reset will clear it
  reset()
}

// Handle step transitions
const handleSourceTypeSelected = (type: 'pdf' | 'manual' | 'template') => {
  selectSourceType(type)
}

const handlePDFUploadComplete = async () => {
  // PDF analysis and session creation happens in uploadPDFFile
  // Just transition to summary
}

const handleSummaryConfirm = async () => {
  if (sourceType.value === 'manual' || sourceType.value === 'template') {
    await createManualSession()
  }
  handleComplete()
}
</script>

<template>
  <div class="source-selection-container">
    <!-- Header -->
    <div class="selection-header">
      <h2>{{ $t('courses.editor.setupCourse') }}</h2>
      <p class="subtitle">
        {{ $t('courses.editor.setupDescription') }}
      </p>
    </div>

    <!-- Progress Indicator -->
    <div class="progress-steps">
      <div
        :class="['step', { active: currentStep === 'source-type', completed: currentStep !== 'source-type' }]"
      >
        <span class="step-number">1</span>
        <span class="step-label">{{ $t('courses.editor.selectSource') }}</span>
      </div>
      <div class="step-connector"></div>

      <div
        v-if="sourceType === 'pdf'"
        :class="['step', { active: currentStep === 'upload', completed: currentStep !== 'upload' && currentStep !== 'source-type' }]"
      >
        <span class="step-number">2</span>
        <span class="step-label">{{ $t('courses.editor.uploadPdf') }}</span>
      </div>
      <div v-if="sourceType === 'pdf'" class="step-connector"></div>

      <div
        :class="['step', { active: currentStep === 'summary', completed: currentStep === 'complete' }]"
      >
        <span class="step-number">{{ sourceType === 'pdf' ? 3 : 2 }}</span>
        <span class="step-label">{{ $t('courses.editor.review') }}</span>
      </div>
    </div>

    <!-- Content Area -->
    <div class="selection-content">
      <!-- Step 1: Source Type Selection -->
      <SourceTypeSelector
        v-if="currentStep === 'source-type'"
        :is-loading="isLoading"
        @select="handleSourceTypeSelected"
      />

      <!-- Step 2: PDF Upload (if PDF selected) -->
      <PDFUploadPanel
        v-else-if="currentStep === 'upload'"
        :is-loading="isLoading"
        :error="error"
        @upload="uploadPDFFile"
        @back="goToPreviousStep"
      />

      <!-- Step 3: Summary & Confirmation -->
      <SessionSummaryPanel
        v-else-if="currentStep === 'summary'"
        :source-type="sourceType"
        :uploaded-file="uploadedFile"
        :pdf-analysis="pdfAnalysis"
        :is-loading="isLoading"
        :error="error"
        @confirm="handleSummaryConfirm"
        @back="goToPreviousStep"
      />

      <!-- Complete State -->
      <div v-else-if="currentStep === 'complete'" class="completion-message">
        <div class="success-icon">✓</div>
        <h3>{{ $t('courses.editor.sessionCreated') }}</h3>
        <p>{{ $t('courses.editor.readyForPhase2') }}</p>
        <button
          class="btn btn-primary"
          @click="handleComplete"
        >
          {{ $t('courses.editor.proceedToPhase2') }}
        </button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
      <button
        class="error-close"
        @click="clearError"
      >
        ×
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="selection-footer">
      <button
        v-if="currentStep !== 'source-type' && currentStep !== 'complete'"
        class="btn btn-secondary"
        @click="goToPreviousStep"
        :disabled="isLoading"
      >
        {{ $t('common.back') }}
      </button>

      <button
        class="btn btn-secondary"
        @click="handleCancel"
        :disabled="isLoading"
      >
        {{ $t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.source-selection-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
  padding: 24px;
  background: white;
  border-radius: 8px;
}

.selection-header {
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 16px;
}

.selection-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Progress Steps */
.progress-steps {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 6px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.step.active {
  opacity: 1;
}

.step.completed {
  opacity: 1;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #666;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.step.active .step-number {
  background: #2196f3;
  color: white;
}

.step.completed .step-number {
  background: #4caf50;
  color: white;
}

.step-label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-align: center;
  max-width: 80px;
}

.step-connector {
  flex: 0.5;
  height: 2px;
  background: #e0e0e0;
  margin-top: 18px;
}

/* Content Area */
.selection-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.completion-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px 20px;
  text-align: center;
}

.success-icon {
  font-size: 48px;
  color: #4caf50;
}

.completion-message h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.completion-message p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #ffebee;
  border: 1px solid #ef5350;
  border-radius: 6px;
  color: #c62828;
  font-size: 14px;
}

.error-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 20px;
  padding: 0;
  line-height: 1;
}

/* Footer */
.selection-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #eeeeee;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .source-selection-container {
    padding: 16px;
    gap: 16px;
  }

  .progress-steps {
    flex-direction: column;
    gap: 8px;
  }

  .step-connector {
    width: 2px;
    height: 16px;
    margin: 0;
  }

  .selection-footer {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
