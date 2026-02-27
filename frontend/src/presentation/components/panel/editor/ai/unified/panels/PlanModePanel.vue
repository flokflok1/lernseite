<script setup lang="ts">
/**
 * PlanModePanel — Plan visualization with phases, steps, actions.
 * Features: scope selector, step detail, pause/resume, progress bar.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ContentPlan, PlanStep, PlanScope } from '../types'
import StepDetailPanel from './StepDetailPanel.vue'
import PlanEmptyState from './PlanEmptyState.vue'

interface Props {
  plan: ContentPlan | null
  isCreating: boolean
  isExecuting: boolean
  isDraft: boolean
  isApproved: boolean
  isPaused?: boolean
  isCompleted?: boolean
  isFailed?: boolean
  isSaving?: boolean
  isApproving?: boolean
  hasFiles?: boolean
  selectedStepId?: string | null
  completedSteps?: number
  failedSteps?: number
}

const props = withDefaults(defineProps<Props>(), {
  hasFiles: false,
  isPaused: false,
  isCompleted: false,
  isFailed: false,
  isSaving: false,
  isApproving: false,
  selectedStepId: null,
  completedSteps: 0,
  failedSteps: 0,
})

const emit = defineEmits<{
  createPlan: [scope: PlanScope, scopeId?: string]
  reorderStep: [phaseIndex: number, fromIndex: number, toIndex: number]
  removeStep: [phaseIndex: number, stepIndex: number]
  selectStep: [stepId: string | null]
  savePlan: []
  approve: []
  execute: []
  discard: []
  finalizePlan: []
  pause: []
  resume: []
}>()

const { t } = useI18n()

// ── Status ───────────────────────────────────────────────────
const statusLabel = computed(() => {
  const status = props.plan?.status || 'draft'
  return t(`aiEditor.plan.status.${status}`)
})

const statusColor = computed(() => {
  const map: Record<string, string> = {
    draft: 'status-draft',
    approved: 'status-approved',
    executing: 'status-executing',
    completed: 'status-completed',
    paused: 'status-paused',
    failed: 'status-failed',
  }
  return map[props.plan?.status || 'draft'] || ''
})

// ── Steps ────────────────────────────────────────────────────
const totalSteps = computed(() => {
  if (!props.plan) return 0
  return props.plan.phases.reduce((sum, p) => sum + p.steps.length, 0)
})

const progressPercent = computed(() => {
  if (totalSteps.value === 0) return 0
  return Math.round((props.completedSteps / totalSteps.value) * 100)
})

const selectedStepData = computed(() => {
  if (!props.plan || !props.selectedStepId) return null
  for (const phase of props.plan.phases) {
    const step = phase.steps.find(s => s.step_id === props.selectedStepId)
    if (step) return { step, phaseTitle: phase.title }
  }
  return null
})

function stepIcon(status: string) {
  const map: Record<string, string> = {
    pending: '○', running: '◉', completed: '✓', failed: '✗', skipped: '—',
  }
  return map[status] || '○'
}

function moveStep(phaseIdx: number, stepIdx: number, direction: 'up' | 'down') {
  const newIdx = direction === 'up' ? stepIdx - 1 : stepIdx + 1
  emit('reorderStep', phaseIdx, stepIdx, newIdx)
}

function onStepClick(step: PlanStep) {
  emit('selectStep', props.selectedStepId === step.step_id ? null : step.step_id)
}
</script>

<template>
  <div class="plan-panel">
    <!-- Empty State -->
    <PlanEmptyState
      v-if="!plan"
      :is-creating="isCreating"
      :has-files="hasFiles"
      @create-plan="(scope, scopeId) => emit('createPlan', scope, scopeId)"
    />

    <!-- Plan View -->
    <template v-else>
      <!-- Header -->
      <div class="plan-header">
        <div class="plan-meta">
          <span class="plan-status" :class="statusColor">{{ statusLabel }}</span>
          <span class="plan-stats">
            {{ totalSteps }} {{ t('aiEditor.plan.steps') }} · ~{{ plan.estimated_total_tokens.toLocaleString() }} {{ t('aiEditor.plan.tokens') }}
          </span>
        </div>
        <div class="plan-actions">
          <button class="btn-discard" @click="emit('discard')" :title="t('aiEditor.plan.discard')">✕</button>

          <!-- Draft actions -->
          <button v-if="isDraft" class="btn-secondary" :disabled="isSaving" @click="emit('savePlan')">
            {{ isSaving ? t('aiEditor.plan.saving') : t('aiEditor.plan.save') }}
          </button>
          <button v-if="isDraft" class="btn-primary" :disabled="isApproving" @click="emit('approve')">
            {{ isApproving ? t('aiEditor.plan.approving') : t('aiEditor.plan.approve') }}
          </button>

          <!-- Approved → Execute -->
          <button
            v-if="isApproved"
            class="btn-success"
            :disabled="isExecuting"
            @click="emit('execute')"
          >
            {{ t('aiEditor.plan.execute') }}
          </button>

          <!-- Executing → Pause -->
          <button
            v-if="isExecuting"
            class="btn-warning"
            @click="emit('pause')"
          >
            {{ t('aiEditor.plan.pause') }}
          </button>

          <!-- Paused → Resume -->
          <button
            v-if="isPaused"
            class="btn-success"
            @click="emit('resume')"
          >
            {{ t('aiEditor.plan.resume') }}
          </button>

          <!-- Completed → Finalize (adopt results) -->
          <button
            v-if="isCompleted"
            class="btn-success"
            @click="emit('finalizePlan')"
          >
            {{ t('aiEditor.plan.finalize') }}
          </button>

          <!-- Failed → New Plan -->
          <button
            v-if="isFailed"
            class="btn-primary"
            @click="emit('discard')"
          >
            {{ t('aiEditor.plan.newPlan') }}
          </button>
        </div>
      </div>

      <!-- Progress Bar (visible during/after execution) -->
      <div v-if="isExecuting || completedSteps > 0 || failedSteps > 0" class="progress-section">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }" />
        </div>
        <div class="progress-info">
          <span>{{ t('aiEditor.plan.progress.stepsCompleted', { completed: completedSteps, total: totalSteps }) }}</span>
          <span v-if="failedSteps > 0" class="progress-failed">
            {{ t('aiEditor.plan.progress.failed', { count: failedSteps }) }}
          </span>
          <span v-if="plan.actual_tokens > 0" class="progress-tokens">
            {{ t('aiEditor.plan.progress.tokensUsed') }}: {{ plan.actual_tokens.toLocaleString() }}
          </span>
        </div>
      </div>

      <!-- Completed / Failed Summary -->
      <div v-if="isCompleted || isFailed" class="plan-summary">
        <span class="plan-summary-icon">{{ isCompleted ? '✓' : '✗' }}</span>
        <span class="plan-summary-text">
          {{ isCompleted ? t('aiEditor.plan.completedSummary', { completed: completedSteps, total: totalSteps }) : t('aiEditor.plan.failedSummary', { failed: failedSteps, completed: completedSteps, total: totalSteps }) }}
        </span>
        <span v-if="plan.actual_tokens > 0" class="plan-summary-tokens">
          {{ plan.actual_tokens.toLocaleString() }} {{ t('aiEditor.plan.tokens') }}
        </span>
      </div>

      <!-- Step Detail (expanded) -->
      <StepDetailPanel
        v-if="selectedStepData"
        :step="selectedStepData.step"
        :phase-title="selectedStepData.phaseTitle"
        @close="emit('selectStep', null)"
      />

      <!-- Phases & Steps -->
      <div class="plan-content">
        <div v-for="(phase, phaseIdx) in plan.phases" :key="phase.phase_id" class="phase">
          <div class="phase-header">
            <span class="phase-number">{{ phaseIdx + 1 }}</span>
            <span class="phase-title">{{ phase.title }}</span>
            <span class="phase-count">{{ phase.steps.length }}</span>
          </div>
          <div class="steps-list">
            <div
              v-for="(step, stepIdx) in phase.steps"
              :key="step.step_id"
              class="step"
              :class="[
                'step-' + step.status,
                { 'step-selected': selectedStepId === step.step_id }
              ]"
              @click="onStepClick(step)"
            >
              <span class="step-icon">{{ stepIcon(step.status) }}</span>
              <div class="step-body">
                <div class="step-title">{{ step.target_title || step.skill_code }}</div>
                <div v-if="step.target_title && step.skill_code" class="step-skill">
                  {{ step.skill_code }}
                </div>
              </div>
              <div v-if="isDraft" class="step-controls" @click.stop>
                <button
                  v-if="stepIdx > 0"
                  class="step-btn"
                  @click="moveStep(phaseIdx, stepIdx, 'up')"
                >↑</button>
                <button
                  v-if="stepIdx < phase.steps.length - 1"
                  class="step-btn"
                  @click="moveStep(phaseIdx, stepIdx, 'down')"
                >↓</button>
                <button
                  class="step-btn step-btn-delete"
                  @click="emit('removeStep', phaseIdx, stepIdx)"
                >✕</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.plan-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}
/* ── Header ──────────────────────────────────── */
.plan-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border, #374151);
  flex-shrink: 0;
}
.plan-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.plan-status {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}
.status-draft { color: #fbbf24; background: rgba(251, 191, 36, 0.1); }
.status-approved { color: #60a5fa; background: rgba(96, 165, 250, 0.1); }
.status-executing { color: #a78bfa; background: rgba(167, 139, 250, 0.1); }
.status-completed { color: #34d399; background: rgba(52, 211, 153, 0.1); }
.status-paused { color: #fb923c; background: rgba(251, 146, 60, 0.1); }
.status-failed { color: #f87171; background: rgba(248, 113, 113, 0.1); }

.plan-stats {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
}
.plan-actions {
  display: flex;
  gap: 0.375rem;
  align-items: center;
}
.btn-discard {
  width: 1.75rem; height: 1.75rem;
  display: flex; align-items: center; justify-content: center;
  background: transparent; color: var(--color-text-tertiary, #6b7280);
  border: 1px solid var(--color-border, #374151); border-radius: 0.25rem;
  cursor: pointer; font-size: 0.75rem; transition: all 0.15s;
}
.btn-discard:hover { color: #f87171; border-color: #f87171; }
.btn-secondary, .btn-primary, .btn-success, .btn-warning {
  padding: 0.375rem 0.75rem; border: none; border-radius: 0.375rem;
  font-size: 0.75rem; cursor: pointer; color: #fff; transition: background 0.15s;
}
.btn-secondary:disabled, .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: var(--color-surface-secondary, #374151); color: var(--color-text-secondary, #d1d5db); }
.btn-secondary:hover { background: var(--color-surface-tertiary, #4b5563); }
.btn-primary { background: var(--color-primary, #6366f1); }
.btn-primary:hover { background: var(--color-primary-hover, #4f46e5); }
.btn-success { background: #059669; }
.btn-success:hover:not(:disabled) { background: #047857; }
.btn-success:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-warning { background: #d97706; }
.btn-warning:hover { background: #b45309; }

/* ── Progress Bar ────────────────────────────── */
.progress-section {
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--color-border, #374151);
  flex-shrink: 0;
}
.progress-bar-bg {
  height: 0.25rem;
  background: var(--color-surface-secondary, #1f2937);
  border-radius: 0.125rem;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 0.125rem;
  transition: width 0.3s ease;
}
.progress-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
}
.progress-failed { color: #f87171; }
.progress-tokens { margin-left: auto; }
/* ── Summary ────────────────────────────────── */
.plan-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--color-border, #374151);
  background: var(--color-surface-secondary, #1f2937);
  flex-shrink: 0;
}
.plan-summary-icon { font-size: 0.875rem; }
.plan-summary-text {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #d1d5db);
  flex: 1;
}
.plan-summary-tokens {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
  font-family: monospace;
}
/* ── Content ─────────────────────────────────── */
.plan-content { flex: 1; overflow-y: auto; padding: 0.75rem; }
/* ── Phase ───────────────────────────────────── */
.phase { margin-bottom: 1rem; }
.phase-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.375rem 0;
}
.phase-number {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary, #6366f1);
  color: #fff;
  border-radius: 50%;
  font-size: 0.6875rem;
  font-weight: 700;
  flex-shrink: 0;
}
.phase-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #f3f4f6);
  flex: 1;
}
.phase-count {
  font-size: 0.625rem;
  color: var(--color-text-tertiary, #6b7280);
  background: var(--color-surface-secondary, #1f2937);
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
}

/* ── Steps ───────────────────────────────────── */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-left: 0.75rem;
  padding-left: 0.75rem;
  border-left: 2px solid var(--color-border, #374151);
}
.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.625rem;
  border-radius: 0.375rem;
  background: var(--color-surface, #111827);
  transition: background 0.1s;
  cursor: pointer;
}
.step:hover { background: var(--color-surface-secondary, #1f2937); }
.step:hover .step-controls { opacity: 1; }
.step-selected {
  background: var(--color-surface-secondary, #1f2937);
  outline: 1px solid var(--color-primary, #6366f1);
  outline-offset: -1px;
}

.step-icon {
  width: 1rem;
  text-align: center;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.step-pending .step-icon { color: var(--color-text-tertiary, #6b7280); }
.step-running .step-icon { color: #60a5fa; }
.step-completed .step-icon { color: #34d399; }
.step-failed .step-icon { color: #f87171; }

.step-body {
  flex: 1;
  min-width: 0;
}
.step-title {
  font-size: 0.8125rem;
  color: var(--color-text-primary, #e5e7eb);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.step-skill {
  font-size: 0.625rem;
  color: var(--color-text-tertiary, #6b7280);
  font-family: monospace;
  margin-top: 0.125rem;
}

.step-controls {
  display: flex;
  gap: 0.125rem;
  opacity: 0;
  transition: opacity 0.15s;
}
.step-btn {
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--color-text-tertiary, #6b7280);
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.625rem;
  transition: all 0.1s;
}
.step-btn:hover { color: var(--color-text-primary, #fff); background: var(--color-surface-secondary, #374151); }
.step-btn-delete:hover { color: #f87171; }
</style>
