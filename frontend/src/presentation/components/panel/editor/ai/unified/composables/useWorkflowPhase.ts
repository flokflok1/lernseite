import { ref, computed } from 'vue'
import type { WorkflowPhase, GenerateProgress, GenerateResult } from '../types'
import { executeSkill as apiExecuteSkill } from '@/infrastructure/api/clients/panel/editor/unified/unified.api'
import { finalizeSession as apiFinalizeSession } from '@/infrastructure/api/clients/panel/editor/authoring/courseAuthoring.api'

export function useWorkflowPhase() {
  const phase = ref<WorkflowPhase>('plan')
  const generateProgress = ref<GenerateProgress | null>(null)
  const generateResult = ref<GenerateResult | null>(null)
  const isGenerating = ref(false)
  const error = ref<string | null>(null)
  let generationEpoch = 0

  const isPlan = computed(() => phase.value === 'plan')
  const isGenerate = computed(() => phase.value === 'generate')
  const isAccept = computed(() => phase.value === 'accept')
  const hasResult = computed(() => generateResult.value !== null)

  function setPhase(newPhase: WorkflowPhase): void {
    phase.value = newPhase
  }

  async function startGenerate(
    skillCode: string,
    courseId: string,
    options?: {
      targetType?: string
      targetId?: string
      parameters?: Record<string, unknown>
      promptOverride?: string
    }
  ): Promise<GenerateResult | null> {
    const epoch = ++generationEpoch
    phase.value = 'generate'
    isGenerating.value = true
    error.value = null
    generateProgress.value = {
      current: 0,
      total: 1,
      label: skillCode,
      percent: 0,
      skillCode,
    }

    try {
      const response = await apiExecuteSkill({
        skill_code: skillCode,
        course_id: courseId,
        target_type: options?.targetType as 'chapter' | 'lesson' | undefined,
        target_id: options?.targetId,
        parameters: options?.parameters || {},
        prompt_override: options?.promptOverride,
      })

      if (epoch !== generationEpoch) return null

      const result: GenerateResult = {
        generationId: response.generation_id,
        skillCode: response.skill_code || skillCode,
        content: response.content,
        tokensInput: response.tokens_input,
        tokensOutput: response.tokens_output,
        modelName: response.model_name,
        targetType: options?.targetType,
        targetId: options?.targetId,
      }

      generateResult.value = result
      generateProgress.value = { current: 1, total: 1, label: skillCode, percent: 100, skillCode }
      phase.value = 'accept'
      return result
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Generation failed'
      phase.value = 'plan'
      return null
    } finally {
      isGenerating.value = false
    }
  }

  function acceptResult(): GenerateResult | null {
    const result = generateResult.value
    generateResult.value = null
    generateProgress.value = null
    phase.value = 'plan'
    return result
  }

  function rejectResult(): void {
    generateResult.value = null
    generateProgress.value = null
    phase.value = 'plan'
  }

  async function finalize(sessionId: string): Promise<boolean> {
    isGenerating.value = true
    error.value = null
    try {
      await apiFinalizeSession(sessionId)
      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Finalization failed'
      return false
    } finally {
      isGenerating.value = false
    }
  }

  function reset(): void {
    generationEpoch++
    phase.value = 'plan'
    generateProgress.value = null
    generateResult.value = null
    isGenerating.value = false
    error.value = null
  }

  return {
    phase, generateProgress, generateResult, isGenerating, error,
    isPlan, isGenerate, isAccept, hasResult,
    setPhase, startGenerate, acceptResult, rejectResult, finalize, reset,
  }
}
