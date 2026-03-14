/**
 * Composable for exam management business logic.
 *
 * Shared composable for ExamManager component.
 * Provides state management, form handling, and API operations for exams.
 */

import { ref, computed, onMounted } from 'vue'
import {
  adminListExams,
  adminCreateExam,
  adminDeleteExam,
  adminGenerateExam,
  type Exam,
  type ExamCreateRequest,
  type ExamGenerateRequest
} from '@/infrastructure/api/clients/panel/admin'
import { fetchExamTypes, type ExamType } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'

interface ExamManagerOptions {
  courseId: string
}

function createDefaultCreateForm(): ExamCreateRequest {
  return {
    title: '',
    description: '',
    exam_type: 'practice',
    duration_minutes: 60,
    passing_score: 50,
    total_points: 100,
    published: false
  }
}

function createDefaultGenerateForm(): ExamGenerateRequest {
  return {
    title: '',
    description: '',
    exam_standard: 'FI_AP1',
    difficulty: 'intermediate',
    duration_minutes: 90,
    passing_score: 50,
    total_points: 100,
    question_distribution: {
      mcq: 20,
      fill_blanks: 8,
      short_answer: 2,
      case_study: 0
    }
  }
}

export function useExamManager(options: ExamManagerOptions) {
  const exams = ref<Exam[]>([])
  const examTypes = ref<ExamType[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)
  const showCreateDialog = ref(false)
  const showGenerateDialog = ref(false)

  const createForm = ref<ExamCreateRequest>(createDefaultCreateForm())
  const generateForm = ref<ExamGenerateRequest>(createDefaultGenerateForm())

  const totalQuestions = computed((): number => {
    return Object.values(generateForm.value.question_distribution).reduce((a, b) => a + b, 0)
  })

  const canCreate = computed((): boolean => {
    return !!createForm.value.title
  })

  const canGenerate = computed((): boolean => {
    return !!generateForm.value.title && totalQuestions.value >= 5
  })

  async function loadExams(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      exams.value = await adminListExams(options.courseId)
    } catch (err: any) {
      console.error('Error loading exams:', err)
      error.value = err.response?.data?.message || null
    } finally {
      loading.value = false
    }
  }

  async function createExam(): Promise<boolean> {
    if (!canCreate.value) return false

    try {
      await adminCreateExam(options.courseId, createForm.value)
      showCreateDialog.value = false
      createForm.value = createDefaultCreateForm()
      await loadExams()
      return true
    } catch (err: any) {
      console.error('Error creating exam:', err)
      throw err
    }
  }

  async function generateExam(): Promise<{ job_id: string; exam_id: string }> {
    if (!canGenerate.value) throw new Error('Invalid generate form')

    try {
      const result = await adminGenerateExam(options.courseId, generateForm.value)
      showGenerateDialog.value = false
      generateForm.value = createDefaultGenerateForm()
      setTimeout(() => loadExams(), 5000)
      return result
    } catch (err: any) {
      console.error('Error generating exam:', err)
      throw err
    }
  }

  async function deleteExam(exam: Exam): Promise<boolean> {
    try {
      await adminDeleteExam(exam.exam_id)
      await loadExams()
      return true
    } catch (err: any) {
      console.error('Error deleting exam:', err)
      throw err
    }
  }

  async function loadExamTypes(): Promise<void> {
    try {
      examTypes.value = await fetchExamTypes()
    } catch {
      // Non-critical — generate dialog still works with empty list
    }
  }

  onMounted(() => {
    loadExams()
    loadExamTypes()
  })

  return {
    exams,
    examTypes,
    loading,
    error,
    showCreateDialog,
    showGenerateDialog,
    createForm,
    generateForm,
    totalQuestions,
    canCreate,
    canGenerate,
    loadExams,
    createExam,
    generateExam,
    deleteExam
  }
}
