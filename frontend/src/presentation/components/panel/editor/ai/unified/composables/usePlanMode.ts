/**
 * usePlanMode — Content Plan lifecycle management
 *
 * Manages: plan creation (manual + file), editing, approval, execution.
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ContentPlan, PlanPhase, PlanStep } from '../types'
import {
  createPlan,
  createPlanFromFile,
  getPlan,
  updatePlan,
  approvePlan,
  executePlan,
  listPlans,
} from '@/infrastructure/api/clients/panel/editor/unified/unified.api'

export function usePlanMode() {
  const { t } = useI18n()

  // ── State ───────────────────────────────────────────────────────
  const currentPlan = ref<ContentPlan | null>(null)
  const planHistory = ref<ContentPlan[]>([])
  const isCreating = ref(false)
  const isExecuting = ref(false)
  const error = ref<string | null>(null)

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

  async function createNewPlan(courseId: string, scope = 'course', scopeId?: string) {
    isCreating.value = true
    error.value = null
    try {
      const plan = await createPlan({ course_id: courseId, scope: scope as any, scope_id: scopeId })
      currentPlan.value = _normalizePlan(plan)
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
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
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    } finally {
      isCreating.value = false
    }
  }

  async function loadPlan(planId: string) {
    error.value = null
    try {
      const plan = await getPlan(planId)
      currentPlan.value = _normalizePlan(plan)
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    }
  }

  async function loadPlanHistory(courseId: string) {
    try {
      const plans = await listPlans(courseId)
      planHistory.value = (plans || []).map(_normalizePlan)
    } catch (e: any) {
      error.value = e.message
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
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    }
  }

  async function approve() {
    if (!currentPlan.value) return
    error.value = null
    try {
      const updated = await approvePlan(currentPlan.value.plan_id)
      currentPlan.value = _normalizePlan(updated)
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    }
  }

  async function execute() {
    if (!currentPlan.value) return
    isExecuting.value = true
    error.value = null
    try {
      const result = await executePlan(currentPlan.value.plan_id)
      if (currentPlan.value) {
        currentPlan.value.status = result.status as any
      }
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    } finally {
      isExecuting.value = false
    }
  }

  function clearPlan() {
    currentPlan.value = null
    error.value = null
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
  }
}

// ── Helpers ─────────────────────────────────────────────────────

function _normalizePlan(raw: any): ContentPlan {
  const planData = typeof raw.plan_data === 'string' ? JSON.parse(raw.plan_data) : raw.plan_data
  return {
    plan_id: raw.plan_id,
    course_id: raw.course_id,
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
