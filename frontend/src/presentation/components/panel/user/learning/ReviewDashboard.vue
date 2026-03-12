<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useReviewStore } from '@/application/stores/modules/learning/review.store'
import ReviewCard from './ReviewCard.vue'
import MasteryHeatmap from './MasteryHeatmap.vue'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'navigate-to-lm': [methodId: string]
  'navigate-to-chapter': [chapterId: string]
}>()
const { t } = useI18n()
const store = useReviewStore()

async function loadData() {
  await Promise.all([
    store.loadQueue(props.courseId),
    store.loadMastery(props.courseId),
  ])
}

onMounted(loadData)
watch(() => props.courseId, loadData)
</script>

<template>
  <div class="space-y-6">
    <!-- Stats Header -->
    <div v-if="store.stats" class="grid grid-cols-3 gap-4">
      <div class="rounded-lg bg-blue-50 p-4 text-center">
        <div class="text-2xl font-bold text-blue-700">{{ store.dueCount }}</div>
        <div class="text-xs text-blue-600">
          {{ t('panel.review.dueCount', { count: store.dueCount }) }}
        </div>
      </div>
      <div class="rounded-lg bg-green-50 p-4 text-center">
        <div class="text-2xl font-bold text-green-700">
          {{ store.stats.mastered_count }}
        </div>
        <div class="text-xs text-green-600">
          {{ t('panel.review.mastered', { count: store.stats.mastered_count }) }}
        </div>
      </div>
      <div class="rounded-lg bg-purple-50 p-4 text-center">
        <div class="text-2xl font-bold text-purple-700">
          {{ Math.round(store.avgMastery) }}%
        </div>
        <div class="text-xs text-purple-600">
          {{ t('panel.review.avgMastery', { pct: Math.round(store.avgMastery) }) }}
        </div>
      </div>
    </div>

    <!-- Review Queue -->
    <section v-if="store.queue.length > 0">
      <h2 class="text-lg font-semibold mb-3">{{ t('panel.review.title') }}</h2>
      <div class="grid gap-3 sm:grid-cols-2">
        <ReviewCard
          v-for="item in store.queue"
          :key="item.schedule_id"
          :item="item"
          @start-review="emit('navigate-to-lm', $event)"
        />
      </div>
    </section>

    <!-- No reviews message -->
    <div v-else-if="!store.loading" class="text-center py-8 text-gray-500">
      <p>{{ t('panel.review.noReviews') }}</p>
      <p v-if="store.stats?.next_review" class="text-sm mt-1">
        {{ t('panel.review.nextReview', { date: new Date(store.stats.next_review).toLocaleDateString() }) }}
      </p>
    </div>

    <!-- Mastery Heatmap -->
    <section v-if="store.mastery.length > 0">
      <h2 class="text-lg font-semibold mb-3">{{ t('panel.review.masteryTitle') }}</h2>
      <MasteryHeatmap
        :entries="store.mastery"
        @select-chapter="emit('navigate-to-chapter', $event)"
      />
    </section>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  </div>
</template>
