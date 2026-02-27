/**
 * useSkillExecution — Skill catalog, selection, and execution
 */
import { ref, computed } from 'vue'
import type { SkillConfig, GenerationResult, BatchProgress } from '../types'
import {
  getSkillCatalog,
  executeSkill as executeSkillApi,
} from '@/infrastructure/api/clients/panel/editor/unified/unified.api'

export function useSkillExecution() {
  // ── State ───────────────────────────────────────────────────────
  const skills = ref<SkillConfig[]>([])
  const selectedSkill = ref<SkillConfig | null>(null)
  const currentResult = ref<GenerationResult | null>(null)
  const isLoadingCatalog = ref(false)
  const isExecuting = ref(false)
  const error = ref<string | null>(null)

  // Batch state
  const batchProgress = ref<BatchProgress>({
    total_steps: 0,
    completed_steps: 0,
    failed_steps: 0,
    current_step_index: 0,
    current_skill_code: null,
    is_running: false,
    is_paused: false,
  })

  // ── Computed ────────────────────────────────────────────────────
  const skillsByCategory = computed(() => {
    const groups: Record<string, SkillConfig[]> = {}
    for (const skill of skills.value) {
      if (!groups[skill.category]) groups[skill.category] = []
      groups[skill.category].push(skill)
    }
    return groups
  })

  const categories = computed(() => Object.keys(skillsByCategory.value))

  // ── Actions ─────────────────────────────────────────────────────

  async function loadCatalog() {
    isLoadingCatalog.value = true
    error.value = null
    try {
      skills.value = await getSkillCatalog()
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    } finally {
      isLoadingCatalog.value = false
    }
  }

  function selectSkill(skill: SkillConfig) {
    selectedSkill.value = skill
    currentResult.value = null
    error.value = null
  }

  function clearSelection() {
    selectedSkill.value = null
    currentResult.value = null
    error.value = null
  }

  async function execute(
    courseId: string,
    params: {
      targetType?: string
      targetId?: string
      parameters?: Record<string, unknown>
      promptOverride?: string
    } = {},
  ) {
    if (!selectedSkill.value) return
    if (!courseId) {
      error.value = 'No course selected'
      return
    }
    isExecuting.value = true
    error.value = null
    currentResult.value = null

    try {
      const result = await executeSkillApi({
        skill_code: selectedSkill.value.code,
        course_id: courseId,
        target_type: params.targetType as any,
        target_id: params.targetId,
        parameters: params.parameters,
        prompt_override: params.promptOverride,
      })
      currentResult.value = result
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    } finally {
      isExecuting.value = false
    }
  }

  function acceptResult(): GenerationResult | null {
    const result = currentResult.value
    currentResult.value = null
    selectedSkill.value = null
    return result
  }

  function rejectResult() {
    currentResult.value = null
  }

  return {
    skills,
    selectedSkill,
    currentResult,
    isLoadingCatalog,
    isExecuting,
    error,
    skillsByCategory,
    categories,
    batchProgress,
    loadCatalog,
    selectSkill,
    clearSelection,
    execute,
    acceptResult,
    rejectResult,
  }
}
