/**
 * useTutorChat - Chat messaging and TTS composable
 *
 * Manages sending messages to the tutor API, text-to-speech playback,
 * and chat scroll behavior.
 */

import { ref, nextTick, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import { tutorChat, tutorTTS } from '@/application/services/api/learning'

interface UseTutorChatOptions {
  chatContainer: Ref<HTMLDivElement | null>
}

interface UseTutorChatReturn {
  userInput: Ref<string>
  sendMessage: () => Promise<void>
  playTTS: (text: string) => Promise<void>
  formatTime: (date: Date) => string
}

export function useTutorChat({ chatContainer }: UseTutorChatOptions): UseTutorChatReturn {
  const { t } = useI18n()
  const tutorStore = useTutorStore()
  const userInput = ref('')

  function scrollToBottom(): void {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }

  async function playTTS(text: string): Promise<void> {
    if (!tutorStore.settings.ttsEnabled) return

    try {
      const audioUrl = await tutorTTS({
        text,
        voice: tutorStore.settings.personality.voiceId || 'alloy'
      })

      const audio = new Audio(audioUrl)
      tutorStore.setSpeaking(true, audio)

      audio.onended = () => {
        tutorStore.setSpeaking(false)
      }

      audio.onerror = () => {
        tutorStore.setSpeaking(false)
      }

      await audio.play()
    } catch (error) {
      console.error('TTS error:', error)
      tutorStore.setSpeaking(false)
    }
  }

  async function sendMessage(): Promise<void> {
    const message = userInput.value.trim()
    if (!message || tutorStore.isLoading) return

    userInput.value = ''

    tutorStore.addMessage('user', message)

    await nextTick()
    scrollToBottom()

    tutorStore.isLoading = true
    tutorStore.isTyping = true

    try {
      const contextIds = tutorStore.contextIds
      const response = await tutorChat({
        message,
        context: tutorStore.contextDescription,
        systemPrompt: tutorStore.effectiveSystemPrompt,
        history: tutorStore.messages.slice(-10).map(m => ({
          role: m.role === 'user' ? 'user' : 'assistant',
          content: m.content
        })),
        courseId: contextIds.courseId || undefined,
        chapterId: contextIds.chapterId || undefined,
        lessonId: contextIds.lessonId || undefined,
        methodId: contextIds.methodId || undefined
      })

      tutorStore.isTyping = false

      tutorStore.addMessage('tutor', response.message)

      await nextTick()
      scrollToBottom()

      if (tutorStore.settings.ttsEnabled && tutorStore.settings.ttsAutoPlay) {
        await playTTS(response.message)
      }
    } catch (error) {
      console.error('Tutor chat error:', error)
      tutorStore.addMessage('tutor', t('tutor.errorMessage'))
    } finally {
      tutorStore.isLoading = false
      tutorStore.isTyping = false
    }
  }

  function formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return {
    userInput,
    sendMessage,
    playTTS,
    formatTime
  }
}
