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
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ plan.title }}
        </h3>
        <div class="flex items-center gap-3 text-xs text-[var(--color-text-secondary)]">
          <span>{{ plan.total_questions }} {{ t('panel.examCourseGenerator.questions') }}</span>
          <span>{{ plan.chapters.length }} {{ t('panel.examCourseGenerator.chapters') }}</span>
          <span>{{ Math.round(plan.total_points) }} {{ t('panel.examCourseGenerator.points') }}</span>
        </div>
      </div>

      <!-- Chapter List -->
      <div class="space-y-2">
        <div
          v-for="(ch, idx) in plan.chapters"
          :key="ch.topic"
          class="flex items-center justify-between px-3 py-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)]"
        >
          <div class="flex items-center gap-3">
            <span class="text-xs font-mono text-[var(--color-text-secondary)] w-6">
              {{ idx + 1 }}
            </span>
            <span class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ formatTopic(ch.topic) }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs text-[var(--color-text-secondary)]">
              {{ ch.question_count }} {{ t('panel.examCourseGenerator.questions') }}
            </span>
            <div class="flex gap-1">
              <span
                v-for="lm in ch.lm_types"
                :key="lm"
                class="px-1.5 py-0.5 text-xs rounded bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
              >
                LM{{ lm }}
              </span>
            </div>
          </div>
        </div>
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
        <div v-if="generating" class="flex items-center gap-2">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--color-primary)]" />
          <span class="text-xs text-[var(--color-text-secondary)]">
            {{ t('panel.examCourseGenerator.generatingHint') }}
          </span>
        </div>
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
        {{ result.tokens_used }} Tokens
      </p>
      <a
        :href="`/panel/courses/${result.course_id}/edit`"
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
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CoursePlan, GenerateResult } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import { previewExamCourse, generateExamCourse } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import { fetchExamTypes } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import type { ExamType } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import { archiveListRegions } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import type { ExamRegion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { adminGetAIModelsRegistry } from '@/infrastructure/api/clients/panel/admin/ai/models.api'
import type { AIModelRegistryItem, AIProviderInfo } from '@/infrastructure/api/clients/panel/admin/types'

const { t, locale } = useI18n()

// --- Exam type & region ---
const examTypes = ref<ExamType[]>([])
const examType = ref('')
const regions = ref<ExamRegion[]>([])
const region = ref('alle')

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

onMounted(async () => {
  const [typesResult, regionsResult, registryResult] = await Promise.allSettled([
    fetchExamTypes(),
    archiveListRegions(),
    adminGetAIModelsRegistry(),
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
})

function formatTopic(topic: string): string {
  return topic.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

async function handlePreview() {
  previewing.value = true
  error.value = null
  result.value = null
  try {
    plan.value = await previewExamCourse(examType.value, region.value)
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Preview failed'
  } finally {
    previewing.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  error.value = null
  try {
    result.value = await generateExamCourse(examType.value, region.value, {
      provider: selectedProvider.value || undefined,
      model: selectedModel.value || undefined,
    })
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Generation failed'
  } finally {
    generating.value = false
  }
}
</script>
