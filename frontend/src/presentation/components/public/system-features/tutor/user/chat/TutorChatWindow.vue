<script setup lang="ts">
/**
 * TutorChatWindow - Chat window for the AI tutor companion
 *
 * Displays the chat header, settings panel, message history, and input area.
 * Separated from TutorCompanion to keep each component under 500 LOC.
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTutorStore, DEFAULT_PERSONALITIES } from '@/application/stores/modules/learning/tutor.store'
import { useTutorChat } from './composables/useTutorChat'

const { t } = useI18n()

const emit = defineEmits<{
  close: []
}>()

const tutorStore = useTutorStore()

const showSettings = ref(false)
const chatContainer = ref<HTMLDivElement | null>(null)

const { userInput, sendMessage, playTTS, formatTime } = useTutorChat({ chatContainer })

const hasContext = computed(() => {
  const ctx = tutorStore.contextIds
  return !!(ctx.courseId || ctx.chapterId || ctx.lessonId || ctx.methodId)
})

function statusText(): string {
  if (tutorStore.isTyping) return t('tutor.statusTyping')
  if (tutorStore.isSpeaking) return t('tutor.statusSpeaking')
  if (hasContext.value) return t('tutor.statusContext')
  return t('tutor.statusIdle')
}
</script>

<template>
  <div
    class="fixed z-50 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
    :class="[
      tutorStore.settings.position === 'bottom-right' ? 'right-6 bottom-36' : 'left-6 bottom-36'
    ]"
    style="max-height: 500px; height: 60vh;"
  >
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center gap-3">
      <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </div>

      <div class="flex-1 min-w-0">
        <h3 class="text-white font-semibold truncate">
          {{ tutorStore.settings.customPersonalityText ? $t('tutor.myTutor') : tutorStore.settings.personality.name }}
        </h3>
        <p class="text-indigo-200 text-sm truncate">
          {{ statusText() }}
        </p>
      </div>

      <!-- Context indicator -->
      <div
        v-if="hasContext"
        class="px-2 py-0.5 rounded-full bg-green-500/30 text-green-100 text-xs flex items-center gap-1"
        :title="tutorStore.contextDescription"
      >
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        {{ $t('tutor.context') }}
      </div>

      <div class="flex items-center gap-1">
        <!-- Settings -->
        <button
          @click="showSettings = !showSettings"
          class="p-2 rounded-lg hover:bg-white/20 transition-colors"
          :title="$t('tutor.settings')"
        >
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>

        <!-- Close -->
        <button
          @click="emit('close')"
          class="p-2 rounded-lg hover:bg-white/20 transition-colors"
          :title="$t('tutor.close')"
        >
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Settings Panel -->
    <div v-if="showSettings" class="p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600 max-h-48 overflow-y-auto">
      <h4 class="font-medium text-gray-900 dark:text-white mb-3">{{ $t('tutor.settingsTitle') }}</h4>

      <!-- Personality Selection -->
      <div class="mb-4">
        <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">{{ $t('tutor.personality') }}</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="personality in DEFAULT_PERSONALITIES"
            :key="personality.id"
            @click="tutorStore.setPersonality(personality); tutorStore.saveSettings()"
            class="p-2 text-left rounded-lg border transition-colors"
            :class="[
              tutorStore.settings.personality.id === personality.id && !tutorStore.settings.customPersonalityText
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                : 'border-gray-200 dark:border-gray-600 hover:border-indigo-300'
            ]"
          >
            <div class="font-medium text-sm text-gray-900 dark:text-white">{{ personality.name }}</div>
          </button>
        </div>
      </div>

      <!-- Custom Personality -->
      <div class="mb-4">
        <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">{{ $t('tutor.customDescription') }}</label>
        <textarea
          v-model="tutorStore.settings.customPersonalityText"
          @change="tutorStore.saveSettings()"
          :placeholder="$t('tutor.customPlaceholder')"
          class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm resize-none"
          rows="2"
        ></textarea>
      </div>

      <!-- TTS Toggle -->
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600 dark:text-gray-300">{{ $t('tutor.tts') }}</span>
        <button
          @click="tutorStore.setTTSEnabled(!tutorStore.settings.ttsEnabled); tutorStore.saveSettings()"
          class="relative w-12 h-6 rounded-full transition-colors"
          :class="tutorStore.settings.ttsEnabled ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'"
        >
          <span
            class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform"
            :class="tutorStore.settings.ttsEnabled ? 'translate-x-6' : ''"
          ></span>
        </button>
      </div>

      <!-- Auto-play TTS -->
      <div v-if="tutorStore.settings.ttsEnabled" class="flex items-center justify-between">
        <span class="text-sm text-gray-600 dark:text-gray-300">{{ $t('tutor.ttsAutoPlay') }}</span>
        <button
          @click="tutorStore.setTTSAutoPlay(!tutorStore.settings.ttsAutoPlay); tutorStore.saveSettings()"
          class="relative w-12 h-6 rounded-full transition-colors"
          :class="tutorStore.settings.ttsAutoPlay ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'"
        >
          <span
            class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform"
            :class="tutorStore.settings.ttsAutoPlay ? 'translate-x-6' : ''"
          ></span>
        </button>
      </div>
    </div>

    <!-- Chat Messages -->
    <div
      ref="chatContainer"
      class="flex-1 overflow-y-auto p-4 space-y-3"
    >
      <!-- Welcome message if empty -->
      <div v-if="tutorStore.messages.length === 0" class="text-center py-6">
        <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
          <svg class="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
          </svg>
        </div>
        <h4 class="font-medium text-gray-900 dark:text-white mb-1">
          {{ $t('tutor.welcomeTitle') }}
        </h4>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ $t('tutor.welcomeHint') }}
        </p>
      </div>

      <!-- Messages -->
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
            <!-- TTS button for tutor messages -->
            <button
              v-if="message.role === 'tutor' && tutorStore.settings.ttsEnabled"
              @click="playTTS(message.content)"
              class="hover:text-indigo-400 transition-colors"
              :title="$t('tutor.readAloud')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Typing indicator -->
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

    <!-- Input Area -->
    <div class="p-3 border-t border-gray-200 dark:border-gray-700">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <input
          v-model="userInput"
          type="text"
          :placeholder="$t('tutor.inputPlaceholder')"
          class="flex-1 px-4 py-2 rounded-full border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          :disabled="tutorStore.isLoading"
        />
        <button
          type="submit"
          :disabled="!userInput.trim() || tutorStore.isLoading"
          class="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>

      <!-- Stop speaking button -->
      <button
        v-if="tutorStore.isSpeaking"
        @click="tutorStore.stopSpeaking()"
        class="mt-2 w-full py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
      >
        {{ $t('tutor.stopSpeaking') }}
      </button>
    </div>
  </div>
</template>
