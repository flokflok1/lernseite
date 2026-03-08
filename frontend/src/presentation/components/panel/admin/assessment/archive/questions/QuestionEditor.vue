<!--
  QuestionEditor - Inline editor for a single archive question.
  Shows fields in two columns with quality indicator and solution section.
-->

<template>
  <div class="border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] p-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ t('panel.examArchive.questionEditor.fields.questionNumber') }}: {{ localNumber }}
        </span>
        <span
          class="inline-block w-2.5 h-2.5 rounded-full"
          :class="qualityDotClass"
          :title="qualityLabel"
        />
      </div>
      <button
        @click="emit('cancel')"
        class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        :title="t('panel.examArchive.questionEditor.cancel')"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Two-column fields -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <!-- Left column -->
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.questionText') }}
          </label>
          <textarea
            v-model="localText"
            rows="4"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.scenarioTitle') }}
          </label>
          <input
            v-model="localScenarioTitle"
            type="text"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.scenarioText') }}
          </label>
          <textarea
            v-model="localScenarioText"
            rows="3"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>

      <!-- Right column -->
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.questionType') }}
          </label>
          <select
            v-model="localType"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          >
            <option v-for="qtype in questionTypes" :key="qtype" :value="qtype">
              {{ t(`panel.examArchive.questionEditor.types.${qtype}`) }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.points') }}
          </label>
          <input
            v-model.number="localPoints"
            type="number"
            min="0"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.difficulty') }}
          </label>
          <select
            v-model="localDifficulty"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          >
            <option value="">-</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.questionEditor.fields.questionNumber') }}
          </label>
          <input
            v-model="localNumber"
            type="text"
            class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>
    </div>

    <!-- Topics row -->
    <div class="mb-4">
      <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
        {{ t('panel.examArchive.questionEditor.fields.topics') }}
      </label>
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="(topic, idx) in localTopics"
          :key="idx"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary,#7c3aed)]"
        >
          {{ topic }}
          <button
            @click="removeTopic(idx)"
            class="hover:text-[var(--color-error,#dc2626)] transition-colors"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <span
          v-if="localTopics.length === 0"
          class="text-xs text-[var(--color-text-secondary)] italic"
        >
          {{ t('panel.examArchive.noQuestions') }}
        </span>
      </div>
    </div>

    <!-- Curriculum tags -->
    <div class="mb-4">
      <CurriculumTagSection :question-id="question.question_id" />
    </div>

    <!-- Solution section -->
    <div class="mb-4">
      <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
        {{ t('panel.examArchive.questionEditor.fields.solution') }}
      </label>

      <!-- MCQ: options list with radio -->
      <div v-if="localType === 'mcq' && mcqOptions.length > 0" class="space-y-2">
        <div
          v-for="(opt, idx) in mcqOptions"
          :key="idx"
          class="flex items-center gap-2"
        >
          <input
            type="radio"
            :name="`mcq-correct-${question.question_id}`"
            :checked="mcqCorrectIndex === idx"
            @change="setMcqCorrect(idx)"
            class="accent-[var(--color-primary)]"
          />
          <span class="text-sm text-[var(--color-text-primary)]">{{ opt }}</span>
        </div>
      </div>

      <!-- Calculation: single-line input -->
      <input
        v-else-if="localType === 'calculation'"
        v-model="localSolutionText"
        type="text"
        class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
        :placeholder="t('panel.examArchive.questionEditor.fields.solutionText')"
      />

      <!-- Other: textarea -->
      <textarea
        v-else
        v-model="localSolutionText"
        rows="3"
        class="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
        :placeholder="t('panel.examArchive.questionEditor.fields.solutionText')"
      />
    </div>

    <!-- Footer buttons -->
    <div class="flex items-center justify-between border-t border-[var(--color-border)] pt-3">
      <button
        @click="handleDelete"
        class="px-3 py-1.5 text-sm rounded border border-red-300 text-red-600 hover:bg-red-50 transition-colors"
      >
        {{ t('panel.examArchive.questionEditor.delete') }}
      </button>
      <div class="flex gap-2">
        <button
          @click="emit('cancel')"
          class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg)] transition-colors"
        >
          {{ t('panel.examArchive.questionEditor.cancel') }}
        </button>
        <button
          @click="handleSave"
          class="px-3 py-1.5 text-sm rounded text-white transition-colors"
          style="background-color: var(--color-primary, #7c3aed);"
        >
          {{ t('panel.examArchive.questionEditor.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveQuestion, QuestionEdit } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import CurriculumTagSection from './CurriculumTagSection.vue'

const { t } = useI18n()

const questionTypes = ['mcq', 'calculation', 'essay', 'code', 'fill_blank', 'case_study', 'drag_drop', 'matching']

interface Props {
  question: ArchiveQuestion
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [data: QuestionEdit]
  cancel: []
  delete: []
}>()

// Local copies of each field
const localText = ref(props.question.question_text ?? '')
const localType = ref(props.question.question_type ?? 'essay')
const localPoints = ref(props.question.points ?? 0)
const localTopics = ref<string[]>([...(props.question.topics ?? [])])
const localSolutionText = ref(props.question.solution_text ?? '')
const localScenarioTitle = ref(props.question.scenario_title ?? '')
const localScenarioText = ref(props.question.scenario_text ?? '')
const localNumber = ref(props.question.question_number ?? '')
const localDifficulty = ref(props.question.difficulty ?? '')
const localSolution = ref<Record<string, any>>({ ...(props.question.solution ?? {}) })

// MCQ helpers
const mcqOptions = computed<string[]>(() => {
  const data = props.question.data
  if (data && Array.isArray(data.options)) {
    return data.options as string[]
  }
  return []
})

const mcqCorrectIndex = computed(() => {
  const sol = localSolution.value
  if (sol && typeof sol.correct_index === 'number') {
    return sol.correct_index as number
  }
  return -1
})

function setMcqCorrect(idx: number) {
  localSolution.value = { ...localSolution.value, correct_index: idx }
}

function removeTopic(idx: number) {
  localTopics.value.splice(idx, 1)
}

// Quality dot logic
type Quality = 'green' | 'yellow' | 'red'

const quality = computed<Quality>(() => {
  const hasText = localText.value.trim().length > 0
  const hasPoints = localPoints.value > 0
  if (!hasText || !hasPoints) return 'red'

  const hasSolution = localSolutionText.value.trim().length > 0 || Object.keys(localSolution.value).length > 0
  const hasTopics = localTopics.value.length > 0
  if (!hasSolution || !hasTopics) return 'yellow'

  return 'green'
})

const qualityDotClass = computed(() => ({
  'bg-green-500': quality.value === 'green',
  'bg-yellow-500': quality.value === 'yellow',
  'bg-red-500': quality.value === 'red',
}))

const qualityLabel = computed(() => t(`panel.examArchive.questionEditor.quality.${quality.value}`))

// Save: only send changed fields
function handleSave() {
  const changes: QuestionEdit = {}
  const q = props.question

  if (localText.value !== (q.question_text ?? '')) changes.question_text = localText.value
  if (localType.value !== (q.question_type ?? '')) changes.question_type = localType.value
  if (localPoints.value !== (q.points ?? 0)) changes.points = localPoints.value
  if (localSolutionText.value !== (q.solution_text ?? '')) changes.solution_text = localSolutionText.value
  if (localScenarioTitle.value !== (q.scenario_title ?? '')) changes.scenario_title = localScenarioTitle.value
  if (localScenarioText.value !== (q.scenario_text ?? '')) changes.scenario_text = localScenarioText.value
  if (localNumber.value !== (q.question_number ?? '')) changes.question_number = localNumber.value
  if (localDifficulty.value !== (q.difficulty ?? '')) changes.difficulty = localDifficulty.value

  const origTopics = q.topics ?? []
  if (JSON.stringify(localTopics.value) !== JSON.stringify(origTopics)) {
    changes.topics = [...localTopics.value]
  }

  if (JSON.stringify(localSolution.value) !== JSON.stringify(q.solution ?? {})) {
    changes.solution = { ...localSolution.value }
  }

  emit('save', changes)
}

function handleDelete() {
  if (window.confirm(t('panel.examArchive.questionEditor.bulkDeleteConfirm', { count: 1 }))) {
    emit('delete')
  }
}
</script>
