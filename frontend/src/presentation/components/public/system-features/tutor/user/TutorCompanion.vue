<script setup lang="ts">
/**
 * TutorCompanion - Global 3D AI Tutor Widget
 *
 * A floating 3D avatar tutor that accompanies users throughout the app.
 * Avatar and Chat window are SEPARATE - Avatar floats freely, chat opens separately.
 *
 * Extracted sub-components:
 * - TutorChatWindow.vue - Chat window with messages, settings, and input
 * - composables/useTutorAvatar.ts - Three.js avatar setup and animation
 * - composables/useTutorChat.ts - Chat messaging and TTS logic
 */

import { ref, onMounted } from 'vue'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import { useTutorAvatar } from './composables/useTutorAvatar'
import TutorChatWindow from './TutorChatWindow.vue'

const tutorStore = useTutorStore()

const avatarContainer = ref<HTMLDivElement | null>(null)
const showChat = ref(false)

useTutorAvatar({ avatarContainer })

function toggleChat(): void {
  showChat.value = !showChat.value
}

onMounted(() => {
  tutorStore.loadSettings()
})
</script>

<template>
  <div v-if="tutorStore.settings.enabled">
    <!-- Floating 3D Avatar (separate from chat) -->
    <div
      class="fixed z-40 transition-all duration-500 cursor-pointer group"
      :class="[
        tutorStore.settings.position === 'bottom-right' ? 'right-6 bottom-6' : 'left-6 bottom-6'
      ]"
      @click="toggleChat"
    >
      <div class="relative">
        <!-- Glow ring when speaking -->
        <div
          v-if="tutorStore.isSpeaking"
          class="absolute inset-0 rounded-full bg-green-400/30 animate-ping"
          style="width: 140px; height: 140px; margin: -10px;"
        ></div>

        <!-- Thinking ring -->
        <div
          v-if="tutorStore.isTyping"
          class="absolute inset-0 rounded-full border-4 border-yellow-400/50 animate-spin"
          style="width: 140px; height: 140px; margin: -10px; border-top-color: transparent;"
        ></div>

        <!-- 3D Avatar Canvas -->
        <div
          ref="avatarContainer"
          class="w-[120px] h-[120px] rounded-full overflow-hidden bg-gradient-to-br from-indigo-500/20 to-purple-600/20 backdrop-blur-sm border-2 border-white/20 shadow-2xl group-hover:scale-110 transition-transform duration-300"
        ></div>

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
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          </span>
          <span v-else-if="tutorStore.isTyping" class="text-white text-xs">...</span>
        </div>

        <!-- Chat bubble hint -->
        <div
          v-if="!showChat && tutorStore.messages.length === 0"
          class="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
        >
          {{ $t('tutor.clickMe') }}
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-gray-900 rotate-45"></div>
        </div>
      </div>
    </div>

    <!-- Chat Window -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <TutorChatWindow
        v-if="showChat"
        @close="showChat = false"
      />
    </Transition>
  </div>
</template>
