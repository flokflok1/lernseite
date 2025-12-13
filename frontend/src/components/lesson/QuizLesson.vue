<template>
  <div class="quiz-lesson bg-white rounded-lg shadow-sm">
    <!-- Loading State -->
    <div v-if="playerStore.quizLoading" class="p-8 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Quiz wird geladen...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="playerStore.quizError" class="p-8">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="text-4xl mb-3">❌</div>
        <h3 class="text-xl font-bold text-red-900 mb-2">Fehler</h3>
        <p class="text-red-700">{{ playerStore.quizError }}</p>
      </div>
    </div>

    <!-- Quiz Result View -->
    <div v-else-if="playerStore.isQuizCompleted && playerStore.quizResult" class="p-8">
      <QuizResult
        :result="playerStore.quizResult"
        :quiz="playerStore.quiz"
        @retry="handleRetry"
        @continue="handleContinue"
      />
    </div>

    <!-- Quiz Active View -->
    <div v-else-if="playerStore.isQuizLoaded && playerStore.quiz" class="flex flex-col h-full">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ playerStore.isExamMode ? '📋' : '📝' }}</span>
              <h3 class="text-2xl font-bold text-gray-900">
                {{ playerStore.quiz.title }}
              </h3>
            </div>
            <p v-if="playerStore.quiz.description" class="text-gray-600">
              {{ playerStore.quiz.description }}
            </p>
          </div>

          <!-- Exam Badge -->
          <div v-if="playerStore.isExamMode" class="ml-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
              🎓 Prüfung
            </span>
          </div>
        </div>

        <!-- Quiz Info Bar -->
        <div class="flex items-center gap-6 text-sm text-gray-700">
          <div class="flex items-center gap-2">
            <span>📊</span>
            <span>{{ playerStore.quizQuestions.length }} Fragen</span>
          </div>
          <div v-if="playerStore.quiz.passing_score_percentage" class="flex items-center gap-2">
            <span>🎯</span>
            <span>{{ playerStore.quiz.passing_score_percentage }}% zum Bestehen</span>
          </div>
          <div v-if="playerStore.quiz.time_limit_seconds" class="flex items-center gap-2">
            <span>⏱️</span>
            <span>{{ formatTime(playerStore.quiz.time_limit_seconds) }} Zeit</span>
          </div>
          <div class="flex items-center gap-2 ml-auto">
            <span>⏰</span>
            <span class="font-mono">{{ formatTime(playerStore.quizTimeSpent) }}</span>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="mt-4">
          <div class="flex items-center justify-between mb-1 text-xs text-gray-600">
            <span>Fortschritt</span>
            <span>{{ Math.round(playerStore.quizProgress) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all"
              :style="{ width: `${playerStore.quizProgress}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Questions List -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <div
          v-for="(question, index) in playerStore.quizQuestions"
          :key="question.question_id"
          class="border border-gray-200 rounded-lg p-5 bg-white"
          :class="{
            'border-primary-300 bg-primary-50': playerStore.quizAnswers[question.question_id]
          }"
        >
          <!-- Question Header -->
          <div class="flex items-start gap-3 mb-4">
            <div class="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm font-semibold text-gray-700">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <h4 class="text-lg font-semibold text-gray-900 mb-1">
                {{ question.question_text }}
              </h4>
              <div class="flex items-center gap-3 text-xs text-gray-500">
                <span class="px-2 py-0.5 bg-gray-100 rounded">{{ questionTypeLabel(question.type) }}</span>
                <span>{{ question.points }} {{ question.points === 1 ? 'Punkt' : 'Punkte' }}</span>
              </div>
            </div>
          </div>

          <!-- Question Input (based on type) -->
          <div class="ml-11">
            <!-- Single Choice -->
            <SingleChoiceQuestion
              v-if="question.type === 'single_choice'"
              :question="question"
              :model-value="playerStore.quizAnswers[question.question_id]"
              @update:model-value="(answer) => handleAnswerUpdate(question.question_id, answer)"
            />

            <!-- Multiple Choice -->
            <MultipleChoiceQuestion
              v-else-if="question.type === 'multiple_choice'"
              :question="question"
              :model-value="playerStore.quizAnswers[question.question_id]"
              @update:model-value="(answer) => handleAnswerUpdate(question.question_id, answer)"
            />

            <!-- True/False -->
            <TrueFalseQuestion
              v-else-if="question.type === 'true_false'"
              :question="question"
              :model-value="playerStore.quizAnswers[question.question_id]"
              @update:model-value="(answer) => handleAnswerUpdate(question.question_id, answer)"
            />

            <!-- Fill Blank (Future) -->
            <div v-else class="p-4 bg-gray-50 rounded border border-gray-200 text-center text-gray-500">
              Fragetyp "{{ question.type }}" wird noch nicht unterstützt
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Footer -->
      <div class="p-6 border-t border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600">
            <span v-if="playerStore.allQuestionsAnswered" class="text-green-600 font-medium">
              ✓ Alle Fragen beantwortet
            </span>
            <span v-else class="text-yellow-600 font-medium">
              ⚠️ {{ unansweredCount }} Frage(n) noch offen
            </span>
          </div>

          <Button
            variant="primary"
            size="lg"
            :disabled="!playerStore.allQuestionsAnswered || playerStore.quizSubmitting"
            :loading="playerStore.quizSubmitting"
            @click="handleSubmit"
          >
            <span v-if="playerStore.quizSubmitting">Wird eingereicht...</span>
            <span v-else>{{ playerStore.isExamMode ? 'Prüfung abgeben' : 'Quiz abgeben' }}</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Empty State (no quiz loaded) -->
    <div v-else class="p-8 text-center">
      <div class="text-6xl mb-4">📝</div>
      <h3 class="text-2xl font-bold text-gray-900 mb-2">Kein Quiz verfügbar</h3>
      <p class="text-gray-600">Für diese Lektion ist kein Quiz vorhanden.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { usePlayerStore } from '@/store/player.store'
import type { Lesson, QuizAnswerSubmission } from '@/api/player.api'
import Button from '@/components/ui/Button.vue'
import QuizResult from './QuizResult.vue'
import SingleChoiceQuestion from './quiz/SingleChoiceQuestion.vue'
import MultipleChoiceQuestion from './quiz/MultipleChoiceQuestion.vue'
import TrueFalseQuestion from './quiz/TrueFalseQuestion.vue'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  lesson: Lesson
  courseId: string  // UUID
  moduleId: string  // UUID (chapterId)
}

interface Emits {
  (e: 'completed'): void
  (e: 'continue'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// Store
// ============================================================================

const playerStore = usePlayerStore()

// ============================================================================
// Computed
// ============================================================================

const unansweredCount = computed(() => {
  if (!playerStore.quiz) return 0
  return playerStore.quizQuestions.length - Object.keys(playerStore.quizAnswers).length
})

// ============================================================================
// Methods
// ============================================================================

const questionTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    single_choice: 'Single Choice',
    multiple_choice: 'Multiple Choice',
    true_false: 'Richtig/Falsch',
    fill_blank: 'Lückentext',
    matching: 'Zuordnung'
  }
  return labels[type] || type
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleAnswerUpdate = (questionId: number, answer: QuizAnswerSubmission): void => {
  playerStore.updateQuizAnswer(questionId, answer)
}

const handleSubmit = async (): Promise<void> => {
  if (!playerStore.allQuestionsAnswered) {
    return
  }

  try {
    await playerStore.submitQuiz(props.courseId, props.moduleId, props.lesson.lesson_id)
    emit('completed')
  } catch (err) {
    console.error('Failed to submit quiz:', err)
  }
}

const handleRetry = (): void => {
  playerStore.resetQuizState()
  loadQuiz()
}

const handleContinue = (): void => {
  emit('continue')
}

const loadQuiz = async (): Promise<void> => {
  try {
    await playerStore.loadQuizForLesson(props.lesson.lesson_id)
  } catch (err) {
    console.error('Failed to load quiz:', err)
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadQuiz()
})

onUnmounted(() => {
  // Don't reset quiz state on unmount - preserve for navigation
})
</script>

<style scoped>
.quiz-lesson {
  min-height: 600px;
}
</style>
