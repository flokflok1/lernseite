/**
 * usePlanMode — Content Plan lifecycle management
 *
 * Manages: plan creation (manual + file), editing, approval, execution.
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  ContentPlan,
  PlanPhase,
  PlanStep,
  PlanScope,
  PlanStatus,
  WizardPhase,
  CourseMeta,
  ChapterDraft,
  PlanChatMessage,
} from '../types'
import {
  createPlan,
  createPlanFromFile,
  createPhasedPlan,
  advanceToPhase2,
  advanceToPhase3,
  sendPlanChat,
  getPlan,
  updatePlan,
  approvePlan,
  executePlan,
  listPlans,
  deletePlan as apiDeletePlan,
  archivePlan as apiArchivePlan,
} from '@/infrastructure/api/clients/panel/editor/unified/unified.api'

export function usePlanMode() {
  const { t } = useI18n()

  // ── State ───────────────────────────────────────────────────────
  const currentPlan = ref<ContentPlan | null>(null)
  const planHistory = ref<ContentPlan[]>([])
  const isCreating = ref(false)
  const isExecuting = ref(false)
  const error = ref<string | null>(null)

  // ── Phase Wizard State ────────────────────────────────────────
  const currentPhase = ref<WizardPhase>(1)
  const courseMeta = ref<CourseMeta | null>(null)
  const chapters = ref<ChapterDraft[]>([])
  const chatMessages = ref<PlanChatMessage[]>([])
  const isChatting = ref(false)

  // ── Computed ────────────────────────────────────────────────────
  const hasPlan = computed(() => !!currentPlan.value)
  const isDraft = computed(() => currentPlan.value?.status === 'draft')
  const isApproved = computed(() => currentPlan.value?.status === 'approved')
  const totalSteps = computed(() => {
    if (!currentPlan.value) return 0
    return currentPlan.value.phases.reduce((sum, p) => sum + p.steps.length, 0)
  })
  const completedSteps = computed(() => {
    if (!currentPlan.value) return 0
    return currentPlan.value.phases.reduce(
      (sum, p) => sum + p.steps.filter(s => s.status === 'completed').length, 0
    )
  })

  // ── Actions ─────────────────────────────────────────────────────

  async function createNewPlan(courseId: string, scope: PlanScope = 'course', scopeId?: string) {
    isCreating.value = true
    error.value = null
    try {
      const plan = await createPlan({ course_id: courseId, scope, scope_id: scopeId })
      currentPlan.value = _normalizePlan(plan)
    } catch (e: unknown) {
      _handleError(e, 'createNewPlan')
    } finally {
      isCreating.value = false
    }
  }

  async function createFromFile(courseId: string, fileId: string) {
    isCreating.value = true
    error.value = null
    try {
      const plan = await createPlanFromFile({ course_id: courseId, file_id: fileId })
      currentPlan.value = _normalizePlan(plan)
    } catch (e: unknown) {
      _handleError(e, 'createFromFile')
    } finally {
      isCreating.value = false
    }
  }

  async function loadPlan(planId: string) {
    error.value = null
    try {
      const plan = await getPlan(planId)
      currentPlan.value = _normalizePlan(plan)

      // Restore wizard phase from plan state
      const status = currentPlan.value.status
      if (status === 'executing' || status === 'completed' || status === 'paused' || status === 'approved') {
        currentPhase.value = 4
        if (status === 'executing') {
          isExecuting.value = true
          _startProgressPolling(planId)
        }
      } else if (currentPlan.value.current_phase) {
        currentPhase.value = currentPlan.value.current_phase as WizardPhase
      }
      // Restore sub-state
      courseMeta.value = currentPlan.value.course_meta || null
      chapters.value = currentPlan.value.chapters || []
      chatMessages.value = currentPlan.value.chat_history || []
    } catch (e: unknown) {
      _handleError(e, 'loadPlan')
    }
  }

  async function loadPlanHistory(courseId: string) {
    try {
      const plans = await listPlans(courseId)
      planHistory.value = (plans || []).map(_normalizePlan)
    } catch (e: unknown) {
      _handleError(e, 'loadPlanHistory')
    }
  }

  function reorderStep(phaseIndex: number, fromIndex: number, toIndex: number) {
    if (!currentPlan.value) return
    const phase = currentPlan.value.phases[phaseIndex]
    if (!phase) return
    const [moved] = phase.steps.splice(fromIndex, 1)
    phase.steps.splice(toIndex, 0, moved)
    phase.steps.forEach((s, i) => (s.order = i + 1))
  }

  function removeStep(phaseIndex: number, stepIndex: number) {
    if (!currentPlan.value) return
    currentPlan.value.phases[phaseIndex]?.steps.splice(stepIndex, 1)
  }

  function addStep(phaseIndex: number, step: PlanStep) {
    if (!currentPlan.value) return
    currentPlan.value.phases[phaseIndex]?.steps.push(step)
  }

  async function savePlan() {
    if (!currentPlan.value) return
    error.value = null
    try {
      const updated = await updatePlan(currentPlan.value.plan_id, {
        plan_data: { phases: currentPlan.value.phases },
      })
      currentPlan.value = _normalizePlan(updated)
    } catch (e: unknown) {
      _handleError(e, 'savePlan')
    }
  }

  async function approve() {
    if (!currentPlan.value) return
    error.value = null
    try {
      const updated = await approvePlan(currentPlan.value.plan_id)
      currentPlan.value = _normalizePlan(updated)
    } catch (e: unknown) {
      _handleError(e, 'approve')
    }
  }

  let _pollTimer: ReturnType<typeof setInterval> | null = null

  async function execute() {
    if (!currentPlan.value) return
    isExecuting.value = true
    error.value = null
    try {
      await executePlan(currentPlan.value.plan_id)
      // Backend returns 202 immediately — start polling for progress
      _startProgressPolling(currentPlan.value.plan_id)
    } catch (e: unknown) {
      _handleError(e, 'execute')
      isExecuting.value = false
    }
  }

  function _startProgressPolling(planId: string) {
    _stopProgressPolling()
    _pollTimer = setInterval(async () => {
      try {
        const plan = await getPlan(planId)
        if (currentPlan.value) {
          currentPlan.value = _normalizePlan(plan)
        }
        // Stop polling when execution is done
        if (plan.status !== 'executing') {
          _stopProgressPolling()
          isExecuting.value = false
        }
      } catch {
        // Ignore polling errors, keep trying
      }
    }, 3000)
  }

  function _stopProgressPolling() {
    if (_pollTimer) {
      clearInterval(_pollTimer)
      _pollTimer = null
    }
  }

  // ── Phase Wizard Actions ───────────────────────────────────────

  async function generatePhase1(courseId: string, topic?: string, fileIds?: string[]) {
    isCreating.value = true
    error.value = null
    try {
      const plan = await createPhasedPlan({
        course_id: courseId,
        topic,
        file_ids: fileIds,
      })
      currentPlan.value = _normalizePlan(plan)
      courseMeta.value = plan.course_meta || null
      currentPhase.value = 1
      chatMessages.value = []
    } catch (e: unknown) {
      _handleError(e, 'generatePhase1')
    } finally {
      isCreating.value = false
    }
  }

  async function confirmPhase() {
    if (!currentPlan.value) return
    const planId = currentPlan.value.plan_id

    isCreating.value = true
    error.value = null
    try {
      if (currentPhase.value === 1) {
        const plan = await advanceToPhase2(planId)
        currentPlan.value = _normalizePlan(plan)
        chapters.value = plan.chapters || []
        currentPhase.value = 2
      } else if (currentPhase.value === 2) {
        const plan = await advanceToPhase3(planId)
        currentPlan.value = _normalizePlan(plan)
        currentPhase.value = 3
      } else if (currentPhase.value === 3) {
        await approve()
        currentPhase.value = 4
      }
      chatMessages.value = []
    } catch (e: unknown) {
      _handleError(e, 'confirmPhase')
    } finally {
      isCreating.value = false
    }
  }

  function goBackToPhase(phase: WizardPhase) {
    if (phase < currentPhase.value) {
      currentPhase.value = phase
    }
  }

  async function sendPlanChatMessage(message: string): Promise<string> {
    if (!currentPlan.value) return ''

    isChatting.value = true
    error.value = null
    try {
      chatMessages.value.push({ role: 'user', content: message })
      const result = await sendPlanChat(currentPlan.value.plan_id, message)

      chatMessages.value.push({
        role: 'assistant',
        content: result.assistant_message,
      })

      if (result.plan) {
        currentPlan.value = _normalizePlan(result.plan)
        courseMeta.value = result.plan.course_meta || courseMeta.value
        chapters.value = result.plan.chapters || chapters.value
      }

      return result.assistant_message
    } catch (e: unknown) {
      _handleError(e, 'sendPlanChatMessage')
      return ''
    } finally {
      isChatting.value = false
    }
  }

  async function finalizePlan() {
    const planId = currentPlan.value?.plan_id
    if (!planId) return

    error.value = null
    try {
      await apiArchivePlan(planId)
    } catch (e) {
      console.warn('[usePlanMode] Archive failed, deleting instead:', e)
      try { await apiDeletePlan(planId) } catch { /* ignore */ }
    }

    // Reset UI state
    _stopProgressPolling()
    isExecuting.value = false
    currentPlan.value = null
    currentPhase.value = 1
    courseMeta.value = null
    chapters.value = []
    chatMessages.value = []
    planHistory.value = planHistory.value.filter(p => p.plan_id !== planId)
  }

  async function clearPlan() {
    const planId = currentPlan.value?.plan_id
    _stopProgressPolling()
    isExecuting.value = false
    currentPlan.value = null
    error.value = null
    currentPhase.value = 1
    courseMeta.value = null
    chapters.value = []
    chatMessages.value = []

    // Delete from backend if plan existed
    if (planId) {
      try {
        await apiDeletePlan(planId)
        planHistory.value = planHistory.value.filter(p => p.plan_id !== planId)
      } catch (e) {
        console.warn('[usePlanMode] Backend delete failed (plan cleared locally):', e)
      }
    }
  }

  async function deletePlanFromHistory(planId: string) {
    error.value = null
    try {
      await apiDeletePlan(planId)
      planHistory.value = planHistory.value.filter(p => p.plan_id !== planId)
    } catch (e: unknown) {
      _handleError(e, 'deletePlanFromHistory')
    }
  }

  // ── Error Helper ──────────────────────────────────────────────

  function _handleError(e: unknown, context: string) {
    const err = e as { response?: { data?: { error?: { message?: string } } }; message?: string }
    error.value = err.response?.data?.error?.message || err.message || String(e)
    console.error(`[usePlanMode] ${context} failed:`, e)
  }

  return {
    currentPlan,
    planHistory,
    isCreating,
    isExecuting,
    error,
    hasPlan,
    isDraft,
    isApproved,
    totalSteps,
    completedSteps,
    createNewPlan,
    createFromFile,
    loadPlan,
    loadPlanHistory,
    reorderStep,
    removeStep,
    addStep,
    savePlan,
    approve,
    execute,
    clearPlan,
    finalizePlan,
    deletePlanFromHistory,
    // Phase Wizard
    currentPhase,
    courseMeta,
    chapters,
    chatMessages,
    isChatting,
    generatePhase1,
    confirmPhase,
    goBackToPhase,
    sendPlanChatMessage,
  }
}

// ── Helpers ─────────────────────────────────────────────────────

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function _normalizePlan(raw: Record<string, any>): ContentPlan {
  const planData = typeof raw.plan_data === 'string' ? JSON.parse(raw.plan_data) : raw.plan_data
  const courseMeta = typeof raw.course_meta === 'string' ? JSON.parse(raw.course_meta) : raw.course_meta
  const chapters = typeof raw.chapters === 'string' ? JSON.parse(raw.chapters) : raw.chapters
  const chatHistory = typeof raw.chat_history === 'string' ? JSON.parse(raw.chat_history) : raw.chat_history
  return {
    plan_id: raw.plan_id,
    course_id: raw.course_id,
    current_phase: raw.current_phase,
    course_meta: courseMeta || undefined,
    chapters: chapters || undefined,
    chat_history: chatHistory || undefined,
    scope: raw.scope,
    scope_id: raw.scope_id,
    status: raw.status,
    phases: planData?.phases || [],
    estimated_total_tokens: raw.estimated_tokens || 0,
    actual_tokens: raw.actual_tokens || 0,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
  }
}
