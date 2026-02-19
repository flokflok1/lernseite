<!--
  TutorStepCard - Displays a single tutorial step with speech bubble,
  calculator hint, and schema preview.
-->

<template>
  <div class="step-card">
    <div class="step-header">
      <span class="step-badge">{{ $t('lesson.tutorPlayer.step', { number: stepNumber }) }}</span>
      <h3 class="step-title">{{ step.title }}</h3>
    </div>

    <!-- Speech Bubble -->
    <div class="speech-bubble">
      <p>{{ step.speech }}</p>
    </div>

    <!-- Calculator Hint -->
    <div v-if="step.calculator" class="calculator-box">
      <div class="calc-header">
        <span class="calc-icon">{{ $t('lesson.tutorPlayer.calculatorIcon') }}</span>
        <span class="calc-label">{{ $t('lesson.tutorPlayer.calculatorHint') }}</span>
      </div>
      <div class="calc-input">
        <code>{{ step.calculator }}</code>
      </div>
      <div v-if="step.result" class="calc-result">
        <span class="equals">=</span>
        <span class="result-value">{{ step.result }}</span>
      </div>
    </div>

    <!-- Schema Preview -->
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
 * TutorStepCard - Renders a single tutorial step's content.
 */
import type { TutorialStep } from './composables/useTutorPlayer'

interface Props {
  step: TutorialStep
  stepNumber: number
}

defineProps<Props>()
</script>

<style scoped>
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
</style>
