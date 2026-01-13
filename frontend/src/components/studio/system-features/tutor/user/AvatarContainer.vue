<script setup lang="ts">
/**
 * AvatarContainer - Main container for the 3D Avatar System
 *
 * Features:
 * - Floating avatar with chat
 * - Classroom/Whiteboard mode for courses
 * - Feedback button (separate window)
 * - Avatar settings panel
 * - Lip-sync integration
 */

import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import Avatar3D from './Avatar3D.vue'
import FeedbackWindow from './FeedbackWindow.vue'
import { useAvatarStore, PRESET_AVATARS, type AvatarMode } from '@/store/modules/ui'
import { useTutorStore, DEFAULT_PERSONALITIES } from '@/store/modules/learning'
import { tutorChat, tutorTTS } from '@/api/tutor.api'

// Stores
const avatarStore = useAvatarStore()
const tutorStore = useTutorStore()

// Props
const props = defineProps<{
  courseId?: string
  lessonId?: string
  courseName?: string
}>()

// State
const showChat = ref(false)
const showSettings = ref(false)
const showFeedback = ref(false)
const showAvatarPicker = ref(false)
const userInput = ref('')
const chatContainer = ref<HTMLDivElement | null>(null)
const isExpanded = ref(false)

// Computed
const currentMode = computed<AvatarMode>(() => {
  if (props.courseId && avatarStore.settings.showWhiteboardInCourse) {
    return 'classroom'
  }
  return avatarStore.settings.mode
})

const positionClasses = computed(() => {
  const base = 'fixed z-40 transition-all duration-500'
  if (avatarStore.settings.position === 'bottom-right') {
    return `${base} right-6 bottom-6`
  }
  return `${base} left-6 bottom-6`
})

const avatarSize = computed(() => {
  if (isExpanded.value || currentMode.value === 'classroom') {
    return 'w-[300px] h-[300px]'
  }
  return 'w-[120px] h-[120px]'
})

// Methods
const toggleChat = () => {
  showChat.value = !showChat.value
  if (showChat.value) {
    showSettings.value = false
  }
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const openFeedback = () => {
  showFeedback.value = true
}

const closeFeedback = () => {
  showFeedback.value = false
}

const onFeedbackSubmitted = (feedbackId: string) => {
  console.log('Feedback submitted:', feedbackId)
}

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || tutorStore.isLoading) return

  userInput.value = ''
  tutorStore.addMessage('user', message)

  await nextTick()
  scrollToBottom()

  tutorStore.isLoading = true
  tutorStore.isTyping = true

  try {
    const response = await tutorChat({
      message,
      context: tutorStore.contextDescription,
      systemPrompt: tutorStore.effectiveSystemPrompt,
      history: tutorStore.messages.slice(-10).map(m => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: m.content
      }))
    })

    tutorStore.isTyping = false
    tutorStore.addMessage('tutor', response.message)

    await nextTick()
    scrollToBottom()

    // Auto-play TTS
    if (tutorStore.settings.ttsEnabled && tutorStore.settings.ttsAutoPlay) {
      await playTTS(response.message)
    }
  } catch (error) {
    console.error('Chat error:', error)
    tutorStore.addMessage('tutor', 'Entschuldigung, es gab einen Fehler.')
  } finally {
    tutorStore.isLoading = false
    tutorStore.isTyping = false
  }
}

const playTTS = async (text: string) => {
  if (!tutorStore.settings.ttsEnabled) return

  try {
    const audioUrl = await tutorTTS({
      text,
      voice: tutorStore.settings.personality.voiceId || 'alloy'
    })

    const audio = new Audio(audioUrl)

    // Connect to lip-sync analyzer
    if (avatarStore.settings.lipSyncEnabled) {
      avatarStore.connectAudioForLipSync(audio)
    }

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

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const selectAvatar = (presetId: string) => {
  avatarStore.selectPreset(presetId)
  showAvatarPicker.value = false
}

const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Watch for speaking to auto-expand
watch(() => tutorStore.isSpeaking, (speaking) => {
  if (speaking && avatarStore.settings.autoExpandOnSpeaking) {
    isExpanded.value = true
  }
})

// Update context
watch([() => props.courseId, () => props.lessonId, () => props.courseName], () => {
  tutorStore.updateContext({
    courseId: props.courseId || null,
    lessonId: props.lessonId || null,
    courseName: props.courseName || null
  })
})

// Lifecycle
onMounted(() => {
  tutorStore.loadSettings()
  avatarStore.loadSettings()
  avatarStore.initAudioAnalyzer()
})

onUnmounted(() => {
  avatarStore.cleanup()
})
</script>

<template>
  <div v-if="tutorStore.settings.enabled">
    <!-- ============================================== -->
    <!-- FLOATING AVATAR -->
    <!-- ============================================== -->
    <div :class="positionClasses" class="group">
      <!-- Avatar Container -->
      <div class="relative">
        <!-- Glow effects -->
        <div
          v-if="tutorStore.isSpeaking"
          class="absolute inset-0 rounded-full bg-green-400/30 animate-ping pointer-events-none"
          :style="{ width: isExpanded ? '320px' : '140px', height: isExpanded ? '320px' : '140px', margin: '-10px' }"
        ></div>

        <div
          v-if="tutorStore.isTyping"
          class="absolute inset-0 rounded-full border-4 border-yellow-400/50 animate-spin pointer-events-none"
          :style="{ width: isExpanded ? '320px' : '140px', height: isExpanded ? '320px' : '140px', margin: '-10px', borderTopColor: 'transparent' }"
        ></div>

        <!-- 3D Avatar -->
        <div
          :class="[
            avatarSize,
            'rounded-full overflow-hidden cursor-pointer',
            'bg-gradient-to-br from-indigo-500/20 to-purple-600/20',
            'backdrop-blur-sm border-2 border-white/20 shadow-2xl',
            'transition-all duration-300 group-hover:scale-105'
          ]"
          @click="toggleChat"
        >
          <Avatar3D
            :mode="currentMode"
            :show-whiteboard="currentMode === 'classroom'"
            :whiteboard-content="avatarStore.whiteboardContent"
          />
        </div>

        <!-- Status Badge -->
        <div
          class="absolute -top-1 -right-1 w-5 h-5 rounded-full border-2 border-white shadow-lg flex items-center justify-center"
          :class="[
            tutorStore.isSpeaking ? 'bg-green-500' :
            tutorStore.isTyping ? 'bg-yellow-500' :
            'bg-indigo-500'
          ]"
        >
          <span v-if="tutorStore.isSpeaking" class="text-white text-xs">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3z"/>
            </svg>
          </span>
          <span v-else-if="tutorStore.isTyping" class="text-white text-xs">...</span>
        </div>

        <!-- Action Buttons (neben Avatar) -->
        <div
          class="absolute -right-12 top-1/2 -translate-y-1/2 flex flex-col gap-2"
          :class="avatarStore.settings.position === 'bottom-left' ? '-right-12' : '-left-12'"
        >
          <!-- Feedback Button -->
          <button
            @click.stop="openFeedback"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            title="Feedback geben"
          >
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </button>

          <!-- Expand/Collapse Button -->
          <button
            @click.stop="toggleExpand"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            :title="isExpanded ? 'Verkleinern' : 'Vergrößern'"
          >
            <svg v-if="isExpanded" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
            </svg>
            <svg v-else class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
            </svg>
          </button>

          <!-- Settings Button -->
          <button
            @click.stop="showSettings = !showSettings"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            title="Einstellungen"
          >
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
        </div>

        <!-- Hint bubble -->
        <div
          v-if="!showChat && tutorStore.messages.length === 0"
          class="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg pointer-events-none"
        >
          Klick mich an!
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-gray-900 rotate-45"></div>
        </div>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- SETTINGS PANEL -->
    <!-- ============================================== -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-x-4"
      enter-to-class="opacity-100 translate-x-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 translate-x-4"
    >
      <div
        v-if="showSettings"
        class="fixed z-50 w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
        :class="[
          avatarStore.settings.position === 'bottom-right' ? 'right-6 bottom-44' : 'left-6 bottom-44'
        ]"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center justify-between">
          <h3 class="text-white font-semibold">Avatar Einstellungen</h3>
          <button @click="showSettings = false" class="p-1 rounded hover:bg-white/20 text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="p-4 max-h-96 overflow-y-auto space-y-4">
          <!-- Avatar Style -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Avatar wählen
            </label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="preset in PRESET_AVATARS"
                :key="preset.id"
                @click="selectAvatar(preset.id)"
                class="p-2 rounded-lg border transition-colors text-left"
                :class="[
                  avatarStore.settings.appearance.style === preset.style
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600 hover:border-indigo-300'
                ]"
              >
                <div class="text-lg mb-1">{{ preset.style === 'robot' ? '🤖' : preset.style === 'anime' ? '🎭' : '👤' }}</div>
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ preset.name }}</div>
              </button>
            </div>
          </div>

          <!-- Personality -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Persönlichkeit
            </label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="personality in DEFAULT_PERSONALITIES"
                :key="personality.id"
                @click="tutorStore.setPersonality(personality); tutorStore.saveSettings()"
                class="p-2 rounded-lg border transition-colors text-left"
                :class="[
                  tutorStore.settings.personality.id === personality.id
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600 hover:border-indigo-300'
                ]"
              >
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ personality.name }}</div>
              </button>
            </div>
          </div>

          <!-- Position -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Position
            </label>
            <div class="flex gap-2">
              <button
                @click="avatarStore.settings.position = 'bottom-left'; avatarStore.saveSettings()"
                class="flex-1 py-2 px-3 rounded-lg border transition-colors text-sm"
                :class="[
                  avatarStore.settings.position === 'bottom-left'
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600'
                ]"
              >
                Links
              </button>
              <button
                @click="avatarStore.settings.position = 'bottom-right'; avatarStore.saveSettings()"
                class="flex-1 py-2 px-3 rounded-lg border transition-colors text-sm"
                :class="[
                  avatarStore.settings.position === 'bottom-right'
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600'
                ]"
              >
                Rechts
              </button>
            </div>
          </div>

          <!-- Toggles -->
          <div class="space-y-3">
            <!-- TTS -->
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Sprachausgabe</span>
              <button
                @click="tutorStore.setTTSEnabled(!tutorStore.settings.ttsEnabled); tutorStore.saveSettings()"
                class="relative w-10 h-5 rounded-full transition-colors"
                :class="tutorStore.settings.ttsEnabled ? 'bg-indigo-600' : 'bg-gray-300'"
              >
                <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform" :class="tutorStore.settings.ttsEnabled ? 'translate-x-5' : ''"></span>
              </button>
            </div>

            <!-- Lip-Sync -->
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Lip-Sync</span>
              <button
                @click="avatarStore.toggleLipSync()"
                class="relative w-10 h-5 rounded-full transition-colors"
                :class="avatarStore.settings.lipSyncEnabled ? 'bg-indigo-600' : 'bg-gray-300'"
              >
                <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform" :class="avatarStore.settings.lipSyncEnabled ? 'translate-x-5' : ''"></span>
              </button>
            </div>

            <!-- Auto-expand -->
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Beim Sprechen vergrößern</span>
              <button
                @click="avatarStore.settings.autoExpandOnSpeaking = !avatarStore.settings.autoExpandOnSpeaking; avatarStore.saveSettings()"
                class="relative w-10 h-5 rounded-full transition-colors"
                :class="avatarStore.settings.autoExpandOnSpeaking ? 'bg-indigo-600' : 'bg-gray-300'"
              >
                <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform" :class="avatarStore.settings.autoExpandOnSpeaking ? 'translate-x-5' : ''"></span>
              </button>
            </div>

            <!-- Whiteboard in courses -->
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Whiteboard in Kursen</span>
              <button
                @click="avatarStore.settings.showWhiteboardInCourse = !avatarStore.settings.showWhiteboardInCourse; avatarStore.saveSettings()"
                class="relative w-10 h-5 rounded-full transition-colors"
                :class="avatarStore.settings.showWhiteboardInCourse ? 'bg-indigo-600' : 'bg-gray-300'"
              >
                <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform" :class="avatarStore.settings.showWhiteboardInCourse ? 'translate-x-5' : ''"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ============================================== -->
    <!-- CHAT WINDOW -->
    <!-- ============================================== -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <div
        v-if="showChat"
        class="fixed z-50 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        :class="[
          avatarStore.settings.position === 'bottom-right' ? 'right-6' : 'left-6',
          isExpanded ? 'bottom-80' : 'bottom-36'
        ]"
        style="max-height: 500px; height: 60vh;"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-white font-semibold truncate">
              {{ tutorStore.settings.personality.name }}
            </h3>
            <p class="text-indigo-200 text-sm truncate">
              {{ tutorStore.isTyping ? 'schreibt...' : tutorStore.isSpeaking ? 'spricht...' : 'KI-Tutor' }}
            </p>
          </div>
          <button @click="showChat = false" class="p-2 rounded-lg hover:bg-white/20 text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-3">
          <div v-if="tutorStore.messages.length === 0" class="text-center py-6">
            <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 dark:text-white mb-1">Hallo!</h4>
            <p class="text-sm text-gray-500">Frag mich alles!</p>
          </div>

          <div
            v-for="message in tutorStore.messages"
            :key="message.id"
            class="flex"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] rounded-2xl px-4 py-2"
              :class="[
                message.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
              ]"
            >
              <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
              <div
                class="text-xs mt-1 flex items-center gap-2"
                :class="message.role === 'user' ? 'text-indigo-200' : 'text-gray-400'"
              >
                <span>{{ formatTime(message.timestamp) }}</span>
                <button
                  v-if="message.role === 'tutor' && tutorStore.settings.ttsEnabled"
                  @click="playTTS(message.content)"
                  class="hover:text-indigo-400 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div v-if="tutorStore.isTyping" class="flex justify-start">
            <div class="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex gap-1">
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-3 border-t border-gray-200 dark:border-gray-700">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="userInput"
              type="text"
              placeholder="Schreib eine Nachricht..."
              class="flex-1 px-4 py-2 rounded-full border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              :disabled="tutorStore.isLoading"
            />
            <button
              type="submit"
              :disabled="!userInput.trim() || tutorStore.isLoading"
              class="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </form>

          <button
            v-if="tutorStore.isSpeaking"
            @click="tutorStore.stopSpeaking()"
            class="mt-2 w-full py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            Sprachausgabe stoppen
          </button>
        </div>
      </div>
    </Transition>

    <!-- ============================================== -->
    <!-- FEEDBACK WINDOW -->
    <!-- ============================================== -->
    <FeedbackWindow
      v-if="showFeedback"
      :course-id="courseId"
      :lesson-id="lessonId"
      :context="courseName"
      @close="closeFeedback"
      @submitted="onFeedbackSubmitted"
    />
  </div>
</template>
