<!--
  OralExamFeedbackPanel - Displays feedback results for oral examination
  Shows score, covered/missing points, and suggestions
-->

<template>
  <div class="space-y-6">
    <!-- Transcription -->
    <div v-if="showTranscript && transcription" class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
      <h3 class="font-semibold text-gray-900 dark:text-white mb-2">{{ $t('lesson.oral.yourAnswerTranscript') }}:</h3>
      <p class="text-gray-600 dark:text-gray-300 text-sm">{{ transcription }}</p>
    </div>

    <!-- Feedback Result -->
    <div v-if="feedback" class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-900 dark:text-white">{{ $t('lesson.oral.evaluation') }}</h3>
        <div class="flex items-center gap-2">
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center font-bold text-xl"
            :class="scoreColorClass"
          >
            {{ feedback.score }}%
          </div>
        </div>
      </div>

      <p class="text-gray-600 dark:text-gray-300 mb-4">{{ feedback.feedback }}</p>

      <!-- Covered Points -->
      <div v-if="feedback.covered_points.length > 0" class="mb-4">
        <h4 class="text-sm font-medium text-green-700 dark:text-green-400 mb-2">{{ $t('lesson.oral.coveredPoints') }}:</h4>
        <ul class="space-y-1">
          <li v-for="point in feedback.covered_points" :key="point" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
            <svg class="w-4 h-4 text-green-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            {{ point }}
          </li>
        </ul>
      </div>

      <!-- Missing Points -->
      <div v-if="feedback.missing_points.length > 0" class="mb-4">
        <h4 class="text-sm font-medium text-red-700 dark:text-red-400 mb-2">{{ $t('lesson.oral.missingPoints') }}:</h4>
        <ul class="space-y-1">
          <li v-for="point in feedback.missing_points" :key="point" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
            <svg class="w-4 h-4 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
            {{ point }}
          </li>
        </ul>
      </div>

      <!-- Suggestions -->
      <div v-if="feedback.suggestions.length > 0">
        <h4 class="text-sm font-medium text-blue-700 dark:text-blue-400 mb-2">{{ $t('lesson.oral.suggestions') }}:</h4>
        <ul class="space-y-1">
          <li v-for="suggestion in feedback.suggestions" :key="suggestion" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
            <svg class="w-4 h-4 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>
            {{ suggestion }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-center gap-4">
      <button
        v-if="allowRetry"
        @click="$emit('retry')"
        class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        {{ $t('lesson.oral.retryAnswer') }}
      </button>
      <button
        @click="$emit('next')"
        class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
      >
        {{ isLastBlock ? $t('lesson.oral.completeExam') : $t('lesson.oral.nextBlock') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * OralExamFeedbackPanel
 *
 * Displays the feedback results after an oral examination answer,
 * including score, covered/missing points, suggestions, and navigation.
 */
import { computed } from 'vue'
import type { FeedbackResult } from '@/application/composables/system-features/useOralExamination'

interface Props {
  feedback: FeedbackResult | null
  transcription: string
  showTranscript: boolean
  allowRetry: boolean
  isLastBlock: boolean
}

const props = defineProps<Props>()

defineEmits<{
  retry: []
  next: []
}>()

const scoreColorClass = computed((): string => {
  if (!props.feedback) return ''
  if (props.feedback.score >= 70) return 'bg-green-100 text-green-700'
  if (props.feedback.score >= 50) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
})
</script>
