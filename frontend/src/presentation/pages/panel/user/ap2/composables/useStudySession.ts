/**
 * useStudySession — orchestriert den 3-Phasen Active-Recall-Flow für ein Topic.
 *
 * Lifecycle:
 *   start(slug) → Items laden + Session anlegen (Backend)
 *   submitAttempt(itemId, answer) → Backend bewertet → Feedback im State
 *   nextItem() → nächstes Item in aktueller Phase
 *   nextPhase() → wechselt zu nächster Phase (blurt → cued → application → done)
 *   end() → Session schließen + Reset
 */

import { ref, computed } from 'vue'
import {
  getAp2TopicDetail,
  startAp2Session,
  endAp2Session,
  submitAp2Attempt,
  type Ap2Item,
  type Ap2Topic,
  type Ap2SubmitResponse,
  type ItemType,
  type Phase,
} from '@/infrastructure/api/clients/panel/user/exams'

export type StudyPhase = 'blurt' | 'cued' | 'application' | 'done'
const PHASE_ORDER: StudyPhase[] = ['blurt', 'cued', 'application', 'done']

export function useStudySession() {
  const topic = ref<Ap2Topic | null>(null)
  const items = ref<Record<ItemType, Ap2Item[]>>({ blurt: [], cued: [], application: [] })
  const currentPhase = ref<StudyPhase>('blurt')
  const currentIndex = ref(0)
  const sessionId = ref<string | null>(null)

  const lastResponse = ref<Ap2SubmitResponse | null>(null)
  const phaseScores = ref<{ earned: number; total: number }>({ earned: 0, total: 0 })

  const loading = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const currentItems = computed(() =>
    currentPhase.value === 'done' ? [] : items.value[currentPhase.value as ItemType] ?? []
  )
  const currentItem = computed<Ap2Item | null>(
    () => currentItems.value[currentIndex.value] ?? null
  )
  const totalInPhase = computed(() => currentItems.value.length)
  const isLastInPhase = computed(
    () => currentIndex.value >= currentItems.value.length - 1
  )

  async function start(topicSlug: string) {
    loading.value = true
    error.value = null
    lastResponse.value = null
    phaseScores.value = { earned: 0, total: 0 }
    try {
      const detail = await getAp2TopicDetail(topicSlug)
      topic.value = detail.topic
      items.value = detail.items as Record<ItemType, Ap2Item[]>

      // Erste verfügbare Phase finden (manche Topics haben evtl. keine Blurts)
      currentPhase.value = pickFirstAvailablePhase(items.value)
      currentIndex.value = 0

      const session = await startAp2Session({
        session_type: 'topic_study',
        topic_id: detail.topic.topic_id,
        metadata: { phases_done: [] },
      })
      sessionId.value = session.session_id
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'unknown error'
    } finally {
      loading.value = false
    }
  }

  function pickFirstAvailablePhase(its: Record<ItemType, Ap2Item[]>): StudyPhase {
    for (const p of ['blurt', 'cued', 'application'] as StudyPhase[]) {
      if (its[p as ItemType]?.length > 0) return p
    }
    return 'done'
  }

  async function submitAnswer(answerText: string, qualityOverride?: number) {
    if (!currentItem.value || !sessionId.value) return
    submitting.value = true
    error.value = null
    try {
      const phase = currentPhase.value as Phase
      const res = await submitAp2Attempt({
        item_id: currentItem.value.item_id,
        phase,
        answer_text: answerText,
        session_id: sessionId.value,
        user_quality_override: qualityOverride,
      })
      lastResponse.value = res
      phaseScores.value.earned += res.points_earned
      phaseScores.value.total += res.points_total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'submit failed'
    } finally {
      submitting.value = false
    }
  }

  function nextItem() {
    lastResponse.value = null
    if (currentIndex.value < currentItems.value.length - 1) {
      currentIndex.value++
    } else {
      nextPhase()
    }
  }

  function nextPhase() {
    lastResponse.value = null
    currentIndex.value = 0
    const idx = PHASE_ORDER.indexOf(currentPhase.value)
    let next = PHASE_ORDER[idx + 1] ?? 'done'
    // Skippe Phasen ohne Items
    while (next !== 'done' && (items.value[next as ItemType]?.length ?? 0) === 0) {
      const ni = PHASE_ORDER.indexOf(next)
      next = PHASE_ORDER[ni + 1] ?? 'done'
    }
    currentPhase.value = next
  }

  async function end() {
    if (sessionId.value) {
      try {
        await endAp2Session(sessionId.value)
      } catch (e) {
        console.warn('[AP2] end session failed:', e)
      }
    }
    sessionId.value = null
  }

  return {
    topic, items, currentPhase, currentIndex, currentItem,
    totalInPhase, isLastInPhase, currentItems,
    lastResponse, phaseScores, sessionId,
    loading, submitting, error,
    start, submitAnswer, nextItem, nextPhase, end,
  }
}
