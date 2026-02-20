<template>
  <div class="methods-section">
    <div v-if="methods.length === 0" class="empty-message">
      <span class="empty-icon">📚</span>
      <p>{{ $t('lesson.methodExecution.noMethods') }}</p>
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
/**
 * MethodCardList Component
 * =========================
 * Grid of learning method cards with generate buttons
 */
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

// ============================================================================
// Methods
// ============================================================================

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
/* Methods Section */
.methods-section {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.empty-message {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

/* Methods List */
.methods-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Method Card */
.method-card {
  padding: 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.method-card:hover {
  border-color: var(--color-primary, #3b82f6);
}

.method-card--disabled {
  opacity: 0.6;
}

.method-card--executing {
  border-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.05);
}

/* Method Header */
.method-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.method-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.method-icon {
  font-size: 1.25rem;
}

.method-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
}

.method-badge {
  font-size: 0.625rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-basis {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.badge-premium {
  background-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.badge-pro {
  background-color: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

/* Method Description */
.method-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.75rem;
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
  gap: 0.5rem;
}

.meta-tag {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #6b7280);
}

.meta-premium {
  color: #f59e0b;
}

.generate-btn {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  min-width: 90px;
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
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Method Error */
.method-error {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: #ef4444;
}
</style>
