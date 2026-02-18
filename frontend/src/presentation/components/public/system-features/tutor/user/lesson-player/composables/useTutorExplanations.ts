/**
 * useTutorExplanations Composable
 *
 * Manages the explanation list for the Tutor Player:
 * - Load explanation list from API
 * - Select / generate explanations
 * - Edit titles, delete explanations
 *
 * Extracted from useTutorPlayer to keep files under 500 LOC.
 */

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'

import type { Ref } from 'vue'
import type { TutorialStep, ExplanationListItem } from './useTutorPlayer'
import type InteractiveWhiteboard from '../../InteractiveWhiteboard.vue'

export interface ExplanationDeps {
  lessonId: string
  lessonSteps: Ref<TutorialStep[]>
  currentStep: Ref<number>
  whiteboardRef: Ref<InstanceType<typeof InteractiveWhiteboard> | null>
  ttsError: Ref<string | null>
  ttsEnabled: Ref<boolean>
  options?: {
    lessonTitle?: string
    chapterTitle?: string
    courseTitle?: string
    lmType?: string
  }
}

export function useTutorExplanations(deps: ExplanationDeps) {
  const { t } = useI18n()
  const {
    lessonId,
    lessonSteps,
    currentStep,
    whiteboardRef,
    ttsError,
    ttsEnabled
  } = deps

  // State - Explanation List
  const explanationList = ref<ExplanationListItem[]>([])
  const selectedExplanationId = ref<string | null>(null)
  const isLoadingList = ref(false)
  const showNewForm = ref(false)

  // State - Generation
  const isGenerating = ref(false)
  const selectedStyle = ref<string>('adhs')
  const generateWithTTS = ref<boolean>(false)
  const selectedVoice = ref<string>('nova')

  // State - Edit/Delete
  const editingExplanation = ref<ExplanationListItem | null>(null)
  const editTitle = ref('')
  const deleteConfirm = ref<ExplanationListItem | null>(null)

  // ============================================================================
  // Methods - Explanation List
  // ============================================================================

  async function loadExplanationList(): Promise<void> {
    isLoadingList.value = true
    try {
      const response = await http.get(`/lessons/${lessonId}/explanations`)
      if (response.data.success) {
        explanationList.value = response.data.data.explanations || []
        if (explanationList.value.length > 0 && !selectedExplanationId.value) {
          await selectExplanation(explanationList.value[0].explanationId)
        } else if (explanationList.value.length === 0) {
          showNewForm.value = true
        }
      }
    } catch (error) {
      console.error('Failed to load explanation list:', error)
    } finally {
      isLoadingList.value = false
    }
  }

  async function selectExplanation(explanationId: string): Promise<void> {
    selectedExplanationId.value = explanationId
    showNewForm.value = false
    lessonSteps.value = []

    try {
      const response = await http.get(`/lesson-explanation/${explanationId}`)
      if (response.data.success) {
        lessonSteps.value = response.data.data.steps || []
        currentStep.value = 0
        if (whiteboardRef.value) {
          whiteboardRef.value.clearBoard()
        }
      }
    } catch (error) {
      console.error('Failed to load explanation:', error)
      ttsError.value = t('lesson.tutorPlayer.errors.loadingExplanation')
    }
  }

  async function generateSteps(): Promise<void> {
    isGenerating.value = true
    lessonSteps.value = []

    try {
      const response = await http.post('/admin/ai/generate-lesson-steps', {
        lesson_id: lessonId,
        lesson_title: deps.options?.lessonTitle,
        lm_type: deps.options?.lmType,
        chapter_title: deps.options?.chapterTitle,
        style: selectedStyle.value,
        generate_tts: generateWithTTS.value,
        tts_voice: selectedVoice.value
      })

      if (response.data.success) {
        lessonSteps.value = response.data.data.steps || []
        currentStep.value = 0
        showNewForm.value = false

        if (response.data.explanationId) {
          selectedExplanationId.value = response.data.explanationId
        }

        await loadExplanationList()

        if (response.data.audio) {
          ttsEnabled.value = true
        }
      } else {
        throw new Error(response.data.error?.message || t('lesson.tutorPlayer.errors.generationFailed'))
      }
    } catch (error: any) {
      console.error('Lesson steps generation failed:', error)
      ttsError.value = `${t('common.error')}: ${error.response?.data?.error?.message || error.message}`
    } finally {
      isGenerating.value = false
    }
  }

  // ============================================================================
  // Methods - Edit/Delete
  // ============================================================================

  function startEditTitle(expl: ExplanationListItem): void {
    editingExplanation.value = expl
    editTitle.value = expl.title
  }

  function cancelEdit(): void {
    editingExplanation.value = null
    editTitle.value = ''
  }

  async function saveTitle(): Promise<void> {
    if (!editingExplanation.value || !editTitle.value.trim()) return

    try {
      const response = await http.patch(
        `/lesson-explanation/${editingExplanation.value.explanationId}`,
        { title: editTitle.value.trim() }
      )
      if (response.data.success) {
        const idx = explanationList.value.findIndex(
          e => e.explanationId === editingExplanation.value?.explanationId
        )
        if (idx >= 0) {
          explanationList.value[idx].title = editTitle.value.trim()
        }
      }
    } catch (error) {
      console.error('Failed to update title:', error)
      ttsError.value = t('lesson.tutorPlayer.errors.savingTitle')
    } finally {
      cancelEdit()
    }
  }

  function confirmDelete(expl: ExplanationListItem): void {
    deleteConfirm.value = expl
  }

  async function executeDelete(): Promise<void> {
    if (!deleteConfirm.value) return

    try {
      const response = await http.delete(
        `/lesson-explanation/${deleteConfirm.value.explanationId}`
      )
      if (response.data.success) {
        explanationList.value = explanationList.value.filter(
          e => e.explanationId !== deleteConfirm.value?.explanationId
        )

        if (selectedExplanationId.value === deleteConfirm.value.explanationId) {
          selectedExplanationId.value = null
          lessonSteps.value = []
          if (explanationList.value.length > 0) {
            await selectExplanation(explanationList.value[0].explanationId)
          } else {
            showNewForm.value = true
          }
        }
      }
    } catch (error) {
      console.error('Failed to delete explanation:', error)
      ttsError.value = t('lesson.tutorPlayer.errors.deleting')
    } finally {
      deleteConfirm.value = null
    }
  }

  function cancelDelete(): void {
    deleteConfirm.value = null
  }

  // ============================================================================
  // Utilities
  // ============================================================================

  function formatDate(dateStr: string): string {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return d.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return {
    // State - Explanation List
    explanationList,
    selectedExplanationId,
    isLoadingList,
    showNewForm,

    // State - Generation
    isGenerating,
    selectedStyle,
    generateWithTTS,
    selectedVoice,

    // State - Edit/Delete
    editingExplanation,
    editTitle,
    deleteConfirm,

    // Methods - Explanation List
    loadExplanationList,
    selectExplanation,
    generateSteps,

    // Methods - Edit/Delete
    startEditTitle,
    cancelEdit,
    saveTitle,
    confirmDelete,
    executeDelete,
    cancelDelete,

    // Utilities
    formatDate
  }
}
