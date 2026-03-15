<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewQuestion } from '@/infrastructure/api/clients/panel/user/exams'
import { trainerGetAttemptReview } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  attemptId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  back: []
}>()

const { t } = useI18n()

const questions = ref<ReviewQuestion[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const filter = ref<'all' | 'correct' | 'wrong'>('all')

const filteredQuestions = computed(() => {
  if (filter.value === 'correct') return questions.value.filter(q => q.is_correct)
  if (filter.value === 'wrong') return questions.value.filter(q => !q.is_correct)
  return questions.value
})

const stats = computed(() => {
  const total = questions.value.length
  const correct = questions.value.filter(q => q.is_correct).length
  const wrong = total - correct
  const earned = questions.value.reduce((s, q) => s + (q.points_earned || 0), 0)
  const max = questions.value.reduce((s, q) => s + (q.max_points || 0), 0)
  return { total, correct, wrong, earned, max }
})

const formatSolution = (q: ReviewQuestion): string => {
  if (!q.solution) return '—'
  const sol = q.solution as Record<string, unknown>
  if (sol.correctAnswers && Array.isArray(sol.correctAnswers)) {
    return (sol.correctAnswers as string[]).join(', ')
  }
  if (sol.answer) return String(sol.answer)
  if (sol.solution_text) return String(sol.solution_text)
  return JSON.stringify(sol)
}

const formatUserAnswer = (answer: unknown): string => {
  if (answer === null || answer === undefined) return '—'
  if (typeof answer === 'string') return answer
  if (Array.isArray(answer)) return answer.join(', ')
  return JSON.stringify(answer)
}

onMounted(async () => {
  try {
    questions.value = await trainerGetAttemptReview(props.attemptId)
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl mx-auto py-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-[var(--color-text)]">
          {{ t('panel.examTrainer.review.title') }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ t('panel.examTrainer.review.subtitle', {
            correct: stats.correct, total: stats.total, earned: stats.earned, max: stats.max,
          }) }}
        </p>
      </div>
      <button
        class="px-4 py-2 rounded-lg text-sm border border-[var(--color-border)]
               text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]"
        @click="emit('back')"
      >
        {{ t('panel.examTrainer.backToExams') }}
      </button>
    </div>

    <!-- Filter -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="f in (['all', 'correct', 'wrong'] as const)"
        :key="f"
        class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
        :class="filter === f
          ? 'bg-blue-600 text-white'
          : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:text-[var(--color-text)]'"
        @click="filter = f"
      >
        {{ t(`panel.examTrainer.review.filter${f.charAt(0).toUpperCase() + f.slice(1)}`) }}
        <span v-if="f === 'correct'" class="ml-1">({{ stats.correct }})</span>
        <span v-else-if="f === 'wrong'" class="ml-1">({{ stats.wrong }})</span>
        <span v-else class="ml-1">({{ stats.total }})</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-3 rounded-lg bg-red-900/20 border border-red-500/30 text-red-400 text-sm">
      {{ error }}
    </div>

    <!-- Question List -->
    <div v-else class="space-y-4">
      <div
        v-for="(q, idx) in filteredQuestions"
        :key="q.question_id"
        class="p-4 rounded-xl border bg-[var(--color-surface)]"
        :class="q.is_correct ? 'border-emerald-500/30' : 'border-red-500/30'"
      >
        <!-- Question Header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span
              :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                       q.is_correct ? 'bg-emerald-500/20 text-emerald-500' : 'bg-red-500/20 text-red-500']"
            >
              {{ q.is_correct ? '✓' : '✗' }}
            </span>
            <span class="text-sm font-semibold text-[var(--color-text)]">
              {{ t('panel.examTrainer.question', { number: q.question_number || idx + 1 }) }}
            </span>
          </div>
          <span class="text-xs text-[var(--color-text-secondary)]">
            {{ q.points_earned }}/{{ q.max_points }} {{ t('panel.examTrainer.review.pts') }}
          </span>
        </div>

        <!-- Scenario -->
        <div v-if="q.scenario_title" class="text-xs text-amber-500 font-medium mb-1">
          {{ q.scenario_title }}
        </div>

        <!-- Question Text -->
        <p class="text-sm text-[var(--color-text)] mb-3 leading-relaxed">
          {{ q.question_text }}
        </p>

        <!-- Answers Comparison -->
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div class="p-2.5 rounded-lg" :class="q.is_correct ? 'bg-emerald-500/10' : 'bg-red-500/10'">
            <div class="text-xs font-medium mb-1" :class="q.is_correct ? 'text-emerald-400' : 'text-red-400'">
              {{ t('panel.examTrainer.review.yourAnswer') }}
            </div>
            <div class="text-[var(--color-text)]">{{ formatUserAnswer(q.user_answer) }}</div>
          </div>
          <div class="p-2.5 rounded-lg bg-emerald-500/10">
            <div class="text-xs font-medium text-emerald-400 mb-1">
              {{ t('panel.examTrainer.review.correctAnswer') }}
            </div>
            <div class="text-[var(--color-text)]">{{ formatSolution(q) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
