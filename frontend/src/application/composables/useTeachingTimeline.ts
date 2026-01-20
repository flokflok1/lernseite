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
import { ttsApi } from '@/infrastructure/api/tts.api'

// ============================================================================
// Types
// ============================================================================

export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear'
  content?: string
  position: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration: number
  color?: string
  fontSize?: number
  fontWeight?: 'normal' | 'bold'
  lineWidth?: number
}

export interface TeacherAnimation {
  type: 'idle' | 'talking' | 'pointing' | 'thinking' | 'celebrating' | 'explaining'
  pointAt?: { x: number; y: number }
  expression?: 'happy' | 'neutral' | 'thinking' | 'surprised'
}

export interface CalculatorChallenge {
  prompt: string
  expectedResult: number
  tolerance?: number
  hint?: string
  showFormula?: boolean
}

export interface TeachingStep {
  id: string
  speech: string
  whiteboard: WhiteboardAction[]
  animation: TeacherAnimation
  calculatorChallenge?: CalculatorChallenge
  waitForUser?: boolean
  onComplete?: () => void
}

export interface TimelineState {
  currentStepIndex: number
  isPlaying: boolean
  isPaused: boolean
  isSpeaking: boolean
  isWaitingForUser: boolean
  totalSteps: number
}

export interface TimelineCallbacks {
  onSpeechStart?: () => void
  onSpeechEnd?: () => void
  onWhiteboardAction?: (action: WhiteboardAction) => Promise<void>
  onAnimationChange?: (animation: TeacherAnimation) => void
  onCalculatorChallenge?: (challenge: CalculatorChallenge) => void
  onStepComplete?: (step: TeachingStep, index: number) => void
  onTimelineComplete?: () => void
  onError?: (error: Error) => void
}

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

  async function start(teachingSteps: TeachingStep[], options?: TimelineCallbacks) {
    steps.value = teachingSteps
    callbacks = options || {}
    currentStepIndex.value = -1
    isPlaying.value = true
    isPaused.value = false

    await next()
  }

  async function next() {
    if (currentStepIndex.value >= steps.value.length - 1) {
      // Timeline complete
      isPlaying.value = false
      callbacks.onTimelineComplete?.()
      return
    }

    currentStepIndex.value++
    await executeStep(steps.value[currentStepIndex.value])
  }

  async function previous() {
    if (currentStepIndex.value <= 0) return

    stopCurrentStep()
    currentStepIndex.value--
    await executeStep(steps.value[currentStepIndex.value])
  }

  async function goToStep(index: number) {
    if (index < 0 || index >= steps.value.length) return

    stopCurrentStep()
    currentStepIndex.value = index
    await executeStep(steps.value[index])
  }

  function pause() {
    isPaused.value = true
    // Pause audio AND stop speaking animation
    if (currentAudio) {
      currentAudio.pause()
    }
    // Important: Stop speaking state so avatar mouth stops
    isSpeaking.value = false
  }

  function resume() {
    isPaused.value = false
    if (currentAudio) {
      currentAudio.play()
      // Resume speaking animation when audio resumes
      isSpeaking.value = true
    }
  }

  function stop() {
    stopCurrentStep()
    isPlaying.value = false
    isPaused.value = false
    currentStepIndex.value = -1
  }

  // ============================================================================
  // Step Execution
  // ============================================================================

  async function executeStep(step: TeachingStep) {
    if (!step) return

    try {
      // 1. Start speaking animation IMMEDIATELY when text appears
      //    This makes the avatar's mouth move right away while TTS loads
      isSpeaking.value = true
      callbacks.onSpeechStart?.()

      // 2. Set animation (talking animation)
      callbacks.onAnimationChange?.(step.animation)

      // 3. Execute whiteboard actions and speech in parallel
      const whiteboardPromise = executeWhiteboardActions(step.whiteboard)
      const speechPromise = executeSpeech(step.speech)

      await Promise.all([whiteboardPromise, speechPromise])

      // 3. Handle calculator challenge if present
      if (step.calculatorChallenge) {
        isWaitingForUser.value = true
        callbacks.onCalculatorChallenge?.(step.calculatorChallenge)
        // Timeline pauses here - user must call submitCalculatorResult()
        return
      }

      // 4. Handle waitForUser
      if (step.waitForUser) {
        isWaitingForUser.value = true
        // Timeline pauses here - user must call continueAfterWait()
        return
      }

      // 5. Step complete
      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)

      // 6. Auto-advance if not at end
      if (hasNext.value && isPlaying.value && !isPaused.value) {
        // Small delay between steps
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

  async function executeWhiteboardActions(actions: WhiteboardAction[]) {
    for (const action of actions) {
      if (isPaused.value) {
        // Wait until resumed
        await waitUntilResumed()
      }

      if (callbacks.onWhiteboardAction) {
        await callbacks.onWhiteboardAction(action)
      } else {
        // Default: just wait for duration
        await delay(action.duration)
      }
    }
  }

  async function executeSpeech(text: string): Promise<void> {
    if (!text) return

    // Note: isSpeaking is already set to true in executeStep() for immediate visual feedback

    try {
      // Text preprocessing for pronunciation is now done on the backend!
      // The backend loads pronunciation rules from the database (tts_pronunciations table)
      // and uses AI to generate pronunciations for unknown words.

      // Generate TTS audio - start immediately, don't wait
      const ttsPromise = ttsApi.speak({
        text: text,  // Backend handles preprocessing
        voice: 'thorsten',
        speed: 0.9,  // Slightly slower for clearer pronunciation
        language: 'de'  // Tell backend to use German pronunciation rules
      })

      // Wait for TTS response
      const response = await ttsPromise

      if (response.success && response.data?.audio_url) {
        // Play audio immediately
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
        const baseUrl = apiBaseUrl.replace(/\/api\/v1$/, '')
        const audioUrl = `${baseUrl}${response.data.audio_url}`

        await playAudio(audioUrl)
      } else {
        // Fallback: estimate duration based on text length
        const estimatedDuration = text.length * 50 // ~50ms per character
        await delay(estimatedDuration)
      }
    } catch (error) {
      console.warn('TTS error, using fallback timing:', error)
      // Fallback timing
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

  // NOTE: Text preprocessing for pronunciation is now done on the backend!
  // The backend loads pronunciation rules from the database (tts_pronunciations table)
  // and uses AI to generate pronunciations for unknown words.
  // See: /api/v1/tts/speak endpoint and TTSService.preprocess_text()

  // ============================================================================
  // User Interaction
  // ============================================================================

  function submitCalculatorResult(result: number, isCorrect: boolean) {
    if (!isWaitingForUser.value) return

    isWaitingForUser.value = false

    const step = currentStep.value
    if (step) {
      // Update animation based on result
      if (isCorrect) {
        callbacks.onAnimationChange?.({
          type: 'celebrating',
          expression: 'happy'
        })
      } else {
        callbacks.onAnimationChange?.({
          type: 'thinking',
          expression: 'thinking'
        })
      }

      step.onComplete?.()
      callbacks.onStepComplete?.(step, currentStepIndex.value)
    }

    // Continue to next step after brief delay
    setTimeout(() => {
      if (hasNext.value && isPlaying.value) {
        next()
      } else {
        isPlaying.value = false
        callbacks.onTimelineComplete?.()
      }
    }, isCorrect ? 1500 : 2500)
  }

  function continueAfterWait() {
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

  function skipCurrentStep() {
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

  function stopCurrentStep() {
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

  async function waitUntilResumed() {
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

// ============================================================================
// Lesson Content Generator
// ============================================================================

export function generateBezugskalkulationLesson(task: {
  question: string
  values: {
    quantity: number
    unitPrice: number
    supplierDiscount: number
    cashDiscount: number
    shippingCost: number
  }
  result: number
}): TeachingStep[] {
  const { quantity, unitPrice, supplierDiscount, cashDiscount, shippingCost } = task.values

  // Calculate intermediate values
  const lep = quantity * unitPrice
  const rabattBetrag = lep * (supplierDiscount / 100)
  const zep = lep - rabattBetrag
  const skontoBetrag = zep * (cashDiscount / 100)
  const bep = zep - skontoBetrag
  const einstandspreis = bep + shippingCost

  const formatCurrency = (n: number) => n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'

  return [
    {
      id: 'intro',
      speech: `Okay, lass uns zusammen eine Bezugskalkulation durchrechnen! ${task.question}`,
      whiteboard: [
        { type: 'write', content: 'Bezugskalkulation', position: { x: 280, y: 30 }, fontSize: 28, fontWeight: 'bold', duration: 1200, color: '#1e40af' }
      ],
      animation: { type: 'explaining', expression: 'happy' }
    },
    {
      id: 'step1-lep',
      speech: `Wir starten mit dem Listeneinkaufspreis. Das ist der Preis, den der Lieferant im Katalog angibt. Wir rechnen: ${quantity} Stück mal ${formatCurrency(unitPrice)}.`,
      whiteboard: [
        { type: 'write', content: '1  Listeneinkaufspreis (LEP)', position: { x: 30, y: 80 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${quantity} × ${formatCurrency(unitPrice)}`, position: { x: 400, y: 80 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.2 } }
    },
    {
      id: 'step1-calc',
      speech: `Jetzt bist du dran! Tippe die Rechnung in den Taschenrechner ein.`,
      whiteboard: [
        { type: 'highlight', content: `${quantity} × ${unitPrice} = ?`, position: { x: 400, y: 110 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${quantity} × ${unitPrice.toFixed(2)}`,
        expectedResult: lep,
        tolerance: 0.01,
        hint: 'Stückzahl mal Stückpreis ergibt den Listeneinkaufspreis'
      }
    },
    {
      id: 'step1-result',
      speech: `Perfekt! ${formatCurrency(lep)} ist richtig. Das ist unser Listeneinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(lep)}`, position: { x: 550, y: 80 }, fontSize: 20, duration: 600, color: '#10b981' }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    },
    {
      id: 'step2-rabatt',
      speech: `Jetzt ziehen wir den Lieferantenrabatt von ${supplierDiscount}% ab. Rabatte sind Preisnachlässe, die wir vom Lieferanten bekommen.`,
      whiteboard: [
        { type: 'write', content: `2  − Lieferantenrabatt (${supplierDiscount}%)`, position: { x: 30, y: 130 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(lep)} × ${supplierDiscount}%`, position: { x: 400, y: 130 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.35 } }
    },
    {
      id: 'step2-calc',
      speech: `Berechne den Rabattbetrag: ${formatCurrency(lep)} mal ${supplierDiscount} Prozent.`,
      whiteboard: [
        { type: 'highlight', content: `${lep.toFixed(2)} × 0,${supplierDiscount.toString().padStart(2, '0')} = ?`, position: { x: 400, y: 160 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${lep.toFixed(2)} × ${supplierDiscount / 100}`,
        expectedResult: rabattBetrag,
        tolerance: 0.01,
        hint: `Tipp: ${supplierDiscount}% = ${supplierDiscount / 100}`
      }
    },
    {
      id: 'step2-result',
      speech: `Richtig! ${formatCurrency(rabattBetrag)} Rabatt.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(rabattBetrag)}`, position: { x: 550, y: 130 }, fontSize: 20, duration: 600, color: '#ef4444' }
      ],
      animation: { type: 'talking', expression: 'happy' }
    },
    {
      id: 'step3-zep',
      speech: `Nach Abzug des Rabatts erhalten wir den Zieleinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: '3  = Zieleinkaufspreis (ZEP)', position: { x: 30, y: 180 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(lep)} − ${formatCurrency(rabattBetrag)}`, position: { x: 400, y: 180 }, fontSize: 18, duration: 800 },
        { type: 'write', content: `= ${formatCurrency(zep)}`, position: { x: 550, y: 180 }, fontSize: 20, duration: 600, color: '#3b82f6' }
      ],
      animation: { type: 'explaining' }
    },
    {
      id: 'step4-skonto',
      speech: `Jetzt kommt das Skonto von ${cashDiscount}%. Skonto ist ein Preisnachlass für schnelle Zahlung.`,
      whiteboard: [
        { type: 'write', content: `4  − Lieferantenskonto (${cashDiscount}%)`, position: { x: 30, y: 230 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(zep)} × ${cashDiscount}%`, position: { x: 400, y: 230 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.5 } }
    },
    {
      id: 'step4-calc',
      speech: `Berechne das Skonto.`,
      whiteboard: [
        { type: 'highlight', content: `${zep.toFixed(2)} × 0,0${cashDiscount} = ?`, position: { x: 400, y: 260 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${zep.toFixed(2)} × ${cashDiscount / 100}`,
        expectedResult: skontoBetrag,
        tolerance: 0.01
      }
    },
    {
      id: 'step4-result',
      speech: `Super! ${formatCurrency(skontoBetrag)} Skonto.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(skontoBetrag)}`, position: { x: 550, y: 230 }, fontSize: 20, duration: 600, color: '#ef4444' }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    },
    {
      id: 'step5-bep',
      speech: `Nach Abzug des Skontos haben wir den Bareinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: '5  = Bareinkaufspreis (BEP)', position: { x: 30, y: 280 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(zep)} − ${formatCurrency(skontoBetrag)}`, position: { x: 400, y: 280 }, fontSize: 18, duration: 800 },
        { type: 'write', content: `= ${formatCurrency(bep)}`, position: { x: 550, y: 280 }, fontSize: 20, duration: 600, color: '#3b82f6' }
      ],
      animation: { type: 'explaining' }
    },
    {
      id: 'step6-bezugskosten',
      speech: `Jetzt addieren wir die Bezugskosten von ${formatCurrency(shippingCost)}. Das sind zum Beispiel Versand oder Verpackung.`,
      whiteboard: [
        { type: 'write', content: '6  + Bezugskosten', position: { x: 30, y: 330 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `+ ${formatCurrency(shippingCost)}`, position: { x: 550, y: 330 }, fontSize: 20, duration: 600, color: '#10b981' }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.7, y: 0.7 } }
    },
    {
      id: 'final',
      speech: `Und jetzt das Ergebnis! Der Einstandspreis beträgt ${formatCurrency(einstandspreis)}. Das ist der Preis, den wir wirklich für die Ware bezahlen. Super gemacht!`,
      whiteboard: [
        { type: 'underline', content: '', position: { x: 30, y: 370 }, endPosition: { x: 650, y: 370 }, duration: 500, lineWidth: 2 },
        { type: 'write', content: '= Einstandspreis', position: { x: 30, y: 380 }, fontSize: 22, fontWeight: 'bold', duration: 1000, color: '#1e40af' },
        { type: 'write', content: `${formatCurrency(einstandspreis)}`, position: { x: 520, y: 380 }, fontSize: 24, fontWeight: 'bold', duration: 800, color: '#10b981' },
        { type: 'box', position: { x: 500, y: 368 }, endPosition: { x: 670, y: 415 }, duration: 600, color: '#10b981', lineWidth: 3 }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    }
  ]
}
