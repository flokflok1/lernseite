/**
 * useLessonEditor Composable
 *
 * Shared business logic for the lesson editor used by both
 * LessonEditorWindow and LessonEditorPanel variants.
 *
 * Handles form state, validation, auto-save, quiz/exam question
 * management, and API create/update calls.
 */

import { ref, computed, onMounted } from 'vue'
import {
  adminCreateLesson,
  adminUpdateLesson,
  type AdminLesson,
  type AdminLessonCreateRequest,
  type AdminLessonUpdateRequest,
  type LessonType
} from '@/infrastructure/api/clients/panel/admin'

export interface QuizQuestion {
  text: string
  options: Array<{ text: string }>
  correct_indices: number[]
}

export interface ExamQuestion {
  text: string
  points: number
}

export interface LessonFormContent {
  text: string
  video_url: string
  video_description: string
  questions: QuizQuestion[]
  exam_questions: ExamQuestion[]
}

export interface LessonForm {
  title: string
  description: string
  lesson_type: string
  order_index: number
  duration_minutes: number
  content: LessonFormContent
}

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export interface LessonEditorPayload {
  lessonId?: string
  courseId?: string
  moduleId?: number
  lesson?: AdminLesson
}

interface UseLessonEditorOptions {
  getPayload: () => LessonEditorPayload | undefined
  onPayloadUpdate: (patch: Record<string, unknown>) => void
}

function createEmptyContent(): LessonFormContent {
  return {
    text: '',
    video_url: '',
    video_description: '',
    questions: [],
    exam_questions: []
  }
}

function createDefaultForm(): LessonForm {
  return {
    title: '',
    description: '',
    lesson_type: '',
    order_index: 1,
    duration_minutes: 15,
    content: createEmptyContent()
  }
}

const LESSON_TYPE_LABELS: Record<string, string> = {
  text: 'Text-Lektion',
  video: 'Video-Lektion',
  quiz: 'Quiz',
  interactive: 'Interaktive Lektion',
  exercise: 'Übung',
  ai: 'KI-Lektion',
  exam: 'Prüfung'
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function useLessonEditor(options: UseLessonEditorOptions) {
  const { getPayload, onPayloadUpdate } = options

  // State
  const lesson = ref<AdminLesson | null>(null)
  const saveStatus = ref<SaveStatus>('idle')
  const errorMessage = ref<string | null>(null)
  const isCreating = ref(false)
  const form = ref<LessonForm>(createDefaultForm())

  let saveTimeout: number | null = null

  // Computed
  const payload = computed(() => getPayload())
  const isNewLesson = computed(() => !payload.value?.lessonId)
  const moduleId = computed(() => payload.value?.moduleId as number)
  const lessonId = computed(() => payload.value?.lessonId as string | undefined)

  const lessonTypeLabel = computed((): string => {
    return LESSON_TYPE_LABELS[form.value.lesson_type] || form.value.lesson_type
  })

  const validationErrors = computed((): string[] => {
    const errors: string[] = []

    if (!form.value.title.trim()) {
      errors.push('Titel ist erforderlich')
    }

    if (!form.value.lesson_type) {
      errors.push('Lektionstyp ist erforderlich')
    }

    if (form.value.lesson_type === 'video' && !form.value.content.video_url) {
      errors.push('Video-URL ist erforderlich')
    }

    if (form.value.lesson_type === 'quiz') {
      if (form.value.content.questions.length === 0) {
        errors.push('Mindestens 1 Frage erforderlich')
      }

      form.value.content.questions.forEach((q, idx) => {
        if (!q.text.trim()) {
          errors.push(`Frage ${idx + 1}: Text fehlt`)
        }
        if (q.options.length < 2) {
          errors.push(`Frage ${idx + 1}: Mindestens 2 Antworten erforderlich`)
        }
        if (q.correct_indices.length === 0) {
          errors.push(`Frage ${idx + 1}: Mindestens 1 richtige Antwort markieren`)
        }
      })
    }

    return errors
  })

  // Methods
  function populateForm(): void {
    if (!lesson.value) return

    form.value = {
      title: lesson.value.title || '',
      description: (lesson.value as Record<string, unknown>).description as string || '',
      lesson_type: lesson.value.lesson_type || '',
      order_index: lesson.value.order_index || 1,
      duration_minutes: lesson.value.duration_minutes || 15,
      content: (lesson.value.content as LessonFormContent) || createEmptyContent()
    }
  }

  function loadLesson(): void {
    if (isNewLesson.value) return

    if (payload.value?.lesson) {
      lesson.value = payload.value.lesson
      populateForm()
    }
  }

  function handleTypeChange(): void {
    form.value.content = createEmptyContent()
    debouncedSave()
  }

  function debouncedSave(): void {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    saveTimeout = window.setTimeout(() => {
      saveLesson()
    }, 800)
  }

  async function saveLesson(): Promise<void> {
    if (validationErrors.value.length > 0) {
      saveStatus.value = 'error'
      errorMessage.value = 'Validierung fehlgeschlagen'
      setTimeout(() => {
        saveStatus.value = 'idle'
        errorMessage.value = null
      }, 3000)
      return
    }

    if (isCreating.value) return

    saveStatus.value = 'saving'

    try {
      if (isNewLesson.value && !lesson.value) {
        if (!moduleId.value) {
          throw new Error('Modul-ID fehlt')
        }

        isCreating.value = true

        const createData: AdminLessonCreateRequest = {
          title: form.value.title,
          lesson_type: (form.value.lesson_type as LessonType) || 'text',
          content: form.value.content,
          duration_minutes: form.value.duration_minutes,
          published: false,
          free_preview: false
        }

        const newLesson = await adminCreateLesson(moduleId.value, createData)
        lesson.value = newLesson

        onPayloadUpdate({
          lessonId: newLesson.lesson_id,
          lesson: newLesson
        })

        isCreating.value = false
      } else if (lessonId.value || lesson.value?.lesson_id) {
        const lid = lessonId.value || lesson.value!.lesson_id

        const updateData: AdminLessonUpdateRequest = {
          title: form.value.title,
          lesson_type: (form.value.lesson_type as LessonType) || undefined,
          content: form.value.content,
          duration_minutes: form.value.duration_minutes,
          order_index: form.value.order_index
        }

        const updatedLesson = await adminUpdateLesson(lid, updateData)
        lesson.value = updatedLesson

        onPayloadUpdate({ lesson: updatedLesson })
      }

      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)

      window.dispatchEvent(new CustomEvent('lesson-updated', {
        detail: {
          moduleId: moduleId.value,
          lessonId: lesson.value?.lesson_id
        }
      }))
    } catch (err: unknown) {
      console.error('Error saving lesson:', err)
      isCreating.value = false
      saveStatus.value = 'error'
      const error = err as { response?: { data?: { message?: string } }; message?: string }
      errorMessage.value = error.response?.data?.message || error.message || null
      setTimeout(() => {
        saveStatus.value = 'idle'
        errorMessage.value = null
      }, 3000)
    }
  }

  // Quiz handlers
  function addQuestion(): void {
    form.value.content.questions.push({
      text: '',
      options: [{ text: '' }, { text: '' }],
      correct_indices: []
    })
    debouncedSave()
  }

  function removeQuestion(idx: number): void {
    form.value.content.questions.splice(idx, 1)
    debouncedSave()
  }

  function addOption(questionIdx: number): void {
    form.value.content.questions[questionIdx].options.push({ text: '' })
    debouncedSave()
  }

  function removeOption(questionIdx: number, optionIdx: number): void {
    const question = form.value.content.questions[questionIdx]
    question.options.splice(optionIdx, 1)
    question.correct_indices = question.correct_indices
      .filter(i => i !== optionIdx)
      .map(i => (i > optionIdx ? i - 1 : i))
    debouncedSave()
  }

  // Exam handlers
  function addExamQuestion(): void {
    form.value.content.exam_questions.push({ text: '', points: 10 })
    debouncedSave()
  }

  function removeExamQuestion(idx: number): void {
    form.value.content.exam_questions.splice(idx, 1)
    debouncedSave()
  }

  // Lifecycle
  onMounted(() => {
    loadLesson()
  })

  return {
    // State
    form,
    saveStatus,
    errorMessage,
    // Computed
    moduleId,
    lessonTypeLabel,
    validationErrors,
    // Methods
    debouncedSave,
    handleTypeChange,
    addQuestion,
    removeQuestion,
    addOption,
    removeOption,
    addExamQuestion,
    removeExamQuestion
  }
}
