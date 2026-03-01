<script setup lang="ts">
/**
 * StepDetailPanel — Expanded view for a single plan step.
 * Shows skill info, target, parameters, and generation result.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PlanStep } from '../../types'

interface Props {
  step: PlanStep
  phaseTitle?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()

const statusIcon = computed(() => {
  const map: Record<string, string> = {
    pending: '○', running: '◉', completed: '✓', failed: '✗', skipped: '—',
  }
  return map[props.step.status] || '○'
})

const statusClass = computed(() => `step-status-${props.step.status}`)

const paramEntries = computed(() => {
  if (!props.step.parameters) return []
  return Object.entries(props.step.parameters)
})

const hasResult = computed(() => !!props.step.result)

function skillLabel(code: string): string {
  const camel = code.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase())
  const key = `aiEditor.skills.${camel}.name`
  const translated = t(key)
  return translated !== key ? translated : code.replace(/_/g, ' ')
}
</script>

<template>
  <div class="step-detail">
    <div class="step-detail-header">
      <div class="step-detail-title-row">
        <span class="step-detail-icon" :class="statusClass">{{ statusIcon }}</span>
        <h4 class="step-detail-title">{{ step.target_title || skillLabel(step.skill_code) }}</h4>
      </div>
      <button class="step-detail-close" @click="emit('close')" :title="t('aiEditor.plan.stepDetail.close')">✕</button>
    </div>

    <!-- Info Grid -->
    <div class="step-detail-grid">
      <div class="detail-row">
        <span class="detail-label">{{ t('aiEditor.plan.stepDetail.skill') }}</span>
        <code class="detail-value detail-code">{{ skillLabel(step.skill_code) }}</code>
      </div>
      <div class="detail-row">
        <span class="detail-label">{{ t('aiEditor.plan.stepDetail.target') }}</span>
        <span class="detail-value">{{ step.target_type }} {{ step.target_id ? `(${step.target_id.slice(0, 8)}…)` : '' }}</span>
      </div>
    </div>

    <!-- Parameters -->
    <div v-if="paramEntries.length > 0" class="step-detail-section">
      <span class="section-label">{{ t('aiEditor.plan.stepDetail.parameters') }}</span>
      <div class="params-grid">
        <div v-for="[key, val] in paramEntries" :key="key" class="param-item">
          <span class="param-key">{{ key }}</span>
          <span class="param-val">{{ val }}</span>
        </div>
      </div>
    </div>

    <!-- Result -->
    <div class="step-detail-section">
      <span class="section-label">{{ t('aiEditor.plan.stepDetail.result') }}</span>
      <div v-if="hasResult" class="result-block">
        <div class="result-meta">
          <span>{{ t('aiEditor.plan.stepDetail.tokensUsed', { input: step.result!.tokens_input, output: step.result!.tokens_output }) }}</span>
          <span v-if="step.result!.model_name" class="result-model">
            {{ t('aiEditor.plan.stepDetail.model') }}: {{ step.result!.model_name }}
          </span>
        </div>
        <pre class="result-content">{{ JSON.stringify(step.result!.content, null, 2).slice(0, 500) }}</pre>
      </div>
      <div v-else class="result-empty">
        {{ t('aiEditor.plan.stepDetail.noResult') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.step-detail {
  background: var(--color-surface, #111827);
  border: 1px solid var(--color-border, #374151);
  border-radius: 0.5rem;
  margin: 0.5rem 0;
  overflow: hidden;
}

.step-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border, #374151);
  background: var(--color-surface-secondary, #1f2937);
}

.step-detail-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.step-detail-icon {
  font-size: 0.875rem;
  flex-shrink: 0;
}
.step-status-pending { color: var(--color-text-tertiary, #6b7280); }
.step-status-running { color: #60a5fa; }
.step-status-completed { color: #34d399; }
.step-status-failed { color: #f87171; }
.step-status-skipped { color: #9ca3af; }

.step-detail-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #f3f4f6);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-detail-close {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--color-text-tertiary, #6b7280);
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.step-detail-close:hover { color: var(--color-text-primary, #fff); }

.step-detail-grid {
  padding: 0.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-label {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
  min-width: 3rem;
}

.detail-value {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #d1d5db);
}

.detail-code {
  background: var(--color-surface-secondary, #1f2937);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
}

.step-detail-section {
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--color-border, #374151);
}

.section-label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-tertiary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.375rem;
}

.params-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--color-surface-secondary, #1f2937);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
}

.param-key {
  color: var(--color-text-tertiary, #6b7280);
}

.param-val {
  color: var(--color-text-secondary, #d1d5db);
  font-weight: 500;
}

.result-block {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
}

.result-model {
  font-family: monospace;
}

.result-content {
  background: var(--color-surface-secondary, #1f2937);
  padding: 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.6875rem;
  color: var(--color-text-secondary, #d1d5db);
  max-height: 8rem;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.result-empty {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #6b7280);
  font-style: italic;
}
</style>
