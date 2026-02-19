<script setup lang="ts">
/**
 * AvatarChatWindow - Chat window for the tutor avatar
 *
 * Displays the message history, typing indicator, and input form.
 * Uses useTutorChat composable for message handling and TTS.
 */

import { ref } from 'vue'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import { useAvatarStore } from '@/application/stores/modules/ui/avatar.store'
import { useTutorChat } from './composables/useTutorChat'

defineProps<{
  isExpanded: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const tutorStore = useTutorStore()
const avatarStore = useAvatarStore()
const chatContainer = ref<HTMLDivElement | null>(null)

const {
  userInput,
  sendMessage,
  playTTS,
  formatTime
} = useTutorChat({ chatContainer })
</script>

<template>
  <div
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
      <button @click="emit('close')" class="p-2 rounded-lg hover:bg-white/20 text-white">
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
</template>
