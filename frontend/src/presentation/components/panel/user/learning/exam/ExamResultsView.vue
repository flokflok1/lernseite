<script setup lang="ts">
/**
 * ExamResultsView Component
 *
 * Displays exam attempt results: overall score, pass/fail status,
 * time spent, and per-topic breakdown. Provides actions to repeat
 * the same exam or generate a new one with configurable options.
 */
import { ref } from 'vue'

interface Props {
  attemptResult: {
    passed: boolean
    percentage: number
    score: number
    max_score: number
    time_spent_seconds: number
    results_by_topic: Record<string, {
      correct: number
      total: number
      points: number
      max_points: number
    }>
  }
}

export interface NewExamOptions {
  focusWeakness: boolean
  difficulty: string
}

defineProps<Props>()

const emit = defineEmits<{
  backToOverview: []
  repeatExam: []
  generateNewExam: [options: NewExamOptions]
}>()

const showOptions = ref(false)
const focusWeakness = ref(false)
const difficulty = ref('realistic')

const difficultyOptions = [
  { value: 'easy', labelKey: 'examSimulation.newExam.difficultyEasy' },
  { value: 'medium', labelKey: 'examSimulation.newExam.difficultyMedium' },
  { value: 'hard', labelKey: 'examSimulation.newExam.difficultyHard' },
  { value: 'realistic', labelKey: 'examSimulation.newExam.difficultyRealistic' },
]

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleGenerateNew() {
  emit('generateNewExam', {
    focusWeakness: focusWeakness.value,
    difficulty: difficulty.value,
  })
}
</script>

<template>
  <div>
    <!-- Score Display -->
    <div class="text-center mb-8">
      <div
        :class="[
          'inline-block text-6xl font-bold mb-2',
          attemptResult.passed ? 'text-green-600' : 'text-red-600'
        ]"
      >
        {{ Math.round(attemptResult.percentage) }}%
      </div>
      <p class="text-xl">
        {{ attemptResult.passed ? $t('examSimulation.results.passed') : $t('examSimulation.results.notPassed') }}
      </p>
      <p class="text-gray-500 mt-2">
        {{ attemptResult.score }} / {{ attemptResult.max_score }} {{ $t('examSimulation.exam.points') }} |
        {{ formatTime(attemptResult.time_spent_seconds) }}
      </p>
    </div>

    <!-- Results by Topic -->
    <div class="mb-6">
      <h4 class="font-medium mb-3">{{ $t('examSimulation.results.resultsByTopic') }}</h4>
      <div class="space-y-2">
        <div
          v-for="(data, topic) in attemptResult.results_by_topic"
          :key="topic"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <span>{{ topic }}</span>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">
              {{ data.correct }} / {{ data.total }} {{ $t('examSimulation.results.correct') }}
            </span>
            <span class="font-medium">
              {{ data.points }} / {{ data.max_points }} {{ $t('examSimulation.exam.points') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="space-y-3 mb-4">
      <button
        @click="emit('repeatExam')"
        class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        {{ $t('examSimulation.newExam.repeatSame') }}
      </button>
      <button
        @click="showOptions = !showOptions"
        class="w-full py-3 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
      >
        {{ $t('examSimulation.newExam.generateNew') }}
      </button>
    </div>

    <!-- New Exam Options Panel -->
    <div
      v-if="showOptions"
      class="mb-4 p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]"
    >
      <h4 class="font-medium mb-4">{{ $t('examSimulation.newExam.options') }}</h4>

      <!-- Focus Weakness Toggle -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <span class="text-sm font-medium">{{ $t('examSimulation.newExam.focusWeakness') }}</span>
          <p class="text-xs text-gray-500 mt-0.5">
            {{ $t('examSimulation.newExam.focusWeaknessHint') }}
          </p>
        </div>
        <button
          @click="focusWeakness = !focusWeakness"
          :class="[
            'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
            focusWeakness ? 'bg-blue-600' : 'bg-gray-300'
          ]"
          role="switch"
          :aria-checked="focusWeakness"
        >
          <span
            :class="[
              'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
              focusWeakness ? 'translate-x-6' : 'translate-x-1'
            ]"
          />
        </button>
      </div>

      <!-- Difficulty Dropdown -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-1">
          {{ $t('examSimulation.newExam.difficulty') }}
        </label>
        <select
          v-model="difficulty"
          class="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]
                 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option
            v-for="opt in difficultyOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ $t(opt.labelKey) }}
          </option>
        </select>
      </div>

      <!-- Generate Button -->
      <button
        @click="handleGenerateNew"
        class="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        {{ $t('examSimulation.newExam.generateButton') }}
      </button>
    </div>

    <button
      @click="emit('backToOverview')"
      class="w-full py-3 border rounded-lg hover:bg-gray-50 text-[var(--color-text-secondary)]"
    >
      {{ $t('examSimulation.results.backToOverview') }}
    </button>
  </div>
</template>
