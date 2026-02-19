/**
 * useTheoryExplanation - Composable for theory whiteboard + audio playback
 *
 * Manages the interactive explanation flow: clearing the whiteboard,
 * executing whiteboard actions, and playing TTS audio in sync.
 */
import { ref, computed, watch, type Ref, type ComputedRef } from 'vue'

interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position?: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration?: number
  color?: string
  fontSize?: number
  schema?: Array<{ name: string; operator: string; value: string; highlight?: boolean }>
}

interface WhiteboardRef {
  clearBoard: () => void
  executeActions: (actions: WhiteboardAction[]) => Promise<void>
}

interface TheoryData {
  hasTheory?: boolean
  theory?: Record<string, unknown>
  audioUrl?: string
}

interface UseTheoryExplanationOptions {
  theory: Ref<TheoryData | undefined>
  chapterId: Ref<string>
}

interface UseTheoryExplanationReturn {
  whiteboardRef: Ref<WhiteboardRef | null>
  isAnimating: Ref<boolean>
  isPlaying: Ref<boolean>
  selectedVoice: Ref<string>
  hasTheory: ComputedRef<boolean>
  theoryContent: ComputedRef<Record<string, unknown>>
  whiteboardActions: ComputedRef<WhiteboardAction[]>
  audioUrl: ComputedRef<string | undefined>
  startExplanation: () => Promise<void>
  stopExplanation: () => void
  onActionComplete: (action: WhiteboardAction) => void
}

export function useTheoryExplanation(
  options: UseTheoryExplanationOptions
): UseTheoryExplanationReturn {
  const whiteboardRef = ref<WhiteboardRef | null>(null)
  const isAnimating = ref(false)
  const isPlaying = ref(false)
  const selectedVoice = ref('nova')

  let audioElement: HTMLAudioElement | null = null

  const hasTheory = computed((): boolean => {
    return !!(options.theory.value?.hasTheory && options.theory.value?.theory)
  })

  const theoryContent = computed((): Record<string, unknown> => {
    return (options.theory.value?.theory as Record<string, unknown>) || {}
  })

  const whiteboardActions = computed((): WhiteboardAction[] => {
    return (theoryContent.value.whiteboardActions as WhiteboardAction[]) || []
  })

  const audioUrl = computed((): string | undefined => {
    return options.theory.value?.audioUrl
  })

  function onActionComplete(action: WhiteboardAction): void {
    console.log('Action complete:', action.type)
  }

  function playAudioFile(url: string): void {
    if (audioElement) {
      audioElement.pause()
      audioElement = null
    }

    audioElement = new Audio(url)
    audioElement.onended = () => {
      isPlaying.value = false
    }
    audioElement.onerror = (e) => {
      console.error('Audio playback error:', e)
      isPlaying.value = false
    }
    audioElement.play().catch(err => {
      console.error('Failed to play audio:', err)
    })
  }

  async function startExplanation(): Promise<void> {
    if (!whiteboardRef.value) return

    isPlaying.value = true
    isAnimating.value = true

    whiteboardRef.value.clearBoard()

    if (audioUrl.value) {
      playAudioFile(audioUrl.value)
    }

    if (whiteboardActions.value.length > 0) {
      await whiteboardRef.value.executeActions(whiteboardActions.value)
    }

    isAnimating.value = false
  }

  function stopExplanation(): void {
    isPlaying.value = false
    isAnimating.value = false

    if (audioElement) {
      audioElement.pause()
      audioElement.currentTime = 0
    }
  }

  // Stop explanation when chapter changes
  watch(options.chapterId, () => {
    stopExplanation()
  })

  return {
    whiteboardRef,
    isAnimating,
    isPlaying,
    selectedVoice,
    hasTheory,
    theoryContent,
    whiteboardActions,
    audioUrl,
    startExplanation,
    stopExplanation,
    onActionComplete
  }
}

export type { WhiteboardAction }
