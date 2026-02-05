<!--
  Admin Lesson Editor Panel - Phase 6 Complete

  Full-featured lesson editor with:
  - Auto-save (debounced 800ms)
  - Type-specific content editors (text, video, quiz, exam)
  - Validation
  - Save status indicator
-->

<template>
  <div class="admin-lesson-editor-panel h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Context & Save Status -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <p class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('features.lessonEditor.moduleLabel') }} <span class="font-medium text-[var(--color-text-primary)]">{{ moduleId }}</span>
        </p>
        <!-- Save Status Indicator -->
        <div class="flex items-center gap-2 text-xs">
          <span v-if="saveStatus === 'saving'" class="text-blue-600 flex items-center gap-1">
            <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ $t('features.lessonEditor.saving') }}
          </span>
          <span v-else-if="saveStatus === 'saved'" class="text-green-600 flex items-center gap-1">
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            {{ $t('features.lessonEditor.saved') }}
          </span>
          <span v-else-if="saveStatus === 'error'" class="text-red-600">
            {{ errorMessage || $t('common.error') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="space-y-6 max-w-3xl mx-auto">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('features.lessonEditor.lessonTitle') }}
          </label>
          <input
            v-model="form.title"
            @input="debouncedSave"
            type="text"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('features.lessonEditor.titlePlaceholder')"
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('features.lessonEditor.description') }}
          </label>
          <textarea
            v-model="form.description"
            @input="debouncedSave"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('features.lessonEditor.descriptionPlaceholder')"
          ></textarea>
        </div>

        <!-- Lesson Type -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('features.lessonEditor.lessonType') }}
          </label>
          <select
            v-model="form.lesson_type"
            @change="handleTypeChange"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="">{{ $t('features.lessonEditor.selectType') }}</option>
            <option value="text">📄 {{ $t('features.lessonEditor.types.text') }}</option>
            <option value="video">🎥 {{ $t('features.lessonEditor.types.video') }}</option>
            <option value="quiz">❓ {{ $t('features.lessonEditor.types.quiz') }}</option>
            <option value="interactive">🎮 {{ $t('features.lessonEditor.types.interactive') }}</option>
            <option value="exercise">💪 {{ $t('features.lessonEditor.types.exercise') }}</option>
            <option value="ai">🤖 {{ $t('features.lessonEditor.types.ai') }}</option>
            <option value="exam">📝 {{ $t('features.lessonEditor.types.exam') }}</option>
          </select>
        </div>

        <!-- Order & Duration -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.lessonEditor.order') }}
            </label>
            <input
              v-model.number="form.order_index"
              @input="debouncedSave"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.lessonEditor.duration') }}
            </label>
            <input
              v-model.number="form.duration_minutes"
              @input="debouncedSave"
              type="number"
              min="0"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="15"
            />
          </div>
        </div>

        <!-- Type-Specific Content -->
        <div v-if="form.lesson_type" class="border-t border-[var(--color-border)] pt-6">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
            {{ lessonTypeLabel }} - {{ $t('features.lessonEditor.content') }}
          </h3>

          <!-- TEXT Editor -->
          <div v-if="form.lesson_type === 'text'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('features.lessonEditor.textContent') }}
              </label>
              <textarea
                v-model="form.content.text"
                @input="debouncedSave"
                rows="12"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-mono text-sm"
                :placeholder="$t('features.lessonEditor.textPlaceholder')"
              ></textarea>
              <p class="text-xs text-[var(--color-text-tertiary)] mt-1">{{ $t('features.lessonEditor.markdownHint') }}</p>
            </div>
          </div>

          <!-- VIDEO Editor -->
          <div v-else-if="form.lesson_type === 'video'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('features.lessonEditor.videoUrl') }}
              </label>
              <input
                v-model="form.content.video_url"
                @input="debouncedSave"
                type="url"
                required
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('features.lessonEditor.videoUrlPlaceholder')"
              />
              <p class="text-xs text-[var(--color-text-tertiary)] mt-1">{{ $t('features.lessonEditor.videoUrlHint') }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('features.lessonEditor.videoDescription') }}
              </label>
              <textarea
                v-model="form.content.video_description"
                @input="debouncedSave"
                rows="4"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('features.lessonEditor.videoDescPlaceholder')"
              ></textarea>
            </div>
          </div>

          <!-- QUIZ Editor -->
          <div v-else-if="form.lesson_type === 'quiz'" class="space-y-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ $t('features.lessonEditor.questions') }} ({{ form.content.questions.length }})
              </h4>
              <button
                @click="addQuestion"
                class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
              >
                {{ $t('features.lessonEditor.addQuestion') }}
              </button>
            </div>

            <div v-for="(question, qIdx) in form.content.questions" :key="qIdx" class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 space-y-3">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1">
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                    {{ $t('features.lessonEditor.question') }} {{ qIdx + 1 }}
                  </label>
                  <input
                    v-model="question.text"
                    @input="debouncedSave"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  />
                </div>
                <button
                  @click="removeQuestion(qIdx)"
                  class="p-2 text-red-600 hover:bg-red-500/10 rounded"
                  :title="$t('features.lessonEditor.deleteQuestion')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div class="space-y-2">
                <label class="block text-sm font-medium text-[var(--color-text-primary)]">
                  {{ $t('features.lessonEditor.answerOptions') }}
                </label>
                <div v-for="(option, oIdx) in question.options" :key="oIdx" class="flex items-center gap-2">
                  <input
                    v-model="question.correct_indices"
                    :value="oIdx"
                    @change="debouncedSave"
                    type="checkbox"
                    class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded"
                  />
                  <input
                    v-model="option.text"
                    @input="debouncedSave"
                    type="text"
                    required
                    class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    :placeholder="`Option ${oIdx + 1}`"
                  />
                  <button
                    v-if="question.options.length > 2"
                    @click="removeOption(qIdx, oIdx)"
                    class="p-2 text-red-600 hover:bg-red-500/10 rounded"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <button
                  v-if="question.options.length < 5"
                  @click="addOption(qIdx)"
                  class="text-sm text-[var(--color-primary)] hover:underline"
                >
                  {{ $t('features.lessonEditor.addOption') }}
                </button>
              </div>
            </div>

            <div v-if="form.content.questions.length === 0" class="text-center py-8 text-[var(--color-text-tertiary)]">
              {{ $t('features.lessonEditor.noQuestions') }}
            </div>
          </div>

          <!-- EXAM Editor -->
          <div v-else-if="form.lesson_type === 'exam'" class="space-y-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ $t('features.lessonEditor.examQuestions') }} ({{ form.content.exam_questions.length }})
              </h4>
              <button
                @click="addExamQuestion"
                class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
              >
                {{ $t('features.lessonEditor.addExamQuestion') }}
              </button>
            </div>

            <div v-for="(question, idx) in form.content.exam_questions" :key="idx" class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 space-y-3">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1">
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                    {{ $t('features.lessonEditor.question') }} {{ idx + 1 }}
                  </label>
                  <textarea
                    v-model="question.text"
                    @input="debouncedSave"
                    rows="2"
                    required
                    class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  ></textarea>
                </div>
                <button
                  @click="removeExamQuestion(idx)"
                  class="p-2 text-red-600 hover:bg-red-500/10 rounded"
                  :title="$t('features.lessonEditor.deleteQuestion')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div>
                <label class="block text-sm text-[var(--color-text-primary)] mb-1">
                  {{ $t('features.lessonEditor.points') }}
                </label>
                <input
                  v-model.number="question.points"
                  @input="debouncedSave"
                  type="number"
                  min="1"
                  class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="10"
                />
              </div>
            </div>

            <div v-if="form.content.exam_questions.length === 0" class="text-center py-8 text-[var(--color-text-tertiary)]">
              {{ $t('features.lessonEditor.noExamQuestions') }}
            </div>
          </div>

          <!-- OTHER Types Placeholder -->
          <div v-else class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-sm text-blue-700">
              ℹ️ {{ $t('features.lessonEditor.notImplemented', { type: lessonTypeLabel }) }}
            </p>
          </div>
        </div>

        <!-- Validation Messages -->
        <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-sm font-semibold text-red-800 mb-2">{{ $t('features.lessonEditor.validation.title') }}</p>
          <ul class="list-disc list-inside text-sm text-red-700 space-y-1">
            <li v-for="(error, idx) in validationErrors" :key="idx">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'

const { t } = useI18n()
import type { LsxPanel } from '@/application/stores/modules/desktop'
import {
  adminCreateLesson,
  adminUpdateLesson,
  type AdminLesson,
  type AdminLessonCreateRequest,
  type AdminLessonUpdateRequest,
  type LessonType
} from '@/application/services/api/admin'

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const panelStore = usePanelStore()

// State
const lesson = ref<AdminLesson | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const errorMessage = ref<string | null>(null)
const isCreating = ref(false)

// Form
const form = ref({
  title: '',
  description: '',
  lesson_type: '',
  order_index: 1,
  duration_minutes: 15,
  content: {
    text: '',
    video_url: '',
    video_description: '',
    questions: [] as Array<{
      text: string
      options: Array<{ text: string }>
      correct_indices: number[]
    }>,
    exam_questions: [] as Array<{
      text: string
      points: number
    }>
  }
})

// Auto-save timeout
let saveTimeout: number | null = null

// Computed
const isNewLesson = computed(() => !props.panel.payload?.lessonId)
const _courseId = computed(() => props.panel.payload?.courseId as string)  // UUID
const moduleId = computed(() => props.panel.payload?.moduleId as number)
const lessonId = computed(() => props.panel.payload?.lessonId as string | undefined)  // UUID

const lessonTypeLabel = computed(() => {
  const typeKey = form.value.lesson_type
  if (!typeKey) return ''
  return t(`features.lessonEditor.typeLabels.${typeKey}`) || typeKey
})

const validationErrors = computed(() => {
  const errors: string[] = []

  if (!form.value.title.trim()) {
    errors.push(t('features.lessonEditor.validation.titleRequired'))
  }

  if (!form.value.lesson_type) {
    errors.push(t('features.lessonEditor.validation.typeRequired'))
  }

  if (form.value.lesson_type === 'video' && !form.value.content.video_url) {
    errors.push(t('features.lessonEditor.validation.videoUrlRequired'))
  }

  if (form.value.lesson_type === 'quiz') {
    if (form.value.content.questions.length === 0) {
      errors.push(t('features.lessonEditor.validation.minOneQuestion'))
    }

    form.value.content.questions.forEach((q, idx) => {
      if (!q.text.trim()) {
        errors.push(t('features.lessonEditor.validation.questionTextMissing', { num: idx + 1 }))
      }
      if (q.options.length < 2) {
        errors.push(t('features.lessonEditor.validation.minTwoAnswers', { num: idx + 1 }))
      }
      if (q.correct_indices.length === 0) {
        errors.push(t('features.lessonEditor.validation.minOneCorrect', { num: idx + 1 }))
      }
    })
  }

  return errors
})

// Methods
const loadLesson = () => {
  if (isNewLesson.value) {
    return
  }

  if (props.panel.payload?.lesson) {
    lesson.value = props.panel.payload.lesson
    populateForm()
  }
}

const populateForm = () => {
  if (!lesson.value) return

  form.value = {
    title: lesson.value.title || '',
    description: lesson.value.description || '',
    lesson_type: lesson.value.lesson_type || '',
    order_index: lesson.value.order_index || 1,
    duration_minutes: lesson.value.duration_minutes || 15,
    content: lesson.value.content || {
      text: '',
      video_url: '',
      video_description: '',
      questions: [],
      exam_questions: []
    }
  }
}

const handleTypeChange = () => {
  // Reset content when type changes
  form.value.content = {
    text: '',
    video_url: '',
    video_description: '',
    questions: [],
    exam_questions: []
  }
  debouncedSave()
}

const debouncedSave = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }

  saveTimeout = window.setTimeout(() => {
    saveLesson()
  }, 800)
}

const saveLesson = async () => {
  if (validationErrors.value.length > 0) {
    saveStatus.value = 'error'
    errorMessage.value = t('features.lessonEditor.validation.failed')
    setTimeout(() => {
      saveStatus.value = 'idle'
      errorMessage.value = null
    }, 3000)
    return
  }

  // Prevent multiple creations
  if (isCreating.value) return

  saveStatus.value = 'saving'

  try {
    if (isNewLesson.value && !lesson.value) {
      // Create new lesson
      if (!moduleId.value) {
        throw new Error(t('features.lessonEditor.errors.moduleIdMissing'))
      }

      isCreating.value = true

      const createData: AdminLessonCreateRequest = {
        title: form.value.title,
        lesson_type: form.value.lesson_type as LessonType || 'text',
        content: form.value.content,
        duration_minutes: form.value.duration_minutes,
        published: false,
        free_preview: false
      }

      const newLesson = await adminCreateLesson(moduleId.value, createData)
      lesson.value = newLesson

      // Update panel payload so subsequent saves are updates
      panelStore.updatePanelPayload(props.panel.id, {
        lessonId: newLesson.lesson_id,
        lesson: newLesson
      })

      isCreating.value = false
    } else if (lessonId.value || lesson.value?.lesson_id) {
      // Update existing lesson
      const lid = lessonId.value || lesson.value!.lesson_id

      const updateData: AdminLessonUpdateRequest = {
        title: form.value.title,
        lesson_type: form.value.lesson_type as LessonType || undefined,
        content: form.value.content,
        duration_minutes: form.value.duration_minutes,
        order_index: form.value.order_index
      }

      const updatedLesson = await adminUpdateLesson(lid, updateData)
      lesson.value = updatedLesson

      // Update panel payload
      panelStore.updatePanelPayload(props.panel.id, {
        lesson: updatedLesson
      })
    }

    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)

    // Dispatch event to notify parent panels (e.g., ModuleEditor) about lesson updates
    window.dispatchEvent(new CustomEvent('lesson-updated', {
      detail: {
        moduleId: moduleId.value,
        lessonId: lesson.value?.lesson_id
      }
    }))
  } catch (err: any) {
    console.error('Error saving lesson:', err)
    isCreating.value = false
    saveStatus.value = 'error'
    errorMessage.value = err.response?.data?.message || err.message
    setTimeout(() => {
      saveStatus.value = 'idle'
      errorMessage.value = null
    }, 3000)
  }
}

// Quiz Handlers
const addQuestion = () => {
  form.value.content.questions.push({
    text: '',
    options: [
      { text: '' },
      { text: '' }
    ],
    correct_indices: []
  })
  debouncedSave()
}

const removeQuestion = (idx: number) => {
  form.value.content.questions.splice(idx, 1)
  debouncedSave()
}

const addOption = (questionIdx: number) => {
  form.value.content.questions[questionIdx].options.push({ text: '' })
  debouncedSave()
}

const removeOption = (questionIdx: number, optionIdx: number) => {
  const question = form.value.content.questions[questionIdx]
  question.options.splice(optionIdx, 1)

  // Update correct_indices
  question.correct_indices = question.correct_indices
    .filter(i => i !== optionIdx)
    .map(i => i > optionIdx ? i - 1 : i)

  debouncedSave()
}

// Exam Handlers
const addExamQuestion = () => {
  form.value.content.exam_questions.push({
    text: '',
    points: 10
  })
  debouncedSave()
}

const removeExamQuestion = (idx: number) => {
  form.value.content.exam_questions.splice(idx, 1)
  debouncedSave()
}

// Lifecycle
onMounted(() => {
  loadLesson()
})
</script>
