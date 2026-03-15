<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import SimulationSidebar from './SimulationSidebar.vue'
import SimulationResults from './SimulationResults.vue'
import QuestionCard from './QuestionCard.vue'
import Modal from '@/presentation/components/shared/ui/Modal.vue'
import type { TrainerExam, TrainerQuestion, AnswerResult } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerSubmitAnswer,
  trainerCompleteAttempt,
} from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  exam: TrainerExam
  questions: TrainerQuestion[]
  attemptId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  exit: []
  retry: []
  review: [attemptId: string]
}>()

const { t } = useI18n()

// ---------------------------------------------------------------------------
// Timer
// ---------------------------------------------------------------------------
const timeLimitSeconds = computed(() => (props.exam.duration_minutes || 90) * 60)
const remainingSeconds = ref(timeLimitSeconds.value)
let timerInterval: ReturnType<typeof setInterval> | null = null

const timerText = computed(() => {
  const s = remainingSeconds.value
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
})

const timerClass = computed(() => {
  if (remainingSeconds.value <= 300) return 'text-red-500 animate-pulse'
  if (remainingSeconds.value <= 600) return 'text-amber-500'
  return 'text-[var(--color-text)]'
})

const startTimer = () => {
  timerInterval = setInterval(() => {
    if (remainingSeconds.value <= 0) {
      handleAutoSubmit()
      return
    }
    remainingSeconds.value--
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// ---------------------------------------------------------------------------
// Question State
// ---------------------------------------------------------------------------
const currentIndex = ref(0)
const answers = ref<Map<string, unknown>>(new Map())
const reviewMarked = ref<Set<string>>(new Set())
const isComplete = ref(false)
const examResult = ref<{ score: number; total_points: number; percentage: number; passed: boolean } | null>(null)
const showConfirmDialog = ref(false)
const questionCardRef = ref<InstanceType<typeof QuestionCard> | null>(null)

const currentQuestion = computed(() => props.questions[currentIndex.value] ?? null)

const statuses = computed(() =>
  props.questions.map(q => ({
    questionId: q.question_id,
    answered: answers.value.has(q.question_id),
    markedForReview: reviewMarked.value.has(q.question_id),
  }))
)

const unansweredCount = computed(() =>
  props.questions.length - answers.value.size
)

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
const handleSubmitAnswer = async (questionId: string, answer: unknown) => {
  try {
    answers.value.set(questionId, answer)
    const result: AnswerResult = await trainerSubmitAnswer(questionId, answer)
    questionCardRef.value?.setResult(result)
  } catch (e) {
    // Don't block simulation for grading errors
  }
}

const handleNextQuestion = () => {
  if (currentIndex.value < props.questions.length - 1) {
    currentIndex.value++
  }
}

const navigateTo = (index: number) => {
  if (index >= 0 && index < props.questions.length) {
    currentIndex.value = index
  }
}

const toggleReview = () => {
  if (!currentQuestion.value) return
  const qid = currentQuestion.value.question_id
  if (reviewMarked.value.has(qid)) {
    reviewMarked.value.delete(qid)
  } else {
    reviewMarked.value.add(qid)
  }
}

const isCurrentReview = computed(() =>
  currentQuestion.value ? reviewMarked.value.has(currentQuestion.value.question_id) : false
)

const requestFinish = () => {
  showConfirmDialog.value = true
}

const handleFinish = async () => {
  showConfirmDialog.value = false
  await finalize()
}

const handleAutoSubmit = async () => {
  stopTimer()
  await finalize()
}

const finalize = async () => {
  stopTimer()
  try {
    const result = await trainerCompleteAttempt(props.attemptId)
    examResult.value = result
  } catch {
    examResult.value = {
      score: 0, total_points: 0, percentage: 0, passed: false,
    }
  }
  isComplete.value = true
}

// ---------------------------------------------------------------------------
// Keyboard navigation
// ---------------------------------------------------------------------------
const handleKeydown = (e: KeyboardEvent) => {
  if (isComplete.value || showConfirmDialog.value) return
  if (e.key === 'ArrowRight') handleNextQuestion()
  if (e.key === 'ArrowLeft' && currentIndex.value > 0) currentIndex.value--
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------
onMounted(() => {
  startTimer()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Timer Bar -->
    <div
      class="flex items-center justify-between px-4 py-2.5 bg-[var(--color-surface)]
             border-b border-[var(--color-border)] shrink-0"
    >
      <div>
        <div class="font-semibold text-sm text-[var(--color-text)]">{{ exam.title }}</div>
        <div class="text-xs text-[var(--color-text-secondary)]">
          {{ t('panel.examTrainer.simulation.meta', {
            count: questions.length,
            points: exam.total_points || 100,
          }) }}
        </div>
      </div>
      <div
        :class="['font-mono text-xl font-bold flex items-center gap-2', timerClass]"
        aria-live="polite"
        role="timer"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ timerText }}
      </div>
      <button
        class="px-5 py-2 rounded-lg text-sm font-semibold bg-emerald-600 text-white
               hover:bg-emerald-700 transition-colors"
        @click="requestFinish"
      >
        {{ t('panel.examTrainer.simulation.finish') }}
      </button>
    </div>

    <!-- Body -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar (left) -->
      <SimulationSidebar
        v-if="!isComplete"
        :statuses="statuses"
        :current-index="currentIndex"
        @navigate="navigateTo"
      />

      <!-- Question Area -->
      <div v-if="!isComplete" class="flex-1 overflow-y-auto p-6">
        <div class="max-w-3xl mx-auto">
          <!-- Question Header -->
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-semibold text-blue-500">
              {{ t('panel.examTrainer.questionOf', {
                current: currentIndex + 1,
                total: questions.length,
              }) }}
            </span>
            <div class="flex items-center gap-2">
              <button
                :class="['px-3 py-1 text-xs rounded-md border transition-all',
                         isCurrentReview
                           ? 'bg-purple-500 text-white border-purple-500'
                           : 'border-purple-500 text-purple-400 hover:bg-purple-500/10']"
                :aria-pressed="isCurrentReview"
                @click="toggleReview"
              >
                <svg class="w-3.5 h-3.5 inline mr-1" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7"/>
                </svg>
                {{ t('panel.examTrainer.simulation.markReview') }}
              </button>
              <span class="text-xs text-[var(--color-text-secondary)] bg-[var(--color-surface)]
                           px-2.5 py-1 rounded-full">
                {{ t('panel.examTrainer.points', { count: currentQuestion?.points || 0 }) }}
              </span>
            </div>
          </div>

          <!-- Question Card -->
          <QuestionCard
            v-if="currentQuestion"
            ref="questionCardRef"
            :question="currentQuestion"
            :question-index="currentIndex"
            :total-questions="questions.length"
            @submit="handleSubmitAnswer"
            @next="handleNextQuestion"
          />

          <!-- Keyboard Hint -->
          <div class="mt-6 text-center text-xs text-[var(--color-text-secondary)]">
            {{ t('panel.examTrainer.simulation.keyboardHint') }}
          </div>
        </div>
      </div>

      <!-- Results -->
      <SimulationResults
        v-if="isComplete && examResult"
        :score="examResult.score"
        :total-points="examResult.total_points"
        :percentage="examResult.percentage"
        :passed="examResult.passed"
        :question-count="questions.length"
        @back-to-overview="emit('exit')"
        @retry="emit('retry')"
        @review="emit('review', attemptId)"
      />
    </div>

    <!-- Confirmation Dialog -->
    <Modal
      :show="showConfirmDialog"
      :title="t('panel.examTrainer.simulation.confirmTitle')"
      size="sm"
      @close="showConfirmDialog = false"
    >
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.simulation.confirmText', { count: unansweredCount }) }}
      </p>
      <template #footer>
        <button
          class="px-4 py-2 rounded-lg text-sm border border-[var(--color-border)]
                 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]"
          @click="showConfirmDialog = false"
        >
          {{ t('panel.examTrainer.simulation.confirmCancel') }}
        </button>
        <button
          class="px-4 py-2 rounded-lg text-sm font-semibold bg-emerald-600 text-white
                 hover:bg-emerald-700"
          @click="handleFinish"
        >
          {{ t('panel.examTrainer.simulation.confirmSubmit') }}
        </button>
      </template>
    </Modal>
  </div>
</template>
