/**
 * useOralExamination Composable
 * =============================
 * Manages the oral examination flow including question generation,
 * audio recording handling, text answers, TTS playback, and feedback.
 */
import { ref, computed } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'

// =============================================================================
// Types
// =============================================================================

export type ExamPhase = 'intro' | 'question' | 'answer' | 'feedback' | 'complete'

export interface ExaminerMessage {
  role: 'examiner' | 'user'
  content: string
  timestamp: Date
  audioUrl?: string
}

export interface FeedbackResult {
  score: number
  feedback: string
  covered_points: string[]
  missing_points: string[]
  suggestions: string[]
}

export interface OralMethodData {
  topic: string
  format: string
  examiner_persona: string
  difficulty: string
  topic_blocks?: Array<{
    topic: string
    key_points: string
  }>
  duration_minutes: number
  allow_thinking_time: boolean
  allow_retry: boolean
  use_audio: boolean
  show_transcript: boolean
  criteria: {
    content: boolean
    structure: boolean
    clarity: boolean
    reactions: boolean
  }
}

export interface UseOralExaminationReturn {
  phase: Ref<ExamPhase>
  currentBlockIndex: Ref<number>
  isLoading: Ref<boolean>
  isPlayingAudio: Ref<boolean>
  error: Ref<string | null>
  examinerMessages: Ref<ExaminerMessage[]>
  currentQuestion: Ref<string>
  userAnswer: Ref<string>
  transcription: Ref<string>
  feedbackResult: Ref<FeedbackResult | null>
  totalBlocks: ComputedRef<number>
  progressPercent: ComputedRef<number>
  examinerPersonaLabel: ComputedRef<string>
  startExam: () => Promise<void>
  handleRecording: (blob: Blob, duration: number) => Promise<void>
  handleTextAnswer: () => Promise<void>
  nextBlock: () => void
  completeExam: () => Promise<void>
  playAudio: (url: string) => void
  retryAnswer: () => void
}

// =============================================================================
// Composable
// =============================================================================

export function useOralExamination(
  methodData: ComputedRef<OralMethodData>,
  onCompleted: () => void
): UseOralExaminationReturn {
  const { t } = useI18n()

  // ===========================================================================
  // State
  // ===========================================================================

  const phase = ref<ExamPhase>('intro')
  const currentBlockIndex = ref(0)
  const isLoading = ref(false)
  const isPlayingAudio = ref(false)
  const error = ref<string | null>(null)

  const examinerMessages = ref<ExaminerMessage[]>([])
  const currentQuestion = ref('')
  const userAnswer = ref('')
  const transcription = ref('')
  const feedbackResult = ref<FeedbackResult | null>(null)

  // ===========================================================================
  // Computed
  // ===========================================================================

  const currentBlock = computed(() => {
    return methodData.value.topic_blocks?.[currentBlockIndex.value]
  })

  const totalBlocks = computed((): number => {
    return methodData.value.topic_blocks?.length || 1
  })

  const progressPercent = computed((): number => {
    return ((currentBlockIndex.value + 1) / totalBlocks.value) * 100
  })

  const examinerPersonaLabel = computed((): string => {
    const persona = methodData.value.examiner_persona
    return t(`lesson.oral.personas.${persona}`)
  })

  // ===========================================================================
  // TTS Helper
  // ===========================================================================

  function speakText(text: string): void {
    if (!methodData.value.use_audio) return

    try {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'de-DE'
      utterance.rate = 0.95
      window.speechSynthesis.speak(utterance)

      const lastMessage = examinerMessages.value[examinerMessages.value.length - 1]
      if (lastMessage) {
        lastMessage.audioUrl = 'web-speech-api://stub'
      }
    } catch (e) {
      console.warn('TTS failed:', e)
    }
  }

  function addMessage(role: 'examiner' | 'user', content: string): void {
    examinerMessages.value.push({
      role,
      content,
      timestamp: new Date()
    })
  }

  // ===========================================================================
  // Exam Flow
  // ===========================================================================

  async function startExam(): Promise<void> {
    phase.value = 'question'
    isLoading.value = true
    error.value = null

    try {
      const questionTopic = currentBlock.value?.topic || methodData.value.topic

      // TODO: Implement tutorChat API call - stub response for now
      const response = {
        message: t('lesson.oral.stubQuestion', { topic: questionTopic })
          || `Please explain the concept of ${questionTopic}. Take your time and provide a comprehensive explanation.`
      }

      currentQuestion.value = response.message
      addMessage('examiner', response.message)
      speakText(response.message)
    } catch (e: any) {
      error.value = e.message || t('lesson.oral.errors.startFailed')
    } finally {
      isLoading.value = false
    }
  }

  async function handleRecording(_blob: Blob, _duration: number): Promise<void> {
    phase.value = 'answer'
    isLoading.value = true
    error.value = null

    try {
      const expectedPoints = currentBlock.value?.key_points
        ? currentBlock.value.key_points.split('\n').filter((p: string) => p.trim())
        : []

      // TODO: Implement analyzeOralExplanation API call - stub response for now
      const result = {
        transcription: `[Stub transcription: User provided an oral explanation on topic]`,
        analysis: {
          score: 75,
          feedback: t('lesson.oral.stubAnalysisFeedback') || 'Your explanation covers the main points well.',
          covered_points: expectedPoints.slice(0, Math.min(2, expectedPoints.length)),
          missing_points: expectedPoints.slice(2),
          suggestions: [
            'Try to provide more specific examples',
            'Use clearer transitions between ideas'
          ]
        }
      }

      transcription.value = result.transcription
      userAnswer.value = result.transcription
      addMessage('user', result.transcription)

      // TODO: Implement tutorChat API call - stub response for now
      const examinerResponse = {
        message: t('lesson.oral.stubAnalysis')
          || `Good attempt! You covered ${result.analysis.covered_points.length} key points. Continue with the next part of the explanation.`
      }

      currentQuestion.value = examinerResponse.message
      addMessage('examiner', examinerResponse.message)
      speakText(examinerResponse.message)

      feedbackResult.value = result.analysis
      phase.value = 'feedback'
    } catch (e: any) {
      error.value = e.message || t('lesson.oral.errors.analysisFailed')
      phase.value = 'question'
    } finally {
      isLoading.value = false
    }
  }

  async function handleTextAnswer(): Promise<void> {
    if (!userAnswer.value.trim()) return

    phase.value = 'answer'
    isLoading.value = true
    error.value = null

    try {
      addMessage('user', userAnswer.value)

      // TODO: Implement tutorChat API call - stub response for now
      const examinerResponse = {
        message: t('lesson.oral.stubEvaluation')
          || 'Thank you for your answer. Let me ask you a follow-up question...'
      }

      currentQuestion.value = examinerResponse.message
      addMessage('examiner', examinerResponse.message)
      speakText(examinerResponse.message)

      userAnswer.value = ''
      phase.value = 'question'
    } catch (e: any) {
      error.value = e.message || t('lesson.oral.errors.processingFailed')
      phase.value = 'question'
    } finally {
      isLoading.value = false
    }
  }

  function nextBlock(): void {
    if (currentBlockIndex.value < totalBlocks.value - 1) {
      currentBlockIndex.value++
      feedbackResult.value = null
      phase.value = 'question'
      startExam()
    } else {
      completeExam()
    }
  }

  async function completeExam(): Promise<void> {
    phase.value = 'complete'
    isLoading.value = true

    try {
      // TODO: Implement tutorChat API call - stub response for now
      const summaryResponse = {
        message: t('lesson.oral.stubSummary')
          || 'Excellent oral examination! You have demonstrated good understanding of the topic. Well done!'
      }

      addMessage('examiner', summaryResponse.message)
      speakText(summaryResponse.message)
    } catch (e) {
      console.error('Failed to generate summary:', e)
    } finally {
      isLoading.value = false
    }

    onCompleted()
  }

  function playAudio(url: string): void {
    if (isPlayingAudio.value) return

    const audio = new Audio(url)
    isPlayingAudio.value = true

    audio.onended = () => {
      isPlayingAudio.value = false
    }
    audio.onerror = () => {
      isPlayingAudio.value = false
    }

    audio.play()
  }

  function retryAnswer(): void {
    feedbackResult.value = null
    phase.value = 'question'
  }

  // ===========================================================================
  // Return
  // ===========================================================================

  return {
    phase,
    currentBlockIndex,
    isLoading,
    isPlayingAudio,
    error,
    examinerMessages,
    currentQuestion,
    userAnswer,
    transcription,
    feedbackResult,
    totalBlocks,
    progressPercent,
    examinerPersonaLabel,
    startExam,
    handleRecording,
    handleTextAnswer,
    nextBlock,
    completeExam,
    playAudio,
    retryAnswer
  }
}
