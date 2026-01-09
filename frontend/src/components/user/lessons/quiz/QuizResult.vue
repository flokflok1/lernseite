<template>
  <div class="quiz-result">
    <!-- Result Header -->
    <div class="text-center mb-8">
      <div class="text-6xl mb-4">
        {{ result.passed ? '🎉' : '😔' }}
      </div>
      <h2 class="text-3xl font-bold text-gray-900 mb-2">
        {{ result.passed ? $t('lesson.quiz.result.passed') : $t('lesson.quiz.result.failed') }}
      </h2>
      <p class="text-gray-600">
        {{ result.is_exam ? $t('lesson.quiz.result.examCompleted') : $t('lesson.quiz.result.quizCompleted') }}
      </p>
    </div>

    <!-- Score Card -->
    <div class="bg-gradient-to-br from-blue-50 to-purple-50 border-2 rounded-xl p-8 mb-8"
      :class="{
        'border-green-300': result.passed,
        'border-red-300': !result.passed
      }"
    >
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <!-- Score Percentage -->
        <div class="text-center">
          <div class="text-4xl font-bold mb-1"
            :class="{
              'text-green-600': result.passed,
              'text-red-600': !result.passed
            }"
          >
            {{ result.score_percentage }}%
          </div>
          <div class="text-sm text-gray-600">{{ $t('lesson.quiz.result.achieved') }}</div>
        </div>

        <!-- Points -->
        <div class="text-center">
          <div class="text-4xl font-bold text-gray-900 mb-1">
            {{ result.total_points }}/{{ result.max_points }}
          </div>
          <div class="text-sm text-gray-600">{{ $t('lesson.quiz.result.pointsLabel') }}</div>
        </div>

        <!-- Correct Answers -->
        <div class="text-center">
          <div class="text-4xl font-bold text-gray-900 mb-1">
            {{ correctAnswersCount }}/{{ result.question_results.length }}
          </div>
          <div class="text-sm text-gray-600">{{ $t('lesson.quiz.result.correct') }}</div>
        </div>

        <!-- Time Spent -->
        <div class="text-center">
          <div class="text-4xl font-bold text-gray-900 mb-1">
            {{ formatTime(result.time_spent_seconds) }}
          </div>
          <div class="text-sm text-gray-600">{{ $t('lesson.quiz.result.timeLabel') }}</div>
        </div>
      </div>

      <!-- Passing Score Info -->
      <div v-if="quiz?.passing_score_percentage" class="mt-6 pt-6 border-t border-gray-200 text-center">
        <p class="text-sm text-gray-600">
          <span class="font-medium">{{ $t('lesson.quiz.result.requiredToPass') }}</span>
          {{ quiz.passing_score_percentage }}%
        </p>
      </div>
    </div>

    <!-- Question Results (if allowed to show) -->
    <div v-if="quiz?.show_correct_answers && result.question_results.length > 0" class="mb-8">
      <h3 class="text-xl font-bold text-gray-900 mb-4">{{ $t('lesson.quiz.result.detailedResults') }}</h3>

      <div class="space-y-4">
        <div
          v-for="(questionResult, index) in result.question_results"
          :key="questionResult.question_id"
          class="border rounded-lg p-5"
          :class="{
            'border-green-200 bg-green-50': questionResult.is_correct,
            'border-red-200 bg-red-50': !questionResult.is_correct
          }"
        >
          <!-- Question Header -->
          <div class="flex items-start gap-3 mb-3">
            <div
              class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
              :class="{
                'bg-green-500': questionResult.is_correct,
                'bg-red-500': !questionResult.is_correct
              }"
            >
              {{ questionResult.is_correct ? '✓' : '✗' }}
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 mb-1">
                {{ $t('lesson.quiz.result.question') }} {{ index + 1 }}
              </h4>
              <p class="text-sm text-gray-700">
                {{ getQuestionText(questionResult.question_id) }}
              </p>
            </div>
            <div class="text-sm font-medium"
              :class="{
                'text-green-700': questionResult.is_correct,
                'text-red-700': !questionResult.is_correct
              }"
            >
              {{ questionResult.earned_points }}/{{ questionResult.max_points }} {{ $t('lesson.quiz.result.pointsLabel') }}
            </div>
          </div>

          <!-- User's Answer -->
          <div class="ml-11 space-y-2">
            <div class="text-sm">
              <span class="font-medium text-gray-700">{{ $t('lesson.quiz.result.yourAnswer') }}</span>
              <span class="ml-2 text-gray-900">
                {{ formatUserAnswer(questionResult.user_answer) }}
              </span>
            </div>

            <!-- Correct Answer (if wrong) -->
            <div v-if="!questionResult.is_correct && questionResult.correct_answer" class="text-sm">
              <span class="font-medium text-gray-700">{{ $t('lesson.quiz.result.correctAnswer') }}</span>
              <span class="ml-2 text-green-700 font-medium">
                {{ formatCorrectAnswer(questionResult.correct_answer) }}
              </span>
            </div>

            <!-- Explanation -->
            <div v-if="questionResult.explanation" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-900">
              <span class="font-medium">💡 {{ $t('lesson.quiz.result.explanation') }}</span>
              <p class="mt-1">{{ questionResult.explanation }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Exam Mode Message -->
    <div v-else-if="result.is_exam" class="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <p class="text-sm text-yellow-800">
        <strong>{{ $t('lesson.ai.hint') }}:</strong> {{ $t('lesson.quiz.result.examNote') }}
      </p>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-4 justify-center">
      <!-- Retry Button (if allowed) -->
      <Button
        v-if="quiz?.allow_retry && !result.passed"
        variant="outline"
        size="lg"
        @click="$emit('retry')"
      >
        🔄 {{ $t('lesson.quiz.result.retry') }}
      </Button>

      <!-- Continue Button -->
      <Button
        variant="primary"
        size="lg"
        @click="$emit('continue')"
      >
        {{ result.passed ? $t('lesson.quiz.result.continue') : $t('lesson.quiz.result.backToOverview') }}
      </Button>
    </div>

    <!-- Attempt History -->
    <div v-if="result.is_exam" class="mt-8 pt-8 border-t border-gray-200">
      <p class="text-xs text-gray-500 text-center">
        {{ $t('lesson.quiz.result.attemptCompleted', { date: formatDate(result.submitted_at) }) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { QuizResult, QuizData, QuizAnswerSubmission } from '@/api/player.api'
import Button from '@/components/shared/ui/Button.vue'

const { t } = useI18n()

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  result: QuizResult
  quiz: QuizData | null
}

interface Emits {
  (e: 'retry'): void
  (e: 'continue'): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

// ============================================================================
// Computed
// ============================================================================

const correctAnswersCount = computed(() => {
  return props.result.question_results.filter(q => q.is_correct).length
})

// ============================================================================
// Methods
// ============================================================================

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getQuestionText = (questionId: number): string => {
  const question = props.quiz?.questions.find(q => q.question_id === questionId)
  return question?.question_text || t('lesson.quiz.result.questionNotFound')
}

const formatUserAnswer = (answer: QuizAnswerSubmission): string => {
  if (answer.answer_boolean !== undefined) {
    return answer.answer_boolean ? t('lesson.quiz.result.true') : t('lesson.quiz.result.false')
  }

  if (answer.answer_text) {
    return answer.answer_text
  }

  if (answer.selected_option_ids && answer.selected_option_ids.length > 0) {
    return answer.selected_option_ids
      .map(id => getOptionText(answer.question_id, id))
      .filter(Boolean)
      .join(', ')
  }

  return t('lesson.quiz.result.noAnswer')
}

const formatCorrectAnswer = (correctAnswer: any): string => {
  if (typeof correctAnswer === 'boolean') {
    return correctAnswer ? t('lesson.quiz.result.true') : t('lesson.quiz.result.false')
  }

  if (typeof correctAnswer === 'string') {
    return correctAnswer
  }

  if (Array.isArray(correctAnswer)) {
    return correctAnswer.join(', ')
  }

  return String(correctAnswer)
}

const getOptionText = (questionId: number, optionId: string | number): string => {
  const question = props.quiz?.questions.find(q => q.question_id === questionId)
  const option = question?.options?.find(o => o.id === optionId)
  return option?.text || String(optionId)
}
</script>
