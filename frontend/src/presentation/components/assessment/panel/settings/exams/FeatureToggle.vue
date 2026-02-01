<!--
  FeatureToggle - Individual Feature Toggle Item
  Sub-component of SystemFeaturesTab
-->

<template>
  <div class="feature-item" :class="{ enabled: modelValue, inherited: inherited !== null && modelValue === inherited }">
    <div class="feature-toggle">
      <input
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
        class="feature-checkbox"
      />
    </div>
    <div class="feature-code">{{ code }}</div>
    <div class="feature-info">
      <div class="feature-label">{{ label }}</div>
      <div class="feature-desc">{{ description }}</div>
    </div>
    <div class="feature-cost">
      <span class="cost-value">{{ tokenCost }}</span>
      <span class="cost-label">{{ $t('windows.aiStudioFeatures.tokens') }}</span>
    </div>
    <div v-if="inherited !== null" class="inherited-badge" :class="{ active: modelValue === inherited }">
      {{ modelValue === inherited ? $t('windows.aiStudioFeatures.inherited') : $t('windows.aiStudioFeatures.overridden') }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
  code: string
  label: string
  description: string
  tokenCost: number
  inherited?: boolean | null
}>()

defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()
</script>

<style scoped>
.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  transition: background 0.15s;
}

.feature-item:hover { background: var(--color-surface-secondary); }
.feature-item.enabled { background: rgba(16, 185, 129, 0.05); }

.feature-toggle { flex-shrink: 0; }

.feature-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.feature-code {
  width: 48px;
  font-family: monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  text-align: center;
}

.feature-info {
  flex: 1;
  min-width: 0;
}

.feature-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.feature-desc {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
}

.feature-cost {
  text-align: right;
  flex-shrink: 0;
}

.cost-value {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.cost-label {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
}

.inherited-badge {
  font-size: 0.625rem;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
}

.inherited-badge.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
}
</style>
