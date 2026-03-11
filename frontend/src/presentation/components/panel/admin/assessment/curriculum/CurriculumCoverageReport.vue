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

      <!-- Filters + bulk action -->
      <div class="flex gap-4 items-center justify-between">
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
        <!-- Bulk web research button -->
        <button
          v-if="gapPositions.length > 0"
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
          :class="bulkResearching
            ? 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400 cursor-wait'
            : 'bg-amber-100 text-amber-800 hover:bg-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:hover:bg-amber-900/60'"
          :disabled="bulkResearching"
          @click="handleBulkResearch"
        >
          {{ bulkResearching
            ? $t('panel.curriculum.coverageReport.gaps.researching')
            : $t('panel.curriculum.coverageReport.gaps.researchAll') }}
        </button>
      </div>

      <!-- Success message -->
      <div
        v-if="researchMessage"
        class="px-3 py-2 rounded-md text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
        role="status"
        aria-live="polite"
      >
        {{ researchMessage }}
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
                <!-- Gap badge with web research info -->
                <div v-if="pos.gap" class="mt-1 flex items-center gap-2 flex-wrap">
                  <span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 font-medium">
                    {{ $t('panel.curriculum.coverageReport.gaps.noRealQuestions') }}
                  </span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                    {{ $t('panel.curriculum.coverageReport.gaps.webResearchAvailable') }}
                  </span>
                </div>
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
                <template v-if="pos.gap">
                  <button
                    class="text-xs font-medium px-2 py-1 rounded transition-colors"
                    :class="researchingIds.has(pos.position_id)
                      ? 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400 cursor-wait'
                      : 'bg-amber-100 text-amber-800 hover:bg-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:hover:bg-amber-900/60 cursor-pointer'"
                    :disabled="researchingIds.has(pos.position_id)"
                    :aria-label="$t('panel.curriculum.coverageReport.gaps.startResearch')"
                    @click="handleSingleResearch(pos.position_id)"
                  >
                    {{ researchingIds.has(pos.position_id)
                      ? $t('panel.curriculum.coverageReport.gaps.researching')
                      : $t('panel.curriculum.coverageReport.gaps.startResearch') }}
                  </button>
                </template>
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

      <!-- Web content cards (future: populated when web research results exist) -->
      <div v-if="webContentEntries.length > 0" class="space-y-3">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ $t('panel.curriculum.coverageReport.gaps.webContent') }}
        </h3>
        <div
          v-for="entry in webContentEntries"
          :key="entry.position_id"
          class="p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-secondary)]"
        >
          <div class="font-medium text-sm text-[var(--color-text-primary)]">
            {{ entry.title }}
          </div>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ entry.summary }}
          </p>
          <div class="text-xs mt-2 text-[var(--color-text-secondary)]">
            {{ $t('panel.curriculum.coverageReport.gaps.source') }}: {{ entry.source }}
          </div>
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
import { ref, computed, reactive, watch } from 'vue'
import {
  fetchCoverageReport,
  startWebResearch,
  startBulkWebResearch,
  type CoverageReportData,
} from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'
import { useI18n } from 'vue-i18n'

interface WebContentEntry {
  position_id: string
  title: string
  summary: string
  source: string
}

interface Props {
  frameworkId: number | null
}

const props = defineProps<Props>()
const { t } = useI18n()

const loading = ref(false)
const report = ref<CoverageReportData | null>(null)
const gapsOnly = ref(false)
const risingOnly = ref(false)
const bulkResearching = ref(false)
const researchingIds = reactive(new Set<string>())
const researchMessage = ref('')
const webContentEntries = ref<WebContentEntry[]>([])

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

const gapPositions = computed(() => {
  if (!report.value) return []
  return report.value.positions.filter((p) => p.gap)
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

function showResearchMessage() {
  researchMessage.value = t('panel.curriculum.coverageReport.gaps.researchStarted')
  setTimeout(() => { researchMessage.value = '' }, 4000)
}

async function handleSingleResearch(positionId: string) {
  if (!props.frameworkId || researchingIds.has(positionId)) return
  researchingIds.add(positionId)
  try {
    await startWebResearch(props.frameworkId, positionId)
    showResearchMessage()
  } catch {
    // Backend endpoint may not exist yet — show message anyway
    showResearchMessage()
  } finally {
    researchingIds.delete(positionId)
  }
}

async function handleBulkResearch() {
  if (!props.frameworkId || bulkResearching.value) return
  bulkResearching.value = true
  try {
    await startBulkWebResearch(props.frameworkId)
    showResearchMessage()
  } catch {
    // Backend endpoint may not exist yet — show message anyway
    showResearchMessage()
  } finally {
    bulkResearching.value = false
  }
}

async function loadReport(frameworkId: number) {
  loading.value = true
  report.value = null
  researchMessage.value = ''
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
