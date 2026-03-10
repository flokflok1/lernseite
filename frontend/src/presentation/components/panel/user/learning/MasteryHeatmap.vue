<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { MasteryEntry } from '@/infrastructure/api/clients/panel/user/learning/reviews.api'

interface Props {
  entries: MasteryEntry[]
}

defineProps<Props>()
const emit = defineEmits<{
  'select-chapter': [chapterId: string]
}>()
const { t } = useI18n()

function masteryBg(score: number): string {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-green-400'
  if (score >= 40) return 'bg-yellow-400'
  if (score >= 20) return 'bg-orange-400'
  return 'bg-red-400'
}
</script>

<template>
  <div class="space-y-2">
    <div
      v-for="entry in entries"
      :key="entry.chapter_id"
      class="flex items-center gap-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
      @click="emit('select-chapter', entry.chapter_id)"
    >
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-1">
          <span class="text-sm font-medium truncate">{{ entry.chapter_title }}</span>
          <span class="text-xs text-gray-500">
            {{ entry.mastered_lms }}/{{ entry.total_lms }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="h-2 rounded-full transition-all"
            :class="masteryBg(entry.avg_mastery)"
            :style="{ width: `${Math.round(entry.avg_mastery)}%` }"
          />
        </div>
      </div>
      <div v-if="entry.due_reviews > 0" class="flex-shrink-0">
        <span class="inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-white bg-red-500 rounded-full">
          {{ entry.due_reviews }}
        </span>
      </div>
    </div>
    <p v-if="entries.length === 0" class="text-sm text-gray-400 text-center py-4">
      {{ t('panel.review.noReviews') }}
    </p>
  </div>
</template>
