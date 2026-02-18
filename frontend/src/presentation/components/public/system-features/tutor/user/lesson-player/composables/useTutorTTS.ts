/**
 * useTutorTTS Composable
 *
 * Text-to-Speech integration for the Tutor Player:
 * - OpenAI TTS API calls
 * - Browser SpeechSynthesis fallback
 * - Audio playback state management
 *
 * Extracted from useTutorPlayer to keep files under 500 LOC.
 */

import { ref, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'

export function useTutorTTS() {
  const { t } = useI18n()

  // State
  const ttsEnabled = ref(false)
  const isSpeaking = ref(false)
  const selectedTTSModel = ref<string>('tts-1')
  const selectedVoice = ref<string>('nova')
  const audioElement = ref<HTMLAudioElement | null>(null)
  const ttsError = ref<string | null>(null)

  /**
   * Stop any current speech playback
   */
  function stopSpeaking(): void {
    window.speechSynthesis?.cancel()
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value = null
    }
    isSpeaking.value = false
  }

  /**
   * Speak text using browser SpeechSynthesis API (fallback)
   */
  function speakWithBrowser(text: string): void {
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

  /**
   * Speak text using OpenAI TTS API with browser fallback
   */
  async function speak(text: string): Promise<void> {
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

  /**
   * Toggle TTS on/off, speaking current text if enabled
   */
  function toggleTTS(currentSpeechText?: string): void {
    ttsEnabled.value = !ttsEnabled.value
    if (ttsEnabled.value && currentSpeechText) {
      speak(currentSpeechText)
    } else {
      stopSpeaking()
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    stopSpeaking()
  })

  return {
    ttsEnabled,
    isSpeaking,
    selectedTTSModel,
    selectedVoice,
    ttsError,
    stopSpeaking,
    speak,
    speakWithBrowser,
    toggleTTS
  }
}
