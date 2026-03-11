<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h1 class="text-2xl font-bold text-[var(--color-text)]">
        {{ t('examCockpit.title') }}
      </h1>

      <!-- Exam Type Selector -->
      <div class="flex items-center gap-3">
        <label
          for="exam-type-select"
          class="text-sm font-medium text-[var(--color-text-secondary)]"
        >
          {{ t('examCockpit.selectExamType') }}
        </label>
        <select
          id="exam-type-select"
          v-model="selectedExamType"
          class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          :disabled="loadingTypes"
        >
          <option
            v-for="et in examTypes"
            :key="et.key"
            :value="et.key"
          >
            {{ et.display_name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="flex items-center justify-center py-16"
      aria-live="polite"
    >
      <div class="flex items-center gap-3 text-[var(--color-text-secondary)]">
        <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="text-sm">{{ t('examCockpit.loading') }}</span>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 rounded-xl p-6 text-center"
    >
      <p class="text-sm text-red-600 dark:text-red-400">{{ t('examCockpit.error') }}</p>
      <button
        class="mt-3 text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
        @click="loadCockpitData"
      >
        {{ t('examCockpit.retry') }}
      </button>
    </div>

    <!-- Dashboard Content -->
    <template v-else-if="cockpitData">
      <!-- Readiness -->
      <ExamCockpitReadiness
        :readiness="cockpitData.overall_readiness"
        :coverage-percent="cockpitData.coverage_percent"
        :total-positions="cockpitData.total_positions"
        :gap-count="cockpitData.gap_count"
      />

      <!-- Recommendations -->
      <ExamCockpitRecommendations
        :recommendations="cockpitData.recommendations"
      />

      <!-- Strengths & Weaknesses -->
      <ExamCockpitWeaknesses
        :weaknesses="cockpitData.critical_weaknesses"
        :strengths="cockpitData.strengths"
      />

      <!-- Predictions -->
      <ExamCockpitPredictions
        :predictions="cockpitData.predictions"
      />
    </template>

    <!-- No Exam Types -->
    <div
      v-else-if="!loadingTypes && examTypes.length === 0"
      class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-8 text-center"
    >
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ t('examCockpit.noExamTypes') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchCockpitData,
  type CockpitData,
} from '@/infrastructure/api/clients/panel/user/exams/cockpit.api'
import { fetchAvailableTypes } from '@/infrastructure/api/clients/panel/user/exams/goals.api'
import {
  ExamCockpitReadiness,
  ExamCockpitRecommendations,
  ExamCockpitWeaknesses,
  ExamCockpitPredictions,
} from './cockpit'

const { t } = useI18n()

interface ExamTypeOption {
  key: string
  display_name: string
}

const examTypes = ref<ExamTypeOption[]>([])
const selectedExamType = ref('')
const cockpitData = ref<CockpitData | null>(null)
const loading = ref(false)
const loadingTypes = ref(true)
const error = ref(false)

const loadExamTypes = async () => {
  loadingTypes.value = true
  try {
    const types = await fetchAvailableTypes()
    examTypes.value = types.map((t: any) => ({
      key: t.key || t.exam_type || t,
      display_name: t.display_name || t.label || t.key || t,
    }))
    if (examTypes.value.length > 0 && !selectedExamType.value) {
      selectedExamType.value = examTypes.value[0].key
    }
  } catch {
    examTypes.value = []
  } finally {
    loadingTypes.value = false
  }
}

const loadCockpitData = async () => {
  if (!selectedExamType.value) return
  loading.value = true
  error.value = false
  cockpitData.value = null
  try {
    cockpitData.value = await fetchCockpitData(selectedExamType.value)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

watch(selectedExamType, (newVal) => {
  if (newVal) {
    loadCockpitData()
  }
})

onMounted(async () => {
  await loadExamTypes()
})
</script>
