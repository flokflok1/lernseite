<!--
  CurriculumMappingPanel — Shows exam-type linking, auto-mapping,
  coverage details per position, and relevance data.
-->

<template>
  <div class="space-y-4">
    <!-- Exam Type Linking -->
    <div class="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-surface-secondary)] border border-[var(--color-border)]">
      <label class="text-sm font-medium text-[var(--color-text-primary)] shrink-0">
        {{ t('panel.curriculum.mapping.examType') }}
      </label>
      <select
        v-model="selectedExamType"
        class="flex-1 px-3 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
      >
        <option value="">{{ t('panel.curriculum.mapping.selectExamType') }}</option>
        <option v-for="et in examTypes" :key="et.exam_type" :value="et.exam_type">
          {{ et.display_name?.[locale] || et.exam_type }}
        </option>
      </select>
      <button
        :disabled="!selectedExamType || linking"
        class="px-3 py-1.5 text-sm text-white rounded transition-colors disabled:opacity-50"
        style="background-color: var(--color-primary, #7c3aed);"
        @click="handleLink"
      >
        {{ linking ? '...' : t('panel.curriculum.mapping.link') }}
      </button>
      <button
        :disabled="!selectedExamType || mapping"
        class="px-3 py-1.5 text-sm text-white rounded transition-colors disabled:opacity-50"
        style="background-color: var(--color-success, #16a34a);"
        @click="handleAutoMap"
      >
        {{ mapping ? t('panel.curriculum.mapping.mapping') : t('panel.curriculum.mapping.autoMap') }}
      </button>
    </div>

    <!-- Link Success -->
    <div
      v-if="linkSuccess && !mapResult"
      class="p-3 rounded-lg text-sm border bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-700 dark:text-green-300"
    >
      {{ t('panel.curriculum.mapping.linkSuccess') }}
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="p-3 rounded-lg text-sm border bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-700 dark:text-red-300"
    >
      {{ error }}
    </div>

    <!-- Auto-Map Results -->
    <div
      v-if="mapResult"
      class="p-3 rounded-lg text-sm border"
      :class="mapResult.errors > 0
        ? 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-900/20 dark:border-amber-700 dark:text-amber-300'
        : 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-700 dark:text-green-300'"
    >
      {{ t('panel.curriculum.mapping.mapResult', {
        mapped: mapResult.mapped,
        skipped: mapResult.skipped,
        errors: mapResult.errors
      }) }}
    </div>

    <!-- Coverage Detail Table -->
    <div v-if="positions.length" class="border border-[var(--color-border)] rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-[var(--color-surface-secondary)] text-left">
            <th class="px-3 py-2 font-medium text-[var(--color-text-secondary)]">
              {{ t('panel.curriculum.mapping.position') }}
            </th>
            <th class="px-3 py-2 font-medium text-[var(--color-text-secondary)] text-center w-20">
              {{ t('panel.curriculum.mapping.objectives') }}
            </th>
            <th class="px-3 py-2 font-medium text-[var(--color-text-secondary)] text-center w-20">
              {{ t('panel.curriculum.mapping.questions') }}
            </th>
            <th class="px-3 py-2 font-medium text-[var(--color-text-secondary)] text-center w-28">
              {{ t('panel.curriculum.mapping.relevance') }}
            </th>
            <th class="px-3 py-2 font-medium text-[var(--color-text-secondary)] text-center w-20">
              {{ t('panel.curriculum.mapping.trend') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pos in positions"
            :key="pos.position_id"
            class="border-t border-[var(--color-border)] hover:bg-[var(--color-surface-secondary)] transition-colors"
          >
            <td class="px-3 py-2">
              <span class="font-mono text-xs text-[var(--color-info-text,#2563eb)] mr-1.5">
                {{ pos.section_code }}.{{ pos.position_code }}
              </span>
              <span class="text-[var(--color-text-primary)]">{{ positionTitle(pos) }}</span>
            </td>
            <td class="px-3 py-2 text-center text-[var(--color-text-secondary)]">
              {{ pos.objective_count }}
            </td>
            <td class="px-3 py-2 text-center">
              <span
                class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                :class="pos.question_count > 0
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'"
              >
                {{ pos.question_count }}
              </span>
            </td>
            <td class="px-3 py-2 text-center">
              <template v-if="relevanceMap[pos.position_id]">
                <div class="flex items-center justify-center gap-1">
                  <div
                    class="h-2 rounded-full bg-[var(--color-primary,#7c3aed)]"
                    :style="{ width: Math.max(relevanceMap[pos.position_id].appearance_rate * 60, 4) + 'px' }"
                  />
                  <span class="text-xs text-[var(--color-text-secondary)]">
                    {{ Math.round(relevanceMap[pos.position_id].appearance_rate * 100) }}%
                  </span>
                </div>
              </template>
              <span v-else class="text-xs text-[var(--color-text-secondary)]">—</span>
            </td>
            <td class="px-3 py-2 text-center">
              <template v-if="relevanceMap[pos.position_id]?.trend">
                <span class="text-xs" :class="trendClass(relevanceMap[pos.position_id].trend)">
                  {{ trendIcon(relevanceMap[pos.position_id].trend) }}
                  {{ t(`panel.curriculum.mapping.trend_${relevanceMap[pos.position_id].trend}`) }}
                </span>
              </template>
              <span v-else class="text-xs text-[var(--color-text-secondary)]">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div
      v-if="!positions.length && !loading"
      class="text-center py-8 text-sm text-[var(--color-text-secondary)]"
    >
      {{ t('panel.curriculum.mapping.noData') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchExamTypes } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import type { ExamType } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import type { CoveragePositionDetail, RelevanceEntry } from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'
import { useCurriculum } from '../composables'

interface Props {
  frameworkId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{ refresh: [] }>()
const { t, locale } = useI18n()

const {
  coverage,
  relevance,
  loading,
  error,
  loadMappingData,
  linkToExamType,
  runAutoMap,
} = useCurriculum()

const examTypes = ref<ExamType[]>([])
const selectedExamType = ref('')
const linking = ref(false)
const mapping = ref(false)
const linkSuccess = ref(false)
const mapResult = ref<{ mapped: number; skipped: number; errors: number } | null>(null)

const positions = computed<CoveragePositionDetail[]>(
  () => coverage.value?.positions || [],
)

const relevanceMap = computed<Record<number, RelevanceEntry>>(() => {
  const map: Record<number, RelevanceEntry> = {}
  for (const r of relevance.value) {
    map[r.position_id] = r
  }
  return map
})

async function loadData() {
  await loadMappingData(props.frameworkId)
}

async function handleLink() {
  if (!selectedExamType.value) return
  linking.value = true
  linkSuccess.value = false
  const ok = await linkToExamType(props.frameworkId, selectedExamType.value)
  linkSuccess.value = ok
  linking.value = false
}

async function handleAutoMap() {
  if (!selectedExamType.value) return
  mapping.value = true
  mapResult.value = null
  const stats = await runAutoMap(selectedExamType.value)
  if (stats) {
    mapResult.value = stats
    await loadData()
    emit('refresh')
  }
  mapping.value = false
}

function positionTitle(pos: CoveragePositionDetail): string {
  const title = pos.position_title
  if (typeof title === 'object' && title !== null) {
    return (title as Record<string, string>)[locale.value]
      || (title as Record<string, string>)['de']
      || Object.values(title)[0] || ''
  }
  try {
    const parsed = JSON.parse(String(title))
    if (typeof parsed === 'object') return parsed[locale.value] || parsed['de'] || ''
    return String(parsed)
  } catch {
    return String(title || '')
  }
}

function trendIcon(trend: string): string {
  if (trend === 'rising') return '\u2191'
  if (trend === 'declining') return '\u2193'
  return '\u2192'
}

function trendClass(trend: string): string {
  if (trend === 'rising') return 'text-red-600 dark:text-red-400 font-medium'
  if (trend === 'declining') return 'text-green-600 dark:text-green-400'
  return 'text-[var(--color-text-secondary)]'
}

onMounted(async () => {
  const [typesResult] = await Promise.allSettled([fetchExamTypes()])
  if (typesResult.status === 'fulfilled') {
    examTypes.value = typesResult.value
  }
  await loadData()
})

watch(() => props.frameworkId, () => {
  linkSuccess.value = false
  mapResult.value = null
  selectedExamType.value = ''
  loadData()
})
</script>
