<!--
  ExamTab — Exam course generation tab in the Unified AI Editor.
  Two-level selector: Program (Beruf/Zertifizierung) → Part (AP1, AP2, etc.)
  Sections: AI Cluster Intelligence + Course Generation.
-->
<template>
  <div class="h-full overflow-y-auto p-4 space-y-6">
    <!-- Program + Part + Region Selector -->
    <div class="grid grid-cols-3 gap-3">
      <div>
        <label class="block text-[10px] font-medium text-[var(--color-text-secondary)] mb-1">
          {{ t('aiEditor.exam.selectProgram') }}
        </label>
        <select
          v-model="selectedProgramKey"
          class="w-full px-2.5 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-xs"
          @change="handleProgramChange"
        >
          <option v-for="p in programs" :key="p.program_key" :value="p.program_key">
            {{ p.icon }} {{ p.display_name?.[locale] || p.program_key }}
          </option>
        </select>
      </div>
      <div>
        <label class="block text-[10px] font-medium text-[var(--color-text-secondary)] mb-1">
          {{ t('aiEditor.exam.selectPart') }}
        </label>
        <select
          v-model="selectedExamType"
          class="w-full px-2.5 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-xs"
          @change="handlePartChange"
        >
          <option v-for="part in currentParts" :key="part.exam_type" :value="part.exam_type">
            {{ part.display_name?.[locale] || part.exam_type }}
          </option>
        </select>
      </div>
      <div>
        <label class="block text-[10px] font-medium text-[var(--color-text-secondary)] mb-1">
          {{ t('panel.examCourseGenerator.selectRegion') }}
        </label>
        <select
          v-model="region"
          class="w-full px-2.5 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-xs"
        >
          <option v-for="r in regions" :key="r.region_code" :value="r.region_code">
            {{ t(`exams.regions.${r.region_code}`, r.display_name?.[locale] || r.region_code) }}
          </option>
        </select>
      </div>
    </div>

    <!-- Cluster Intelligence -->
    <ExamClusterSuggestion
      :clusters="exam.existingClusters.value"
      :suggestion="exam.suggestion.value"
      :suggesting="exam.suggestingClusters.value"
      :applying="exam.applyingClusters.value"
      :error="exam.clusterError.value"
      @suggest="handleSuggestClusters"
      @apply="handleApplyClusters"
    />

    <!-- Divider -->
    <div class="border-t border-[var(--color-border)]" />

    <!-- Course Generation -->
    <ExamCourseWorkflow
      :plan="exam.plan.value"
      :result="exam.result.value"
      :progress="exam.progress.value"
      :progress-percent="exam.progressPercent.value"
      :previewing="exam.previewing.value"
      :generating="exam.generating.value"
      :error="exam.courseError.value"
      @preview="handlePreview"
      @generate="handleGenerate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useExamCourse } from '../composables/editor/useExamCourse'
import ExamClusterSuggestion from './exam/ExamClusterSuggestion.vue'
import ExamCourseWorkflow from './exam/ExamCourseWorkflow.vue'
import { fetchPrograms } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import type { ExamProgram, ExamType } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import { archiveListRegions } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import type { ExamRegion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

const { t, locale } = useI18n()
const exam = useExamCourse()

const modelSelector = inject<any>('modelSelector')
const onCourseCreated = inject<((courseId: string, courseTitle: string) => void) | undefined>('onCourseCreated', undefined)

const programs = ref<ExamProgram[]>([])
const selectedProgramKey = ref('')
const selectedExamType = ref('')
const regions = ref<ExamRegion[]>([])
const region = ref('alle')

const currentParts = computed<ExamType[]>(() => {
  const prog = programs.value.find(p => p.program_key === selectedProgramKey.value)
  return prog?.parts || []
})

onMounted(async () => {
  const [programsResult, regionsResult] = await Promise.allSettled([
    fetchPrograms(),
    archiveListRegions(),
  ])

  if (programsResult.status === 'fulfilled' && programsResult.value.length > 0) {
    programs.value = programsResult.value
    // Select first program (sorted by sort_order from DB)
    const firstProg = programsResult.value[0]
    selectedProgramKey.value = firstProg.program_key
    if (firstProg.parts.length > 0) {
      selectedExamType.value = firstProg.parts[0].exam_type
      exam.loadClusters(selectedExamType.value)
    }
  }

  if (regionsResult.status === 'fulfilled') {
    regions.value = regionsResult.value
  }
})

function handleProgramChange() {
  const parts = currentParts.value
  if (parts.length > 0) {
    selectedExamType.value = parts[0].exam_type
    exam.loadClusters(selectedExamType.value)
  } else {
    selectedExamType.value = ''
  }
}

function handlePartChange() {
  if (selectedExamType.value) {
    exam.loadClusters(selectedExamType.value)
  }
}

function getModelOptions() {
  if (!modelSelector) return undefined
  const p = modelSelector.selectedProvider?.value
  const m = modelSelector.selectedModel?.value
  return p && m ? { provider: p, model: m } : undefined
}

function handleSuggestClusters() {
  exam.requestSuggestion(selectedExamType.value, region.value, getModelOptions())
}

function handleApplyClusters() {
  exam.applyClusterSuggestion(selectedExamType.value)
}

function handlePreview() {
  exam.previewCourse(selectedExamType.value, region.value)
}

async function handleGenerate() {
  await exam.generateCourse(selectedExamType.value, region.value, getModelOptions())
  if (exam.result.value?.course_id && onCourseCreated) {
    const title = exam.plan.value?.title || `${selectedExamType.value} – ${t('aiEditor.exam.generatedCourse')}`
    onCourseCreated(exam.result.value.course_id, title)
  }
}
</script>
