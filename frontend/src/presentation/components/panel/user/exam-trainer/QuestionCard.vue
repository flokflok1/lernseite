<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import type { TrainerQuestion, AnswerResult } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  question: TrainerQuestion
  questionIndex?: number
  totalQuestions?: number
}

const props = withDefaults(defineProps<Props>(), {
  questionIndex: 0,
  totalQuestions: 0,
})

const emit = defineEmits<{
  submit: [questionId: string, answer: unknown]
  next: []
}>()

const { t } = useI18n()

const userAnswer = ref<unknown>('')
const result = ref<AnswerResult | null>(null)
const isSubmitting = ref(false)

const questionType = computed(() => props.question.question_type || 'free_text')

const mcqOptions = computed<string[]>(() => {
  const data = props.question.data
  if (data && Array.isArray(data.options)) {
    return data.options as string[]
  }
  return []
})

const canSubmit = computed(() => {
  if (result.value) return false
  if (isSubmitting.value) return false
  if (questionType.value === 'mcq') return userAnswer.value !== ''
  return typeof userAnswer.value === 'string' && userAnswer.value.trim() !== ''
})

const handleSubmit = async () => {
  if (!canSubmit.value) return
  isSubmitting.value = true
  emit('submit', props.question.question_id, userAnswer.value)
}

const handleNext = () => {
  userAnswer.value = ''
  result.value = null
  isSubmitting.value = false
  emit('next')
}

/** Called by parent to set the answer result */
const setResult = (answerResult: AnswerResult) => {
  result.value = answerResult
  isSubmitting.value = false
}

defineExpose({ setResult })
</script>

<template>
  <div class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
    <!-- Progress indicator -->
    <div v-if="totalQuestions > 0" class="mb-4 text-sm text-[var(--color-text-secondary)]">
      {{ t('panel.examTrainer.questionOf', { current: questionIndex + 1, total: totalQuestions }) }}
      &middot;
      {{ t('panel.examTrainer.points', { count: question.points }) }}
    </div>

    <!-- Scenario -->
    <div
      v-if="question.scenario_title || question.scenario_text"
      class="mb-4 p-4 rounded-lg bg-blue-50 border border-blue-200"
    >
      <h4 class="font-semibold text-blue-800 mb-1">
        {{ t('panel.examTrainer.scenario') }}
        <span v-if="question.scenario_title">: {{ question.scenario_title }}</span>
      </h4>
      <div
        v-if="question.scenario_text"
        class="text-sm text-blue-700 whitespace-pre-line prose prose-sm prose-blue max-w-none"
        v-html="renderMarkdown(question.scenario_text)"
      />
    </div>

    <!-- Question text -->
    <h3 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('panel.examTrainer.question', { number: question.question_number }) }}
    </h3>
    <p class="text-[var(--color-text)] mb-6 whitespace-pre-line">{{ question.question_text }}</p>

    <!-- Answer input -->
    <div v-if="!result" class="mb-4">
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ t('panel.examTrainer.yourAnswer') }}
      </label>

      <!-- MCQ -->
      <div v-if="questionType === 'mcq'" class="space-y-2">
        <label
          v-for="(option, idx) in mcqOptions"
          :key="idx"
          class="flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors"
          :class="userAnswer === option
            ? 'border-blue-500 bg-blue-50'
            : 'border-[var(--color-border)] hover:bg-gray-50'"
        >
          <input
            v-model="userAnswer"
            type="radio"
            :value="option"
            class="mt-0.5"
          />
          <span class="text-[var(--color-text)]">{{ option }}</span>
        </label>
      </div>

      <!-- Calculation -->
      <input
        v-else-if="questionType === 'calculation'"
        v-model="userAnswer"
        type="text"
        class="w-full p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]
               text-[var(--color-text)] focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        :placeholder="t('panel.examTrainer.yourAnswer')"
      />

      <!-- Essay / Free text / Default -->
      <textarea
        v-else
        v-model="userAnswer"
        rows="5"
        class="w-full p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]
               text-[var(--color-text)] focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
        :placeholder="t('panel.examTrainer.yourAnswer')"
      />
    </div>

    <!-- Submit button -->
    <button
      v-if="!result"
      :disabled="!canSubmit"
      class="px-6 py-2.5 rounded-lg font-medium transition-colors"
      :class="canSubmit
        ? 'bg-blue-600 text-white hover:bg-blue-700'
        : 'bg-gray-200 text-gray-500 cursor-not-allowed'"
      @click="handleSubmit"
    >
      <span v-if="isSubmitting">...</span>
      <span v-else>{{ t('panel.examTrainer.submit') }}</span>
    </button>

    <!-- Result -->
    <div v-if="result" class="mt-4">
      <div
        class="p-4 rounded-lg mb-4"
        :class="result.correct ? 'bg-emerald-50 border border-emerald-300' : 'bg-red-50 border border-red-300'"
      >
        <p class="font-semibold" :class="result.correct ? 'text-emerald-700' : 'text-red-700'">
          {{ result.correct ? t('panel.examTrainer.correct') : t('panel.examTrainer.incorrect') }}
        </p>
        <p class="text-sm mt-1 text-[var(--color-text-secondary)]">
          {{ result.earned_points }}/{{ result.max_points }}
          {{ t('panel.examTrainer.points', { count: result.max_points }) }}
        </p>
      </div>

      <div v-if="result.explanation" class="p-4 rounded-lg bg-gray-50 border border-gray-200 mb-4">
        <h4 class="font-medium text-[var(--color-text)] mb-1">
          {{ t('panel.examTrainer.explanation') }}
        </h4>
        <p class="text-sm text-[var(--color-text-secondary)] whitespace-pre-line">
          {{ result.explanation }}
        </p>
      </div>

      <button
        class="px-6 py-2.5 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        @click="handleNext"
      >
        {{ t('panel.examTrainer.nextQuestion') }}
      </button>
    </div>
  </div>
</template>
