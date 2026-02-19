<!--
  Math Task Modal - IHK Exam Style

  Features:
  - Task is displayed, solution is hidden
  - User must calculate and enter answer first
  - After submission: check or reveal solution
  - Solution path collapsible (after answer)
  - Dark Mode Support
-->

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <div class="flex items-center gap-3">
            <span class="text-2xl">&#x1F9EE;</span>
            <div>
              <h2 class="modal-title">
                {{ taskData.title || $t('lesson.mathTask.defaultTitle') }}
              </h2>
              <p v-if="methodName" class="modal-subtitle">
                {{ methodName }}
              </p>
            </div>
          </div>
          <button @click="$emit('close')" class="close-btn">
            &#x2715;
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Task Counter -->
          <div v-if="taskNumber" class="task-counter">
            {{ $t('lesson.mathTask.taskCounter', { current: taskNumber, total: totalTasks }) }}
          </div>

          <!-- Question Section -->
          <div class="task-section question-section">
            <div class="section-icon">&#x1F4DD;</div>
            <div class="section-content">
              <h3 class="section-title">{{ $t('lesson.mathTask.question') }}</h3>
              <p class="question-text">{{ taskData.question }}</p>
            </div>
          </div>

          <!-- Answer Input Section -->
          <div class="answer-section">
            <div class="answer-header">
              <span class="answer-icon">&#x270F;&#xFE0F;</span>
              <label class="answer-label">{{ $t('lesson.mathTask.yourAnswer') }}</label>
            </div>

            <div class="answer-input-wrapper">
              <input
                v-model="userAnswer"
                type="text"
                class="answer-input"
                :placeholder="getPlaceholder()"
                :disabled="hasSubmitted"
                @keyup.enter="checkAnswer"
              />

              <button
                v-if="!hasSubmitted"
                @click="checkAnswer"
                class="check-btn"
                :disabled="!userAnswer.trim()"
              >
                {{ $t('lesson.mathTask.checkAnswer') }}
              </button>
            </div>

            <!-- Answer Feedback -->
            <div v-if="hasSubmitted" class="answer-feedback" :class="feedbackClass">
              <span class="feedback-icon">{{ isCorrect ? '&#x2705;' : '&#x274C;' }}</span>
              <span class="feedback-text">
                {{ isCorrect ? $t('lesson.mathTask.correct') : $t('lesson.mathTask.incorrect') }}
              </span>
            </div>
          </div>

          <!-- Solution, Steps, Explanation -->
          <MathTaskSolutionPanel
            :task-data="taskData"
            :can-show-solution="canShowSolution"
            :has-submitted="hasSubmitted"
            :is-correct="isCorrect"
            :show-solution="showSolution"
            :show-steps="showSteps"
            :show-explanation="showExplanation"
            @toggle-solution="toggleSolution"
            @toggle-steps="toggleSteps"
            @update:show-explanation="showExplanation = $event"
          />
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <div class="footer-left">
            <span class="token-info">
              {{ $t('lesson.mathTask.tokensUsed', { count: tokensUsed }) }}
            </span>
          </div>
          <div class="footer-buttons">
            <button
              v-if="hasSubmitted"
              @click="resetTask"
              class="btn-outline"
            >
              &#x1F504; {{ $t('lesson.mathTask.retry') }}
            </button>
            <button @click="$emit('newTask')" class="btn-secondary">
              &#x27A1;&#xFE0F; {{ $t('lesson.mathTask.newTask') }}
            </button>
            <button @click="$emit('close')" class="btn-primary">
              {{ $t('lesson.mathTask.close') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * MathTaskModal - IHK-style math task with answer checking.
 * Uses useMathTaskChecker composable for answer logic
 * and MathTaskSolutionPanel for collapsible solution display.
 */
import type { TaskData } from '@/application/composables/learning/useMathTaskChecker'
import { useMathTaskChecker } from '@/application/composables/learning/useMathTaskChecker'
import MathTaskSolutionPanel from './MathTaskSolutionPanel.vue'

interface Props {
  taskData: TaskData
  methodName?: string
  tokensUsed?: number
  showInput?: boolean
  taskNumber?: number
  totalTasks?: number
}

const props = withDefaults(defineProps<Props>(), {
  tokensUsed: 0,
  showInput: true,
  taskNumber: 0,
  totalTasks: 0
})

defineEmits(['close', 'newTask'])

const {
  userAnswer,
  hasSubmitted,
  isCorrect,
  showSteps,
  showSolution,
  showExplanation,
  canShowSolution,
  feedbackClass,
  getPlaceholder,
  checkAnswer,
  toggleSolution,
  toggleSteps,
  resetTask
} = useMathTaskChecker(() => props.taskData)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--color-surface, #ffffff);
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: linear-gradient(135deg, var(--color-primary-50, #eff6ff) 0%, var(--color-surface, #ffffff) 100%);
}

:root.dark .modal-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, var(--color-surface, #1f2937) 100%);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
}

.modal-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s;
  font-size: 1.25rem;
}

.close-btn:hover {
  background-color: var(--color-background, #f3f4f6);
  color: var(--color-text-primary, #111827);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.task-counter {
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: var(--color-background, #f9fafb);
  border-radius: 0.5rem;
}

.task-section {
  margin-bottom: 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  overflow: hidden;
}

.question-section {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-primary-50, #eff6ff);
  border-color: var(--color-primary-200, #bfdbfe);
}

:root.dark .question-section {
  background-color: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.section-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.section-content {
  flex: 1;
}

.section-title {
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-text {
  font-size: 1rem;
  color: var(--color-text-primary, #111827);
  line-height: 1.6;
}

/* Answer Section */
.answer-section {
  margin-bottom: 1rem;
  padding: 1.25rem;
  background-color: var(--color-surface, #ffffff);
  border: 2px solid var(--color-primary, #3b82f6);
  border-radius: 0.75rem;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.answer-icon {
  font-size: 1.25rem;
}

.answer-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
}

.answer-input-wrapper {
  display: flex;
  gap: 0.75rem;
}

.answer-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background-color: var(--color-background, #f9fafb);
  color: var(--color-text-primary, #111827);
  font-size: 1rem;
  transition: all 0.2s;
}

.answer-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.answer-input:disabled {
  background-color: var(--color-background, #f3f4f6);
  cursor: not-allowed;
}

.check-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.check-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.check-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.answer-feedback {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.feedback-correct {
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.feedback-incorrect {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.feedback-icon {
  font-size: 1.25rem;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-background, #f9fafb);
}

.token-info {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.footer-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-outline {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  background-color: transparent;
}

.btn-outline:hover {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-text-secondary, #9ca3af);
}

.btn-secondary {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  background-color: var(--color-surface, #ffffff);
}

.btn-secondary:hover {
  background-color: var(--color-background, #f3f4f6);
  border-color: var(--color-text-secondary, #9ca3af);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>
