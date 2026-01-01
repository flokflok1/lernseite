/**
 * Tutor Companion Store
 *
 * Global state for the 3D AI Tutor that accompanies users throughout the app.
 * Manages chat history, personality settings, TTS, and UI state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Types
export interface TutorMessage {
  id: string
  role: 'user' | 'tutor'
  content: string
  timestamp: Date
  isPlaying?: boolean  // For TTS
}

export interface TutorPersonality {
  id: string
  name: string
  description: string
  systemPrompt: string
  voiceId?: string  // For TTS voice selection
}

export interface TutorSettings {
  enabled: boolean
  minimized: boolean
  position: 'bottom-right' | 'bottom-left'
  ttsEnabled: boolean
  ttsAutoPlay: boolean
  personality: TutorPersonality
  customPersonalityText: string | null
}

// Default personalities
export const DEFAULT_PERSONALITIES: TutorPersonality[] = [
  {
    id: 'friendly',
    name: 'Freundlich',
    description: 'Ein warmherziger und geduldiger Tutor',
    systemPrompt: `Du bist ein freundlicher und warmherziger KI-Tutor namens "Lumi".
Du begleitest Lernende durch ihre Lernreise auf LernsystemX.
Du bist geduldig, ermutigend und feierst jeden Fortschritt.
Du verwendest eine lockere, aber respektvolle Sprache.
Du gibst hilfreiche Tipps und motivierst die Lernenden weiterzumachen.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.`,
    voiceId: 'alloy'
  },
  {
    id: 'strict',
    name: 'Streng',
    description: 'Ein fordernder Professor der das Beste erwartet',
    systemPrompt: `Du bist ein strenger aber fairer KI-Tutor namens "Professor Max".
Du hast hohe Erwartungen an deine Schüler und akzeptierst keine Ausreden.
Du bist direkt und präzise in deinen Erklärungen.
Du lobst nur wenn es wirklich verdient ist.
Du forderst die Lernenden heraus, über sich hinauszuwachsen.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.`,
    voiceId: 'onyx'
  },
  {
    id: 'humorous',
    name: 'Humorvoll',
    description: 'Ein witziger Tutor der Lernen spaßig macht',
    systemPrompt: `Du bist ein humorvoller KI-Tutor namens "Witzi".
Du machst Lernen unterhaltsam mit Witzen, Wortspielen und lustigen Beispielen.
Du findest das Lustige in jedem Thema, ohne den Lerninhalt zu vernachlässigen.
Du verwendest Memes und Pop-Kultur-Referenzen wenn passend.
Du hältst die Stimmung leicht und motivierst durch Spaß.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.`,
    voiceId: 'fable'
  },
  {
    id: 'patient',
    name: 'Geduldig',
    description: 'Ein sehr geduldiger Mentor der alles so oft erklärt wie nötig',
    systemPrompt: `Du bist ein extrem geduldiger KI-Tutor namens "Mentor Sam".
Du erklärst Dinge so oft und auf so viele verschiedene Arten wie nötig.
Du wirst niemals ungeduldig oder frustriert.
Du zerlegst komplexe Themen in kleinste, verständliche Schritte.
Du versicherst den Lernenden, dass es okay ist, Zeit zu brauchen.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.`,
    voiceId: 'thorsten'
  }
]

export const useTutorStore = defineStore('tutor', () => {
  // State
  const messages = ref<TutorMessage[]>([])
  const isLoading = ref(false)
  const isTyping = ref(false)
  const isSpeaking = ref(false)
  const currentAudio = ref<HTMLAudioElement | null>(null)

  const settings = ref<TutorSettings>({
    enabled: true,
    minimized: true,  // Start minimized
    position: 'bottom-right',
    ttsEnabled: true,
    ttsAutoPlay: false,
    personality: DEFAULT_PERSONALITIES[0],  // Friendly by default
    customPersonalityText: null
  })

  // Current context (what page/course the user is on)
  const currentContext = ref({
    page: 'dashboard',
    courseId: null as string | null,
    courseName: null as string | null,
    chapterId: null as string | null,
    chapterName: null as string | null,
    lessonId: null as string | number | null,
    lessonName: null as string | null,
    methodId: null as string | null,
    methodType: null as number | null
  })

  // Computed
  const isOpen = computed(() => settings.value.enabled && !settings.value.minimized)

  const effectiveSystemPrompt = computed(() => {
    if (settings.value.customPersonalityText) {
      return `Du bist ein KI-Tutor auf LernsystemX. ${settings.value.customPersonalityText}
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.`
    }
    return settings.value.personality.systemPrompt
  })

  const contextDescription = computed(() => {
    const ctx = currentContext.value
    const parts: string[] = []

    if (ctx.courseName) {
      parts.push(`Kurs: "${ctx.courseName}"`)
    }
    if (ctx.chapterName) {
      parts.push(`Kapitel: "${ctx.chapterName}"`)
    }
    if (ctx.lessonName) {
      parts.push(`Lektion: "${ctx.lessonName}"`)
    }
    if (ctx.methodType !== null) {
      parts.push(`Lernmethode: LM${ctx.methodType.toString().padStart(2, '0')}`)
    }

    if (parts.length > 0) {
      return `Der User ist gerade hier: ${parts.join(', ')}.`
    }
    return `Der User ist gerade auf der ${ctx.page}-Seite.`
  })

  // Context IDs for API (for knowledge loading)
  const contextIds = computed(() => ({
    courseId: currentContext.value.courseId,
    chapterId: currentContext.value.chapterId,
    lessonId: currentContext.value.lessonId,
    methodId: currentContext.value.methodId
  }))

  // Actions
  const toggle = () => {
    settings.value.minimized = !settings.value.minimized
  }

  const open = () => {
    settings.value.minimized = false
  }

  const minimize = () => {
    settings.value.minimized = true
  }

  const setEnabled = (enabled: boolean) => {
    settings.value.enabled = enabled
  }

  const setPosition = (position: 'bottom-right' | 'bottom-left') => {
    settings.value.position = position
  }

  const setPersonality = (personality: TutorPersonality) => {
    settings.value.personality = personality
    settings.value.customPersonalityText = null
  }

  const setCustomPersonality = (text: string) => {
    settings.value.customPersonalityText = text
  }

  const setTTSEnabled = (enabled: boolean) => {
    settings.value.ttsEnabled = enabled
  }

  const setTTSAutoPlay = (autoPlay: boolean) => {
    settings.value.ttsAutoPlay = autoPlay
  }

  const updateContext = (context: Partial<typeof currentContext.value>) => {
    currentContext.value = { ...currentContext.value, ...context }
  }

  const addMessage = (role: 'user' | 'tutor', content: string): TutorMessage => {
    // Generate UUID with fallback for older browsers
    const generateId = (): string => {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
      }
      // Fallback for browsers without crypto.randomUUID
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    }

    const message: TutorMessage = {
      id: generateId(),
      role,
      content,
      timestamp: new Date()
    }
    messages.value.push(message)
    return message
  }

  const clearMessages = () => {
    messages.value = []
  }

  const stopSpeaking = () => {
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }
    isSpeaking.value = false
  }

  const setSpeaking = (speaking: boolean, audio?: HTMLAudioElement) => {
    isSpeaking.value = speaking
    if (audio) {
      currentAudio.value = audio
    }
  }

  // Persist settings to localStorage
  const loadSettings = () => {
    const saved = localStorage.getItem('tutor-settings')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        // Merge with defaults to handle new properties
        settings.value = {
          ...settings.value,
          ...parsed,
          // Restore personality object from ID
          personality: DEFAULT_PERSONALITIES.find(p => p.id === parsed.personality?.id) || DEFAULT_PERSONALITIES[0]
        }
      } catch (e) {
        console.warn('Failed to load tutor settings:', e)
      }
    }
  }

  const saveSettings = () => {
    localStorage.setItem('tutor-settings', JSON.stringify(settings.value))
  }

  // Watch for settings changes and persist
  // Note: Call saveSettings() after changing settings

  return {
    // State
    messages,
    isLoading,
    isTyping,
    isSpeaking,
    settings,
    currentContext,

    // Computed
    isOpen,
    effectiveSystemPrompt,
    contextDescription,
    contextIds,

    // Actions
    toggle,
    open,
    minimize,
    setEnabled,
    setPosition,
    setPersonality,
    setCustomPersonality,
    setTTSEnabled,
    setTTSAutoPlay,
    updateContext,
    addMessage,
    clearMessages,
    stopSpeaking,
    setSpeaking,
    loadSettings,
    saveSettings,

    // Constants
    DEFAULT_PERSONALITIES
  }
})
