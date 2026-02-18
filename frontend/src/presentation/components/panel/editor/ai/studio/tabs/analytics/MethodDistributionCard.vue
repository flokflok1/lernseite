<!--
  MethodDistributionCard.vue

  Displays a horizontal bar chart of learning method usage distribution.
  Used as a sub-component of AnalyticsTab.

  Phase: KI-Studio Pro - Analytics Tab
-->

<template>
  <div class="stats-card">
    <div class="card-header">
      <span class="card-icon">🧩</span>
      <span class="card-title">{{ $t('aiEditorAnalytics.methodDistribution') }}</span>
    </div>
    <div class="method-list">
      <div
        v-for="method in visibleMethods"
        :key="method.method_type"
        class="method-item"
      >
        <div class="method-info">
          <span class="method-badge">LM{{ String(method.method_type).padStart(2, '0') }}</span>
          <span class="method-name">{{ method.method_name }}</span>
        </div>
        <div class="method-bar-container">
          <div
            class="method-bar"
            :style="{ width: getBarWidth(method.count) }"
          ></div>
          <span class="method-count">{{ method.count }}</span>
        </div>
      </div>
      <div v-if="!methods.length" class="text-sm text-[var(--color-text-tertiary)] text-center py-4">
        {{ $t('aiEditorAnalytics.noMethods') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MethodDistributionEntry } from '../composables/useAnalyticsData'

const props = defineProps<{
  methods: MethodDistributionEntry[]
}>()

const visibleMethods = computed(() => props.methods.slice(0, 8))

function getBarWidth(count: number): string {
  const max = Math.max(...props.methods.map(m => m.count), 1)
  return `${(count / max) * 100}%`
}
</script>

<style scoped>
.method-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.method-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.method-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 150px;
}

.method-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.method-name {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.method-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.method-bar {
  height: 0.5rem;
  background: var(--color-primary);
  border-radius: 0.25rem;
  min-width: 4px;
}

.method-count {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  min-width: 2rem;
  text-align: right;
}
</style>
