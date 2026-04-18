/**
 * useAp2Stats — lädt + cached Dashboard-Daten aus dem AP2-Backend.
 * Bietet refresh() für manuelles Neuladen nach einem Attempt.
 */

import { ref, computed, onMounted } from 'vue'
import { getAp2Stats, type Ap2Stats } from '@/infrastructure/api/clients/panel/user/exams'

export function useAp2Stats(autoLoad = true) {
  const stats = ref<Ap2Stats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function load() {
    loading.value = true
    error.value = null
    try {
      stats.value = await getAp2Stats()
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'unknown error'
      error.value = msg
      console.warn('[AP2] stats load failed:', msg)
    } finally {
      loading.value = false
    }
  }

  if (autoLoad) onMounted(load)

  // Convenience-Computed
  const overall = computed(() => stats.value?.overall ?? null)
  const bereichStats = computed(() => stats.value?.bereich_stats ?? {})
  const bereichPass = computed(() => stats.value?.bereich_pass ?? {})
  const topicStats = computed(() => stats.value?.topic_stats ?? [])
  const weaknesses = computed(() => stats.value?.weaknesses ?? [])
  const recentRegressions = computed(() => stats.value?.recent_regressions ?? [])
  const reviewQueueCount = computed(() => stats.value?.review_queue_count ?? 0)

  return {
    stats,
    loading,
    error,
    refresh: load,
    overall,
    bereichStats,
    bereichPass,
    topicStats,
    weaknesses,
    recentRegressions,
    reviewQueueCount,
  }
}
