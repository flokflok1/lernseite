<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AttemptHistoryEntry } from '@/infrastructure/api/clients/panel/user/exams'
import { trainerGetHistory } from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

const attempts = ref<AttemptHistoryEntry[]>([])
const isLoading = ref(true)

const reversedAttempts = computed(() => [...attempts.value].reverse())

const chartMax = computed(() =>
  Math.max(100, ...attempts.value.map(a => a.percentage ?? 0))
)

const avgScore = computed(() => {
  const valid = attempts.value.filter(a => a.percentage != null)
  if (valid.length === 0) return 0
  return Math.round(valid.reduce((s, a) => s + (a.percentage ?? 0), 0) / valid.length)
})

const passRate = computed(() => {
  const valid = attempts.value.filter(a => a.passed != null)
  if (valid.length === 0) return 0
  return Math.round(valid.filter(a => a.passed).length / valid.length * 100)
})

const trend = computed(() => {
  if (attempts.value.length < 2) return 'neutral'
  const recent = attempts.value.slice(0, 3)
  const older = attempts.value.slice(3, 6)
  if (older.length === 0) return 'neutral'
  const recentAvg = recent.reduce((s, a) => s + (a.percentage ?? 0), 0) / recent.length
  const olderAvg = older.reduce((s, a) => s + (a.percentage ?? 0), 0) / older.length
  if (recentAvg > olderAvg + 5) return 'up'
  if (recentAvg < olderAvg - 5) return 'down'
  return 'neutral'
})

const barColor = (pct: number | null): string => {
  if (pct == null) return 'bg-gray-500'
  if (pct >= 70) return 'bg-emerald-500'
  if (pct >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
}

onMounted(async () => {
  try {
    attempts.value = await trainerGetHistory(20)
  } catch {
    // silently fail — dashboard is non-critical
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div>
    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
    </div>

    <!-- Empty State -->
    <div v-else-if="attempts.length === 0" class="text-center py-8 text-[var(--color-text-secondary)]">
      {{ t('panel.examTrainer.progress.noData') }}
    </div>

    <div v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-3 gap-3 mb-6">
        <div class="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
          <div class="text-xs text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examTrainer.progress.avgScore') }}
          </div>
          <div class="text-2xl font-bold" :class="avgScore >= 50 ? 'text-emerald-500' : 'text-red-500'">
            {{ avgScore }}%
          </div>
        </div>
        <div class="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
          <div class="text-xs text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examTrainer.progress.passRate') }}
          </div>
          <div class="text-2xl font-bold" :class="passRate >= 50 ? 'text-emerald-500' : 'text-amber-500'">
            {{ passRate }}%
          </div>
        </div>
        <div class="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
          <div class="text-xs text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examTrainer.progress.trend') }}
          </div>
          <div class="text-2xl font-bold">
            <span v-if="trend === 'up'" class="text-emerald-500">↑</span>
            <span v-else-if="trend === 'down'" class="text-red-500">↓</span>
            <span v-else class="text-[var(--color-text-secondary)]">→</span>
          </div>
        </div>
      </div>

      <!-- Bar Chart (CSS-only) -->
      <div class="mb-4">
        <h3 class="text-sm font-semibold text-[var(--color-text)] mb-3">
          {{ t('panel.examTrainer.progress.chartTitle') }}
        </h3>
        <div class="flex items-end gap-1.5 h-32">
          <div
            v-for="a in reversedAttempts"
            :key="a.attempt_id"
            class="flex-1 min-w-[12px] max-w-[40px] flex flex-col items-center gap-1"
          >
            <span class="text-[10px] text-[var(--color-text-secondary)]">
              {{ a.percentage ?? 0 }}%
            </span>
            <div
              :class="['w-full rounded-t-sm transition-all', barColor(a.percentage)]"
              :style="{ height: `${Math.max(4, ((a.percentage ?? 0) / chartMax) * 100)}%` }"
              :title="`${a.exam_title} — ${a.percentage}%`"
            />
            <span class="text-[9px] text-[var(--color-text-secondary)]">
              {{ formatDate(a.completed_at) }}
            </span>
          </div>
        </div>
        <!-- Pass line -->
        <div class="relative -mt-[calc(50%+1rem)] mb-[calc(50%+1rem)] pointer-events-none">
          <div class="border-t border-dashed border-amber-500/40 w-full" />
          <span class="text-[9px] text-amber-500/60 absolute -top-3 right-0">50%</span>
        </div>
      </div>

      <!-- History List -->
      <h3 class="text-sm font-semibold text-[var(--color-text)] mb-2">
        {{ t('panel.examTrainer.progress.historyTitle') }}
      </h3>
      <div class="space-y-2">
        <div
          v-for="a in attempts"
          :key="a.attempt_id"
          class="flex items-center justify-between p-3 rounded-lg bg-[var(--color-surface)]
                 border border-[var(--color-border)]"
        >
          <div>
            <div class="text-sm font-medium text-[var(--color-text)]">{{ a.exam_title }}</div>
            <div class="text-xs text-[var(--color-text-secondary)]">{{ formatDate(a.completed_at) }}</div>
          </div>
          <div class="flex items-center gap-3">
            <span
              :class="['text-sm font-bold',
                       (a.percentage ?? 0) >= 50 ? 'text-emerald-500' : 'text-red-500']"
            >
              {{ a.percentage ?? 0 }}%
            </span>
            <span
              :class="['text-xs px-2 py-0.5 rounded-full font-medium',
                       a.passed
                         ? 'bg-emerald-500/15 text-emerald-500'
                         : 'bg-red-500/15 text-red-500']"
            >
              {{ a.passed ? t('panel.examTrainer.passed') : t('panel.examTrainer.failed') }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
