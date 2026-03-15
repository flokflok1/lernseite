<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import TopicHeatmap from './TopicHeatmap.vue'
import QuestionCard from './QuestionCard.vue'
import type { TrainerExam, TrainerQuestion, TopicStat, AnswerResult } from '@/infrastructure/api/clients/panel/user/exams'
import {
  trainerListExams,
  trainerGetQuestions,
  trainerGetTopics,
  trainerGetTopicQuestions,
  trainerSubmitAnswer,
  trainerStartExam,
  trainerCompleteAttempt,
  generatePracticeExam,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

// ----------------------------------------------------------------------------
// State
// ----------------------------------------------------------------------------
type TabKey = 'exams' | 'simulations' | 'topics' | 'practice'

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

// New exam generation state
const generatingNewExam = ref(false)
const showNewExamOptions = ref(false)
const newExamFocusWeakness = ref(false)
const newExamDifficulty = ref('realistic')
const lastExamId = ref<string | null>(null)

// ----------------------------------------------------------------------------
// Computed
// ----------------------------------------------------------------------------
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
  ]
  if (questions.value.length > 0) {
    base.push({ key: 'practice', label: t('panel.examTrainer.tabs.practice') })
  }
  return base
})

// ----------------------------------------------------------------------------
// Data Loading
// ----------------------------------------------------------------------------
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

// ----------------------------------------------------------------------------
// Actions
// ----------------------------------------------------------------------------
const startExamPractice = async (exam: TrainerExam) => {
  isLoading.value = true
  error.value = null
  try {
    const [id, qs] = await Promise.all([
      trainerStartExam(exam.exam_id),
      trainerGetQuestions(exam.exam_id),
    ])
    attemptId.value = id
    questions.value = qs
    currentQuestionIndex.value = 0
    examComplete.value = false
    examResult.value = null
    lastExamId.value = exam.exam_id
    showNewExamOptions.value = false
    activeTab.value = 'practice'
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

const startTopicPractice = async (topic: string) => {
  isLoading.value = true
  error.value = null
  try {
    const qs = await trainerGetTopicQuestions(topic)
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

const handleGenerateNewExam = async (options: {
  focusWeakness: boolean
  difficulty: string
}) => {
  generatingNewExam.value = true
  error.value = null
  try {
    const data = await generatePracticeExam({
      examType: 'ihk',
      difficulty: options.difficulty,
      focusWeakness: options.focusWeakness,
      questionCount: 20,
    })
    questions.value = data.questions
    currentQuestionIndex.value = 0
    examComplete.value = false
    examResult.value = null
    attemptId.value = null
    showNewExamOptions.value = false
    activeTab.value = 'practice'
  } catch (e) {
    error.value = String(e)
  } finally {
    generatingNewExam.value = false
  }
}

// ----------------------------------------------------------------------------
// Lifecycle
// ----------------------------------------------------------------------------
onMounted(() => {
  loadExams()
  loadTopics()
})
</script>

<template>
  <div>
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
            @click="startExamPractice(exam)"
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

        <!-- Generating overlay -->
        <div v-if="generatingNewExam" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3" />
          <p class="text-[var(--color-text-secondary)]">
            {{ t('examSimulation.newExam.generating') }}
          </p>
        </div>

        <!-- Action Buttons -->
        <div v-else class="max-w-md mx-auto space-y-3">
          <button
            v-if="lastExamId"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium
                   hover:bg-blue-700 transition-colors"
            @click="repeatSameExam"
          >
            {{ t('examSimulation.newExam.repeatSame') }}
          </button>
          <button
            class="w-full py-3 border border-blue-600 text-blue-600 rounded-lg font-medium
                   hover:bg-blue-50 transition-colors"
            @click="showNewExamOptions = !showNewExamOptions"
          >
            {{ t('examSimulation.newExam.generateNew') }}
          </button>

          <!-- New Exam Options Panel -->
          <div
            v-if="showNewExamOptions"
            class="p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-left"
          >
            <h4 class="font-medium mb-4">{{ t('examSimulation.newExam.options') }}</h4>

            <!-- Focus Weakness Toggle -->
            <div class="flex items-center justify-between mb-4">
              <div>
                <span class="text-sm font-medium">{{ t('examSimulation.newExam.focusWeakness') }}</span>
                <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  {{ t('examSimulation.newExam.focusWeaknessHint') }}
                </p>
              </div>
              <button
                @click="newExamFocusWeakness = !newExamFocusWeakness"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors shrink-0 ml-3',
                  newExamFocusWeakness ? 'bg-blue-600' : 'bg-gray-300'
                ]"
                role="switch"
                :aria-checked="newExamFocusWeakness"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    newExamFocusWeakness ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>

            <!-- Difficulty Dropdown -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">
                {{ t('examSimulation.newExam.difficulty') }}
              </label>
              <select
                v-model="newExamDifficulty"
                class="w-full px-3 py-2 rounded-lg border border-[var(--color-border)]
                       bg-[var(--color-surface)] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="easy">{{ t('examSimulation.newExam.difficultyEasy') }}</option>
                <option value="medium">{{ t('examSimulation.newExam.difficultyMedium') }}</option>
                <option value="hard">{{ t('examSimulation.newExam.difficultyHard') }}</option>
                <option value="realistic">{{ t('examSimulation.newExam.difficultyRealistic') }}</option>
              </select>
            </div>

            <!-- Generate Button -->
            <button
              class="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium
                     hover:bg-blue-700 transition-colors"
              @click="handleGenerateNewExam({ focusWeakness: newExamFocusWeakness, difficulty: newExamDifficulty })"
            >
              {{ t('examSimulation.newExam.generateButton') }}
            </button>
          </div>

          <button
            class="w-full py-3 border rounded-lg hover:bg-gray-50
                   text-[var(--color-text-secondary)] transition-colors"
            @click="backToOverview"
          >
            {{ t('panel.examTrainer.backToExams') }}
          </button>
        </div>
      </div>

      <!-- Active question -->
      <QuestionCard
        v-else-if="currentQuestion"
        ref="questionCardRef"
        :question="currentQuestion"
        :question-index="currentQuestionIndex"
        :total-questions="questions.length"
        @submit="handleSubmitAnswer"
        @next="handleNextQuestion"
      />
    </div>
  </div>
</template>
