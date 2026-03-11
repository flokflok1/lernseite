<template>
  <div class="space-y-4">
    <!-- No framework selected -->
    <div
      v-if="!frameworkId"
      class="text-center py-12 text-[var(--color-text-secondary)]"
    >
      <p class="text-sm">{{ $t('panel.curriculum.coverageReport.noFramework') }}</p>
    </div>

    <!-- Loading -->
    <div
      v-else-if="loading"
      class="flex items-center justify-center py-12"
      aria-live="polite"
    >
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]" />
      <span class="ml-3 text-sm text-[var(--color-text-secondary)]">
        {{ $t('panel.curriculum.coverageReport.loading') }}
      </span>
    </div>

    <!-- Data loaded -->
    <template v-else-if="report">
      <!-- Summary header -->
      <div class="grid grid-cols-3 gap-3">
        <div
          class="p-3 rounded-lg text-center"
          style="background-color: var(--color-info-bg, #eff6ff);"
        >
          <div class="text-xl font-bold" style="color: var(--color-info-text, #2563eb);">
            {{ report.summary.coverage_percent }}%
          </div>
          <div class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('panel.curriculum.coverageReport.summary', {
              covered: report.summary.covered_positions,
              total: report.summary.total_positions,
              percent: report.summary.coverage_percent
            }) }}
          </div>
        </div>
        <div
          class="p-3 rounded-lg text-center"
          style="background-color: var(--color-error-bg, #fef2f2);"
        >
          <div class="text-xl font-bold" style="color: var(--color-error-text, #dc2626);">
            {{ report.summary.gap_positions }}
          </div>
          <div class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('panel.curriculum.coverageReport.gaps', { count: report.summary.gap_positions }) }}
          </div>
        </div>
        <div
          class="p-3 rounded-lg text-center"
          style="background-color: var(--color-warning-bg, #fef3c7);"
        >
          <div class="text-xl font-bold" style="color: var(--color-warning-text, #92400e);">
            {{ report.summary.low_confidence_count }}
          </div>
          <div class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('panel.curriculum.coverageReport.lowConfidence', { count: report.summary.low_confidence_count }) }}
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex gap-4 items-center">
        <label class="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] cursor-pointer">
          <input
            v-model="gapsOnly"
            type="checkbox"
            class="rounded border-[var(--color-border)]"
          />
          {{ $t('panel.curriculum.coverageReport.filters.gapsOnly') }}
        </label>
        <label class="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] cursor-pointer">
          <input
            v-model="risingOnly"
            type="checkbox"
            class="rounded border-[var(--color-border)]"
          />
          {{ $t('panel.curriculum.coverageReport.filters.risingOnly') }}
        </label>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto border border-[var(--color-border)] rounded-lg">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-[var(--color-surface-secondary)] text-left text-[var(--color-text-secondary)]">
              <th class="px-3 py-2 font-medium">{{ $t('panel.curriculum.coverageReport.columns.position') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.questions') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.objectives') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.coverage') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.relevance') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.trend') }}</th>
              <th class="px-3 py-2 font-medium text-center">{{ $t('panel.curriculum.coverageReport.columns.gap') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="pos in filteredPositions"
              :key="pos.position_id"
              class="border-t border-[var(--color-border)] transition-colors"
              :class="pos.gap ? 'bg-red-50 dark:bg-red-950/20' : 'hover:bg-[var(--color-surface-secondary)]'"
            >
              <td class="px-3 py-2">
                <span class="font-medium text-[var(--color-text-primary)]">{{ pos.code }}</span>
                <span class="ml-2 text-[var(--color-text-secondary)]">{{ pos.title }}</span>
              </td>
              <td class="px-3 py-2 text-center text-[var(--color-text-primary)]">{{ pos.question_count }}</td>
              <td class="px-3 py-2 text-center text-[var(--color-text-primary)]">{{ pos.objective_count }}</td>
              <td class="px-3 py-2 text-center">
                <span
                  class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                  :class="coverageClass(pos.coverage_percent)"
                >
                  {{ pos.coverage_percent }}%
                </span>
              </td>
              <td class="px-3 py-2 text-center text-[var(--color-text-primary)]">
                {{ pos.relevance_score.toFixed(2) }}
              </td>
              <td class="px-3 py-2 text-center">
                <span :title="pos.trend">{{ trendArrow(pos.trend) }}</span>
              </td>
              <td class="px-3 py-2 text-center">
                <span
                  v-if="pos.gap"
                  class="text-xs font-medium"
                  style="color: var(--color-error-text, #dc2626);"
                >
                  {{ $t('panel.curriculum.coverageReport.gapYes') }}
                </span>
                <span
                  v-else
                  class="text-xs text-[var(--color-text-secondary)]"
                >
                  {{ $t('panel.curriculum.coverageReport.gapNo') }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div
          v-if="filteredPositions.length === 0"
          class="p-6 text-center text-sm text-[var(--color-text-secondary)]"
        >
          {{ $t('panel.curriculum.coverageReport.empty') }}
        </div>
      </div>
    </template>

    <!-- Empty / error fallback -->
    <div
      v-else
      class="text-center py-12 text-sm text-[var(--color-text-secondary)]"
    >
      {{ $t('panel.curriculum.coverageReport.empty') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { fetchCoverageReport, type CoverageReportData } from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

interface Props {
  frameworkId: number | null
}

const props = defineProps<Props>()

const loading = ref(false)
const report = ref<CoverageReportData | null>(null)
const gapsOnly = ref(false)
const risingOnly = ref(false)

const filteredPositions = computed(() => {
  if (!report.value) return []
  let positions = report.value.positions
  if (gapsOnly.value) {
    positions = positions.filter((p) => p.gap)
  }
  if (risingOnly.value) {
    positions = positions.filter((p) => p.trend === 'rising')
  }
  return positions
})

function trendArrow(trend: string): string {
  if (trend === 'rising') return '\u2191'
  if (trend === 'declining') return '\u2193'
  return '\u2192'
}

function coverageClass(percent: number): string {
  if (percent >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
  if (percent >= 50) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
}

async function loadReport(frameworkId: number) {
  loading.value = true
  report.value = null
  try {
    report.value = await fetchCoverageReport(frameworkId)
  } catch {
    report.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => props.frameworkId,
  (id) => {
    if (id) {
      loadReport(id)
    } else {
      report.value = null
    }
  },
  { immediate: true },
)
</script>
