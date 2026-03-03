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
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

// ----------------------------------------------------------------------------
// State
// ----------------------------------------------------------------------------
type TabKey = 'exams' | 'topics' | 'practice'

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

// ----------------------------------------------------------------------------
// Computed
// ----------------------------------------------------------------------------
const currentQuestion = computed<TrainerQuestion | null>(() => {
  if (questions.value.length === 0) return null
  return questions.value[currentQuestionIndex.value] ?? null
})

const tabs = computed(() => {
  const base = [
    { key: 'exams' as TabKey, label: t('panel.examTrainer.tabs.exams') },
    { key: 'topics' as TabKey, label: t('panel.examTrainer.tabs.topics') },
  ]
  if (questions.value.length > 0) {
    base.push({ key: 'practice' as TabKey, label: t('panel.examTrainer.tabs.practice') })
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
  activeTab.value = 'exams'
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
    <div v-if="error" class="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
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
      <div v-if="examComplete" class="text-center py-12">
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
        <button
          class="px-6 py-2.5 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          @click="backToOverview"
        >
          {{ t('panel.examTrainer.backToExams') }}
        </button>
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
