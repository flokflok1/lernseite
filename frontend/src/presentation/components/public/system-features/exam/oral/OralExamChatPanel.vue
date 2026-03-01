<!--
  OralExamChatPanel - Chat history and input for oral examination
  Shows examiner/user messages, audio recording, and text input
-->

<template>
  <div class="space-y-6">
    <!-- Progress Bar -->
    <div class="bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
      <div
        class="bg-purple-600 h-2 rounded-full transition-all duration-300"
        :style="{ width: `${progressPercent}%` }"
      ></div>
    </div>

    <!-- Chat History -->
    <div class="space-y-4 max-h-[400px] overflow-y-auto p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[80%] rounded-2xl px-4 py-3"
          :class="message.role === 'user'
            ? 'bg-purple-600 text-white rounded-br-none'
            : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-none shadow-sm'"
        >
          <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs opacity-60">
              {{ new Date(message.timestamp).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) }}
            </span>
            <button
              v-if="message.audioUrl"
              @click="$emit('play-audio', message.audioUrl)"
              class="text-xs opacity-60 hover:opacity-100 flex items-center gap-1"
            >
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
              </svg>
              {{ $t('lesson.oral.play') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-white dark:bg-gray-700 rounded-2xl rounded-bl-none px-4 py-3">
          <div class="flex gap-1">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl">
      {{ error }}
    </div>

    <!-- Answer Input -->
    <div v-if="!isLoading" class="space-y-4">
      <!-- Audio Recording -->
      <div v-if="useAudio">
        <AudioRecorder
          ref="audioRecorderRef"
          :max-duration="120"
          @recorded="$emit('recorded', $event.blob, $event.duration)"
        />
      </div>

      <!-- Or Text Input -->
      <div class="relative">
        <span v-if="useAudio" class="absolute -top-3 left-4 px-2 bg-white dark:bg-gray-900 text-xs text-gray-500">
          {{ $t('lesson.oral.orWriteAnswer') }}
        </span>
        <textarea
          :value="userAnswer"
          @input="$emit('update:userAnswer', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          :placeholder="$t('lesson.oral.answerPlaceholder')"
          class="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
          @keydown.enter.ctrl="$emit('submit-text')"
        ></textarea>
        <button
          v-if="!useAudio || userAnswer.trim()"
          @click="$emit('submit-text')"
          :disabled="!userAnswer.trim() || isLoading"
          class="absolute bottom-3 right-3 p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * OralExamChatPanel
 *
 * Renders the chat history between examiner and user, plus audio recording
 * and text input controls for the oral examination flow.
 */
import { ref } from 'vue'
import { AudioRecorder } from '@/presentation/components/public/learning/audio'
import type { ExaminerMessage } from '@/application/composables/system-features/useOralExamination'

interface Props {
  messages: ExaminerMessage[]
  isLoading: boolean
  error: string | null
  userAnswer: string
  useAudio: boolean
  progressPercent: number
}

defineProps<Props>()

defineEmits<{
  'play-audio': [url: string]
  'recorded': [blob: Blob, duration: number]
  'update:userAnswer': [value: string]
  'submit-text': []
}>()

const audioRecorderRef = ref<InstanceType<typeof AudioRecorder> | null>(null)

function resetRecorder(): void {
  audioRecorderRef.value?.reset()
}

defineExpose({ resetRecorder })
</script>
