<!--
  StatsCard - Reusable Analytics Card
  Sub-component of AnalyticsTab
-->

<template>
  <div class="stats-card" :class="{ 'lg:col-span-2': fullWidth }">
    <!-- Header -->
    <div class="card-header">
      <span class="card-icon">{{ icon }}</span>
      <span class="card-title">{{ title }}</span>
    </div>

    <!-- Content Slot -->
    <div class="card-content">
      <slot></slot>
    </div>

    <!-- Footer Slot -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  fullWidth?: boolean
}>()
</script>

<style scoped>
.stats-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.card-icon {
  font-size: 1.25rem;
}

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
}

.card-content {
  padding: 1rem;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}
</style>
