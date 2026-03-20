<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import SimulationMode from './SimulationMode.vue'
import ReviewMode from './ReviewMode.vue'
import TopicHeatmap from './TopicHeatmap.vue'
import ProgressDashboard from './ProgressDashboard.vue'
import TopicPrognosis from './TopicPrognosis.vue'
import type { TrainerQuestion, TrainerExam, Anlage, TrainerProgram } from '@/infrastructure/api/clients/panel/user/exams'
import type { TrainerDashboard } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerGetDashboard,
  trainerGetPrograms,
  trainerGenerateExam,
  trainerGetAnlagen,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

type View = 'programs' | 'dashboard' | 'simulation' | 'review'
const view = ref<View>('programs')
const dashboard = ref<TrainerDashboard | null>(null)
const programs = ref<TrainerProgram[]>([])
const selectedProgram = ref<TrainerProgram | null>(null)
const isLoading = ref(false)
const isGenerating = ref(false)

// Simulation state
const simQuestions = ref<TrainerQuestion[]>([])
const simAttemptId = ref('')
const simAnlagen = ref<Anlage[]>([])
const simDuration = ref(90)
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
  total_points: simQuestions.value.reduce((s, q) => s + Number(q.points || 5), 0),
  duration_minutes: simDuration.value,
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
    programs.value = await trainerGetPrograms()
  } finally {
    isLoading.value = false
  }
})

const selectProgram = async (prog: TrainerProgram) => {
  selectedProgram.value = prog
  isLoading.value = true
  try {
    dashboard.value = await trainerGetDashboard()
    view.value = 'dashboard'
  } finally {
    isLoading.value = false
  }
}

const examModes = [
  { key: 'practice', icon: '\uD83D\uDCD6', labelKey: 'panel.examTrainer.adaptive.modePractice', questions: 10, minutes: 0 },
  { key: 'quick', icon: '\u26A1', labelKey: 'panel.examTrainer.adaptive.modeQuick', questions: 10, minutes: 30 },
  { key: 'half', icon: '\uD83D\uDCDD', labelKey: 'panel.examTrainer.adaptive.modeHalf', questions: 20, minutes: 45 },
  { key: 'full', icon: '\uD83C\uDFAF', labelKey: 'panel.examTrainer.adaptive.modeFull', questions: 40, minutes: 90 },
]

const startAdaptiveExam = async (questionCount: number = 20, durationMinutes: number = 90) => {
  isGenerating.value = true
  simDuration.value = durationMinutes
  try {
    const exam = await trainerGenerateExam(questionCount, durationMinutes)
    simQuestions.value = exam.questions
    simAttemptId.value = exam.attempt_id

    // Load anlagen from all source exams
    const examIds = [...new Set(
      exam.questions.map((q: TrainerQuestion & { exam_id?: string }) => q.exam_id).filter(Boolean)
    )] as string[]
    const allAnlagen: (Anlage & { exam_id?: string })[] = []
    for (const eid of examIds) {
      try {
        const a = await trainerGetAnlagen(eid)
        // Tag each anlage with its source exam_id
        a.forEach(anlage => { (anlage as Anlage & { exam_id?: string }).exam_id = eid })
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
  if (selectedProgram.value) {
    trainerGetDashboard(selectedProgram.value.course_id).then(d => { dashboard.value = d })
  }
}

const handleSimulationReview = (attemptId: string) => {
  reviewAttemptId.value = attemptId
  view.value = 'review'
}

const handleReviewBack = () => {
  reviewAttemptId.value = null
  view.value = 'dashboard'
  if (selectedProgram.value) {
    trainerGetDashboard(selectedProgram.value.course_id).then(d => { dashboard.value = d })
  }
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

    <!-- PROGRAMS (entry) -->
    <div v-else-if="view === 'programs'" class="space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-[var(--color-text)]">
          {{ t('panel.examTrainer.adaptive.title') }}
        </h1>
        <p class="text-[var(--color-text-secondary)] mt-1">
          {{ t('panel.examTrainer.adaptive.programsSubtitle') }}
        </p>
      </div>
      <div v-if="programs.length === 0" class="text-center py-8 text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.adaptive.noHistory') }}
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="prog in programs"
          :key="prog.program_id"
          class="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]
                 hover:shadow-lg hover:border-blue-500/50 transition-all cursor-pointer"
          @click="selectProgram(prog)"
        >
          <h3 class="text-lg font-semibold text-[var(--color-text)] mb-2">{{ prog.title }}</h3>
          <div class="text-sm text-[var(--color-text-secondary)] space-y-1">
            <p>{{ t('panel.examTrainer.adaptive.questionsCount', { count: prog.total_questions }) }}</p>
            <p>{{ prog.exam_count }} {{ t('panel.examTrainer.simulations.title') }}</p>
          </div>
          <div class="mt-4">
            <div class="h-2 bg-[var(--color-background)] rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"
                :style="{ width: (prog.total_questions > 0 ? Math.round(prog.mastered_questions / prog.total_questions * 100) : 0) + '%' }"
              />
            </div>
            <div class="text-xs text-[var(--color-text-secondary)] mt-1">
              {{ prog.mastered_questions }}/{{ prog.total_questions }} {{ t('panel.examTrainer.adaptive.masteredQuestions') }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div v-else-if="view === 'dashboard' && dashboard" class="space-y-8">
      <!-- Header -->
      <div>
        <button
          class="text-sm text-blue-400 hover:text-blue-300 transition-colors mb-2 flex items-center gap-1"
          @click="view = 'programs'"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('panel.examTrainer.adaptive.backToPrograms') }}
        </button>
        <h1 class="text-2xl font-bold text-[var(--color-text)]">
          {{ selectedProgram?.title || t('panel.examTrainer.adaptive.title') }}
        </h1>
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

      <!-- Exam Mode Selection -->
      <div>
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.adaptive.startExam') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            v-for="mode in examModes"
            :key="mode.key"
            class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]
                   hover:border-blue-500/50 hover:shadow-lg transition-all text-left
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isGenerating"
            @click="startAdaptiveExam(mode.questions, mode.minutes)"
          >
            <div class="text-2xl mb-2">{{ mode.icon }}</div>
            <div class="font-semibold text-[var(--color-text)] mb-1">{{ t(mode.labelKey) }}</div>
            <div class="text-sm text-[var(--color-text-secondary)]">
              {{ mode.minutes > 0
                ? t('panel.examTrainer.adaptive.modeDesc', { count: mode.questions, minutes: mode.minutes })
                : t('panel.examTrainer.adaptive.modePracticeDesc', { count: mode.questions })
              }}
            </div>
          </button>
        </div>
        <div v-if="isGenerating" class="flex items-center justify-center gap-3 mt-4 text-[var(--color-text-secondary)]">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
          {{ t('panel.examTrainer.adaptive.generating') }}
        </div>
      </div>

      <!-- Topic Heatmap (Strengths / Weaknesses) -->
      <div v-if="dashboard.topics && dashboard.topics.length > 0">
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.adaptive.topicsTitle') }}
        </h2>
        <TopicHeatmap
          :topics="dashboard.topics"
          @select-topic="() => {}"
        />
      </div>

      <!-- Topic Prognosis -->
      <div>
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.prognosis.title') }}
        </h2>
        <TopicPrognosis />
      </div>

      <!-- Progress History -->
      <div>
        <h2 class="text-lg font-semibold text-[var(--color-text)] mb-4">
          {{ t('panel.examTrainer.progress.chartTitle') }}
        </h2>
        <ProgressDashboard />
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
