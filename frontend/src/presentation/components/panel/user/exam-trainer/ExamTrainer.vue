<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import TopicHeatmap from './TopicHeatmap.vue'
import QuestionCard from './QuestionCard.vue'
import SimulationMode from './SimulationMode.vue'
import ReviewMode from './ReviewMode.vue'
import ProgressDashboard from './ProgressDashboard.vue'
import type { TrainerExam, TrainerQuestion, TopicStat, AnswerResult, Anlage } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerListExams,
  trainerGetQuestions,
  trainerGetTopics,
  trainerSubmitAnswer,
  trainerStartExam,
  trainerCompleteAttempt,
  trainerPracticeSession,
  trainerGetAnlagen,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

type TabKey = 'exams' | 'simulations' | 'topics' | 'practice' | 'progress'

const activeTab = ref<TabKey>('exams')
const isLoading = ref(false)
const error = ref<string | null>(null)

// Exam list
const exams = ref<TrainerExam[]>([])

// Topics
const topics = ref<TopicStat[]>([])

// Practice state
const questions = ref<TrainerQuestion[]>([])
const currentQuestionIndex = ref(0)
const attemptId = ref<string | null>(null)
const examComplete = ref(false)
const examResult = ref<{ score: number; total_points: number; percentage: number; passed: boolean } | null>(null)
const questionCardRef = ref<InstanceType<typeof QuestionCard> | null>(null)

// Simulation mode
const simulationActive = ref(false)
const simulationExam = ref<TrainerExam | null>(null)

const lastExamId = ref<string | null>(null)
const examAnlagen = ref<Anlage[]>([])
const reviewAttemptId = ref<string | null>(null)

const currentQuestion = computed<TrainerQuestion | null>(() => {
  if (questions.value.length === 0) return null
  return questions.value[currentQuestionIndex.value] ?? null
})

const simulationExams = computed(() =>
  exams.value.filter(e => e.analysis_status === 'ready' && e.question_count > 0)
)

const tabs = computed(() => {
  const base: { key: TabKey; label: string }[] = [
    { key: 'exams', label: t('panel.examTrainer.tabs.exams') },
    { key: 'simulations', label: t('panel.examTrainer.tabs.simulations') },
    { key: 'topics', label: t('panel.examTrainer.tabs.topics') },
    { key: 'progress', label: t('panel.examTrainer.tabs.progress') },
  ]
  if (questions.value.length > 0) {
    base.push({ key: 'practice', label: t('panel.examTrainer.tabs.practice') })
  }
  return base
})

const loadExams = async () => {
  isLoading.value = true
  error.value = null
  try {
    exams.value = await trainerListExams()
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const loadTopics = async () => {
  isLoading.value = true
  error.value = null
  try {
    topics.value = await trainerGetTopics()
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const startExamPractice = async (exam: TrainerExam) => {
  isLoading.value = true
  error.value = null
  try {
    const [id, qs, anlagen] = await Promise.all([
      trainerStartExam(exam.exam_id),
      trainerGetQuestions(exam.exam_id),
      trainerGetAnlagen(exam.exam_id).catch(() => []),
    ])
    attemptId.value = id
    questions.value = qs
    examAnlagen.value = anlagen
    currentQuestionIndex.value = 0
    examComplete.value = false
    examResult.value = null
    lastExamId.value = exam.exam_id
    activeTab.value = 'practice'
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const startSimulation = async (exam: TrainerExam) => {
  isLoading.value = true
  error.value = null
  try {
    const [id, qs, anlagen] = await Promise.all([
      trainerStartExam(exam.exam_id),
      trainerGetQuestions(exam.exam_id),
      trainerGetAnlagen(exam.exam_id).catch(() => []),
    ])
    attemptId.value = id
    questions.value = qs
    examAnlagen.value = anlagen
    simulationExam.value = exam
    simulationActive.value = true
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const exitSimulation = () => {
  simulationActive.value = false
  simulationExam.value = null
  questions.value = []
  attemptId.value = null
}

const startTopicPractice = async (topic: string) => {
  isLoading.value = true
  error.value = null
  try {
    const qs = await trainerPracticeSession({
      examType: 'real',
      topic,
      count: 15,
    })
    attemptId.value = null
    questions.value = qs
    currentQuestionIndex.value = 0
    examComplete.value = false
    examResult.value = null
    activeTab.value = 'practice'
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const handleSubmitAnswer = async (questionId: string, answer: unknown) => {
  try {
    const result: AnswerResult = await trainerSubmitAnswer(questionId, answer)
    questionCardRef.value?.setResult(result)
  } catch (e) {
    error.value = String(e)
  }
}

const handleNextQuestion = async () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  } else {
    // Exam complete
    if (attemptId.value) {
      try {
        examResult.value = await trainerCompleteAttempt(attemptId.value)
      } catch (e) {
        error.value = String(e)
      }
    }
    examComplete.value = true
  }
}

const backToOverview = () => {
  questions.value = []
  attemptId.value = null
  examComplete.value = false
  examResult.value = null
  showNewExamOptions.value = false
  activeTab.value = 'exams'
}

const repeatSameExam = async () => {
  if (!lastExamId.value) return
  const exam = exams.value.find(e => e.exam_id === lastExamId.value)
  if (exam) await startExamPractice(exam)
}

onMounted(() => {
  loadExams()
  loadTopics()
})
</script>

<template>
  <!-- Simulation Mode (full-screen takeover) -->
  <SimulationMode
    v-if="simulationActive && simulationExam && attemptId"
    :exam="simulationExam"
    :questions="questions"
    :anlagen="examAnlagen"
    :attempt-id="attemptId"
    @exit="exitSimulation"
    @retry="startSimulation(simulationExam!)"
    @review="(id: string) => { exitSimulation(); reviewAttemptId = id; activeTab = 'practice' }"
  />

  <div v-else>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text)]">
        {{ t('panel.examTrainer.title') }}
      </h1>
      <p class="text-[var(--color-text-secondary)] mt-1">
        {{ t('panel.examTrainer.subtitle') }}
      </p>
    </div>

    <!-- Error -->
    <div v-if="error" class="mb-4 p-3 rounded-lg bg-red-900/20 border border-red-500/30 text-red-400 text-sm">
      {{ error }}
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b border-[var(--color-border)]">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === tab.key
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text)]'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>

    <!-- Tab: Exams -->
    <div v-else-if="activeTab === 'exams'">
      <p v-if="exams.length === 0" class="text-center py-8 text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.noExams') }}
      </p>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="exam in exams"
          :key="exam.exam_id"
          class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]
                 hover:shadow-md transition-shadow"
        >
          <h3 class="font-semibold text-[var(--color-text)] mb-2">{{ exam.title }}</h3>
          <div class="text-sm text-[var(--color-text-secondary)] space-y-1 mb-4">
            <p>{{ exam.semester }} &middot; {{ exam.season }} {{ exam.year }}</p>
            <p>{{ t('panel.examTrainer.questions', { count: exam.question_count }) }}</p>
          </div>
          <button
            :disabled="exam.analysis_status !== 'ready' || exam.question_count === 0"
            class="w-full px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            :class="exam.analysis_status === 'ready' && exam.question_count > 0
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'"
            @click="startExamPractice(exam)"
          >
            {{ t('panel.examTrainer.startExam') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tab: Simulations -->
    <div v-else-if="activeTab === 'simulations'">
      <div class="mb-4">
        <h2 class="text-lg font-semibold text-[var(--color-text)]">
          {{ t('panel.examTrainer.simulations.title') }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.examTrainer.simulations.subtitle') }}
        </p>
      </div>
      <p v-if="simulationExams.length === 0" class="text-center py-8 text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.noExams') }}
      </p>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="exam in simulationExams"
          :key="exam.exam_id"
          class="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]
                 hover:shadow-md transition-shadow"
        >
          <h3 class="font-semibold text-[var(--color-text)] mb-2">{{ exam.title }}</h3>
          <div class="text-sm text-[var(--color-text-secondary)] space-y-1 mb-4">
            <p>{{ exam.semester }} &middot; {{ exam.season }} {{ exam.year }}</p>
            <div class="flex flex-wrap gap-3 mt-2">
              <span class="inline-flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ t('panel.examTrainer.simulations.duration', { minutes: exam.duration_minutes || 90 }) }}
              </span>
              <span v-if="exam.total_points">
                {{ t('panel.examTrainer.simulations.points', { count: exam.total_points }) }}
              </span>
              <span>
                {{ t('panel.examTrainer.questions', { count: exam.question_count }) }}
              </span>
            </div>
          </div>
          <button
            class="w-full px-4 py-2.5 rounded-lg font-medium text-sm transition-colors
                   bg-emerald-600 text-white hover:bg-emerald-700"
            @click="startSimulation(exam)"
          >
            {{ t('panel.examTrainer.simulations.start') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tab: Topics -->
    <div v-else-if="activeTab === 'topics'">
      <div class="mb-4">
        <h2 class="text-lg font-semibold text-[var(--color-text)]">
          {{ t('panel.examTrainer.topicHeatmap') }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.examTrainer.topicHeatmapDesc') }}
        </p>
      </div>
      <TopicHeatmap :topics="topics" @select-topic="startTopicPractice" />
    </div>

    <!-- Tab: Practice -->
    <div v-else-if="activeTab === 'practice'">
      <!-- Exam complete -->
      <div v-if="examComplete" class="py-8">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-[var(--color-text)] mb-4">
            {{ t('panel.examTrainer.examComplete') }}
          </h2>
          <div v-if="examResult" class="mb-6">
            <p class="text-lg" :class="examResult.passed ? 'text-emerald-600' : 'text-red-600'">
              {{ examResult.passed ? t('panel.examTrainer.passed') : t('panel.examTrainer.failed') }}
            </p>
            <p class="text-[var(--color-text-secondary)] mt-2">
              {{ t('panel.examTrainer.score', {
                score: examResult.score,
                total: examResult.total_points,
                percentage: examResult.percentage,
              }) }}
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="max-w-md mx-auto space-y-3">
          <button
            v-if="attemptId"
            class="w-full py-3 bg-purple-600 text-white rounded-lg font-medium
                   hover:bg-purple-700 transition-colors"
            @click="reviewAttemptId = attemptId; activeTab = 'practice'"
          >
            {{ t('panel.examTrainer.review.viewReview') }}
          </button>
          <button
            v-if="lastExamId"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium
                   hover:bg-blue-700 transition-colors"
            @click="repeatSameExam"
          >
            {{ t('examSimulation.newExam.repeatSame') }}
          </button>
          <button
            class="w-full py-3 border rounded-lg hover:bg-gray-50
                   text-[var(--color-text-secondary)] transition-colors"
            @click="backToOverview"
          >
            {{ t('panel.examTrainer.backToExams') }}
          </button>
        </div>
      </div>

      <!-- Review Mode -->
      <ReviewMode
        v-else-if="reviewAttemptId"
        :attempt-id="reviewAttemptId"
        @back="reviewAttemptId = null; backToOverview()"
      />

      <!-- Active question -->
      <QuestionCard
        v-else-if="currentQuestion"
        ref="questionCardRef"
        :question="currentQuestion"
        :question-index="currentQuestionIndex"
        :total-questions="questions.length"
        :anlagen="examAnlagen"
        @submit="handleSubmitAnswer"
        @next="handleNextQuestion"
      />
    </div>

    <!-- Tab: Progress -->
    <div v-else-if="activeTab === 'progress'">
      <ProgressDashboard />
    </div>
  </div>
</template>
