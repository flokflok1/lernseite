<script setup lang="ts">
/**
 * ExamQuestionPlayer Component
 *
 * Renders the active exam attempt: question display, answer input
 * (multiple choice or free text), and navigation between questions.
 */

import { computed } from 'vue'
import type { ExamQuestion } from '@/infrastructure/api/clients/panel/user/exam/examSimulation.api'

interface Props {
  questions: ExamQuestion[]
  currentQuestionIndex: number
  userAnswers: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:currentQuestionIndex': [index: number]
  'update:userAnswers': [answers: Record<string, string>]
  submit: []
}>()

function selectAnswer(questionId: string, answer: string): void {
  emit('update:userAnswers', { ...props.userAnswers, [questionId]: answer })
}

function updateTextAnswer(questionId: string, value: string): void {
  emit('update:userAnswers', { ...props.userAnswers, [questionId]: value })
}

function goToPrevious(): void {
  emit('update:currentQuestionIndex', props.currentQuestionIndex - 1)
}

function goToNext(): void {
  emit('update:currentQuestionIndex', props.currentQuestionIndex + 1)
}

const currentQuestion = computed(() => props.questions[props.currentQuestionIndex])
</script>

<template>
  <div>
    <!-- Progress Bar -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <span class="text-sm text-gray-500">
          {{ $t('examSimulation.exam.questionOf', {
            current: currentQuestionIndex + 1,
            total: questions.length
          }) }}
        </span>
        <div class="h-2 w-48 bg-gray-200 rounded-full mt-1">
          <div
            class="h-2 bg-blue-600 rounded-full"
            :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"
          ></div>
        </div>
      </div>
      <span class="text-sm font-medium">
        {{ currentQuestion?.points }} {{ $t('examSimulation.exam.points') }}
      </span>
    </div>

    <!-- Question -->
    <div class="mb-6">
      <div class="mb-2 flex items-center gap-2">
        <span class="text-xs bg-gray-100 px-2 py-1 rounded">
          {{ currentQuestion?.topic }}
        </span>
        <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {{ currentQuestion?.type === 'mc' ? 'Multiple Choice' : currentQuestion?.type }}
        </span>
      </div>
      <p class="text-lg">{{ currentQuestion?.question }}</p>
    </div>

    <!-- Multiple Choice Options -->
    <div
      v-if="currentQuestion?.type === 'mc'"
      class="space-y-3 mb-6"
    >
      <button
        v-for="option in currentQuestion?.options"
        :key="option"
        @click="selectAnswer(currentQuestion.question_id, option.charAt(0))"
        :class="[
          'w-full text-left p-4 border-2 rounded-lg transition-colors',
          userAnswers[currentQuestion?.question_id] === option.charAt(0)
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        {{ option }}
      </button>
    </div>

    <!-- Free Text Answer -->
    <div v-else class="mb-6">
      <textarea
        :value="userAnswers[currentQuestion?.question_id]"
        @input="updateTextAnswer(currentQuestion?.question_id, ($event.target as HTMLTextAreaElement).value)"
        rows="4"
        class="w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        :placeholder="$t('examSimulation.exam.yourAnswer')"
      ></textarea>
    </div>

    <!-- Navigation -->
    <div class="flex items-center justify-between">
      <button
        @click="goToPrevious"
        :disabled="currentQuestionIndex === 0"
        class="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
      >
        {{ $t('examSimulation.exam.back') }}
      </button>

      <div class="flex gap-2">
        <button
          v-if="currentQuestionIndex < questions.length - 1"
          @click="goToNext"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {{ $t('examSimulation.exam.next') }}
        </button>
        <button
          v-else
          @click="emit('submit')"
          class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          {{ $t('examSimulation.exam.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>
