<!--
  AiRequestTypesCard.vue

  Displays a grid breakdown of AI request types with counts and token usage.
  Used as a sub-component of AnalyticsTab.

  Phase: KI-Studio Pro - Analytics Tab
-->

<template>
  <div v-if="requestTypes.length" class="stats-card lg:col-span-2">
    <div class="card-header">
      <span class="card-icon">📈</span>
      <span class="card-title">{{ $t('aiEditorAnalytics.aiRequestsByType') }}</span>
    </div>
    <div class="request-types-grid">
      <div
        v-for="typeInfo in requestTypes"
        :key="typeInfo.type"
        class="request-type-item"
      >
        <span class="type-name">{{ formatRequestType(typeInfo.type) }}</span>
        <span class="type-count">{{ typeInfo.count }} {{ $t('aiEditorAnalytics.requests') }}</span>
        <span class="type-tokens">{{ formatTokens(typeInfo.tokens) }} {{ $t('aiEditorAnalytics.tokens') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatTokens } from '../composables/useAnalyticsData'
import { useRequestTypeFormatter } from '../composables/useAnalyticsData'

interface RequestTypeEntry {
  type: string
  count: number
  tokens: number
}

defineProps<{
  requestTypes: RequestTypeEntry[]
}>()

const { formatRequestType } = useRequestTypeFormatter()
</script>

<style scoped>
.request-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
}

.request-type-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.type-name {
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.type-count,
.type-tokens {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
</style>
