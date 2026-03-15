<!--
  ExamCourseGenerator — Admin UI for auto-generating IHK exam courses.
  Workflow: Select exam type + region → Preview plan → Generate course.
  Provider/Model selection allows choosing AI backend for content generation.
-->

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ t('panel.examCourseGenerator.title') }}
      </h2>
    </div>

    <!-- Config Form -->
    <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] p-4 space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Exam Type -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectType') }}
          </label>
          <select
            v-model="examType"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option v-for="et in examTypes" :key="et.exam_type" :value="et.exam_type">
              {{ t(`exams.types.${et.exam_type}`, et.display_name?.[locale] || et.exam_type) }}
            </option>
          </select>
        </div>

        <!-- Region -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectRegion') }}
          </label>
          <select
            v-model="region"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option v-for="r in regions" :key="r.region_code" :value="r.region_code">
              {{ t(`exams.regions.${r.region_code}`, r.display_name?.[locale] || r.region_code) }}
            </option>
          </select>
        </div>
      </div>

      <!-- Framework + Sort Mode -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectFramework') }}
          </label>
          <select
            v-model="selectedFrameworkId"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option :value="null">{{ t('panel.examCourseGenerator.noFramework') }}</option>
            <option v-for="fw in frameworks" :key="fw.framework_id" :value="fw.framework_id">
              {{ fw.name }}
            </option>
          </select>
        </div>
        <div v-if="selectedFrameworkId">
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.sortMode') }}
          </label>
          <select
            v-model="sortMode"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option value="relevance">{{ t('panel.examCourseGenerator.sortRelevance') }}</option>
            <option value="curriculum">{{ t('panel.examCourseGenerator.sortCurriculum') }}</option>
          </select>
        </div>
      </div>

      <!-- AI Provider / Model -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectProvider') }}
          </label>
          <select
            v-model="selectedProvider"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option v-if="availableProviders.length === 0" value="" disabled>
              {{ t('panel.examCourseGenerator.noProviders') }}
            </option>
            <option v-for="p in availableProviders" :key="p.name" :value="p.name">
              {{ p.display_name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectModel') }}
          </label>
          <select
            v-model="selectedModel"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option v-for="m in availableModels" :key="m.model_name" :value="m.model_name">
              {{ m.display_name || m.model_name }}
            </option>
          </select>
        </div>
      </div>

      <button
        @click="handlePreview"
        :disabled="previewing"
        class="px-4 py-2 text-sm rounded text-white transition-colors disabled:opacity-50"
        style="background-color: var(--color-primary, #7c3aed);"
      >
        {{ previewing ? '...' : t('panel.examCourseGenerator.preview') }}
      </button>
    </div>

    <!-- Preview Plan -->
    <div
      v-if="plan"
      class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] p-4 space-y-4"
    >
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">{{ plan.title }}</h3>
        <div class="flex items-center gap-3 text-xs text-[var(--color-text-secondary)]">
          <span>{{ plan.total_questions }} {{ t('panel.examCourseGenerator.questions') }}</span>
          <span>{{ plan.chapters.length }} {{ t('panel.examCourseGenerator.chapters') }}</span>
          <span>{{ Math.round(plan.total_points) }} {{ t('panel.examCourseGenerator.points') }}</span>
        </div>
      </div>
      <div class="space-y-3">
        <ChapterPreviewCard
          v-for="(ch, idx) in plan.chapters"
          :key="ch.topic"
          :chapter="ch"
          :index="idx"
        />
      </div>

      <!-- Simulations -->
      <div v-if="plan.simulation_exam_ids.length > 0" class="text-xs text-[var(--color-text-secondary)]">
        + {{ plan.simulation_exam_ids.length }} {{ t('panel.examCourseGenerator.simulations') }}
      </div>

      <!-- Generate Button -->
      <div class="flex items-center gap-3">
        <button
          @click="handleGenerate"
          :disabled="generating"
          class="px-4 py-2 text-sm rounded text-white transition-colors disabled:opacity-50"
          style="background-color: var(--color-primary, #7c3aed);"
        >
          {{ generating ? t('panel.examCourseGenerator.generating') : t('panel.examCourseGenerator.generate') }}
        </button>
        <div v-if="generating && !generationProgress" class="flex items-center gap-2">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--color-primary)]" />
          <span class="text-xs text-[var(--color-text-secondary)]">
            {{ t('panel.examCourseGenerator.generatingHint') }}
          </span>
        </div>
      </div>

      <!-- Generation Progress Bar -->
      <div
        v-if="generationProgress"
        class="border rounded-lg p-4"
        :class="progressBgClass"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="font-medium text-sm text-[var(--color-text-primary)]">
            {{ t('panel.examCourseGenerator.generatingProgress') }}
          </span>
          <span class="text-sm text-[var(--color-text-secondary)]">
            {{ generationProgress.completed }}/{{ generationProgress.total }}
            {{ t('panel.examCourseGenerator.chaptersReady') }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="h-2 rounded-full transition-all duration-500"
            :class="progressBarClass"
            :style="{ width: progressPercent + '%' }"
          />
        </div>
        <p
          v-if="generationProgress.status === 'ready'"
          class="mt-2 text-green-600 text-sm"
        >
          {{ t('panel.examCourseGenerator.generationComplete') }}
        </p>
        <p
          v-if="generationProgress.failed > 0"
          class="mt-2 text-amber-600 text-sm"
        >
          {{ generationProgress.failed }} {{ t('panel.examCourseGenerator.chaptersFailed') }}
        </p>
      </div>
    </div>

    <!-- Success Result -->
    <div
      v-if="result"
      class="bg-[var(--color-success-bg,#dcfce7)] rounded-lg border border-[var(--color-success-text,#15803d)] p-4"
    >
      <p class="text-sm font-medium text-[var(--color-success-text,#15803d)]">
        {{ t('panel.examCourseGenerator.success') }}
      </p>
      <p class="text-xs text-[var(--color-success-text,#15803d)] mt-1">
        {{ result.chapters_count }} {{ t('panel.examCourseGenerator.chapters') }},
        {{ result.lm_count }} {{ t('panel.examCourseGenerator.lmCount') }},
        {{ result.tokens_used }} {{ t('panel.examCourseGenerator.tokens') }}
      </p>
      <a
        :href="`/panel/courses/${result.course_id}`"
        class="inline-block mt-2 text-sm underline text-[var(--color-primary)]"
      >
        {{ t('panel.examCourseGenerator.openInEditor') }}
      </a>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="bg-[var(--color-error-bg,#fee2e2)] rounded-lg border border-[var(--color-error-text,#dc2626)] p-4"
    >
      <p class="text-sm text-[var(--color-error-text,#dc2626)]">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  CoursePlan,
  GenerateResult,
  GenerationProgress,
} from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import {
  previewExamCourse,
  generateExamCourse,
  getGenerationProgress,
} from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import ChapterPreviewCard from './ChapterPreviewCard.vue'
import { fetchExamTypes } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import type { ExamType } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import { archiveListRegions } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import type { ExamRegion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { adminGetAIModelsRegistry } from '@/infrastructure/api/clients/panel/admin/ai/models.api'
import type { AIModelRegistryItem, AIProviderInfo } from '@/infrastructure/api/clients/panel/admin/types'
import { fetchFrameworks } from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'
import type { CurriculumFramework } from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

const { t, locale } = useI18n()

// --- Exam type & region ---
const examTypes = ref<ExamType[]>([])
const examType = ref('')
const regions = ref<ExamRegion[]>([])
const region = ref('alle')

// --- Curriculum Framework ---
const frameworks = ref<CurriculumFramework[]>([])
const selectedFrameworkId = ref<number | null>(null)
const sortMode = ref('relevance')

// --- AI Provider / Model ---
const providers = ref<AIProviderInfo[]>([])
const models = ref<AIModelRegistryItem[]>([])
const selectedProvider = ref('')
const selectedModel = ref('')

const availableProviders = computed(() =>
  providers.value.filter(p => p.has_api_key)
)

const availableModels = computed(() =>
  models.value.filter(m => m.provider === selectedProvider.value && m.category === 'chat')
)

watch(selectedProvider, () => {
  const first = availableModels.value[0]
  selectedModel.value = first?.model_name || ''
})

// --- Generation state ---
const previewing = ref(false)
const generating = ref(false)
const plan = ref<CoursePlan | null>(null)
const result = ref<GenerateResult | null>(null)
const error = ref<string | null>(null)

// --- Generation progress polling ---
const generationProgress = ref<GenerationProgress | null>(null)
const generatingCourseId = ref<string | null>(null)
let progressInterval: ReturnType<typeof setInterval> | null = null

const progressPercent = computed(() => {
  if (!generationProgress.value) return 0
  const { completed, total } = generationProgress.value
  return Math.round((completed / Math.max(total, 1)) * 100)
})

const progressBgClass = computed(() => {
  const status = generationProgress.value?.status
  if (status === 'ready') return 'bg-green-50 border-green-200'
  if (status === 'failed') return 'bg-red-50 border-red-200'
  if (status === 'partial') return 'bg-amber-50 border-amber-200'
  return 'bg-blue-50 border-blue-200'
})

const progressBarClass = computed(() => {
  const status = generationProgress.value?.status
  if (status === 'ready') return 'bg-green-600'
  if (status === 'failed') return 'bg-red-600'
  if (status === 'partial') return 'bg-amber-600'
  return 'bg-blue-600'
})

function startPolling(courseId: string) {
  generatingCourseId.value = courseId
  progressInterval = setInterval(pollProgress, 3000)
  pollProgress()
}

function stopPolling() {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

async function pollProgress() {
  if (!generatingCourseId.value) return
  try {
    generationProgress.value = await getGenerationProgress(generatingCourseId.value)
    const terminalStatuses = new Set(['ready', 'partial', 'failed'])
    if (terminalStatuses.has(generationProgress.value.status)) {
      stopPolling()
      generating.value = false
    }
  } catch {
    /* ignore polling errors */
  }
}

onUnmounted(() => stopPolling())

onMounted(async () => {
  const [typesResult, regionsResult, registryResult, fwResult] = await Promise.allSettled([
    fetchExamTypes(),
    archiveListRegions(),
    adminGetAIModelsRegistry(),
    fetchFrameworks(),
  ])

  if (typesResult.status === 'fulfilled') {
    examTypes.value = typesResult.value
    if (typesResult.value.length > 0) {
      examType.value = typesResult.value[0].exam_type
    }
  }

  if (regionsResult.status === 'fulfilled') {
    regions.value = regionsResult.value
  }

  if (registryResult.status === 'fulfilled') {
    providers.value = registryResult.value.providers
    models.value = registryResult.value.data
    const firstAvailable = availableProviders.value[0]
    if (firstAvailable) {
      selectedProvider.value = firstAvailable.name
    }
  }

  if (fwResult.status === 'fulfilled') {
    frameworks.value = fwResult.value
  }
})

async function handlePreview() {
  previewing.value = true
  error.value = null
  result.value = null
  generationProgress.value = null
  try {
    plan.value = await previewExamCourse(
      examType.value,
      region.value,
      selectedFrameworkId.value ?? undefined,
      selectedFrameworkId.value ? sortMode.value : undefined,
    )
  } catch (err: any) {
    error.value = err?.response?.data?.error || t('panel.examCourseGenerator.previewFailed')
  } finally {
    previewing.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  error.value = null
  generationProgress.value = null
  try {
    result.value = await generateExamCourse(
      examType.value,
      region.value,
      {
        provider: selectedProvider.value || undefined,
        model: selectedModel.value || undefined,
      },
      selectedFrameworkId.value ?? undefined,
      selectedFrameworkId.value ? sortMode.value : undefined,
    )
    if (result.value.status === 'generating' && result.value.course_id) {
      startPolling(result.value.course_id)
    } else {
      generating.value = false
    }
  } catch (err: any) {
    error.value = err?.response?.data?.error || t('panel.examCourseGenerator.generationFailed')
    generating.value = false
  }
}
</script>
