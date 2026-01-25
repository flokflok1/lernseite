/**
 * useTTS - Composable for Text-to-Speech functionality
 *
 * Supports multiple TTS providers:
 * - Browser TTS (free, instant, no API call)
 * - OpenAI TTS-1 and TTS-1-HD
 * - Custom models from database
 *
 * Usage:
 * ```ts
 * const {
 *   ttsEnabled,
 *   isSpeaking,
 *   selectedModel,
 *   selectedVoice,
 *   speak,
 *   stopSpeaking,
 *   toggleTTS
 * } = useTTS()
 *
 * // Speak text
 * await speak('Hello world')
 *
 * // Toggle TTS on/off
 * toggleTTS()
 * ```
 */

import { ref, computed, readonly, onUnmounted } from 'vue'
import http from '@/application/services/api/system'

// ============================================================================
// Types
// ============================================================================

export interface TTSModel {
  model_name: string
  display_name?: string
  provider?: string
  subcategory?: string
  active?: boolean
}

export interface TTSVoice {
  id: string
  name: string
  provider?: string
}

export interface SpeakOptions {
  voice?: string
  model?: string
  language?: string
  rate?: number
}

// Available voices per provider
const OPENAI_VOICES: TTSVoice[] = [
  { id: 'nova', name: 'Nova (weiblich)', provider: 'openai' },
  { id: 'alloy', name: 'Alloy (neutral)', provider: 'openai' },
  { id: 'echo', name: 'Echo (männlich)', provider: 'openai' },
  { id: 'fable', name: 'Fable (britisch)', provider: 'openai' },
  { id: 'onyx', name: 'Onyx (tief)', provider: 'openai' },
  { id: 'shimmer', name: 'Shimmer (warm)', provider: 'openai' }
]

// ============================================================================
// Composable
// ============================================================================

export function useTTS() {
  // State
  const ttsEnabled = ref(false)
  const isSpeaking = ref(false)
  const selectedModel = ref<string>('tts-1')
  const selectedVoice = ref<string>('nova')
  const generateWithTTS = ref(false)
  const availableModels = ref<TTSModel[]>([])
  const error = ref<string | null>(null)

  // Audio element reference
  let audioElement: HTMLAudioElement | null = null

  // ============================================================================
  // Model Management
  // ============================================================================

  /**
   * Load available TTS models from database
   */
  async function loadModels(): Promise<TTSModel[]> {
    try {
      // Try admin endpoint first
      const response = await http.get('/admin/ai-models', {
        params: { category: 'audio' }
      })

      if (response.data.success) {
        const models = response.data.data.models.filter((m: TTSModel) => m.active)
        availableModels.value = models
        return models
      }
    } catch {
      // Admin endpoint not available
    }

    // Fallback: Try TTS voices endpoint
    try {
      const response = await http.get('/tts/voices')
      if (response.data.success) {
        const models = response.data.data.tts_models || []
        availableModels.value = models
        return models
      }
    } catch {
      // TTS endpoint not available
    }

    // Default models
    availableModels.value = [
      { model_name: 'tts-1', display_name: 'TTS-1 Standard', provider: 'openai' },
      { model_name: 'tts-1-hd', display_name: 'TTS-1-HD High Quality', provider: 'openai' },
      { model_name: 'browser', display_name: 'Browser TTS (kostenlos)', provider: 'browser' }
    ]

    return availableModels.value
  }

  // ============================================================================
  // Playback Control
  // ============================================================================

  /**
   * Stop any ongoing speech
   */
  function stopSpeaking() {
    // Cancel browser TTS
    window.speechSynthesis?.cancel()

    // Stop audio element
    if (audioElement) {
      audioElement.pause()
      audioElement.currentTime = 0
      audioElement = null
    }

    isSpeaking.value = false
  }

  /**
   * Toggle TTS on/off
   * If turning on and there's current text, optionally speak it
   */
  function toggleTTS(currentText?: string) {
    ttsEnabled.value = !ttsEnabled.value

    if (ttsEnabled.value && currentText) {
      speak(currentText)
    } else if (!ttsEnabled.value) {
      stopSpeaking()
    }
  }

  /**
   * Speak text with browser TTS (free, instant)
   */
  function speakWithBrowser(text: string, options: SpeakOptions = {}) {
    if (!window.speechSynthesis) {
      error.value = 'Browser-Sprachausgabe nicht verfügbar'
      isSpeaking.value = false
      return
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = options.language || 'de-DE'
    utterance.rate = options.rate || 0.9

    utterance.onend = () => {
      isSpeaking.value = false
    }

    utterance.onerror = (event) => {
      console.error('Browser TTS error:', event)
      isSpeaking.value = false
      error.value = 'Fehler bei der Sprachausgabe'
    }

    window.speechSynthesis.speak(utterance)
  }

  /**
   * Speak text using selected model
   */
  async function speak(text: string, options: SpeakOptions = {}): Promise<void> {
    if (!text) return

    stopSpeaking()
    isSpeaking.value = true
    error.value = null

    const model = options.model || selectedModel.value
    const voice = options.voice || selectedVoice.value

    // Browser TTS (free, instant, no API call)
    if (model === 'browser') {
      speakWithBrowser(text, options)
      return
    }

    // OpenAI TTS via API
    try {
      const response = await http.post('/tts/speak', {
        text,
        voice,
        provider: 'openai',
        model,
        language: options.language || 'de'
      })

      if (response.data.success && response.data.data.audio_path) {
        // Create audio element
        const audio = new Audio()
        audioElement = audio

        // Get base URL for audio
        const baseUrl = (http.defaults as any).baseURL || ''
        audio.src = `${baseUrl}${response.data.data.audio_path}`

        audio.onended = () => {
          isSpeaking.value = false
          audioElement = null
        }

        audio.onerror = (e) => {
          console.error('Audio playback error:', e)
          isSpeaking.value = false
          error.value = 'Fehler bei der Audiowiedergabe'
          audioElement = null
        }

        await audio.play()
      } else {
        throw new Error(response.data.error || 'TTS-Fehler')
      }
    } catch (err: any) {
      console.error('TTS error:', err)
      isSpeaking.value = false

      // Fallback to browser TTS
      if (err.response?.status === 503 || err.message?.includes('quota')) {
        error.value = 'API-Limit erreicht, verwende Browser-TTS'
        speakWithBrowser(text, options)
      } else {
        error.value = err.message || 'TTS-Fehler'
      }
    }
  }

  /**
   * Play audio from URL
   */
  async function playAudioUrl(url: string): Promise<void> {
    stopSpeaking()
    isSpeaking.value = true

    try {
      const audio = new Audio(url)
      audioElement = audio

      audio.onended = () => {
        isSpeaking.value = false
        audioElement = null
      }

      audio.onerror = () => {
        isSpeaking.value = false
        error.value = 'Fehler bei der Audiowiedergabe'
        audioElement = null
      }

      await audio.play()
    } catch (err: any) {
      isSpeaking.value = false
      error.value = err.message || 'Audiofehler'
    }
  }

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Get only real TTS models (not other audio models)
   */
  const ttsModels = computed(() => {
    return availableModels.value.filter(m => {
      const subcategory = m.subcategory?.toLowerCase()
      const name = m.model_name?.toLowerCase() || ''
      return subcategory === 'tts' || name.startsWith('tts-') || name === 'browser'
    })
  })

  /**
   * Available voices for current provider
   */
  const voices = computed((): TTSVoice[] => {
    const model = selectedModel.value
    if (model === 'browser') {
      // Browser voices would need to be loaded from speechSynthesis.getVoices()
      return [{ id: 'default', name: 'Standard', provider: 'browser' }]
    }
    // OpenAI voices
    return OPENAI_VOICES
  })

  // ============================================================================
  // Cleanup
  // ============================================================================

  onUnmounted(() => {
    stopSpeaking()
  })

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State (readonly)
    ttsEnabled: readonly(ttsEnabled),
    isSpeaking: readonly(isSpeaking),
    selectedModel,  // writable for v-model
    selectedVoice,  // writable for v-model
    generateWithTTS, // writable for v-model
    availableModels: readonly(availableModels),
    error: readonly(error),

    // Computed
    ttsModels,
    voices,

    // Methods
    loadModels,
    speak,
    stopSpeaking,
    toggleTTS,
    playAudioUrl,

    // Clear error
    clearError: () => { error.value = null }
  }
}

export default useTTS
