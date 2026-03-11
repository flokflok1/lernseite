<template>
  <div class="bg-[var(--color-surface)] rounded-xl shadow-sm border border-[var(--color-border)] p-6">
    <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('examCockpit.predictions.title') }}
    </h2>

    <div v-if="predictions.length === 0" class="text-sm text-[var(--color-text-secondary)] italic">
      {{ t('examCockpit.predictions.noPredictions') }}
    </div>

    <ul v-else class="space-y-3">
      <li
        v-for="pred in predictions"
        :key="pred.position_id"
        class="p-3 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)]"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-sm font-medium text-[var(--color-text)]">
            {{ pred.position_code }} - {{ pred.position_title }}
          </span>
          <span
            class="text-xs font-medium px-2 py-0.5 rounded-full"
            :class="confidenceBadgeClass(pred.confidence)"
          >
            {{ confidenceLabel(pred.confidence) }}
          </span>
        </div>

        <!-- Probability bar -->
        <div class="flex items-center gap-2 mt-2">
          <div class="flex-1 h-2 bg-[var(--color-border)] rounded-full overflow-hidden">
            <div
              class="h-full bg-indigo-500 rounded-full transition-all duration-500"
              :style="{ width: `${Math.round(pred.probability * 100)}%` }"
            />
          </div>
          <span class="text-xs font-semibold text-indigo-600 dark:text-indigo-400 w-12 text-right">
            {{ t('examCockpit.predictions.probability', {
              percent: Math.round(pred.probability * 100),
            }) }}
          </span>
        </div>

        <!-- Reasoning -->
        <p v-if="pred.reasoning" class="text-xs text-[var(--color-text-secondary)] mt-2">
          {{ pred.reasoning }}
        </p>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { CockpitPrediction } from '@/infrastructure/api/clients/panel/user/exams/cockpit.api'

interface Props {
  predictions: CockpitPrediction[]
}

defineProps<Props>()
const { t } = useI18n()

const confidenceBadgeClass = (confidence: string): string => {
  switch (confidence) {
    case 'high': return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
    case 'medium': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
    default: return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
}

const confidenceLabel = (confidence: string): string => {
  switch (confidence) {
    case 'high': return t('examCockpit.predictions.confidenceHigh')
    case 'medium': return t('examCockpit.predictions.confidenceMedium')
    default: return t('examCockpit.predictions.confidenceLow')
  }
}
</script>
