/**
 * Type definitions for the teaching timeline system.
 *
 * Shared across useTeachingTimeline composable and lesson generators.
 */

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
