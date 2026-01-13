<script setup lang="ts">
/**
 * KI-Prüfungssimulation Page
 *
 * Allows users to:
 * - View detected exam context (profession, level, weak/strong topics)
 * - Configure exam simulation (smart/manual mode)
 * - Generate AI-powered exams
 * - Take exam attempts and view results
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/modules/core'
import {
  getExamContext,
  createExamSimulation,
  listExamSimulations,
  getExamSimulation,
  generateExamSimulation,
  startExamAttempt,
  submitExamAttempt,
  type ExamContext,
  type ExamSimulation,
  type ExamQuestion,
  type ExamAttempt
} from '@/api/examSimulation.api'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// Course ID from route
const courseId = computed(() => route.params.courseId as string)

// Role-based access
const isCreator = computed(() => {
  const role = authStore.userRole
  return ['admin', 'superadmin', 'teacher', 'creator', 'school_admin', 'company_admin'].includes(role)
})

const isStudent = computed(() => !isCreator.value)

// State
const loading = ref(true)
const generating = ref(false)
const examContext = ref<ExamContext | null>(null)
const simulations = ref<ExamSimulation[]>([])
const currentSimulation = ref<ExamSimulation | null>(null)
const currentAttempt = ref<ExamAttempt | null>(null)
const questions = ref<ExamQuestion[]>([])
const userAnswers = ref<Record<string, string>>({})
const attemptStartTime = ref<number>(0)
const showResults = ref(false)
const attemptResult = ref<any>(null)
const error = ref<string | null>(null)

// Configuration
const mode = ref<'smart' | 'manual'>('smart')
const difficulty = ref<'easy' | 'realistic' | 'hard'>('realistic')
const timeLimit = ref(90)
const customFocus = ref<Record<string, number>>({})

// UI State
const activeTab = ref<'overview' | 'config' | 'exam' | 'history'>('overview')
const currentQuestionIndex = ref(0)

// Load initial data
onMounted(async () => {
  await loadExamContext()
  await loadSimulations()
  loading.value = false
})

// Poll for generation status
watch(
  () => currentSimulation.value?.status,
  async (status) => {
    if (status === 'generating') {
      pollGenerationStatus()
    }
  }
)

async function loadExamContext() {
  try {
    examContext.value = await getExamContext(courseId.value)
    if (examContext.value?.recommended_focus) {
      customFocus.value = { ...examContext.value.recommended_focus }
    }
  } catch (e: any) {
    error.value = t('examSimulation.errors.loadContext')
    console.error(e)
  }
}

async function loadSimulations() {
  try {
    const result = await listExamSimulations({ course_id: courseId.value })
    simulations.value = result.simulations
  } catch (e: any) {
    console.error('Error loading simulations:', e)
  }
}

async function createNewSimulation() {
  try {
    generating.value = true
    error.value = null

    const simulation = await createExamSimulation(courseId.value, {
      mode: mode.value,
      difficulty: difficulty.value,
      time_limit_minutes: timeLimit.value,
      focus_distribution: mode.value === 'manual' ? customFocus.value : undefined
    })

    currentSimulation.value = simulation

    // Start generation
    await generateExamSimulation(simulation.simulation_id)
    pollGenerationStatus()
  } catch (e: any) {
    error.value = t('examSimulation.errors.createSimulation')
    generating.value = false
    console.error(e)
  }
}

async function pollGenerationStatus() {
  if (!currentSimulation.value) return

  const checkStatus = async () => {
    try {
      const sim = await getExamSimulation(currentSimulation.value!.simulation_id)
      currentSimulation.value = sim

      if (sim.status === 'ready') {
        generating.value = false
        await loadSimulations()
        activeTab.value = 'exam'
      } else if (sim.status === 'failed') {
        generating.value = false
        error.value = sim.error_message || t('examSimulation.errors.generationFailed')
      } else if (sim.status === 'generating') {
        setTimeout(checkStatus, 3000)
      }
    } catch (e) {
      console.error('Poll error:', e)
      setTimeout(checkStatus, 5000)
    }
  }

  checkStatus()
}

async function startExam() {
  if (!currentSimulation.value) return

  try {
    const result = await startExamAttempt(currentSimulation.value.simulation_id)
    currentAttempt.value = result.attempt
    questions.value = result.questions
    userAnswers.value = {}
    currentQuestionIndex.value = 0
    attemptStartTime.value = Date.now()
    showResults.value = false
    attemptResult.value = null
  } catch (e: any) {
    error.value = t('examSimulation.errors.startExam')
    console.error(e)
  }
}

async function submitExam() {
  if (!currentSimulation.value || !currentAttempt.value) return

  try {
    const answers = Object.entries(userAnswers.value).map(([questionId, answer]) => ({
      question_id: questionId,
      answer
    }))

    const timeSpent = Math.floor((Date.now() - attemptStartTime.value) / 1000)

    attemptResult.value = await submitExamAttempt(
      currentSimulation.value.simulation_id,
      {
        attempt_id: currentAttempt.value.attempt_id,
        answers,
        time_spent_seconds: timeSpent
      }
    )

    showResults.value = true
    currentAttempt.value = null
    await loadSimulations()
  } catch (e: any) {
    error.value = t('examSimulation.errors.submitExam')
    console.error(e)
  }
}

function selectSimulation(sim: ExamSimulation) {
  currentSimulation.value = sim
  if (sim.status === 'ready') {
    activeTab.value = 'exam'
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function getTopicColor(score: number): string {
  if (score < 50) return 'text-red-600'
  if (score < 70) return 'text-yellow-600'
  if (score < 85) return 'text-blue-600'
  return 'text-green-600'
}

function getDifficultyLabel(diff: string): string {
  const labels: Record<string, string> = {
    easy: t('examSimulation.config.easy'),
    realistic: t('examSimulation.config.realistic'),
    hard: t('examSimulation.config.hard')
  }
  return labels[diff] || diff
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: t('examSimulation.status.pending'),
    generating: t('examSimulation.status.generating'),
    ready: t('examSimulation.status.ready'),
    failed: t('examSimulation.status.failed')
  }
  return labels[status] || status
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-800',
    generating: 'bg-yellow-100 text-yellow-800',
    ready: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100'
}
</script>

<template>
  <div class="exam-simulation-page min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4">
      <!-- Header -->
      <div class="mb-8">
        <button
          @click="router.back()"
          class="text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t('examSimulation.backToCourse') }}
        </button>
        <h1 class="text-3xl font-bold text-gray-900">{{ $t('examSimulation.title') }}</h1>
        <p class="text-gray-600 mt-2">
          {{ $t('examSimulation.description') }}
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">{{ error }}</p>
        <button @click="error = null" class="text-red-600 hover:text-red-800 mt-2 text-sm">
          {{ $t('examSimulation.close') }}
        </button>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Sidebar: Context Overview -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.detectedContext') }}</h2>

            <div v-if="examContext" class="space-y-3">
              <div v-if="examContext.profession">
                <span class="text-gray-500 text-sm">{{ $t('examSimulation.profession') }}</span>
                <p class="font-medium">{{ examContext.profession }}</p>
              </div>
              <div v-if="examContext.exam_level">
                <span class="text-gray-500 text-sm">{{ $t('examSimulation.examLevel') }}</span>
                <p class="font-medium">{{ examContext.exam_level }}</p>
              </div>
              <div v-if="examContext.region">
                <span class="text-gray-500 text-sm">{{ $t('examSimulation.region') }}</span>
                <p class="font-medium">{{ examContext.region }}</p>
              </div>
              <div class="pt-2 border-t">
                <span class="text-gray-500 text-sm">{{ $t('examSimulation.confidence') }}</span>
                <div class="flex items-center gap-2 mt-1">
                  <div class="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-blue-600 h-2 rounded-full"
                      :style="{ width: `${(examContext.confidence || 0) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium">
                    {{ Math.round((examContext.confidence || 0) * 100) }}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Weak Topics -->
          <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.weakTopics') }}</h2>
            <div v-if="examContext?.weak_topics?.length" class="space-y-2">
              <div
                v-for="topic in examContext.weak_topics"
                :key="topic.topic"
                class="flex items-center justify-between"
              >
                <span class="text-sm">{{ topic.topic }}</span>
                <span :class="['text-sm font-medium', getTopicColor(topic.score)]">
                  {{ Math.round(topic.score) }}%
                </span>
              </div>
            </div>
            <p v-else class="text-gray-500 text-sm">{{ $t('examSimulation.noDataAvailable') }}</p>
          </div>

          <!-- Strong Topics -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.strongTopics') }}</h2>
            <div v-if="examContext?.strong_topics?.length" class="space-y-2">
              <div
                v-for="topic in examContext.strong_topics"
                :key="topic.topic"
                class="flex items-center justify-between"
              >
                <span class="text-sm">{{ topic.topic }}</span>
                <span :class="['text-sm font-medium', getTopicColor(topic.score)]">
                  {{ Math.round(topic.score) }}%
                </span>
              </div>
            </div>
            <p v-else class="text-gray-500 text-sm">{{ $t('examSimulation.noDataAvailable') }}</p>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="lg:col-span-2">
          <!-- Student Notice (if no simulations available) -->
          <div v-if="isStudent && simulations.length === 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6 text-center">
            <div class="text-4xl mb-3">📚</div>
            <h3 class="text-lg font-semibold text-yellow-800 mb-2">{{ $t('examSimulation.noExamsAvailable') }}</h3>
            <p class="text-yellow-700">
              {{ $t('examSimulation.noExamsAvailableDesc') }}
            </p>
          </div>

          <!-- Tabs -->
          <div v-if="isCreator || simulations.length > 0" class="bg-white rounded-lg shadow mb-6">
            <div class="border-b flex">
              <button
                @click="activeTab = 'overview'"
                :class="[
                  'px-6 py-4 text-sm font-medium',
                  activeTab === 'overview'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                ]"
              >
                {{ $t('examSimulation.tabs.overview') }}
              </button>
              <!-- Only show config tab for creators -->
              <button
                v-if="isCreator"
                @click="activeTab = 'config'"
                :class="[
                  'px-6 py-4 text-sm font-medium',
                  activeTab === 'config'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                ]"
              >
                {{ $t('examSimulation.tabs.newSimulation') }}
              </button>
              <button
                v-if="currentSimulation?.status === 'ready'"
                @click="activeTab = 'exam'"
                :class="[
                  'px-6 py-4 text-sm font-medium',
                  activeTab === 'exam'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                ]"
              >
                {{ $t('examSimulation.tabs.exam') }}
              </button>
              <button
                @click="activeTab = 'history'"
                :class="[
                  'px-6 py-4 text-sm font-medium',
                  activeTab === 'history'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                ]"
              >
                {{ $t('examSimulation.tabs.history') }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-6">
              <!-- Overview Tab -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-4">{{ $t('examSimulation.overview.title') }}</h3>

                <div v-if="simulations.length === 0" class="text-center py-10">
                  <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-gray-500 mb-4">{{ $t('examSimulation.overview.noSimulations') }}</p>
                  <button
                    @click="activeTab = 'config'"
                    class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    {{ $t('examSimulation.overview.createFirst') }}
                  </button>
                </div>

                <div v-else class="space-y-4">
                  <div
                    v-for="sim in simulations"
                    :key="sim.simulation_id"
                    @click="selectSimulation(sim)"
                    class="border rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors"
                    :class="{ 'border-blue-500 bg-blue-50': currentSimulation?.simulation_id === sim.simulation_id }"
                  >
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="font-medium">{{ sim.title }}</h4>
                        <p class="text-sm text-gray-500">
                          {{ new Date(sim.created_at).toLocaleDateString('de-DE') }}
                        </p>
                      </div>
                      <span :class="['px-2 py-1 text-xs rounded-full', getStatusColor(sim.status)]">
                        {{ getStatusLabel(sim.status) }}
                      </span>
                    </div>
                    <div class="mt-2 flex items-center gap-4 text-sm text-gray-600">
                      <span>{{ getDifficultyLabel(sim.config.difficulty) }}</span>
                      <span>{{ sim.config.time_limit_minutes }} {{ $t('examSimulation.overview.minutes') }}</span>
                      <span v-if="sim.attempt_count > 0">
                        {{ $t('examSimulation.overview.attempts', { count: sim.attempt_count }) }}
                      </span>
                      <span v-if="sim.best_score" class="text-green-600 font-medium">
                        {{ $t('examSimulation.overview.best') }} {{ Math.round(sim.best_score) }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Config Tab -->
              <div v-else-if="activeTab === 'config'">
                <h3 class="text-lg font-semibold mb-6">{{ $t('examSimulation.config.title') }}</h3>

                <!-- Mode Selection -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">{{ $t('examSimulation.config.mode') }}</label>
                  <div class="grid grid-cols-2 gap-4">
                    <button
                      @click="mode = 'smart'"
                      :class="[
                        'p-4 border-2 rounded-lg text-left transition-colors',
                        mode === 'smart'
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      ]"
                    >
                      <div class="font-medium">{{ $t('examSimulation.config.smartMode') }}</div>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ $t('examSimulation.config.smartModeDesc') }}
                      </p>
                    </button>
                    <button
                      @click="mode = 'manual'"
                      :class="[
                        'p-4 border-2 rounded-lg text-left transition-colors',
                        mode === 'manual'
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      ]"
                    >
                      <div class="font-medium">{{ $t('examSimulation.config.manualMode') }}</div>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ $t('examSimulation.config.manualModeDesc') }}
                      </p>
                    </button>
                  </div>
                </div>

                <!-- Difficulty -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">{{ $t('examSimulation.config.difficulty') }}</label>
                  <div class="flex gap-4">
                    <button
                      v-for="diff in ['easy', 'realistic', 'hard'] as const"
                      :key="diff"
                      @click="difficulty = diff"
                      :class="[
                        'flex-1 py-3 px-4 border-2 rounded-lg text-center transition-colors',
                        difficulty === diff
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      ]"
                    >
                      {{ getDifficultyLabel(diff) }}
                    </button>
                  </div>
                </div>

                <!-- Time Limit -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    {{ $t('examSimulation.config.timeLimit', { minutes: timeLimit }) }}
                  </label>
                  <input
                    type="range"
                    v-model="timeLimit"
                    min="15"
                    max="180"
                    step="15"
                    class="w-full"
                  />
                  <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>15 {{ $t('examSimulation.overview.minutes') }}</span>
                    <span>90 {{ $t('examSimulation.overview.minutes') }}</span>
                    <span>180 {{ $t('examSimulation.overview.minutes') }}</span>
                  </div>
                </div>

                <!-- Manual Focus Distribution -->
                <div v-if="mode === 'manual' && Object.keys(customFocus).length > 0" class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    {{ $t('examSimulation.config.topicDistribution') }}
                  </label>
                  <div class="space-y-3">
                    <div v-for="(percent, topic) in customFocus" :key="topic" class="flex items-center gap-3">
                      <span class="w-32 text-sm">{{ topic }}</span>
                      <input
                        type="range"
                        v-model.number="customFocus[topic]"
                        min="0"
                        max="100"
                        step="5"
                        class="flex-1"
                      />
                      <span class="w-12 text-sm font-medium text-right">{{ percent }}%</span>
                    </div>
                  </div>
                </div>

                <!-- Generate Button -->
                <button
                  @click="createNewSimulation"
                  :disabled="generating"
                  class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <template v-if="generating">
                    <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    {{ $t('examSimulation.config.generating') }}
                  </template>
                  <template v-else>
                    {{ $t('examSimulation.config.generateExam') }}
                  </template>
                </button>
              </div>

              <!-- Exam Tab -->
              <div v-else-if="activeTab === 'exam' && currentSimulation?.status === 'ready'">
                <!-- Not Started -->
                <div v-if="!currentAttempt && !showResults" class="text-center py-10">
                  <h3 class="text-xl font-semibold mb-2">{{ currentSimulation.title }}</h3>
                  <p class="text-gray-500 mb-6">
                    {{ currentSimulation.result?.questions?.length || 0 }} {{ $t('examSimulation.exam.questions') }} |
                    {{ currentSimulation.result?.total_points || 100 }} {{ $t('examSimulation.exam.points') }} |
                    {{ currentSimulation.config.time_limit_minutes }} {{ $t('examSimulation.overview.minutes') }}
                  </p>
                  <button
                    @click="startExam"
                    class="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 text-lg"
                  >
                    {{ $t('examSimulation.exam.startExam') }}
                  </button>
                </div>

                <!-- Exam in Progress -->
                <div v-else-if="currentAttempt && !showResults">
                  <div class="mb-6 flex items-center justify-between">
                    <div>
                      <span class="text-sm text-gray-500">{{ $t('examSimulation.exam.questionOf', { current: currentQuestionIndex + 1, total: questions.length }) }}</span>
                      <div class="h-2 w-48 bg-gray-200 rounded-full mt-1">
                        <div
                          class="h-2 bg-blue-600 rounded-full"
                          :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"
                        ></div>
                      </div>
                    </div>
                    <span class="text-sm font-medium">
                      {{ questions[currentQuestionIndex]?.points }} {{ $t('examSimulation.exam.points') }}
                    </span>
                  </div>

                  <!-- Question -->
                  <div class="mb-6">
                    <div class="mb-2 flex items-center gap-2">
                      <span class="text-xs bg-gray-100 px-2 py-1 rounded">
                        {{ questions[currentQuestionIndex]?.topic }}
                      </span>
                      <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {{ questions[currentQuestionIndex]?.type === 'mc' ? 'Multiple Choice' : questions[currentQuestionIndex]?.type }}
                      </span>
                    </div>
                    <p class="text-lg">{{ questions[currentQuestionIndex]?.question }}</p>
                  </div>

                  <!-- Answer Options (MC) -->
                  <div
                    v-if="questions[currentQuestionIndex]?.type === 'mc'"
                    class="space-y-3 mb-6"
                  >
                    <button
                      v-for="option in questions[currentQuestionIndex]?.options"
                      :key="option"
                      @click="userAnswers[questions[currentQuestionIndex].question_id] = option.charAt(0)"
                      :class="[
                        'w-full text-left p-4 border-2 rounded-lg transition-colors',
                        userAnswers[questions[currentQuestionIndex]?.question_id] === option.charAt(0)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      ]"
                    >
                      {{ option }}
                    </button>
                  </div>

                  <!-- Free Text Answer -->
                  <div v-else class="mb-6">
                    <textarea
                      v-model="userAnswers[questions[currentQuestionIndex]?.question_id]"
                      rows="4"
                      class="w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      :placeholder="$t('examSimulation.exam.yourAnswer')"
                    ></textarea>
                  </div>

                  <!-- Navigation -->
                  <div class="flex items-center justify-between">
                    <button
                      @click="currentQuestionIndex--"
                      :disabled="currentQuestionIndex === 0"
                      class="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
                    >
                      {{ $t('examSimulation.exam.back') }}
                    </button>

                    <div class="flex gap-2">
                      <button
                        v-if="currentQuestionIndex < questions.length - 1"
                        @click="currentQuestionIndex++"
                        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        {{ $t('examSimulation.exam.next') }}
                      </button>
                      <button
                        v-else
                        @click="submitExam"
                        class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        {{ $t('examSimulation.exam.submit') }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Results -->
                <div v-else-if="showResults && attemptResult">
                  <div class="text-center mb-8">
                    <div
                      :class="[
                        'inline-block text-6xl font-bold mb-2',
                        attemptResult.passed ? 'text-green-600' : 'text-red-600'
                      ]"
                    >
                      {{ Math.round(attemptResult.percentage) }}%
                    </div>
                    <p class="text-xl">
                      {{ attemptResult.passed ? $t('examSimulation.results.passed') : $t('examSimulation.results.notPassed') }}
                    </p>
                    <p class="text-gray-500 mt-2">
                      {{ attemptResult.score }} / {{ attemptResult.max_score }} {{ $t('examSimulation.exam.points') }} |
                      {{ formatTime(attemptResult.time_spent_seconds) }}
                    </p>
                  </div>

                  <!-- Results by Topic -->
                  <div class="mb-6">
                    <h4 class="font-medium mb-3">{{ $t('examSimulation.results.resultsByTopic') }}</h4>
                    <div class="space-y-2">
                      <div
                        v-for="(data, topic) in attemptResult.results_by_topic"
                        :key="topic"
                        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <span>{{ topic }}</span>
                        <div class="flex items-center gap-4">
                          <span class="text-sm text-gray-500">
                            {{ data.correct }} / {{ data.total }} {{ $t('examSimulation.results.correct') }}
                          </span>
                          <span class="font-medium">
                            {{ data.points }} / {{ data.max_points }} {{ $t('examSimulation.exam.points') }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    @click="showResults = false; activeTab = 'overview'"
                    class="w-full py-3 border rounded-lg hover:bg-gray-50"
                  >
                    {{ $t('examSimulation.results.backToOverview') }}
                  </button>
                </div>
              </div>

              <!-- History Tab -->
              <div v-else-if="activeTab === 'history'">
                <h3 class="text-lg font-semibold mb-4">{{ $t('examSimulation.history.title') }}</h3>

                <div v-if="simulations.length === 0" class="text-center py-10 text-gray-500">
                  {{ $t('examSimulation.history.noExams') }}
                </div>

                <div v-else class="space-y-4">
                  <div
                    v-for="sim in simulations.filter(s => s.attempt_count > 0)"
                    :key="sim.simulation_id"
                    class="border rounded-lg p-4"
                  >
                    <div class="flex items-start justify-between mb-2">
                      <h4 class="font-medium">{{ sim.title }}</h4>
                      <span class="text-sm text-gray-500">
                        {{ $t('examSimulation.history.attempts', { count: sim.attempt_count }) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-6 text-sm">
                      <div>
                        <span class="text-gray-500">{{ $t('examSimulation.history.best') }}</span>
                        <span class="font-medium text-green-600 ml-1">
                          {{ sim.best_score ? Math.round(sim.best_score) + '%' : '-' }}
                        </span>
                      </div>
                      <div>
                        <span class="text-gray-500">{{ $t('examSimulation.history.average') }}</span>
                        <span class="font-medium ml-1">
                          {{ sim.avg_score ? Math.round(sim.avg_score) + '%' : '-' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exam-simulation-page {
  font-family: 'Inter', system-ui, sans-serif;
}

input[type="range"] {
  @apply h-2 rounded-lg appearance-none cursor-pointer bg-gray-200;
}

input[type="range"]::-webkit-slider-thumb {
  @apply w-4 h-4 bg-blue-600 rounded-full appearance-none cursor-pointer;
}
</style>
