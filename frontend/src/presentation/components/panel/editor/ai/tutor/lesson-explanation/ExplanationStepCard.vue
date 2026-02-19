<!--
  ExplanationStepCard - Displays a single teaching step with speech, calculator, and schema
-->

<template>
  <div class="step-card" v-if="step">
    <div class="step-header">
      <span class="step-badge">
        {{ $t('lessonExplanationView.stepBadge', { n: stepNumber }) }}
      </span>
      <h3 class="step-title">
        {{ step.title || $t('lessonExplanationView.stepTitle', { n: stepNumber }) }}
      </h3>
    </div>

    <!-- Speech Bubble -->
    <div class="speech-bubble">
      <p>{{ step.speech }}</p>
    </div>

    <!-- Calculator Hint -->
    <div v-if="step.calculator" class="calculator-box">
      <div class="calc-header">
        <span class="calc-icon">&#x1F522;</span>
        <span class="calc-label">{{ $t('lessonExplanationView.calculatorInput') }}</span>
      </div>
      <div class="calc-input">
        <code>{{ step.calculator }}</code>
      </div>
      <div v-if="step.result" class="calc-result">
        <span class="equals">{{ $t('lessonExplanationView.equals') }}</span>
        <span class="result-value">{{ step.result }}</span>
      </div>
    </div>

    <!-- Schema Preview (fallback when no whiteboard actions) -->
    <div v-if="step.schema && !step.whiteboardActions?.length" class="schema-preview">
      <table>
        <tr v-for="(row, idx) in step.schema" :key="idx" :class="{ highlighted: row.highlight }">
          <td class="schema-name">{{ row.name }}</td>
          <td class="schema-op">{{ row.operator }}</td>
          <td class="schema-value">{{ row.value }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationStepCard - Renders the content of a single teaching step.
 */
import type { TeachingStep } from '@/application/composables/learning/useTheoryManagement'

interface Props {
  step: TeachingStep | null
  stepNumber: number
}

withDefaults(defineProps<Props>(), {
  stepNumber: 1
})
</script>

<style scoped>
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  background: rgba(0, 0, 0, 0.05);
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
</style>
