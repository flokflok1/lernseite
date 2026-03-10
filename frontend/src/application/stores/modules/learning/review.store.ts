/**
 * Review Store — Spaced Repetition state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ReviewItem, ReviewStats, MasteryEntry } from
  '@/infrastructure/api/clients/panel/user/learning/reviews.api'
import {
  fetchReviewQueue, fetchMasteryMap, fetchReviewStats, submitReview,
} from '@/infrastructure/api/clients/panel/user/learning/reviews.api'

export const useReviewStore = defineStore('review', () => {
  const queue = ref<ReviewItem[]>([])
  const stats = ref<ReviewStats | null>(null)
  const mastery = ref<MasteryEntry[]>([])
  const loading = ref(false)

  const dueCount = computed(() => stats.value?.due_count ?? 0)
  const avgMastery = computed(() => stats.value?.avg_mastery ?? 0)
  const hasDueReviews = computed(() => dueCount.value > 0)

  async function loadQueue(courseId: string) {
    loading.value = true
    try {
      const result = await fetchReviewQueue(courseId)
      queue.value = result.items
      stats.value = result.stats
    } finally {
      loading.value = false
    }
  }

  async function loadMastery(courseId: string) {
    mastery.value = await fetchMasteryMap(courseId)
  }

  async function loadStats(courseId: string) {
    stats.value = await fetchReviewStats(courseId)
  }

  async function processReview(
    methodId: string, score: number, timeSeconds: number,
  ) {
    const result = await submitReview(methodId, score, timeSeconds)
    queue.value = queue.value.filter(item => item.method_id !== methodId)
    return result
  }

  function $reset() {
    queue.value = []
    stats.value = null
    mastery.value = []
    loading.value = false
  }

  return {
    queue, stats, mastery, loading,
    dueCount, avgMastery, hasDueReviews,
    loadQueue, loadMastery, loadStats, processReview, $reset,
  }
})
