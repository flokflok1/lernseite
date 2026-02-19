/**
 * useExamSimulation Composable
 *
 * Encapsulates all exam simulation business logic:
 * - Loading exam context and simulation list
 * - Creating/generating new simulations
 * - Starting/submitting exam attempts
 * - Polling for generation status
 * - Utility formatting functions
 */

import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
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
} from '@/infrastructure/api/clients/panel/user/exam/examSimulation.api'

export type ActiveTab = 'overview' | 'config' | 'exam' | 'history'
export type ExamMode = 'smart' | 'manual'
export type ExamDifficulty = 'easy' | 'realistic' | 'hard'

export function useExamSimulation() {
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
  const mode = ref<ExamMode>('smart')
  const difficulty = ref<ExamDifficulty>('realistic')
  const timeLimit = ref(90)
  const customFocus = ref<Record<string, number>>({})

  // UI State
  const activeTab = ref<ActiveTab>('overview')
  const currentQuestionIndex = ref(0)

  // ============================================================================
  // LIFECYCLE & WATCHERS
  // ============================================================================

  onMounted(async () => {
    await loadExamContext()
    await loadSimulations()
    loading.value = false
  })

  watch(
    () => currentSimulation.value?.status,
    (status) => {
      if (status === 'generating') {
        pollGenerationStatus()
      }
    }
  )

  // ============================================================================
  // API METHODS
  // ============================================================================

  async function loadExamContext(): Promise<void> {
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

  async function loadSimulations(): Promise<void> {
    try {
      const result = await listExamSimulations({ course_id: courseId.value })
      simulations.value = result.simulations
    } catch (e: any) {
      console.error('Error loading simulations:', e)
    }
  }

  async function createNewSimulation(): Promise<void> {
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
      await generateExamSimulation(simulation.simulation_id)
      pollGenerationStatus()
    } catch (e: any) {
      error.value = t('examSimulation.errors.createSimulation')
      generating.value = false
      console.error(e)
    }
  }

  async function pollGenerationStatus(): Promise<void> {
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

  async function startExam(): Promise<void> {
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

  async function submitExam(): Promise<void> {
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

  function selectSimulation(sim: ExamSimulation): void {
    currentSimulation.value = sim
    if (sim.status === 'ready') {
      activeTab.value = 'exam'
    }
  }

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

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

  function goBack(): void {
    router.back()
  }

  function dismissError(): void {
    error.value = null
  }

  function returnToOverview(): void {
    showResults.value = false
    activeTab.value = 'overview'
  }

  return {
    // Route/Auth
    courseId,
    isCreator,
    isStudent,

    // State
    loading,
    generating,
    examContext,
    simulations,
    currentSimulation,
    currentAttempt,
    questions,
    userAnswers,
    showResults,
    attemptResult,
    error,

    // Configuration
    mode,
    difficulty,
    timeLimit,
    customFocus,

    // UI State
    activeTab,
    currentQuestionIndex,

    // Actions
    createNewSimulation,
    startExam,
    submitExam,
    selectSimulation,
    goBack,
    dismissError,
    returnToOverview,

    // Utilities
    formatTime,
    getTopicColor,
    getDifficultyLabel,
    getStatusLabel,
    getStatusColor
  }
}
