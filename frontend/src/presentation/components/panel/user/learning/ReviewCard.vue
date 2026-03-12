<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewItem } from '@/infrastructure/api/clients/panel/user/learning/reviews.api'

interface Props {
  item: ReviewItem
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'start-review': [methodId: string]
}>()
const { t } = useI18n()

const masteryColor = computed(() => {
  if (props.item.mastery_score >= 80) return 'text-green-600'
  if (props.item.mastery_score >= 50) return 'text-yellow-600'
  return 'text-red-600'
})

const difficultyClass = computed(() => ({
  easy: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  hard: 'bg-red-100 text-red-700',
}[props.item.difficulty_level]))
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between mb-2">
      <h3 class="font-medium text-sm truncate">{{ item.lm_title }}</h3>
      <span class="text-xs px-2 py-0.5 rounded-full" :class="difficultyClass">
        {{ t(`panel.review.difficulty.${item.difficulty_level}`) }}
      </span>
    </div>
    <p class="text-xs text-gray-500 mb-3">{{ item.chapter_title }}</p>
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-sm font-semibold" :class="masteryColor">
          {{ Math.round(item.mastery_score) }}%
        </span>
        <span v-if="item.current_streak > 0" class="text-xs text-orange-500">
          {{ t('panel.review.streak', { count: item.current_streak }) }}
        </span>
      </div>
      <button
        class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
        @click="emit('start-review', item.method_id)"
      >
        {{ t('panel.review.startReview') }}
      </button>
    </div>
  </div>
</template>
