<script setup lang="ts">
/**
 * OralExplanationLesson - LM24 Muendliche Erklaerung
 *
 * Interactive oral examination simulation where learners explain
 * concepts verbally and receive AI-powered feedback.
 *
 * Features:
 * - Audio recording with Speech-to-Text
 * - AI examiner simulation
 * - Real-time transcription
 * - Detailed feedback on oral explanations
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import OralExamChatPanel from '@/presentation/components/public/system-features/exam/OralExamChatPanel.vue'
import OralExamFeedbackPanel from '@/presentation/components/public/system-features/exam/OralExamFeedbackPanel.vue'
import { useOralExamination } from '@/application/composables/system-features/useOralExamination'
import type { OralMethodData } from '@/application/composables/system-features/useOralExamination'

const { t } = useI18n()

// Props
const props = defineProps<{
  lesson: {
    lesson_id: string
    title: string
    content?: {
      data?: OralMethodData
    }
  }
  courseId: string
  chapterId: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'completed'): void
  (e: 'continue'): void
}>()

// Method data with defaults
const methodData = computed((): OralMethodData => props.lesson.content?.data || {
  topic: t('lesson.oral.defaultTopic'),
  format: 'interview',
  examiner_persona: 'formal',
  difficulty: 'medium',
  topic_blocks: [],
  duration_minutes: 15,
  allow_thinking_time: true,
  allow_retry: false,
  use_audio: true,
  show_transcript: true,
  criteria: {
    content: true,
    structure: true,
    clarity: true,
    reactions: true
  }
})

// Composable for exam logic
const {
  phase,
  currentBlockIndex,
  isLoading,
  error,
  examinerMessages,
  userAnswer,
  transcription,
  feedbackResult,
  totalBlocks,
  progressPercent,
  examinerPersonaLabel,
  startExam,
  handleRecording,
  handleTextAnswer,
  nextBlock,
  playAudio,
  retryAnswer
} = useOralExamination(methodData, () => emit('completed'))

// Refs for sub-component
const chatPanelRef = ref<InstanceType<typeof OralExamChatPanel> | null>(null)

function handleRetry(): void {
  retryAnswer()
  chatPanelRef.value?.resetRecorder()
}
</script>

<template>
  <div class="oral-explanation-lesson">
    <!-- Intro Phase -->
    <div v-if="phase === 'intro'" class="text-center py-8">
      <div class="max-w-2xl mx-auto">
        <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
          <svg class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('lesson.oral.title') }}
        </h2>

        <p class="text-gray-600 dark:text-gray-300 mb-6">
          {{ methodData.topic }}
        </p>

        <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-6 text-left">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ $t('lesson.oral.examDetails') }}:</h3>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.examiner') }}: {{ examinerPersonaLabel }}
            </li>
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.topicBlocks') }}: {{ totalBlocks }}
            </li>
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.duration') }}: {{ $t('lesson.oral.durationValue', { minutes: methodData.duration_minutes }) }}
            </li>
            <li v-if="methodData.use_audio" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              {{ $t('lesson.oral.audioEnabled') }}
            </li>
          </ul>
        </div>

        <button
          @click="startExam"
          :disabled="isLoading"
          class="px-8 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          {{ $t('lesson.oral.startExam') }}
        </button>
      </div>
    </div>

    <!-- Question/Answer Phase -->
    <OralExamChatPanel
      v-else-if="phase === 'question' || phase === 'answer'"
      ref="chatPanelRef"
      :messages="examinerMessages"
      :is-loading="isLoading"
      :error="error"
      :user-answer="userAnswer"
      :use-audio="methodData.use_audio"
      :progress-percent="progressPercent"
      @play-audio="playAudio"
      @recorded="handleRecording"
      @update:user-answer="userAnswer = $event"
      @submit-text="handleTextAnswer"
    />

    <!-- Feedback Phase -->
    <OralExamFeedbackPanel
      v-else-if="phase === 'feedback'"
      :feedback="feedbackResult"
      :transcription="transcription"
      :show-transcript="methodData.show_transcript"
      :allow-retry="methodData.allow_retry"
      :is-last-block="currentBlockIndex >= totalBlocks - 1"
      @retry="handleRetry"
      @next="nextBlock"
    />

    <!-- Complete Phase -->
    <div v-else-if="phase === 'complete'" class="text-center py-8">
      <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
        <svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        {{ $t('lesson.oral.examCompleted') }}
      </h2>

      <div v-if="examinerMessages.length > 0" class="max-w-2xl mx-auto mb-6">
        <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 text-left">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ $t('lesson.oral.finalEvaluation') }}:</h3>
          <p class="text-gray-600 dark:text-gray-300">
            {{ examinerMessages[examinerMessages.length - 1].content }}
          </p>
        </div>
      </div>

      <button
        @click="emit('continue')"
        class="px-8 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors"
      >
        {{ $t('common.continue') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.oral-explanation-lesson {
  min-height: 400px;
}
</style>
