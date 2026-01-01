<template>
  <div class="detailed-steps">
    <div class="steps-header">
      <h3 class="steps-title">Schritt-für-Schritt Anleitung</h3>
      <div v-if="steps.length > 0" class="step-counter">
        Schritt {{ currentStep + 1 }} von {{ steps.length }}
      </div>
    </div>

    <div v-if="steps.length === 0" class="no-steps">
      <p>Noch keine detaillierten Schritte verfügbar.</p>
      <Button v-if="canGenerate" variant="primary" @click="$emit('generate')">
        Schritte generieren
      </Button>
    </div>

    <!-- Steps Navigation -->
    <div v-else class="steps-content">
      <!-- Current Step Display -->
      <div class="current-step">
        <div class="step-badge">{{ currentStep + 1 }}</div>
        <div class="step-details">
          <h4 class="step-title">{{ currentStepData.title }}</h4>
          <p class="step-speech">{{ currentStepData.speech }}</p>

          <!-- Calculator Input -->
          <div v-if="currentStepData.calculator" class="calculator-section">
            <div class="calculator-label">Taschenrechner-Eingabe:</div>
            <div class="calculator-display">
              <span class="calculator-keys">{{ currentStepData.calculator }}</span>
            </div>
            <div v-if="currentStepData.result" class="calculator-result">
              <span class="result-label">Ergebnis:</span>
              <span class="result-value">{{ currentStepData.result }}</span>
            </div>
          </div>

          <!-- Schema Display -->
          <div v-if="currentStepData.schema && currentStepData.schema.length > 0" class="schema-section">
            <div class="schema-table">
              <div
                v-for="(row, idx) in currentStepData.schema"
                :key="idx"
                class="schema-row"
                :class="{ 'schema-row--highlight': row.highlight }"
              >
                <span class="schema-name">{{ row.name }}</span>
                <span class="schema-operator">{{ row.operator }}</span>
                <span class="schema-value">{{ row.value }}</span>
              </div>
            </div>
          </div>

          <!-- Tip / Note -->
          <div v-if="currentStepData.tip" class="step-tip">
            <span class="tip-icon">💡</span>
            <span>{{ currentStepData.tip }}</span>
          </div>
        </div>
      </div>

      <!-- Steps Timeline -->
      <div class="steps-timeline">
        <button
          v-for="(step, idx) in steps"
          :key="idx"
          class="timeline-step"
          :class="{
            'timeline-step--active': idx === currentStep,
            'timeline-step--completed': idx < currentStep
          }"
          @click="currentStep = idx"
        >
          <span class="timeline-number">{{ idx + 1 }}</span>
          <span class="timeline-title">{{ truncateTitle(step.title) }}</span>
        </button>
      </div>

      <!-- Navigation Buttons -->
      <div class="steps-nav">
        <Button
          v-if="currentStep > 0"
          variant="outline"
          size="sm"
          @click="previousStep"
        >
          ← Zurück
        </Button>
        <div v-else></div>

        <Button
          v-if="currentStep < steps.length - 1"
          variant="primary"
          size="sm"
          @click="nextStep"
        >
          Weiter →
        </Button>
        <Button
          v-else
          variant="primary"
          size="sm"
          @click="$emit('completed')"
        >
          Abgeschlossen ✓
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Button from '@/components/ui/Button.vue'

interface SchemaRow {
  name: string
  operator?: string
  value: string
  highlight?: boolean
}

interface Step {
  title: string
  speech: string
  calculator?: string
  result?: string
  schema?: SchemaRow[]
  tip?: string
}

interface Props {
  steps: Step[]
  canGenerate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canGenerate: false
})

defineEmits<{
  (e: 'generate'): void
  (e: 'completed'): void
}>()

const currentStep = ref(0)

const currentStepData = computed(() => {
  return props.steps[currentStep.value] || {
    title: '',
    speech: ''
  }
})

const nextStep = () => {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const truncateTitle = (title: string, maxLength = 25): string => {
  if (!title) return ''
  return title.length > maxLength ? title.slice(0, maxLength) + '...' : title
}
</script>

<style scoped>
.detailed-steps {
  background: var(--color-surface, #ffffff);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.steps-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.step-counter {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  background: var(--color-surface-secondary, #f3f4f6);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.no-steps {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.no-steps p {
  margin-bottom: 1rem;
}

/* Current Step */
.current-step {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.step-badge {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.step-details {
  flex: 1;
}

.step-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.5rem;
}

.step-speech {
  color: var(--color-text-secondary, #374151);
  line-height: 1.6;
  margin: 0 0 1rem;
}

/* Calculator Section */
.calculator-section {
  background: #1f2937;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.calculator-label {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.calculator-display {
  background: #111827;
  border-radius: 0.25rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

.calculator-keys {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 1.25rem;
  color: #10b981;
  letter-spacing: 0.05em;
}

.calculator-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.result-label {
  font-size: 0.875rem;
  color: #9ca3af;
}

.result-value {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 1.125rem;
  color: #fbbf24;
  font-weight: 600;
}

/* Schema Section */
.schema-section {
  margin-bottom: 1rem;
}

.schema-table {
  background: var(--color-surface-secondary, #f9fafb);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border, #e5e7eb);
}

.schema-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 0.875rem;
}

.schema-row:not(:last-child) {
  border-bottom: 1px dashed var(--color-border, #e5e7eb);
}

.schema-row--highlight {
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
}

.schema-name {
  color: var(--color-text-primary, #111827);
}

.schema-operator {
  color: var(--color-text-secondary, #6b7280);
  text-align: center;
  min-width: 1.5rem;
}

.schema-value {
  color: var(--color-primary, #3b82f6);
  text-align: right;
  font-weight: 500;
}

/* Step Tip */
.step-tip {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #92400e;
}

.tip-icon {
  flex-shrink: 0;
}

/* Timeline */
.steps-timeline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-surface-secondary, #f9fafb);
  border-radius: 0.5rem;
}

.timeline-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.75rem;
}

.timeline-step:hover {
  border-color: var(--color-primary, #3b82f6);
}

.timeline-step--active {
  background: var(--color-primary, #3b82f6);
  border-color: var(--color-primary, #3b82f6);
  color: white;
}

.timeline-step--completed {
  background: rgba(16, 185, 129, 0.1);
  border-color: #10b981;
}

.timeline-step--completed .timeline-number {
  background: #10b981;
  color: white;
}

.timeline-number {
  width: 1.25rem;
  height: 1.25rem;
  background: var(--color-surface-secondary, #f3f4f6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.625rem;
}

.timeline-step--active .timeline-number {
  background: white;
  color: var(--color-primary, #3b82f6);
}

.timeline-title {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Navigation */
.steps-nav {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
}
</style>
