<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface QuestionStatus {
  questionId: string
  answered: boolean
  markedForReview: boolean
}

interface Props {
  statuses: QuestionStatus[]
  currentIndex: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  navigate: [index: number]
}>()

const { t } = useI18n()

const answeredCount = computed(() =>
  props.statuses.filter(s => s.answered).length
)

const reviewCount = computed(() =>
  props.statuses.filter(s => s.markedForReview).length
)

const progressPct = computed(() =>
  props.statuses.length > 0
    ? Math.round((answeredCount.value / props.statuses.length) * 100)
    : 0
)

const statusClass = (index: number): string => {
  if (index === props.currentIndex) return 'sim-nav-current'
  const s = props.statuses[index]
  if (!s) return 'sim-nav-open'
  if (s.markedForReview) return 'sim-nav-review'
  if (s.answered) return 'sim-nav-answered'
  return 'sim-nav-open'
}

const statusLabel = (index: number): string => {
  const s = props.statuses[index]
  if (!s) return ''
  if (index === props.currentIndex) return t('panel.examTrainer.simulation.navCurrent')
  if (s.markedForReview) return t('panel.examTrainer.simulation.navReview')
  if (s.answered) return t('panel.examTrainer.simulation.navAnswered')
  return t('panel.examTrainer.simulation.navOpen')
}
</script>

<template>
  <aside class="w-[220px] min-w-[220px] bg-[var(--color-surface)] border-r border-[var(--color-border)]
                flex flex-col gap-2 p-3 overflow-y-auto">
    <!-- Header -->
    <div class="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider pb-1
                border-b border-[var(--color-border)]">
      {{ t('panel.examTrainer.simulation.questions') }}
    </div>

    <!-- Progress -->
    <div class="py-1.5">
      <div class="flex justify-between text-xs text-[var(--color-text-secondary)] mb-1">
        <span>{{ t('panel.examTrainer.simulation.progress', { done: answeredCount, total: statuses.length }) }}</span>
        <span v-if="reviewCount > 0" class="text-purple-400">
          {{ t('panel.examTrainer.simulation.reviewCount', { count: reviewCount }) }}
        </span>
      </div>
      <div class="h-1.5 bg-[var(--color-border)] rounded-full overflow-hidden">
        <div
          class="h-full bg-emerald-500 rounded-full transition-all duration-300"
          :style="{ width: progressPct + '%' }"
        />
      </div>
    </div>

    <!-- Legend -->
    <div class="flex flex-wrap gap-2 py-1 text-[11px] text-[var(--color-text-secondary)]">
      <span class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-sm bg-[var(--color-border)]" />
        {{ t('panel.examTrainer.simulation.legendOpen') }}
      </span>
      <span class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-sm bg-emerald-500" />
        {{ t('panel.examTrainer.simulation.legendAnswered') }}
      </span>
      <span class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-sm bg-purple-500" />
        {{ t('panel.examTrainer.simulation.legendReview') }}
      </span>
    </div>

    <!-- Grid Navigation -->
    <div class="grid grid-cols-5 gap-1">
      <button
        v-for="(_, idx) in statuses"
        :key="idx"
        :class="['aspect-square flex items-center justify-center rounded-md text-xs font-semibold',
                 'cursor-pointer border-2 transition-all duration-150', statusClass(idx)]"
        :aria-label="t('panel.examTrainer.simulation.navLabel', { num: idx + 1, status: statusLabel(idx) })"
        @click="emit('navigate', idx)"
      >
        {{ idx + 1 }}
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sim-nav-open {
  background: var(--color-border);
  color: var(--color-text-secondary);
  border-color: transparent;
}
.sim-nav-open:hover { border-color: var(--color-text-secondary); }

.sim-nav-answered {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: #10b981;
}

.sim-nav-current {
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
  border-color: #3b82f6;
}

.sim-nav-review {
  background: rgba(139, 92, 246, 0.12);
  color: #8b5cf6;
  border-color: #8b5cf6;
}
</style>
