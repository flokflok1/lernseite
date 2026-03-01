/**
 * Unified AI Editor API Client
 *
 * Plans + Skills endpoints for the Unified AI Editor.
 * Base: /api/v1/course-editor/ai/
 */

import http from '@/infrastructure/api/http'
import type {
  ContentPlan,
  CreatePlanRequest,
  CreatePlanFromFileRequest,
  UpdatePlanRequest,
  CreatePhasedPlanRequest,
  PlanChatResponse,
  SkillConfig,
  ExecuteSkillRequest,
  BatchExecuteRequest,
  GenerationResult,
  GenerationHistoryEntry,
} from '@/presentation/components/panel/editor/ai/unified/types'

const BASE = '/course-editor/ai'

// ============================================================================
// Plans API
// ============================================================================

export async function createPlan(data: CreatePlanRequest): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans`, data)
  return res.data.data
}

export async function createPlanFromFile(data: CreatePlanFromFileRequest): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans`, { ...data, source: 'file' })
  return res.data.data
}

export async function getPlan(planId: string): Promise<ContentPlan> {
  const res = await http.get(`${BASE}/plans/${planId}`)
  return res.data.data
}

export async function updatePlan(planId: string, data: UpdatePlanRequest): Promise<ContentPlan> {
  const res = await http.patch(`${BASE}/plans/${planId}`, data)
  return res.data.data
}

export async function approvePlan(planId: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/approve`)
  return res.data.data
}

export async function executePlan(planId: string): Promise<{ plan_id: string; status: string }> {
  const res = await http.post(`${BASE}/plans/${planId}/execute`)
  return res.data.data
}

export async function pausePlan(planId: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/pause`)
  return res.data.data
}

export async function resumePlan(planId: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/resume`)
  return res.data.data
}

export async function archivePlan(planId: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/archive`)
  return res.data.data
}

export async function deletePlan(planId: string): Promise<void> {
  await http.delete(`${BASE}/plans/${planId}`)
}

export async function listPlans(courseId: string, limit = 20, offset = 0): Promise<ContentPlan[]> {
  const res = await http.get(`${BASE}/plans`, { params: { course_id: courseId, limit, offset } })
  return res.data.data
}

// ============================================================================
// Phase Wizard API
// ============================================================================

export async function createPhasedPlan(data: CreatePhasedPlanRequest): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/phased`, data)
  return res.data.data
}

export async function advanceToPhase2(planId: string, qualityLevel?: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/phase2`, {
    quality_level: qualityLevel || 'standard',
  })
  return res.data.data
}

export async function advanceToPhase3(planId: string, qualityLevel?: string): Promise<ContentPlan> {
  const res = await http.post(`${BASE}/plans/${planId}/phase3`, {
    quality_level: qualityLevel || 'standard',
  })
  return res.data.data
}

export async function sendPlanChat(planId: string, message: string, qualityLevel?: string): Promise<PlanChatResponse> {
  const res = await http.post(`${BASE}/plans/${planId}/chat`, {
    message,
    quality_level: qualityLevel || 'standard',
  })
  return res.data.data
}

export async function undoPlanChat(planId: string): Promise<{ plan: ContentPlan; undone: boolean }> {
  const res = await http.post(`${BASE}/plans/${planId}/undo`)
  return res.data.data
}

// ============================================================================
// Skills API
// ============================================================================

export async function getSkillCatalog(): Promise<SkillConfig[]> {
  const res = await http.get(`${BASE}/skills`)
  return res.data.data
}

export async function getSkill(code: string): Promise<SkillConfig> {
  const res = await http.get(`${BASE}/skills/${code}`)
  return res.data.data
}

export async function executeSkill(data: ExecuteSkillRequest): Promise<GenerationResult> {
  const res = await http.post(`${BASE}/skills/execute`, data)
  return res.data.data
}

export async function executeBatch(data: BatchExecuteRequest): Promise<GenerationResult[]> {
  const res = await http.post(`${BASE}/skills/batch`, data)
  return res.data.data
}

// ============================================================================
// History API
// ============================================================================

export async function getGenerationHistory(
  courseId: string,
  limit = 50,
  offset = 0
): Promise<GenerationHistoryEntry[]> {
  const res = await http.get(`${BASE}/skills/history`, {
    params: { course_id: courseId, limit, offset },
  })
  return res.data.data
}
