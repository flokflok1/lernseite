<template>
  <div class="progress-ring-wrapper relative inline-flex items-center justify-center" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" class="transform -rotate-90">
      <!-- Background circle -->
      <circle
        :cx="center" :cy="center" :r="radius"
        fill="none" :stroke-width="strokeWidth"
        :class="dark ? 'text-white/20' : 'text-gray-200 dark:text-gray-700'"
        stroke="currentColor"
      />
      <!-- Progress arc -->
      <circle
        :cx="center" :cy="center" :r="radius"
        fill="none" :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        stroke-linecap="round"
        :class="arcColorClass"
        stroke="currentColor"
        class="transition-all duration-700 ease-out"
      />
    </svg>
    <!-- Center text -->
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span :class="['font-extrabold leading-none', textSizeClass, textColorClass]">
        {{ percentage }}%
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  percentage: number
  size?: number
  strokeWidth?: number
  dark?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 72,
  strokeWidth: 5,
  dark: false
})

const center = computed(() => props.size / 2)
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)

const dashOffset = computed(() => {
  const clamped = Math.min(100, Math.max(0, props.percentage))
  return circumference.value * (1 - clamped / 100)
})

const arcColorClass = computed(() => {
  if (props.dark) {
    if (props.percentage >= 100) return 'text-green-400'
    if (props.percentage > 0) return 'text-white'
    return 'text-white/30'
  }
  if (props.percentage >= 100) return 'text-green-500 dark:text-green-400'
  if (props.percentage > 0) return 'text-blue-500 dark:text-blue-400'
  return 'text-gray-300 dark:text-gray-600'
})

const textColorClass = computed(() => {
  if (props.dark) return 'text-white'
  if (props.percentage >= 100) return 'text-green-600 dark:text-green-400'
  return 'text-gray-900 dark:text-white'
})

const textSizeClass = computed(() => {
  if (props.size >= 80) return 'text-xl'
  if (props.size >= 64) return 'text-base'
  return 'text-xs'
})
</script>
