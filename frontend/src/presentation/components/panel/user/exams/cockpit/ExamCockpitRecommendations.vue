<template>
  <div class="bg-[var(--color-surface)] rounded-xl shadow-sm border border-[var(--color-border)] p-6">
    <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('examCockpit.recommendations.title') }}
    </h2>

    <div v-if="recommendations.length === 0" class="text-sm text-[var(--color-text-secondary)] italic">
      {{ t('examCockpit.recommendations.noRecommendations') }}
    </div>

    <ol v-else class="space-y-3">
      <li
        v-for="rec in recommendations"
        :key="rec.position_code"
        class="flex items-start gap-3 p-3 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)]"
      >
        <!-- Priority Badge -->
        <span
          class="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white"
          :class="severityBgClass(rec.severity)"
        >
          {{ rec.priority }}
        </span>

        <div class="min-w-0 flex-1">
          <!-- Action -->
          <p class="text-sm font-medium text-[var(--color-text)]">
            {{ rec.action }}
          </p>
          <!-- Reason -->
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ rec.reason }}
          </p>
          <!-- Proficiency bar -->
          <div class="mt-2 flex items-center gap-2">
            <div class="flex-1 h-1.5 bg-[var(--color-border)] rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="severityBarClass(rec.severity)"
                :style="{ width: `${rec.proficiency_score}%` }"
              />
            </div>
            <span class="text-xs text-[var(--color-text-secondary)] w-8 text-right">
              {{ rec.proficiency_score }}%
            </span>
          </div>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { CockpitRecommendation } from '@/infrastructure/api/clients/panel/user/exams/cockpit.api'

interface Props {
  recommendations: CockpitRecommendation[]
}

defineProps<Props>()
const { t } = useI18n()

const severityBgClass = (severity: string): string => {
  switch (severity) {
    case 'critical': return 'bg-red-600'
    case 'weak': return 'bg-orange-500'
    default: return 'bg-blue-500'
  }
}

const severityBarClass = (severity: string): string => {
  switch (severity) {
    case 'critical': return 'bg-red-500'
    case 'weak': return 'bg-orange-400'
    default: return 'bg-blue-400'
  }
}
</script>
