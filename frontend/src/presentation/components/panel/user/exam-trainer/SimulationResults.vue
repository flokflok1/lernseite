<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface TopicResult {
  topic: string
  earned: number
  total: number
}

interface Props {
  score: number
  totalPoints: number
  percentage: number
  passed: boolean
  questionCount: number
  topicResults?: TopicResult[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  backToOverview: []
  retry: []
}>()

const { t } = useI18n()

const barColor = computed(() => {
  if (props.percentage >= 70) return 'bg-emerald-500'
  if (props.percentage >= 50) return 'bg-amber-500'
  return 'bg-red-500'
})

const topicColor = (pct: number): string => {
  if (pct >= 70) return 'text-emerald-500'
  if (pct >= 50) return 'text-amber-500'
  return 'text-red-500'
}
</script>

<template>
  <div class="flex flex-col items-center justify-center py-10 px-6 text-center flex-1">
    <!-- Icon -->
    <div
      :class="['w-20 h-20 rounded-full flex items-center justify-center text-4xl mb-5',
               passed ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500']"
      role="img"
      :aria-label="passed ? t('panel.examTrainer.passed') : t('panel.examTrainer.failed')"
    >
      {{ passed ? '✓' : '✗' }}
    </div>

    <!-- Title -->
    <h2
      class="text-2xl font-bold mb-2"
      :class="passed ? 'text-emerald-500' : 'text-red-500'"
    >
      {{ passed ? t('panel.examTrainer.passed') : t('panel.examTrainer.failed') }}
    </h2>

    <!-- Score -->
    <div
      class="text-5xl font-extrabold my-3"
      :class="passed ? 'text-emerald-500' : 'text-red-500'"
    >
      {{ percentage }}%
    </div>

    <!-- Details -->
    <p class="text-sm text-[var(--color-text-secondary)] mb-6">
      {{ t('panel.examTrainer.simulation.resultDetails', {
        score, total: totalPoints, count: questionCount
      }) }}
    </p>

    <!-- Progress Bar -->
    <div class="w-[300px] h-2 bg-[var(--color-border)] rounded-full mb-6 overflow-hidden">
      <div
        :class="['h-full rounded-full transition-all duration-1000', barColor]"
        :style="{ width: percentage + '%' }"
      />
    </div>

    <!-- Topic Breakdown -->
    <div
      v-if="topicResults && topicResults.length > 0"
      class="grid grid-cols-2 gap-2 max-w-[400px] w-full mt-2 mb-6"
    >
      <div
        v-for="tr in topicResults"
        :key="tr.topic"
        class="text-left p-3 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]"
      >
        <div class="text-xs text-[var(--color-text-secondary)] mb-1 truncate">{{ tr.topic }}</div>
        <div class="text-base font-bold" :class="topicColor(tr.total > 0 ? Math.round(tr.earned / tr.total * 100) : 0)">
          {{ tr.total > 0 ? Math.round(tr.earned / tr.total * 100) : 0 }}%
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-3 mt-2">
      <button
        class="px-5 py-2.5 rounded-lg font-medium text-sm border border-[var(--color-border)]
               text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)] transition-colors"
        @click="emit('backToOverview')"
      >
        {{ t('panel.examTrainer.backToExams') }}
      </button>
      <button
        class="px-5 py-2.5 rounded-lg font-medium text-sm bg-blue-600 text-white
               hover:bg-blue-700 transition-colors"
        @click="emit('retry')"
      >
        {{ t('panel.examTrainer.simulation.retry') }}
      </button>
    </div>
  </div>
</template>
