<!--
  MethodCard - Learning Method Card
  Sub-component of LernmethodenTab
-->

<template>
  <div
    class="method-card"
    :class="{ 'has-instances': instanceCount > 0 }"
  >
    <div class="method-header">
      <span class="method-badge">LM{{ String(method.method_number).padStart(2, '0') }}</span>
      <span v-if="method.tier === 'premium'" class="premium-badge">Pro</span>
    </div>
    <h4 class="method-name">{{ method.name }}</h4>
    <p class="method-desc">{{ method.description }}</p>
    <div class="method-footer">
      <span class="method-ki">
        <span class="ki-dot" :class="method.ki_usage"></span>
        {{ formatKiUsage(method.ki_usage) }}
      </span>
      <span class="method-count">
        {{ $t('features.lernmethodenTab.instancesCount', { count: instanceCount }) }}
      </span>
    </div>
    <button
      @click="$emit('generate', method)"
      class="generate-btn"
      :disabled="!canGenerate"
    >
      {{ $t('features.lernmethodenTab.generate') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface LearningMethod {
  method_number: number
  name: string
  description: string
  tier: string
  ki_usage: string
}

defineProps<{
  method: LearningMethod
  instanceCount: number
  canGenerate: boolean
}>()

defineEmits<{
  (e: 'generate', method: LearningMethod): void
}>()

function formatKiUsage(usage: string): string {
  const key = `features.lernmethodenTab.kiUsage.${usage}`
  const translated = t(key)
  return translated !== key ? translated : usage
}
</script>

<style scoped>
.method-card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid transparent;
  border-radius: 0.5rem;
  transition: all 0.15s;
}

.method-card:hover {
  border-color: var(--color-border);
}

.method-card.has-instances {
  border-left: 3px solid var(--color-primary);
}

.method-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.method-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.premium-badge {
  padding: 0.125rem 0.375rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
}

.method-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.method-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.method-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.75rem;
}

.method-ki {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.ki-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.ki-dot.none { background: #9ca3af; }
.ki-dot.optional { background: #60a5fa; }
.ki-dot.low { background: #34d399; }
.ki-dot.medium { background: #fbbf24; }
.ki-dot.high, .ki-dot.intensive { background: #f87171; }

.generate-btn {
  width: 100%;
  padding: 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
