<script setup lang="ts">
/**
 * ExamResultsView Component
 *
 * Displays exam attempt results: overall score, pass/fail status,
 * time spent, and per-topic breakdown.
 */

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

defineProps<Props>()

const emit = defineEmits<{
  backToOverview: []
}>()

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
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

    <button
      @click="emit('backToOverview')"
      class="w-full py-3 border rounded-lg hover:bg-gray-50"
    >
      {{ $t('examSimulation.results.backToOverview') }}
    </button>
  </div>
</template>
