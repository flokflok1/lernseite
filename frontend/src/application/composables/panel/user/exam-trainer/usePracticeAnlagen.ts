/**
 * usePracticeAnlagen — Dynamic Anlagen loading with caching and prefetch.
 *
 * In practice mode, questions come from multiple exams. Each exam has its own
 * set of Anlagen (attachments like tables, diagrams, reference sheets).
 * This composable:
 *
 * 1. Tracks which exam the current question belongs to
 * 2. Loads Anlagen on exam change (not per-question — all questions in one exam share Anlagen)
 * 3. Caches loaded Anlagen so navigating back is instant
 * 4. Prefetches the next exam's Anlagen in the background for seamless transitions
 *
 * DDD Layer: Application (composable / use case orchestration)
 */

import { ref, watch, computed, type Ref } from 'vue'
import { trainerGetAnlagen, type Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface QuestionWithExam {
  exam_id?: string
  [key: string]: unknown
}

export function usePracticeAnlagen(
  questions: Ref<QuestionWithExam[]>,
  currentIndex: Ref<number>,
) {
  const currentAnlagen = ref<Anlage[]>([])
  const activeExamId = ref<string | null>(null)
  const isLoadingAnlagen = ref(false)

  // Cache: exam_id -> Anlage[]
  const cache = new Map<string, Anlage[]>()

  const currentExamTitle = computed(() => {
    const q = questions.value[currentIndex.value]
    return (q as Record<string, unknown>)?.exam_title as string || ''
  })

  async function loadAnlagen(examId: string): Promise<Anlage[]> {
    if (cache.has(examId)) {
      return cache.get(examId)!
    }
    try {
      const anlagen = await trainerGetAnlagen(examId)
      cache.set(examId, anlagen)
      return anlagen
    } catch {
      cache.set(examId, [])
      return []
    }
  }

  function findNextExamId(fromIndex: number): string | null {
    const currentExam = questions.value[fromIndex]?.exam_id
    for (let i = fromIndex + 1; i < questions.value.length; i++) {
      const eid = questions.value[i]?.exam_id
      if (eid && eid !== currentExam) return eid
    }
    return null
  }

  // Watch currentIndex — on exam change, swap Anlagen + prefetch next
  watch(currentIndex, async (idx) => {
    const q = questions.value[idx]
    const examId = q?.exam_id
    if (!examId || examId === activeExamId.value) return

    activeExamId.value = examId
    isLoadingAnlagen.value = true
    currentAnlagen.value = await loadAnlagen(examId)
    isLoadingAnlagen.value = false

    // Prefetch next exam's Anlagen in background
    const nextExamId = findNextExamId(idx)
    if (nextExamId && !cache.has(nextExamId)) {
      loadAnlagen(nextExamId)
    }
  }, { immediate: true })

  function reset() {
    cache.clear()
    activeExamId.value = null
    currentAnlagen.value = []
  }

  return {
    currentAnlagen,
    currentExamTitle,
    activeExamId,
    isLoadingAnlagen,
    reset,
  }
}
