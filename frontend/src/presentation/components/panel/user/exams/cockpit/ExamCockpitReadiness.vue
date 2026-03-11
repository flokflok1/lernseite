<template>
  <div class="bg-[var(--color-surface)] rounded-xl shadow-sm border border-[var(--color-border)] p-6">
    <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('examCockpit.readiness.title') }}
    </h2>

    <div class="flex items-center gap-6">
      <!-- Readiness Circle -->
      <div class="relative w-28 h-28 flex-shrink-0">
        <svg class="w-28 h-28 -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60" cy="60" r="52"
            fill="none"
            stroke="var(--color-border)"
            stroke-width="10"
          />
          <circle
            cx="60" cy="60" r="52"
            fill="none"
            :stroke="readinessColor"
            stroke-width="10"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            class="transition-all duration-700 ease-out"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-2xl font-bold" :style="{ color: readinessColor }">
            {{ readiness }}%
          </span>
        </div>
      </div>

      <!-- Coverage Info -->
      <div class="space-y-2">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('examCockpit.readiness.positionsCovered', {
            covered: coveredPositions,
            total: totalPositions,
          }) }}
        </p>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('examCockpit.readiness.gaps', { count: gapCount }) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  readiness: number
  coveragePercent: number
  totalPositions: number
  gapCount: number
}

const props = defineProps<Props>()
const { t } = useI18n()

const circumference = 2 * Math.PI * 52
const dashOffset = computed(() => circumference - (props.readiness / 100) * circumference)

const coveredPositions = computed(() =>
  Math.round((props.coveragePercent / 100) * props.totalPositions)
)

const readinessColor = computed(() => {
  if (props.readiness > 70) return '#22c55e'
  if (props.readiness >= 40) return '#eab308'
  return '#ef4444'
})
</script>
