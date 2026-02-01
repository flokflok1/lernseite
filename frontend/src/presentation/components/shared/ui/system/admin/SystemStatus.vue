<template>
  <div class="bg-[var(--color-surface)] rounded-lg shadow-sm p-6 border border-[var(--color-border)]">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
        System Status
      </h3>
      <div class="flex items-center gap-2">
        <div
          class="w-3 h-3 rounded-full"
          :class="overallStatusClass"
        ></div>
        <span class="text-sm font-medium" :class="overallStatusTextClass">
          {{ overallStatus }}
        </span>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="space-y-3">
      <!-- Uptime -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm text-[var(--color-text-secondary)]">⏱️ Uptime</span>
        </div>
        <span class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ formattedUptime }}
        </span>
      </div>

      <!-- DB Latency -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm text-[var(--color-text-secondary)]">💾 DB Latency</span>
          <span
            class="w-2 h-2 rounded-full"
            :class="dbLatencyStatusClass"
          ></span>
        </div>
        <span class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ stats.db_latency }}ms
        </span>
      </div>

      <!-- Requests (24h) -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm text-[var(--color-text-secondary)]">📊 Requests (24h)</span>
        </div>
        <span class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ stats.request_count_24h.toLocaleString() }}
        </span>
      </div>

      <!-- Error Rate -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm text-[var(--color-text-secondary)]">⚠️ Error Rate</span>
          <span
            class="w-2 h-2 rounded-full"
            :class="errorRateStatusClass"
          ></span>
        </div>
        <span class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ stats.error_rate.toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-[var(--color-surface)] bg-opacity-75 rounded-lg flex items-center justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SystemStatsData } from '@/application/services/api/admin'

// ============================================================================
// Props
// ============================================================================

interface Props {
  stats: SystemStatsData
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// ============================================================================
// Computed
// ============================================================================

const formattedUptime = computed(() => {
  const seconds = props.stats.uptime

  if (seconds < 60) {
    return `${Math.round(seconds)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m`
  } else if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  } else {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    return `${days}d ${hours}h`
  }
})

const dbLatencyStatusClass = computed(() => {
  const latency = props.stats.db_latency
  if (latency < 50) return 'bg-green-500'
  if (latency < 100) return 'bg-yellow-500'
  return 'bg-red-500'
})

const errorRateStatusClass = computed(() => {
  const rate = props.stats.error_rate
  if (rate < 1) return 'bg-green-500'
  if (rate < 5) return 'bg-yellow-500'
  return 'bg-red-500'
})

const overallStatus = computed(() => {
  const latency = props.stats.db_latency
  const errorRate = props.stats.error_rate

  if (latency >= 100 || errorRate >= 5) return 'Degraded'
  if (latency >= 50 || errorRate >= 1) return 'Warning'
  return 'Healthy'
})

const overallStatusClass = computed(() => {
  switch (overallStatus.value) {
    case 'Healthy':
      return 'bg-green-500'
    case 'Warning':
      return 'bg-yellow-500'
    case 'Degraded':
      return 'bg-red-500'
    default:
      return 'bg-gray-500'
  }
})

const overallStatusTextClass = computed(() => {
  switch (overallStatus.value) {
    case 'Healthy':
      return 'text-green-600'
    case 'Warning':
      return 'text-yellow-600'
    case 'Degraded':
      return 'text-red-600'
    default:
      return 'text-[var(--color-text-secondary)]'
  }
})
</script>
