<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import SimulationMode from './SimulationMode.vue'
import ReviewMode from './ReviewMode.vue'
import TopicHeatmap from './TopicHeatmap.vue'
import ProgressDashboard from './ProgressDashboard.vue'
import TopicPrognosis from './TopicPrognosis.vue'
import QuestionBrowser from './QuestionBrowser.vue'
import PracticeConfigPanel from './PracticeConfigPanel.vue'
import type { TrainerQuestion, TrainerExam, Anlage } from '@/infrastructure/api/clients/panel/user/exams'
import type { TrainerDashboard } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerGetDashboard,
  trainerGenerateExam,
  trainerGetAnlagen,
  trainerPracticeSingle,
  practiceStartSession,
  type PracticeSessionConfig,
} from '@/infrastructure/api/clients/panel/user/exams'

const props = withDefaults(defineProps<{
  programId?: number
  initialView?: 'dashboard' | 'simulation' | 'review'
}>(), {
  initialView: 'dashboard',
})

const { t } = useI18n()

type View = 'dashboard' | 'simulation' | 'review'
const view = ref<View>(props.initialView)
const dashboard = ref<TrainerDashboard | null>(null)
const isLoading = ref(false)
const isGenerating = ref(false)

// Simulation state
const simQuestions = ref<TrainerQuestion[]>([])
const simAttemptId = ref('')
const simAnlagen = ref<Anlage[]>([])
const simDuration = ref(90)
const simTitle = ref('')
const reviewAttemptId = ref<string | null>(null)

// Virtual exam object for SimulationMode compatibility
const virtualExam = computed<TrainerExam>(() => ({
  exam_id: 'adaptive',
  title: simTitle.value || t('panel.examTrainer.adaptive.adaptiveExam'),
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
    dashboard.value = await trainerGetDashboard()
    view.value = props.initialView
  } finally {
    isLoading.value = false
  }
})

const examModes = [
  { key: 'quick', icon: '\u26A1', labelKey: 'panel.examTrainer.adaptive.modeQuick', questions: 10, minutes: 30 },
  { key: 'half', icon: '\uD83D\uDCDD', labelKey: 'panel.examTrainer.adaptive.modeHalf', questions: 20, minutes: 45 },
  { key: 'full', icon: '\uD83C\uDFAF', labelKey: 'panel.examTrainer.adaptive.modeFull', questions: 40, minutes: 90 },
]

const startAdaptiveExam = async (questionCount: number = 20, durationMinutes: number = 90) => {
  isGenerating.value = true
  simDuration.value = durationMinutes
  simTitle.value = ''
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

const startPracticeSession = async (config: PracticeSessionConfig) => {
  isGenerating.value = true
  try {
    const result = await practiceStartSession(config)
    if (!result.attempt_id) return
    simQuestions.value = result.questions as unknown as TrainerQuestion[]
    simAttemptId.value = result.attempt_id
    simDuration.value = config.time_limit_minutes || 0
    const orderLabel = config.order === 'sequential'
      ? t('panel.examTrainer.practice.orderSequential')
      : t('panel.examTrainer.practice.orderMixed')
    simTitle.value = `${t('panel.examTrainer.practice.title')} — ${orderLabel}`
    const examIds = [...new Set(result.questions.map(q => q.exam_id))]
    const anlagenArrays = await Promise.all(examIds.map(id => trainerGetAnlagen(id)))
    simAnlagen.value = anlagenArrays.flat()
    view.value = 'simulation'
  } catch (e) {
    console.error('Practice session failed:', e)
  } finally {
    isGenerating.value = false
  }
}

const handleSimulationExit = () => {
  view.value = 'dashboard'
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

const handlePracticeQuestion = async (questionId: string) => {
  isGenerating.value = true
  try {
    const exam = await trainerPracticeSingle(questionId)
    simQuestions.value = exam.questions
    simAttemptId.value = exam.attempt_id
    simDuration.value = 0
    // Load anlagen for this question's exam
    const examIds = [...new Set(
      exam.questions.map((q: TrainerQuestion & { exam_id?: string }) => q.exam_id).filter(Boolean)
    )] as string[]
    const allAnlagen: Anlage[] = []
    for (const eid of examIds) {
      try { allAnlagen.push(...await trainerGetAnlagen(eid)) } catch { /* ok */ }
    }
    simAnlagen.value = allAnlagen
    view.value = 'simulation'
  } finally {
    isGenerating.value = false
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

    <!-- DASHBOARD -->
    <div v-else-if="view === 'dashboard' && dashboard" class="space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-[var(--color-text)]">
          {{ t('panel.examTrainer.adaptive.title') }}
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
        <!-- Practice Config Panel -->
        <PracticeConfigPanel :disabled="isGenerating" @start="startPracticeSession" />

        <!-- Timed Exam Modes -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
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
              {{ t('panel.examTrainer.adaptive.modeDesc', { count: mode.questions, minutes: mode.minutes }) }}
            </div>
          </button>
        </div>
        <div v-if="isGenerating" class="flex items-center justify-center gap-3 mt-4 text-[var(--color-text-secondary)]">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
          {{ t('panel.examTrainer.adaptive.generating') }}
        </div>
      </div>

      <!-- Question Browser -->
      <QuestionBrowser @practice-question="handlePracticeQuestion" />

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
