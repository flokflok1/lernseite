<template>
  <div class="analytics-kpi-card bg-white rounded-lg shadow-sm p-6 border border-gray-200">
    <!-- Icon & Trend -->
    <div class="flex items-center justify-between mb-3">
      <span v-if="icon" class="text-3xl">{{ icon }}</span>
      <div v-if="trend" class="flex items-center gap-1 text-sm font-medium"
        :class="{
          'text-green-600': trend === 'up',
          'text-red-600': trend === 'down',
          'text-gray-600': trend === 'neutral'
        }"
      >
        <span v-if="trend === 'up'">↑</span>
        <span v-else-if="trend === 'down'">↓</span>
        <span v-else>→</span>
        <span v-if="trendValue">{{ Math.abs(trendValue) }}%</span>
      </div>
    </div>

    <!-- Value -->
    <div class="mb-2">
      <p class="text-3xl font-bold text-gray-900">
        {{ formattedValue }}
      </p>
    </div>

    <!-- Label -->
    <p class="text-sm text-gray-600 mb-1">{{ label }}</p>

    <!-- Description -->
    <p v-if="description" class="text-xs text-gray-500 mt-2">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ============================================================================
// Props
// ============================================================================

interface Props {
  label: string
  value: string | number
  description?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: number
  icon?: string
  format?: 'number' | 'percent' | 'currency' | 'none'
}

const props = withDefaults(defineProps<Props>(), {
  format: 'none'
})

// ============================================================================
// Computed
// ============================================================================

const formattedValue = computed(() => {
  if (typeof props.value === 'string') {
    return props.value
  }

  switch (props.format) {
    case 'number':
      return new Intl.NumberFormat('de-DE').format(props.value)
    case 'percent':
      return `${props.value}%`
    case 'currency':
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(props.value)
    default:
      return props.value
  }
})
</script>
