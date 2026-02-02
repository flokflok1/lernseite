<!--
  MarginCalculator.vue

  Reusable widget for displaying margin calculation
  Margin = (price - cost) / cost * 100

  Props:
  - cost: Provider cost per 1K tokens
  - price: Customer price per 1K tokens (optional, for display)
  - marginPercent: Pre-calculated margin (optional)
  - label: Optional label text
-->

<template>
  <div class="margin-calculator">
    <div v-if="label" class="margin-label">{{ label }}</div>
    <div class="margin-display">
      <span class="margin-value" :class="marginClass">
        {{ displayMargin }}
      </span>
      <span v-if="showIndicator" class="margin-indicator" :class="marginClass">
        {{ marginIndicator }}
      </span>
    </div>
    <div v-if="showCalculation && hasValues" class="margin-calculation">
      <span class="calc-formula">
        ({{ formatPrice(price) }} - {{ formatPrice(cost) }}) / {{ formatPrice(cost) }} × 100
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  cost?: number | null
  price?: number | null
  marginPercent?: number | null
  label?: string
  showIndicator?: boolean
  showCalculation?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cost: null,
  price: null,
  marginPercent: null,
  label: '',
  showIndicator: true,
  showCalculation: false
})

const hasValues = computed(() => {
  return props.cost !== null && props.price !== null
})

const calculatedMargin = computed(() => {
  if (props.marginPercent !== null) {
    return props.marginPercent
  }
  if (!props.cost || !props.price || props.cost === 0) {
    return null
  }
  return ((props.price - props.cost) / props.cost) * 100
})

const displayMargin = computed(() => {
  if (calculatedMargin.value === null) {
    return '-'
  }
  return `${calculatedMargin.value.toFixed(1)}%`
})

const marginClass = computed(() => {
  if (calculatedMargin.value === null) return 'margin-none'
  if (calculatedMargin.value < 0) return 'margin-negative'
  if (calculatedMargin.value < 10) return 'margin-low'
  if (calculatedMargin.value < 30) return 'margin-medium'
  return 'margin-high'
})

const marginIndicator = computed(() => {
  if (calculatedMargin.value === null) return ''
  if (calculatedMargin.value < 0) return '⚠️'
  if (calculatedMargin.value < 10) return '📉'
  if (calculatedMargin.value < 30) return '📊'
  return '📈'
})

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0.0000'
  return value.toFixed(4)
}
</script>

<style scoped>
.margin-calculator {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.margin-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.margin-display {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.margin-value {
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.margin-indicator {
  font-size: 0.75rem;
}

.margin-calculation {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  font-family: monospace;
}

/* Margin level colors */
.margin-none {
  background-color: var(--color-surface-secondary);
  color: var(--color-text-secondary);
}

.margin-negative {
  background-color: rgba(239, 68, 68, 0.15);
  color: rgb(239, 68, 68);
}

.margin-low {
  background-color: rgba(245, 158, 11, 0.15);
  color: rgb(180, 120, 0);
}

.margin-medium {
  background-color: rgba(16, 185, 129, 0.15);
  color: rgb(16, 150, 100);
}

.margin-high {
  background-color: rgba(16, 185, 129, 0.25);
  color: rgb(16, 140, 90);
}
</style>
