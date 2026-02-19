<script setup lang="ts">
/**
 * AudioRecorderControls - Button controls for the AudioRecorder
 *
 * Extracted from AudioRecorder.vue to stay under 500 LOC limit.
 * Renders record/stop/pause/play/download/reset buttons based on recording state.
 */
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  isRecording: boolean
  isPaused: boolean
  isPlaying: boolean
  audioUrl: string | null
  showPlayback: boolean
  showDownload: boolean
}>()

const emit = defineEmits<{
  (e: 'start'): void
  (e: 'stop'): void
  (e: 'toggle-pause'): void
  (e: 'play'): void
  (e: 'stop-playback'): void
  (e: 'download'): void
  (e: 'reset'): void
}>()
</script>

<template>
  <div class="flex items-center justify-center gap-4">
    <!-- Record Button -->
    <button
      v-if="!isRecording && !audioUrl"
      @click="emit('start')"
      class="w-16 h-16 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
      :title="t('common.audio.startRecording')"
    >
      <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="8" />
      </svg>
    </button>

    <!-- Pause Button -->
    <button
      v-if="isRecording"
      @click="emit('toggle-pause')"
      class="w-12 h-12 rounded-full bg-yellow-500 hover:bg-yellow-600 text-white flex items-center justify-center transition-colors"
      :title="isPaused ? t('common.audio.resume') : t('common.audio.pause')"
    >
      <svg v-if="isPaused" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M8 5v14l11-7z" />
      </svg>
      <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
      </svg>
    </button>

    <!-- Stop Button -->
    <button
      v-if="isRecording"
      @click="emit('stop')"
      class="w-16 h-16 rounded-full bg-gray-700 hover:bg-gray-800 text-white flex items-center justify-center transition-colors shadow-lg"
      :title="t('common.audio.stopRecording')"
    >
      <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <rect x="6" y="6" width="12" height="12" rx="2" />
      </svg>
    </button>

    <!-- Playback Controls (after recording) -->
    <template v-if="audioUrl && showPlayback">
      <button
        @click="isPlaying ? emit('stop-playback') : emit('play')"
        class="w-12 h-12 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-colors"
        :title="isPlaying ? t('common.audio.stop') : t('common.audio.play')"
      >
        <svg v-if="isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="4" width="4" height="16" rx="1" />
          <rect x="14" y="4" width="4" height="16" rx="1" />
        </svg>
        <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z" />
        </svg>
      </button>

      <!-- Download Button -->
      <button
        v-if="showDownload"
        @click="emit('download')"
        class="w-12 h-12 rounded-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center transition-colors"
        :title="t('common.audio.download')"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      </button>

      <!-- Reset Button -->
      <button
        @click="emit('reset')"
        class="w-12 h-12 rounded-full bg-gray-500 hover:bg-gray-600 text-white flex items-center justify-center transition-colors"
        :title="t('common.audio.newRecording')"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </template>
  </div>
</template>
