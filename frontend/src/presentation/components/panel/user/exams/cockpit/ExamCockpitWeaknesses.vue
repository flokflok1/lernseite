<template>
  <div class="bg-[var(--color-surface)] rounded-xl shadow-sm border border-[var(--color-border)] p-6">
    <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('panel.examCockpit.weaknesses.title') }}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Critical Weaknesses -->
      <div>
        <h3 class="text-sm font-semibold text-red-500 mb-3">
          {{ t('panel.examCockpit.weaknesses.critical') }}
        </h3>

        <div v-if="weaknesses.length === 0" class="text-xs text-[var(--color-text-secondary)] italic">
          {{ t('panel.examCockpit.weaknesses.noCritical') }}
        </div>

        <ul v-else class="space-y-3">
          <li
            v-for="item in weaknesses"
            :key="item.position_id"
            class="p-3 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-[var(--color-text)]">
                {{ item.position_code }} - {{ item.position_title }}
              </span>
              <span class="text-xs font-bold text-red-600">
                {{ item.proficiency_score }}%
              </span>
            </div>
            <!-- Proficiency bar -->
            <div class="h-1.5 bg-red-100 dark:bg-red-900/20 rounded-full overflow-hidden">
              <div
                class="h-full bg-red-500 rounded-full transition-all duration-500"
                :style="{ width: `${item.proficiency_score}%` }"
              />
            </div>
            <!-- Peer comparison -->
            <p
              v-if="item.peer_comparison"
              class="text-xs text-[var(--color-text-secondary)] mt-1"
            >
              {{ t('panel.examCockpit.weaknesses.peerComparison', {
                percentile: Math.round(item.peer_comparison.percentile * 100),
              }) }}
            </p>
          </li>
        </ul>
      </div>

      <!-- Strengths -->
      <div>
        <h3 class="text-sm font-semibold text-green-500 mb-3">
          {{ t('panel.examCockpit.weaknesses.strengths') }}
        </h3>

        <div v-if="strengths.length === 0" class="text-xs text-[var(--color-text-secondary)] italic">
          {{ t('panel.examCockpit.weaknesses.noStrengths') }}
        </div>

        <ul v-else class="space-y-3">
          <li
            v-for="item in strengths"
            :key="item.position_id"
            class="p-3 rounded-lg bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800/30"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-[var(--color-text)]">
                {{ item.position_code }} - {{ item.position_title }}
              </span>
              <span class="text-xs font-bold text-green-600">
                {{ item.proficiency_score }}%
              </span>
            </div>
            <!-- Proficiency bar -->
            <div class="h-1.5 bg-green-100 dark:bg-green-900/20 rounded-full overflow-hidden">
              <div
                class="h-full bg-green-500 rounded-full transition-all duration-500"
                :style="{ width: `${item.proficiency_score}%` }"
              />
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { CockpitWeaknessEntry } from '@/infrastructure/api/clients/panel/user/exams/cockpit.api'

interface Props {
  weaknesses: CockpitWeaknessEntry[]
  strengths: CockpitWeaknessEntry[]
}

defineProps<Props>()
const { t } = useI18n()
</script>
