<template>
  <div class="progress-bar-wrapper">
    <div v-if="label" class="progress-label">
      <span class="progress-text">{{ label }}</span>
      <span v-if="showPercentage" class="progress-percentage">{{ percentage }}%</span>
    </div>
    <div :class="barClasses">
      <div
        class="progress-fill"
        :style="fillStyle"
        :aria-valuenow="percentage"
        :aria-valuemin="0"
        :aria-valuemax="100"
        role="progressbar"
      >
        <span v-if="showPercentageInside && !label" class="progress-text-inside">
          {{ percentage }}%
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  max?: number
  label?: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  showPercentage?: boolean
  showPercentageInside?: boolean
  striped?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  max: 100,
  color: 'primary',
  size: 'md',
  showPercentage: true,
  showPercentageInside: false,
  striped: false,
  animated: false,
})

const percentage = computed(() => {
  return Math.min(Math.max((props.value / props.max) * 100, 0), 100)
})

const barClasses = computed(() => {
  return [
    'progress-bar',
    `progress-${props.size}`,
    `progress-${props.color}`,
    {
      'progress-striped': props.striped,
      'progress-animated': props.animated,
    },
  ]
})

const fillStyle = computed(() => {
  return {
    width: `${percentage.value}%`,
  }
})
</script>

<style scoped>
.progress-bar-wrapper {
  width: 100%;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.progress-text {
  color: var(--color-text-primary);
  font-weight: 500;
}

.progress-percentage {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  background-color: var(--color-background-secondary);
  border-radius: 9999px;
  overflow: hidden;
  position: relative;
}

.progress-sm { height: 0.5rem; }
.progress-md { height: 1rem; }
.progress-lg { height: 1.5rem; }

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
}

.progress-text-inside {
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

/* Colors */
.progress-primary .progress-fill { background-color: var(--color-primary); }
.progress-success .progress-fill { background-color: #10b981; }
.progress-warning .progress-fill { background-color: #f59e0b; }
.progress-danger .progress-fill { background-color: #ef4444; }
.progress-info .progress-fill { background-color: #3b82f6; }

/* Striped */
.progress-striped .progress-fill {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
}

/* Animated */
.progress-animated .progress-fill {
  animation: progress-stripes 1s linear infinite;
}

@keyframes progress-stripes {
  0% { background-position: 1rem 0; }
  100% { background-position: 0 0; }
}
</style>
