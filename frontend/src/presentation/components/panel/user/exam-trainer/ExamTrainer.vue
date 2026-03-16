<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import TopicHeatmap from './TopicHeatmap.vue'
import SimulationMode from './SimulationMode.vue'
import ReviewMode from './ReviewMode.vue'
import type { TrainerQuestion, TrainerExam, Anlage } from '@/infrastructure/api/clients/panel/user/exams'
import type { TrainerDashboard } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerGetDashboard,
  trainerGenerateExam,
  trainerGetAnlagen,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

type View = 'dashboard' | 'simulation' | 'review'
const view = ref<View>('dashboard')
const dashboard = ref<TrainerDashboard | null>(null)
const isLoading = ref(false)
const isGenerating = ref(false)

// Simulation state
const simQuestions = ref<TrainerQuestion[]>([])
const simAttemptId = ref('')
const simAnlagen = ref<Anlage[]>([])
const reviewAttemptId = ref<string | null>(null)

// Virtual exam object for SimulationMode compatibility
const virtualExam = computed<TrainerExam>(() => ({
  exam_id: 'adaptive',
  title: t('panel.examTrainer.adaptive.adaptiveExam'),
  semester: '',
  year: new Date().getFullYear(),
  season: '',
  part: '',
  question_count: simQuestions.value.length,
  total_points: simQuestions.value.reduce((s, q) => s + (q.points || 5), 0),
  duration_minutes: 90,
  analysis_status: 'ready',
  passing_score: null,
}))

// Pool progress percentage
const poolProgress = computed(() => {
  if (!dashboard.value) return 0
  const { total_questions, mastered_questions } = dashboard.value.pool
  return total_questions > 0 ? Math.round((mastered_questions / total_questions) * 100) : 0
})

onMounted(async () => {
  isLoading.value = true
  try {
    dashboard.value = await trainerGetDashboard()
  } finally {
    isLoading.value = false
  }
})

const startAdaptiveExam = async () => {
  isGenerating.value = true
  try {
    const exam = await trainerGenerateExam(20, 90)
    simQuestions.value = exam.questions
    simAttemptId.value = exam.attempt_id

    // Load anlagen from all source exams
    const examIds = [...new Set(
      exam.questions.map((q: TrainerQuestion & { exam_id?: string }) => q.exam_id).filter(Boolean)
    )] as string[]
    const allAnlagen: Anlage[] = []
    for (const eid of examIds) {
      try {
        const a = await trainerGetAnlagen(eid)
        allAnlagen.push(...a)
      } catch { /* some exams may have no anlagen */ }
    }
    simAnlagen.value = allAnlagen

    view.value = 'simulation'
  } finally {
    isGenerating.value = false
  }
}

const handleSimulationExit = () => {
  view.value = 'dashboard'
  // Refresh dashboard stats
  trainerGetDashboard().then(d => { dashboard.value = d })
}

const handleSimulationReview = (attemptId: string) => {
  reviewAttemptId.value = attemptId
  view.value = 'review'
}

const handleReviewBack = () => {
  reviewAttemptId.value = null
  view.value = 'dashboard'
  trainerGetDashboard().then(d => { dashboard.value = d })
}
</script>

<template>
  <div>
    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>

    <!-- SIMULATION MODE -->
    <SimulationMode
      v-else-if="view === 'simulation'"
      :exam="virtualExam"
      :questions="simQuestions"
      :attempt-id="simAttemptId"
      :anlagen="simAnlagen"
      @exit="handleSimulationExit"
      @retry="startAdaptiveExam"
      @review="handleSimulationReview"
    />

    <!-- REVIEW MODE -->
    <ReviewMode
      v-else-if="view === 'review' && reviewAttemptId"
      :attempt-id="reviewAttemptId"
      @back="handleReviewBack"
    />

    <!-- DASHBOARD (default) -->
    <div v-else-if="dashboard" class="space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-[var(--color-text)]">
          {{ t('panel.examTrainer.adaptive.title') }}
        </h1>
        <p class="text-[var(--color-text-secondary)] mt-1">
          {{ t('panel.examTrainer.adaptive.subtitle') }}
        </p>
      </div>

      <!-- Stats Bar -->
      <div class="grid grid-cols-3 gap-4">
        <div class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] text-center">
          <div class="text-3xl font-bold text-[var(--color-text)]">
            {{ dashboard.pool.total_questions }}
          </div>
          <div class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ t('panel.examTrainer.adaptive.totalQuestions') }}
          </div>
        </div>
        <div class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] text-center">
          <div class="text-3xl font-bold text-blue-400">
            {{ dashboard.pool.seen_questions }}
          </div>
          <div class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ t('panel.examTrainer.adaptive.seenQuestions') }}
          </div>
        </div>
        <div class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] text-center">
          <div class="text-3xl font-bold text-emerald-400">
            {{ dashboard.pool.mastered_questions }}
          </div>
          <div class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ t('panel.examTrainer.adaptive.masteredQuestions') }}
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <div class="flex justify-between text-sm mb-2">
          <span class="text-[var(--color-text-secondary)]">
            {{ t('panel.examTrainer.adaptive.masteredQuestions') }}
          </span>
          <span class="font-medium text-[var(--color-text)]">{{ poolProgress }}%</span>
        </div>
        <div class="h-3 bg-[var(--color-background)] rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all duration-500"
            :style="{ width: poolProgress + '%' }"
          />
        </div>
      </div>

      <!-- CTA Button -->
      <button
        class="w-full p-6 rounded-xl font-semibold text-lg transition-all
               bg-gradient-to-r from-blue-600 to-blue-700 text-white
               hover:from-blue-700 hover:to-blue-800 hover:shadow-lg
               disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isGenerating || dashboard.pool.total_questions === 0"
        @click="startAdaptiveExam"
      >
        <div v-if="isGenerating" class="flex items-center justify-center gap-3">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
          {{ t('panel.examTrainer.adaptive.generating') }}
        </div>
        <div v-else>
          <div>{{ t('panel.examTrainer.adaptive.startExam') }}</div>
          <div class="text-sm font-normal opacity-80 mt-1">
            {{ t('panel.examTrainer.adaptive.startExamDesc', { count: 20, minutes: 90 }) }}
            &middot; {{ t('panel.examTrainer.adaptive.weakFirst') }}
          </div>
        </div>
      </button>

      <!-- Topic Heatmap -->
      <div>
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.adaptive.topicsTitle') }}
        </h2>
        <TopicHeatmap :topics="dashboard.topics" />
      </div>

      <!-- Recent Attempts -->
      <div>
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.adaptive.recentTitle') }}
        </h2>
        <div
          v-if="dashboard.recent_attempts.length === 0"
          class="text-center py-6 text-[var(--color-text-secondary)]"
        >
          {{ t('panel.examTrainer.adaptive.noHistory') }}
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="attempt in dashboard.recent_attempts"
            :key="attempt.attempt_id"
            class="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border)]
                   bg-[var(--color-surface)] hover:shadow-sm transition-shadow cursor-pointer"
            @click="reviewAttemptId = attempt.attempt_id; view = 'review'"
          >
            <div>
              <span class="font-medium text-[var(--color-text)]">
                {{ attempt.exam_title || t('panel.examTrainer.adaptive.adaptiveExam') }}
              </span>
              <span class="text-sm text-[var(--color-text-secondary)] ml-2">
                {{ new Date(attempt.completed_at).toLocaleDateString('de-DE') }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span
                class="text-sm font-medium"
                :class="attempt.passed ? 'text-emerald-400' : 'text-red-400'"
              >
                {{ Math.round(attempt.percentage ?? 0) }}%
              </span>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="attempt.passed
                  ? 'bg-emerald-500/10 text-emerald-400'
                  : 'bg-red-500/10 text-red-400'"
              >
                {{
                  attempt.passed
                    ? t('panel.examTrainer.adaptive.passed')
                    : t('panel.examTrainer.adaptive.failed')
                }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
