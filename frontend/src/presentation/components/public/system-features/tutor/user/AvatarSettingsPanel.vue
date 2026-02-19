<script setup lang="ts">
/**
 * AvatarSettingsPanel - Settings panel for avatar customization
 *
 * Allows selecting avatar style, personality, position,
 * and toggling TTS, lip-sync, auto-expand, and whiteboard options.
 */

import { useAvatarStore, PRESET_AVATARS } from '@/application/stores/modules/ui/avatar.store'
import { useTutorStore, DEFAULT_PERSONALITIES } from '@/application/stores/modules/learning/tutor.store'

const avatarStore = useAvatarStore()
const tutorStore = useTutorStore()

const emit = defineEmits<{
  close: []
}>()

defineProps<{
  show: boolean
}>()

function selectAvatar(presetId: string): void {
  avatarStore.selectPreset(presetId)
}
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 translate-x-4"
    enter-to-class="opacity-100 translate-x-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0 translate-x-4"
  >
    <div
      v-if="show"
      class="fixed z-50 w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
      :class="[
        avatarStore.settings.position === 'bottom-right' ? 'right-6 bottom-44' : 'left-6 bottom-44'
      ]"
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center justify-between">
        <h3 class="text-white font-semibold">Avatar Einstellungen</h3>
        <button @click="emit('close')" class="p-1 rounded hover:bg-white/20 text-white">
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
</template>
