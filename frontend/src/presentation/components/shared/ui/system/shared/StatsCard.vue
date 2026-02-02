<template>
  <div class="bg-[var(--color-surface)] rounded-lg shadow-sm p-6 border border-[var(--color-border)]">
    <!-- Icon & Title -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center"
          :class="iconBgClass"
        >
          <span class="text-2xl">{{ icon }}</span>
        </div>
        <h3 class="text-sm font-medium text-[var(--color-text-secondary)]">
          {{ title }}
        </h3>
      </div>

      <!-- Trend Indicator (optional) -->
      <div v-if="trend !== undefined" class="flex items-center gap-1" :class="trendColorClass">
        <span v-if="trend > 0">↑</span>
        <span v-if="trend < 0">↓</span>
        <span class="text-xs font-medium">{{ Math.abs(trend) }}%</span>
      </div>
    </div>

    <!-- Main Value -->
    <div class="mb-2">
      <p class="text-3xl font-bold text-[var(--color-text-primary)]">
        {{ formattedValue }}
      </p>
    </div>

    <!-- Subtitle -->
    <p v-if="subtitle" class="text-xs text-[var(--color-text-tertiary)]">
      {{ subtitle }}
    </p>

    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-[var(--color-surface)] bg-opacity-75 rounded-lg flex items-center justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ============================================================================
// Props
// ============================================================================

interface Props {
  title: string
  value: number | string
  icon: string
  iconColor?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  subtitle?: string
  trend?: number // Percentage change (positive or negative)
  loading?: boolean
  format?: 'number' | 'percentage' | 'duration' | 'bytes'
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
  loading: false,
  format: 'number'
})

// ============================================================================
// Computed
// ============================================================================

const iconBgClass = computed(() => {
  const colorMap = {
    primary: 'bg-primary-100 text-primary-600',
    success: 'bg-green-100 text-green-600',
    warning: 'bg-yellow-100 text-yellow-600',
    danger: 'bg-red-100 text-red-600',
    info: 'bg-blue-100 text-blue-600'
  }
  return colorMap[props.iconColor] || colorMap.primary
})

const trendColorClass = computed(() => {
  if (props.trend === undefined) return ''
  return props.trend > 0
    ? 'text-green-600'
    : 'text-red-600'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value

  switch (props.format) {
    case 'percentage':
      return `${props.value.toFixed(2)}%`
    case 'duration':
      return formatDuration(props.value)
    case 'bytes':
      return formatBytes(props.value)
    default:
      return props.value.toLocaleString()
  }
})

// ============================================================================
// Methods
// ============================================================================

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m`
  } else if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600)
    return `${hours}h`
  } else {
    const days = Math.floor(seconds / 86400)
    return `${days}d`
  }
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`
}
</script>
