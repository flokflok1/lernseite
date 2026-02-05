/**
 * useTutorPlayer Composable
 * ==========================
 * Business logic for Lesson Tutor Player
 *
 * Handles:
 * - Explanation list management (load, select, create, edit, delete)
 * - Step navigation
 * - TTS (Text-to-Speech) integration
 * - Whiteboard actions coordination
 */
import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/application/services/api/system'
import type InteractiveWhiteboard from '../../InteractiveWhiteboard.vue'

// ============================================================================
// Types
// ============================================================================

export interface SchemaRow {
  name: string
  operator: string
  value: string
  highlight?: boolean
}

export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position?: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration?: number
  color?: string
  fontSize?: number
  schema?: SchemaRow[]
}

export interface TutorialStep {
  title: string
  speech: string
  calculator?: string
  result?: string
  schema?: SchemaRow[]
  whiteboardActions?: WhiteboardAction[]
}

export interface ExplanationListItem {
  explanationId: string
  title: string
  style: string
  hasAudio: boolean
  tokensUsed: number
  createdAt: string
  updatedAt: string
}

// ============================================================================
// Composable
// ============================================================================

export function useTutorPlayer(lessonId: string, options?: {
  lessonTitle?: string
  chapterTitle?: string
  courseTitle?: string
  lmType?: string
}) {
  const { t } = useI18n()

  // State - Steps & Navigation
  const currentStep = ref(0)
  const lessonSteps = ref<TutorialStep[]>([])

  // State - Explanation List
  const explanationList = ref<ExplanationListItem[]>([])
  const selectedExplanationId = ref<string | null>(null)
  const isLoadingList = ref(false)

  // State - Generation
  const isGenerating = ref(false)
  const showNewForm = ref(false)

  // State - Edit/Delete
  const editingExplanation = ref<ExplanationListItem | null>(null)
  const editTitle = ref('')
  const deleteConfirm = ref<ExplanationListItem | null>(null)

  // State - TTS
  const ttsEnabled = ref(false)
  const isSpeaking = ref(false)
  const selectedTTSModel = ref<string>('tts-1')
  const selectedVoice = ref<string>('nova')
  const audioElement = ref<HTMLAudioElement | null>(null)
  const ttsError = ref<string | null>(null)

  // State - Generation Options
  const selectedStyle = ref<string>('adhs')
  const generateWithTTS = ref<boolean>(false)

  // State - Whiteboard
  const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)
  const isAnimatingWhiteboard = ref(false)

  // ============================================================================
  // Computed
  // ============================================================================

  const hasContent = computed(() => lessonSteps.value.length > 0)
  const steps = computed(() => lessonSteps.value)
  const currentStepData = computed(() => steps.value[currentStep.value])

  const hasWhiteboardActions = computed(() => {
    return lessonSteps.value.some(step => step.whiteboardActions && step.whiteboardActions.length > 0)
  })

  // ============================================================================
  // Methods - Explanation List
  // ============================================================================

  async function loadExplanationList() {
    isLoadingList.value = true
    try {
      const response = await http.get(`/lessons/${lessonId}/explanations`)
      if (response.data.success) {
        explanationList.value = response.data.data.explanations || []
        // Auto-select the first (most recent) if available
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

  async function selectExplanation(explanationId: string) {
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

  async function generateSteps() {
    isGenerating.value = true
    lessonSteps.value = []

    try {
      const response = await http.post('/admin/ai/generate-lesson-steps', {
        lesson_id: lessonId,
        lesson_title: options?.lessonTitle,
        lm_type: options?.lmType,
        chapter_title: options?.chapterTitle,
        style: selectedStyle.value,
        generate_tts: generateWithTTS.value,
        tts_voice: selectedVoice.value
      })

      if (response.data.success) {
        lessonSteps.value = response.data.data.steps || []
        currentStep.value = 0
        showNewForm.value = false

        // Set the new explanation as selected
        if (response.data.explanationId) {
          selectedExplanationId.value = response.data.explanationId
        }

        // Reload list to show new entry
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

  function startEditTitle(expl: ExplanationListItem) {
    editingExplanation.value = expl
    editTitle.value = expl.title
  }

  function cancelEdit() {
    editingExplanation.value = null
    editTitle.value = ''
  }

  async function saveTitle() {
    if (!editingExplanation.value || !editTitle.value.trim()) return

    try {
      const response = await http.patch(`/lesson-explanation/${editingExplanation.value.explanationId}`, {
        title: editTitle.value.trim()
      })
      if (response.data.success) {
        // Update in list
        const idx = explanationList.value.findIndex(e => e.explanationId === editingExplanation.value?.explanationId)
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

  function confirmDelete(expl: ExplanationListItem) {
    deleteConfirm.value = expl
  }

  async function executeDelete() {
    if (!deleteConfirm.value) return

    try {
      const response = await http.delete(`/lesson-explanation/${deleteConfirm.value.explanationId}`)
      if (response.data.success) {
        // Remove from list
        explanationList.value = explanationList.value.filter(e => e.explanationId !== deleteConfirm.value?.explanationId)

        // Clear selection if deleted
        if (selectedExplanationId.value === deleteConfirm.value.explanationId) {
          selectedExplanationId.value = null
          lessonSteps.value = []
          // Select next if available
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

  function cancelDelete() {
    deleteConfirm.value = null
  }

  // ============================================================================
  // Methods - Navigation
  // ============================================================================

  function nextStep() {
    if (currentStep.value < steps.value.length - 1) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 0) {
      stopSpeaking()
      currentStep.value--
    }
  }

  function restartTutorial() {
    currentStep.value = 0
    if (whiteboardRef.value) {
      whiteboardRef.value.clearBoard()
    }
  }

  // ============================================================================
  // Methods - TTS
  // ============================================================================

  function toggleTTS() {
    ttsEnabled.value = !ttsEnabled.value
    if (ttsEnabled.value && currentStepData.value) {
      speak(currentStepData.value.speech)
    } else {
      stopSpeaking()
    }
  }

  function stopSpeaking() {
    window.speechSynthesis?.cancel()
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value = null
    }
    isSpeaking.value = false
  }

  async function speak(text: string) {
    stopSpeaking()
    isSpeaking.value = true
    ttsError.value = null

    const model = selectedTTSModel.value

    if (model === 'browser') {
      speakWithBrowser(text)
      return
    }

    try {
      const response = await http.post('/tts/speak', {
        text,
        voice: selectedVoice.value,
        provider: 'openai',
        model: model,
        language: 'de'
      })

      if (response.data.success && response.data.data.audio_path) {
        const audio = new Audio()
        audioElement.value = audio

        const audioUrl = `/api/v1/tts/audio/${response.data.data.audio_url.split('/').pop()}?path=${encodeURIComponent(response.data.data.audio_path)}`
        audio.src = audioUrl

        audio.onended = () => {
          isSpeaking.value = false
          audioElement.value = null
        }
        audio.onerror = () => {
          isSpeaking.value = false
          audioElement.value = null
          ttsError.value = t('lesson.tutorPlayer.errors.audioPlayback')
        }

        await audio.play()
      } else {
        throw new Error(response.data.error?.message || 'TTS failed')
      }
    } catch (error: any) {
      console.error('TTS API error:', error)
      ttsError.value = `${t('lesson.tutorPlayer.errors.tts')}: ${error?.response?.data?.error?.message || error?.message || t('common.unknownError')}`
      speakWithBrowser(text)
    }
  }

  function speakWithBrowser(text: string) {
    if (!window.speechSynthesis) {
      isSpeaking.value = false
      return
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'de-DE'
    utterance.rate = 0.9

    utterance.onend = () => { isSpeaking.value = false }
    utterance.onerror = () => { isSpeaking.value = false }

    window.speechSynthesis.speak(utterance)
  }

  async function startExplanation() {
    // Stop any current speech first
    stopSpeaking()

    // Enable TTS - the watch on currentStep will handle speaking
    ttsEnabled.value = true

    // If already at step 0, manually trigger whiteboard + speech
    // (watch won't fire if value doesn't change)
    if (currentStep.value === 0) {
      const stepData = steps.value[0]
      if (stepData?.whiteboardActions?.length && whiteboardRef.value) {
        isAnimatingWhiteboard.value = true
        whiteboardRef.value.clearBoard()
        await new Promise(resolve => setTimeout(resolve, 100))
        await whiteboardRef.value.executeActions(stepData.whiteboardActions)
        isAnimatingWhiteboard.value = false
      }

      if (stepData?.speech) {
        speak(stepData.speech)
      }
    } else {
      // Setting to 0 will trigger the watch which handles TTS
      currentStep.value = 0
    }
  }

  // ============================================================================
  // Methods - Utilities
  // ============================================================================

  function formatDate(dateStr: string): string {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  // ============================================================================
  // Watchers
  // ============================================================================

  watch(currentStep, async (newStep, oldStep) => {
    const stepData = steps.value[newStep]
    if (!stepData) return

    if (oldStep !== undefined) {
      stopSpeaking()
    }

    // Execute whiteboard animations if available
    if (stepData.whiteboardActions?.length && whiteboardRef.value) {
      isAnimatingWhiteboard.value = true
      try {
        whiteboardRef.value.clearBoard()
        await new Promise(resolve => setTimeout(resolve, 100))
        await whiteboardRef.value.executeActions(stepData.whiteboardActions)
      } catch (err) {
        console.error('Whiteboard animation error:', err)
      } finally {
        isAnimatingWhiteboard.value = false
      }
    }

    // Speak if TTS enabled
    if (ttsEnabled.value && stepData.speech) {
      speak(stepData.speech)
    }
  })

  // ============================================================================
  // Lifecycle
  // ============================================================================

  onUnmounted(() => {
    stopSpeaking()
  })

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State - Steps & Navigation
    currentStep,
    lessonSteps,
    hasContent,
    steps,
    currentStepData,
    hasWhiteboardActions,

    // State - Explanation List
    explanationList,
    selectedExplanationId,
    isLoadingList,
    showNewForm,

    // State - Generation
    isGenerating,
    selectedStyle,
    selectedVoice,
    generateWithTTS,

    // State - Edit/Delete
    editingExplanation,
    editTitle,
    deleteConfirm,

    // State - TTS
    ttsEnabled,
    isSpeaking,
    selectedTTSModel,
    ttsError,

    // State - Whiteboard
    whiteboardRef,
    isAnimatingWhiteboard,

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

    // Methods - Navigation
    nextStep,
    prevStep,
    restartTutorial,

    // Methods - TTS
    toggleTTS,
    stopSpeaking,
    speak,
    startExplanation,

    // Methods - Utilities
    formatDate
  }
}
