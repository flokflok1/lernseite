<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { renderMarkdown } from '@/presentation/components/public/learning/methods/method-execution/renderers/markdown'
import { StructogramBuilder, useStructogram } from '@/presentation/components/public/system-features/interactive/structogram-builder'
import type { StructogramData } from '@/presentation/components/public/system-features/interactive/structogram-builder'
import { AnlageBadge } from './anlagen'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { TrainerQuestion, AnswerResult, Anlage } from '@/infrastructure/api/clients/panel/user/exams'
import ExamTutorPanel from './ExamTutorPanel.vue'

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

// --- Sanitized HTML rendering for question text ---
const ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'b', 'i', 'ul', 'ol', 'li', 'table',
  'thead', 'tbody', 'tr', 'th', 'td', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'div', 'pre', 'code']
const sanitizedQuestionText = computed(() => {
  const text = props.question.question_text || ''
  if (text.includes('<') && text.includes('>')) {
    return DOMPurify.sanitize(text, { ALLOWED_TAGS, ALLOWED_ATTR: ['href', 'title', 'class'] })
  }
  return ''
})
const isHtmlContent = computed(() => sanitizedQuestionText.value.length > 0)

// --- Anlage references (per question's source exam) ---
const questionExamId = computed(() => (props.question as TrainerQuestion & { exam_id?: string }).exam_id || '')

const questionAnlagen = computed(() => {
  if (!questionExamId.value) return []
  return props.anlagen.filter((a: Anlage & { exam_id?: string }) =>
    !a.exam_id || a.exam_id === questionExamId.value
  )
})

const referencedAnlagen = computed(() => {
  // Always show all anlagen from this exam — the student needs access to all materials
  const pool = questionAnlagen.value.length > 0 ? questionAnlagen.value : props.anlagen
  return pool
})

// --- Anlage popout window ---
const openAnlage = (number: number) => {
  const examId = questionExamId.value
  if (!examId) return
  const url = `/exam-trainer/anlage/${examId}/${number}`
  window.open(url, `anlage-${examId}-${number}`, 'width=860,height=700,menubar=no,toolbar=no')
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

// --- AI Tutor state ---
const showTutor = ref(false)
const solutionHint = computed(() => {
  const topics = props.question.topics || []
  return topics.join(', ')
})

// --- Question answer state ---
const userAnswer = ref<unknown>('')
const result = ref<AnswerResult | null>(null)
const isSubmitting = ref(false)

const questionType = computed(() => props.question.question_type || 'free_text')

// Detect structogram questions by type or keywords in question text
const isStructogramQuestion = computed(() => {
  if (questionType.value === 'structogram') return true
  const text = (props.question.question_text || '').toLowerCase()
  return text.includes('struktogramm') || text.includes('programmablaufdiagramm')
    || text.includes('nassi') || text.includes('shneiderman')
})

const structogramData = ref<StructogramData>({ blocks: [] })
function onStructogramUpdate(data: StructogramData) {
  structogramData.value = data
  const s = useStructogram(data)
  userAnswer.value = s.toReadableText()
}

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
  if (isStructogramQuestion.value) return structogramData.value.blocks.length > 0
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
      class="mb-4 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20"
    >
      <h4 class="font-semibold text-blue-400 mb-1">
        {{ t('panel.examTrainer.scenario') }}
        <span v-if="question.scenario_title">: {{ question.scenario_title }}</span>
      </h4>
      <div
        v-if="question.scenario_text"
        class="text-sm text-[var(--color-text-secondary)] whitespace-pre-line prose prose-sm max-w-none"
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
    <div v-if="isHtmlContent" class="text-[var(--color-text)] mb-6 prose prose-invert max-w-none" v-html="sanitizedQuestionText" />
    <p v-else class="text-[var(--color-text)] mb-6 whitespace-pre-line">{{ question.question_text }}</p>

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
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-[var(--color-border)] hover:bg-[var(--color-background)]'"
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

      <!-- Structogram Builder -->
      <StructogramBuilder
        v-else-if="isStructogramQuestion"
        v-model="structogramData"
        @update:model-value="onStructogramUpdate"
      />

      <!-- Code / SQL Editor -->
      <div v-else-if="questionType === 'code'" class="space-y-1">
        <div class="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
          <span class="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-mono">CODE</span>
          <span>SQL, Java, Python, Pseudocode...</span>
        </div>
        <textarea
          v-model="userAnswer"
          rows="10"
          class="w-full p-4 rounded-lg border border-[var(--color-border)] bg-[#1a1b2e]
                 text-emerald-300 font-mono text-sm leading-relaxed
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y
                 placeholder:text-gray-600"
          placeholder="-- Dein Code hier..."
          spellcheck="false"
        />
      </div>

      <!-- Calculation (with room for Rechenweg) -->
      <div v-else-if="questionType === 'calculation'" class="space-y-1">
        <div class="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
          <span class="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono">RECHNUNG</span>
          <span>Rechenweg + Ergebnis</span>
        </div>
        <textarea
          v-model="userAnswer"
          rows="8"
          class="w-full p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)]
                 text-[var(--color-text)] font-mono text-sm leading-relaxed
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y
                 placeholder:text-[var(--color-text-secondary)]"
          placeholder="Rechenweg:&#10;76W - (2 × 9W + 3 × 3,5W) = ...&#10;&#10;Ergebnis: ..."
        />
      </div>

      <!-- Essay / Free text / Default -->
      <div v-else class="space-y-1">
        <div v-if="questionType === 'short_answer'" class="text-xs text-[var(--color-text-secondary)]">
          <span class="px-1.5 py-0.5 rounded bg-[var(--color-background)] text-[var(--color-text-secondary)]">Kurzantwort</span>
        </div>
        <textarea
          v-model="userAnswer"
          :rows="questionType === 'short_answer' ? 4 : 8"
          class="w-full p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)]
                 text-[var(--color-text)] text-sm leading-relaxed
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y
                 placeholder:text-[var(--color-text-secondary)]"
          :placeholder="questionType === 'short_answer'
            ? 'Deine Antwort...'
            : 'Deine Antwort...\n\nTipp: Strukturiere deine Antwort mit Aufzählungen (-, 1., 2.) für bessere Übersicht.'"
        />
      </div>
    </div>

    <!-- Tutor Help Button -->
    <div v-if="!result" class="flex items-center gap-3 mt-3">
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg
               bg-indigo-500/10 text-indigo-400 border border-indigo-500/20
               hover:bg-indigo-500/20 transition-colors"
        @click="showTutor = !showTutor"
      >
        {{ showTutor ? t('panel.examTrainer.tutor.close') : t('panel.examTrainer.tutor.open') }}
      </button>
    </div>

    <!-- Tutor Panel -->
    <div v-if="showTutor && !result" class="mt-3">
      <ExamTutorPanel
        :question-text="question.question_text"
        :scenario-title="question.scenario_title || ''"
        :scenario-text="question.scenario_text || ''"
        :solution-hint="solutionHint"
        :question-type="question.question_type"
        :points="question.points"
        @close="showTutor = false"
      />
    </div>

    <!-- Submit button -->
    <button
      v-if="!result"
      :disabled="!canSubmit"
      class="px-6 py-2.5 rounded-lg font-medium transition-colors"
      :class="canSubmit
        ? 'bg-blue-600 text-white hover:bg-blue-700'
        : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] cursor-not-allowed'"
      @click="handleSubmit"
    >
      <span v-if="isSubmitting">...</span>
      <span v-else>{{ t('panel.examTrainer.submit') }}</span>
    </button>

    <!-- Result -->
    <div v-if="result" class="mt-4">
      <div
        class="p-4 rounded-lg mb-4"
        :class="result.is_correct
          ? 'bg-emerald-500/10 border border-emerald-500/30'
          : result.points_earned > 0
            ? 'bg-amber-500/10 border border-amber-500/30'
            : 'bg-red-500/10 border border-red-500/30'"
      >
        <p class="font-semibold" :class="result.is_correct
          ? 'text-emerald-400'
          : result.points_earned > 0
            ? 'text-amber-400'
            : 'text-red-400'">
          {{ result.is_correct
            ? t('panel.examTrainer.correct')
            : result.points_earned > 0
              ? t('panel.examTrainer.partiallyCorrect')
              : t('panel.examTrainer.incorrect') }}
        </p>
        <p class="text-sm mt-1 text-[var(--color-text-secondary)]">
          {{ result.points_earned }}/{{ result.max_points || question.points }}
          {{ t('panel.examTrainer.points', { count: result.max_points || question.points }) }}
        </p>
      </div>

      <div v-if="result.explanation" class="p-4 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] mb-4">
        <h4 class="font-medium text-[var(--color-text)] mb-1">
          {{ t('panel.examTrainer.explanation') }}
        </h4>
        <p class="text-sm text-[var(--color-text-secondary)] whitespace-pre-line">
          {{ result.explanation }}
        </p>
      </div>

      <!-- Musterlösung -->
      <div v-if="result.correct_answer && !result.is_correct" class="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/20 mb-4">
        <h4 class="font-medium text-emerald-400 mb-1">
          Musterlösung
        </h4>
        <p class="text-sm text-[var(--color-text-secondary)] whitespace-pre-line">
          {{ result.correct_answer }}
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
