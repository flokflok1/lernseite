/**
 * useTeachingTimeline - Composable for synchronized teaching sequences
 *
 * Coordinates:
 * - TTS Speech playback
 * - Whiteboard drawing animations
 * - Avatar animations and expressions
 * - User interaction pauses (calculator input)
 *
 * Usage:
 * const timeline = useTeachingTimeline()
 * await timeline.start(lessonSteps)
 * timeline.next() // Move to next step
 * timeline.pause() // Pause current step
 */

import { ref, computed, readonly } from 'vue'
import { ttsApi } from '@/application/services/api/panel-user'

import type {
  WhiteboardAction,
  TeacherAnimation,
  CalculatorChallenge,
  TeachingStep,
  TimelineState,
  TimelineCallbacks
} from './teachingTimeline.types'

// Re-export types for backward compatibility
export type {
  WhiteboardAction,
  TeacherAnimation,
  CalculatorChallenge,
  TeachingStep,
  TimelineState,
  TimelineCallbacks
}

// Re-export lesson generator for backward compatibility
export { generateBezugskalkulationLesson } from './generateBezugskalkulationLesson'

// ============================================================================
// Composable
// ============================================================================

export function useTeachingTimeline() {
  // State
  const steps = ref<TeachingStep[]>([])
  const currentStepIndex = ref(-1)
  const isPlaying = ref(false)
  const isPaused = ref(false)
  const isSpeaking = ref(false)
  const isWaitingForUser = ref(false)

  // Audio
  let currentAudio: HTMLAudioElement | null = null
  let speechPromiseResolve: (() => void) | null = null

  // Callbacks
  let callbacks: TimelineCallbacks = {}

  // ============================================================================
  // Computed
  // ============================================================================

  const currentStep = computed(() => {
    if (currentStepIndex.value >= 0 && currentStepIndex.value < steps.value.length) {
      return steps.value[currentStepIndex.value]
    }
    return null
  })

  const progress = computed(() => {
    if (steps.value.length === 0) return 0
    return ((currentStepIndex.value + 1) / steps.value.length) * 100
  })

  const hasNext = computed(() => currentStepIndex.value < steps.value.length - 1)
  const hasPrevious = computed(() => currentStepIndex.value > 0)
  const isComplete = computed(() => currentStepIndex.value >= steps.value.length - 1 && !isPlaying.value)

  const state = computed<TimelineState>(() => ({
    currentStepIndex: currentStepIndex.value,
    isPlaying: isPlaying.value,
    isPaused: isPaused.value,
    isSpeaking: isSpeaking.value,
    isWaitingForUser: isWaitingForUser.value,
    totalSteps: steps.value.length
  }))

  // ============================================================================
  // Core Methods
  // ============================================================================

  async function start(teachingSteps: TeachingStep[], options?: TimelineCallbacks): Promise<void> {
    steps.value = teachingSteps
    callbacks = options || {}
    currentStepIndex.value = -1
    isPlaying.value = true
    isPaused.value = false

    await next()
  }

  async function next(): Promise<void> {
    if (currentStepIndex.value >= steps.value.length - 1) {
      isPlaying.value = false
      callbacks.onTimelineComplete?.()
      return
    }

    currentStepIndex.value++
    await executeStep(steps.value[currentStepIndex.value])
  }

  async function previous(): Promise<void> {
    if (currentStepIndex.value <= 0) return

    stopCurrentStep()
    currentStepIndex.value--
    await executeStep(steps.value[currentStepIndex.value])
  }

  async function goToStep(index: number): Promise<void> {
    if (index < 0 || index >= steps.value.length) return

    stopCurrentStep()
    currentStepIndex.value = index
    await executeStep(steps.value[index])
  }

  function pause(): void {
    isPaused.value = true
    if (currentAudio) {
      currentAudio.pause()
    }
    isSpeaking.value = false
  }

  function resume(): void {
    isPaused.value = false
    if (currentAudio) {
      currentAudio.play()
      isSpeaking.value = true
    }
  }

  function stop(): void {
    stopCurrentStep()
    isPlaying.value = false
    isPaused.value = false
    currentStepIndex.value = -1
  }

  // ============================================================================
  // Step Execution
  // ============================================================================

  async function executeStep(step: TeachingStep): Promise<void> {
    if (!step) return

    try {
      // Start speaking animation immediately for visual feedback
      isSpeaking.value = true
      callbacks.onSpeechStart?.()

      // Set animation (talking animation)
      callbacks.onAnimationChange?.(step.animation)

      // Execute whiteboard actions and speech in parallel
      const whiteboardPromise = executeWhiteboardActions(step.whiteboard)
      const speechPromise = executeSpeech(step.speech)

      await Promise.all([whiteboardPromise, speechPromise])

      // Handle calculator challenge if present
      if (step.calculatorChallenge) {
        isWaitingForUser.value = true
        callbacks.onCalculatorChallenge?.(step.calculatorChallenge)
        return
      }

      // Handle waitForUser
      if (step.waitForUser) {
        isWaitingForUser.value = true
        return
      }

      // Step complete
      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)

      // Auto-advance if not at end
      if (hasNext.value && isPlaying.value && !isPaused.value) {
        await delay(500)
        await next()
      } else if (!hasNext.value) {
        isPlaying.value = false
        callbacks.onTimelineComplete?.()
      }
    } catch (error) {
      console.error('Error executing step:', error)
      callbacks.onError?.(error as Error)
    }
  }

  async function executeWhiteboardActions(actions: WhiteboardAction[]): Promise<void> {
    for (const action of actions) {
      if (isPaused.value) {
        await waitUntilResumed()
      }

      if (callbacks.onWhiteboardAction) {
        await callbacks.onWhiteboardAction(action)
      } else {
        await delay(action.duration)
      }
    }
  }

  async function executeSpeech(text: string): Promise<void> {
    if (!text) return

    try {
      // Text preprocessing for pronunciation is done on the backend.
      // The backend loads pronunciation rules from tts_pronunciations table
      // and uses AI to generate pronunciations for unknown words.

      const ttsPromise = ttsApi.speak({
        text: text,
        voice: 'thorsten',
        speed: 0.9,
        language: 'de'
      })

      const response = await ttsPromise

      if (response.success && response.data?.audio_url) {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
        const baseUrl = apiBaseUrl.replace(/\/api\/v1$/, '')
        const audioUrl = `${baseUrl}${response.data.audio_url}`

        await playAudio(audioUrl)
      } else {
        const estimatedDuration = text.length * 50
        await delay(estimatedDuration)
      }
    } catch (error) {
      console.warn('TTS error, using fallback timing:', error)
      await delay(text.length * 50)
    } finally {
      isSpeaking.value = false
      callbacks.onSpeechEnd?.()
    }
  }

  function playAudio(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      currentAudio = new Audio(url)
      speechPromiseResolve = resolve

      currentAudio.onended = () => {
        currentAudio = null
        speechPromiseResolve = null
        resolve()
      }

      currentAudio.onerror = (error) => {
        currentAudio = null
        speechPromiseResolve = null
        reject(error)
      }

      currentAudio.play().catch(reject)
    })
  }

  // ============================================================================
  // User Interaction
  // ============================================================================

  function submitCalculatorResult(result: number, isCorrect: boolean): void {
    if (!isWaitingForUser.value) return

    isWaitingForUser.value = false

    const step = currentStep.value
    if (step) {
      if (isCorrect) {
        callbacks.onAnimationChange?.({ type: 'celebrating', expression: 'happy' })
      } else {
        callbacks.onAnimationChange?.({ type: 'thinking', expression: 'thinking' })
      }

      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)
    }

    setTimeout(() => {
      if (hasNext.value && isPlaying.value) {
        next()
      } else {
        isPlaying.value = false
        callbacks.onTimelineComplete?.()
      }
    }, isCorrect ? 1500 : 2500)
  }

  function continueAfterWait(): void {
    if (!isWaitingForUser.value) return

    isWaitingForUser.value = false

    const step = currentStep.value
    if (step) {
      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)
    }

    if (hasNext.value && isPlaying.value) {
      next()
    } else {
      isPlaying.value = false
      callbacks.onTimelineComplete?.()
    }
  }

  function skipCurrentStep(): void {
    stopCurrentStep()

    const step = currentStep.value
    if (step) {
      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)
    }

    isWaitingForUser.value = false

    if (hasNext.value) {
      next()
    } else {
      isPlaying.value = false
      callbacks.onTimelineComplete?.()
    }
  }

  // ============================================================================
  // Utility
  // ============================================================================

  function stopCurrentStep(): void {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }

    if (speechPromiseResolve) {
      speechPromiseResolve()
      speechPromiseResolve = null
    }

    isSpeaking.value = false
    isWaitingForUser.value = false
  }

  function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async function waitUntilResumed(): Promise<void> {
    while (isPaused.value) {
      await delay(100)
    }
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State (readonly)
    state: readonly(state),
    currentStep: readonly(currentStep),
    currentStepIndex: readonly(currentStepIndex),
    progress: readonly(progress),
    isPlaying: readonly(isPlaying),
    isPaused: readonly(isPaused),
    isSpeaking: readonly(isSpeaking),
    isWaitingForUser: readonly(isWaitingForUser),
    hasNext: readonly(hasNext),
    hasPrevious: readonly(hasPrevious),
    isComplete: readonly(isComplete),

    // Control methods
    start,
    next,
    previous,
    goToStep,
    pause,
    resume,
    stop,
    skipCurrentStep,

    // User interaction
    submitCalculatorResult,
    continueAfterWait
  }
}
