<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import { AnlageBadge } from './anlagen'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { TrainerQuestion, AnswerResult, Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  question: TrainerQuestion
  questionIndex?: number
  totalQuestions?: number
  anlagen?: Anlage[]
  examId?: string
}

const props = withDefaults(defineProps<Props>(), {
  questionIndex: 0,
  totalQuestions: 0,
  anlagen: () => [],
  examId: '',
})

const emit = defineEmits<{
  submit: [questionId: string, answer: unknown]
  next: []
}>()

const { t } = useI18n()
const windowStore = useWindowStore()

// --- Anlage references (per question's source exam) ---
const questionExamId = computed(() => (props.question as TrainerQuestion & { exam_id?: string }).exam_id || '')

const questionAnlagen = computed(() => {
  if (!questionExamId.value) return []
  return props.anlagen.filter((a: Anlage & { exam_id?: string }) =>
    !a.exam_id || a.exam_id === questionExamId.value
  )
})

const referencedAnlagen = computed(() => {
  const pool = questionAnlagen.value.length > 0 ? questionAnlagen.value : props.anlagen
  const text = [
    props.question.question_text,
    props.question.scenario_text,
    props.question.scenario_title,
  ].filter(Boolean).join(' ')

  const matches = text.match(/Anlage[n]?\s+(\d+(?:\s*(?:und|,|bis)\s*\d+)*)/gi) || []
  const numbers = new Set<number>()
  for (const m of matches) {
    for (const n of m.match(/\d+/g) || []) numbers.add(parseInt(n))
  }

  const matched = pool.filter(a => numbers.has(a.number))
  return matched.length > 0 ? matched : (matches.length > 0 ? [] : [])
})

// --- Window management via windowStore ---
const openAnlage = (number: number) => {
  // Find anlage from current question's exam, not from all exams
  const pool = questionAnlagen.value.length > 0 ? questionAnlagen.value : props.anlagen
  const a = pool.find(a => a.number === number)
  if (!a) return

  // Unique key includes exam_id to avoid conflicts between exams
  const anlageKey = `${questionExamId.value}-${number}`
  const existing = windowStore.getPanelsByType('exam-trainer-anlage')
  const match = existing.find(p => p.payload?.anlageKey === anlageKey)
  if (match) {
    if (match.minimized) windowStore.restorePanel(match.id)
    else windowStore.focusPanel(match.id)
    return
  }

  windowStore.openWindow({
    type: 'exam-trainer-anlage',
    title: `${t('panel.examTrainer.anlagen.anlageNr', { number })} — ${a.title}`,
    icon: '\u{1F4CE}',
    payload: { examId: questionExamId.value, anlage: a, anlageKey: `${questionExamId.value}-${number}` },
    size: { width: 640, height: 520 },
  })
}

const openScratchPad = () => {
  const existing = windowStore.getPanelsByType('exam-trainer-scratchpad')
  if (existing.length > 0) {
    const panel = existing[0]
    if (panel.minimized) windowStore.restorePanel(panel.id)
    else windowStore.focusPanel(panel.id)
    return
  }
  windowStore.openWindow({
    type: 'exam-trainer-scratchpad',
    title: t('panel.examTrainer.scratchPad.title'),
    icon: '\u{1F9EE}',
    size: { width: 420, height: 460 },
  })
}

// --- Question answer state ---
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

    <!-- Anlage Badges + scratch pad -->
    <div v-if="referencedAnlagen.length > 0" class="flex flex-wrap items-center gap-2 mb-4">
      <AnlageBadge
        v-for="a in referencedAnlagen"
        :key="a.number"
        :number="a.number"
        :title="a.title"
        @click="openAnlage"
      />
      <button
        class="inline-flex items-center gap-1.5 px-2 py-1 text-xs rounded-lg
               border border-amber-500/40 text-amber-400/70
               hover:bg-amber-500/10 hover:text-amber-400 transition-all"
        @click="openScratchPad"
      >
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        {{ t('panel.examTrainer.scratchPad.title') }}
      </button>
    </div>

    <!-- Scratch pad when no anlagen -->
    <div v-else class="flex items-center gap-2 mb-4">
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
               border border-amber-500/40 bg-amber-500/10 text-amber-400
               hover:bg-amber-500/20 hover:border-amber-500/60 transition-all"
        @click="openScratchPad"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        {{ t('panel.examTrainer.scratchPad.title') }}
      </button>
    </div>

    <!-- Question text -->
    <h3 class="text-lg font-semibold text-[var(--color-text)] mb-4">
      {{ t('panel.examTrainer.question', { number: totalQuestions > 0 ? questionIndex + 1 : question.question_number }) }}
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
