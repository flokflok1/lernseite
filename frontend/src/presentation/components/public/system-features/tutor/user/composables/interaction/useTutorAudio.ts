/**
 * useTutorAudio - Composable for TTS audio playback in TutorAvatar
 *
 * Handles Edge TTS generation, browser TTS fallback, audio playback
 * controls, progress tracking, and typewriter text effect.
 */
import { ref, watch, onUnmounted, type Ref } from 'vue'
import { ttsApi, DEFAULT_TUTOR_VOICE } from '@/infrastructure/api/clients/panel/user'

interface TutorAudioOptions {
  text: Ref<string>
  autoPlay: Ref<boolean>
  voice: Ref<string>
  speed: Ref<number>
  typewriter: Ref<boolean>
  typewriterSpeed: Ref<number>
}

interface TutorAudioEmits {
  onSpeechStart: () => void
  onSpeechEnd: () => void
  onSpeechError: (error: Error) => void
  onSkip: () => void
}

interface TutorAudioReturn {
  isSpeaking: Ref<boolean>
  isThinking: Ref<boolean>
  audioReady: Ref<boolean>
  audioProgress: Ref<number>
  audioDuration: Ref<number>
  displayText: Ref<string>
  generateAndPlayAudio: () => Promise<void>
  playAudio: () => void
  pauseAudio: () => void
  skipToEnd: () => void
  cleanup: () => void
}

export function useTutorAudio(
  options: TutorAudioOptions,
  emits: TutorAudioEmits
): TutorAudioReturn {
  const isSpeaking = ref(false)
  const isThinking = ref(false)
  const audioReady = ref(false)
  const audioProgress = ref(0)
  const audioDuration = ref(0)
  const displayText = ref('')
  const typewriterIndex = ref(0)

  let audioElement: HTMLAudioElement | null = null
  let audioProgressInterval: number | null = null

  function startProgressTracking(): void {
    stopProgressTracking()

    audioProgressInterval = window.setInterval(() => {
      if (audioElement && audioDuration.value > 0) {
        audioProgress.value = (audioElement.currentTime / audioElement.duration) * 100
      }
    }, 100)
  }

  function stopProgressTracking(): void {
    if (audioProgressInterval) {
      clearInterval(audioProgressInterval)
      audioProgressInterval = null
    }
  }

  function fallbackBrowserTTS(): void {
    if (!options.text.value || !('speechSynthesis' in window)) return

    const utterance = new SpeechSynthesisUtterance(options.text.value)
    utterance.lang = 'de-DE'
    utterance.rate = options.speed.value

    utterance.onstart = () => {
      isSpeaking.value = true
      emits.onSpeechStart()
    }

    utterance.onend = () => {
      isSpeaking.value = false
      emits.onSpeechEnd()
    }

    window.speechSynthesis.speak(utterance)
  }

  async function generateAndPlayAudio(): Promise<void> {
    if (!options.text.value || options.text.value.length === 0) return

    isThinking.value = true

    try {
      const response = await ttsApi.speak({
        text: options.text.value,
        voice: options.voice.value,
        speed: options.speed.value
      })

      if (response.success && response.data) {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
        const baseUrl = apiBaseUrl.replace(/\/api\/v1$/, '')
        const audioUrl = `${baseUrl}${response.data.audio_url}`

        if (audioElement) {
          audioElement.pause()
          audioElement = null
        }

        audioElement = new Audio(audioUrl)
        audioDuration.value = response.data.duration_ms || 0
        audioReady.value = true

        audioElement.onplay = () => {
          isSpeaking.value = true
          isThinking.value = false
          emits.onSpeechStart()
          startProgressTracking()
        }

        audioElement.onended = () => {
          isSpeaking.value = false
          audioProgress.value = 100
          stopProgressTracking()
          emits.onSpeechEnd()
        }

        audioElement.onerror = () => {
          isSpeaking.value = false
          isThinking.value = false
          stopProgressTracking()
          console.warn('Audio playback failed, using browser TTS fallback')
          fallbackBrowserTTS()
        }

        if (options.autoPlay.value) {
          await audioElement.play()
        }
      } else {
        console.warn('TTS API failed, using browser TTS fallback:', response.error)
        isThinking.value = false
        fallbackBrowserTTS()
      }
    } catch (error) {
      console.warn('TTS generation error, using browser TTS fallback:', error)
      isThinking.value = false
      fallbackBrowserTTS()
    }
  }

  function playAudio(): void {
    if (audioElement && audioReady.value) {
      audioElement.play()
    }
  }

  function pauseAudio(): void {
    if (audioElement) {
      audioElement.pause()
      isSpeaking.value = false
      stopProgressTracking()
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.pause()
    }
  }

  function skipToEnd(): void {
    pauseAudio()

    if (audioElement) {
      audioElement.currentTime = audioElement.duration
    }

    displayText.value = options.text.value
    isSpeaking.value = false
    audioProgress.value = 100

    emits.onSkip()
    emits.onSpeechEnd()
  }

  function startTypewriter(): void {
    if (!options.typewriter.value) {
      displayText.value = options.text.value
      return
    }

    displayText.value = ''
    typewriterIndex.value = 0

    function typeNext(): void {
      if (typewriterIndex.value < options.text.value.length) {
        displayText.value += options.text.value[typewriterIndex.value]
        typewriterIndex.value++
        setTimeout(typeNext, options.typewriterSpeed.value)
      }
    }

    typeNext()
  }

  function cleanup(): void {
    stopProgressTracking()

    if (audioElement) {
      audioElement.pause()
      audioElement = null
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  // Watch for text changes
  watch(options.text, (newText) => {
    if (newText) {
      audioProgress.value = 0
      audioReady.value = false
      startTypewriter()

      if (options.autoPlay.value) {
        generateAndPlayAudio()
      }
    }
  }, { immediate: true })

  onUnmounted(cleanup)

  return {
    isSpeaking,
    isThinking,
    audioReady,
    audioProgress,
    audioDuration,
    displayText,
    generateAndPlayAudio,
    playAudio,
    pauseAudio,
    skipToEnd,
    cleanup
  }
}

export { DEFAULT_TUTOR_VOICE }
