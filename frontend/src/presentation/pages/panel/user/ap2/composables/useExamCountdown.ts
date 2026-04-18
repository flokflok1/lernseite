/**
 * useExamCountdown — berechnet Tage bis WISO + AP2.
 * Hardcoded auf BW-Termine 2026: WISO 11.05., AP2 12.05.
 */

import { computed, ref, onMounted, onUnmounted } from 'vue'

const WISO_DATE = '2026-05-11'
const AP2_DATE = '2026-05-12'

export function useExamCountdown() {
  const now = ref(new Date())

  let interval: ReturnType<typeof setInterval> | null = null
  onMounted(() => {
    interval = setInterval(() => { now.value = new Date() }, 60_000)  // jede Minute
  })
  onUnmounted(() => { if (interval) clearInterval(interval) })

  function daysUntil(dateStr: string): number {
    const target = new Date(dateStr)
    const diff = target.getTime() - now.value.getTime()
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
  }

  const daysToWiso = computed(() => daysUntil(WISO_DATE))
  const daysToAp2 = computed(() => daysUntil(AP2_DATE))

  return { daysToWiso, daysToAp2 }
}
