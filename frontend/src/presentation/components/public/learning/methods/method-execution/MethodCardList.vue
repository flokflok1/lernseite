<template>
  <div class="methods-section">
    <div v-if="methods.length === 0" class="empty-state">
      <div class="empty-icon-wrap">
        <svg class="empty-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <p class="empty-title">{{ $t('lesson.methodExecution.noMethods') }}</p>
      <p class="empty-hint">{{ $t('lesson.methodExecution.noMethodsHint') }}</p>
    </div>

    <div v-else class="methods-list">
      <div
        v-for="method in methods"
        :key="method.method_id"
        class="method-card"
        :class="{
          'method-card--disabled': !canExecute(method),
          'method-card--executing': isExecuting && executingMethodId === method.method_id
        }"
      >
        <!-- Method Header -->
        <div class="method-top">
          <div class="method-title-row">
            <span class="method-icon">{{ getIcon(method) }}</span>
            <span class="method-name">{{ getName(method) }}</span>
          </div>
          <span class="method-badge" :class="getTierBadgeClass(method)">
            {{ getTierLabel(method) }}
          </span>
        </div>

        <!-- Method Description -->
        <p v-if="method.description" class="method-desc">
          {{ method.description }}
        </p>

        <!-- Method Footer -->
        <div class="method-bottom">
          <div class="method-meta">
            <span class="meta-tag">
              {{ $t('lesson.methodExecution.estimatedTokens', { tokens: method.estimated_tokens || 100 }) }}
            </span>
            <span v-if="method.tier === 'premium'" class="meta-tag meta-premium">
              {{ $t('lesson.methodExecution.premiumOnly') }}
            </span>
          </div>

          <button
            @click="handleGenerate(method)"
            class="generate-btn"
            :disabled="!canExecute(method) || isExecuting"
          >
            <span v-if="isExecuting && executingMethodId === method.method_id" class="spinner"></span>
            <span v-else>{{ $t('lesson.methodExecution.generate') }}</span>
          </button>
        </div>

        <!-- Error Message (if any) -->
        <p v-if="method.error" class="method-error">
          {{ method.error }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { LearningMethod } from '@/domain/models/learning/types'

interface Props {
  methods: LearningMethod[]
  isExecuting: boolean
  executingMethodId?: string
  getIcon: (method: LearningMethod) => string
  getName: (method: LearningMethod) => string
  canExecute: (method: LearningMethod) => boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'generate': [method: LearningMethod]
}>()

const { t } = useI18n()

function handleGenerate(method: LearningMethod): void {
  emit('generate', method)
}

function getTierBadgeClass(method: LearningMethod): string {
  const tier = method.tier || 'basic'
  if (tier === 'premium') return 'badge-premium'
  if (tier === 'pro') return 'badge-pro'
  return 'badge-basis'
}

function getTierLabel(method: LearningMethod): string {
  const tier = method.tier || 'basic'
  return t(`lesson.methodExecution.tiers.${tier}`)
}
</script>

<style scoped>
.methods-section {
  flex: 1;
  overflow-y: auto;
  padding: 0.625rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 1.5rem 1rem;
}

.empty-icon-wrap {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  background-color: var(--color-surface-secondary, #f3f4f6);
}

:root.dark .empty-icon-wrap {
  background-color: rgba(255, 255, 255, 0.08);
}

.empty-svg {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-text-secondary, #9ca3af);
}

.empty-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #374151);
  margin: 0 0 0.25rem;
}

.empty-hint {
  font-size: 0.6875rem;
  color: var(--color-text-secondary, #9ca3af);
  margin: 0;
  line-height: 1.4;
}

/* Methods List */
.methods-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Method Card */
.method-card {
  padding: 0.625rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

:root.dark .method-card {
  background-color: #1f2937;
  border-color: #374151;
}

.method-card:hover {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
  transform: translateY(-1px);
}

.method-card--disabled {
  opacity: 0.6;
}

.method-card--disabled:hover {
  transform: none;
  box-shadow: none;
}

.method-card--executing {
  border-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.04);
}

/* Method Header */
.method-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.375rem;
}

.method-title-row {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.method-icon { font-size: 0.875rem; }

.method-name {
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--color-text-primary, #111827);
}

.method-badge {
  font-size: 0.5625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-basis {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.badge-premium {
  background-color: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}

.badge-pro {
  background-color: rgba(139, 92, 246, 0.12);
  color: #8b5cf6;
}

/* Method Description */
.method-desc {
  font-size: 0.6875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

/* Method Footer */
.method-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.method-meta {
  display: flex;
  gap: 0.375rem;
}

.meta-tag {
  font-size: 0.625rem;
  color: var(--color-text-secondary, #6b7280);
}

.meta-premium { color: #f59e0b; }

.generate-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  border-radius: 0.375rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  min-width: 5rem;
  justify-content: center;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Spinner */
.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Method Error */
.method-error {
  margin: 0.375rem 0 0;
  font-size: 0.6875rem;
  color: #ef4444;
}
</style>
