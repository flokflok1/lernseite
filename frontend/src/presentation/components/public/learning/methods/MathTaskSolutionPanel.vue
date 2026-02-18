<!--
  MathTaskSolutionPanel - Collapsible solution, steps, and explanation sections
-->

<template>
  <div class="solution-panel">
    <!-- Solution Section -->
    <div class="task-section solution-section" :class="{ 'locked': !canShowSolution }">
      <button
        @click="$emit('toggle-solution')"
        class="toggle-btn"
        :disabled="!canShowSolution && !hasSubmitted"
      >
        <span class="section-icon">{{ canShowSolution ? '&#x2705;' : '&#x1F512;' }}</span>
        <span class="section-title">{{ $t('lesson.mathTask.solution') }}</span>
        <span v-if="!canShowSolution && !hasSubmitted" class="lock-hint">
          {{ $t('lesson.mathTask.enterAnswerFirst') }}
        </span>
        <span class="toggle-icon" :class="{ rotated: showSolution }">&#x25BC;</span>
      </button>

      <Transition name="slide">
        <div v-if="showSolution && canShowSolution" class="solution-content">
          <div class="solution-box" :class="{ 'correct': isCorrect, 'incorrect': hasSubmitted && !isCorrect }">
            <strong>{{ taskData.solution }}</strong>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Steps Section -->
    <div class="task-section steps-section" :class="{ 'locked': !canShowSolution }">
      <button
        @click="$emit('toggle-steps')"
        class="toggle-btn"
        :disabled="!canShowSolution"
      >
        <span class="section-icon">&#x1F4CB;</span>
        <span class="section-title">{{ $t('lesson.mathTask.solutionPath', { count: taskData.steps?.length || 0 }) }}</span>
        <span class="toggle-icon" :class="{ rotated: showSteps }">&#x25BC;</span>
      </button>

      <Transition name="slide">
        <div v-if="showSteps && canShowSolution" class="steps-content">
          <div
            v-for="(step, index) in taskData.steps"
            :key="index"
            class="step-item"
          >
            <div class="step-number">{{ step.step || index + 1 }}</div>
            <div class="step-details">
              <p class="step-description">{{ step.description }}</p>
              <code v-if="step.calculation" class="step-calculation">
                {{ step.calculation }}
              </code>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Explanation Section -->
    <div v-if="taskData.explanation && canShowSolution" class="task-section explanation-section">
      <button @click="$emit('update:showExplanation', !showExplanation)" class="toggle-btn">
        <span class="section-icon">&#x1F4A1;</span>
        <span class="section-title">{{ $t('lesson.mathTask.explanation') }}</span>
        <span class="toggle-icon" :class="{ rotated: showExplanation }">&#x25BC;</span>
      </button>

      <Transition name="slide">
        <div v-if="showExplanation" class="explanation-content">
          <p>{{ taskData.explanation }}</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MathTaskSolutionPanel - Renders the collapsible solution,
 * step-by-step breakdown, and explanation sections.
 */
import type { TaskData } from './composables/useMathTaskChecker'

interface Props {
  taskData: TaskData
  canShowSolution: boolean
  hasSubmitted: boolean
  isCorrect: boolean
  showSolution: boolean
  showSteps: boolean
  showExplanation: boolean
}

withDefaults(defineProps<Props>(), {
  canShowSolution: false,
  hasSubmitted: false,
  isCorrect: false,
  showSolution: false,
  showSteps: false,
  showExplanation: false
})

defineEmits<{
  (e: 'toggle-solution'): void
  (e: 'toggle-steps'): void
  (e: 'update:showExplanation', value: boolean): void
}>()
</script>

<style scoped>
.task-section {
  margin-bottom: 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  overflow: hidden;
}

.task-section.locked {
  opacity: 0.6;
}

/* Toggle Buttons */
.toggle-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-background, #f9fafb);
  text-align: left;
  transition: background-color 0.2s;
  color: var(--color-text-primary, #111827);
}

.toggle-btn:hover:not(:disabled) {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
}

.toggle-btn:disabled {
  cursor: not-allowed;
}

:root.dark .toggle-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.05);
}

.section-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.section-title {
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.lock-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #9ca3af);
  font-style: italic;
}

.toggle-icon {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  transition: transform 0.3s;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

/* Solution Box */
.solution-content,
.steps-content,
.explanation-content {
  padding: 1.25rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #ffffff);
}

.solution-box {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  text-align: center;
  font-weight: 600;
}

.solution-box.correct {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.solution-box.incorrect {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

/* Steps */
.step-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px dashed var(--color-border, #e5e7eb);
}

.step-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.step-number {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.step-details {
  flex: 1;
}

.step-description {
  color: var(--color-text-primary, #111827);
  margin-bottom: 0.5rem;
}

.step-calculation {
  display: block;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-background, #f3f4f6);
  border-radius: 0.5rem;
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.875rem;
  color: var(--color-primary, #3b82f6);
  border: 1px solid var(--color-border, #e5e7eb);
}

.explanation-content p {
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.7;
}

/* Slide Transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 500px;
  opacity: 1;
}
</style>
