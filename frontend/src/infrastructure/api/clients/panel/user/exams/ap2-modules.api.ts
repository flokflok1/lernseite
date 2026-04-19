/**
 * AP2 Module API — Diagramm-Module mit Mastery-Loop.
 *
 * Endpoints unter /api/v1/user/exam-trainer/ap2/modules/*
 */

import http from '@/infrastructure/api/http'

const BASE = '/user/exam-trainer/ap2/modules'

export type ModuleStatus =
  | 'locked'
  | 'available'
  | 'learning'
  | 'pending_recall'
  | 'mastered'
  | 'review_failed'

export interface ModuleProgress {
  status: ModuleStatus
  streak_count: number
  total_attempts: number
  passed_attempts: number
  cooldown_until: string | null
  same_day_recall_due_at: string | null
  mastered_at: string | null
  spotcheck_stage: number
  next_spotcheck_at: string | null
}

export interface ModuleCard {
  module_id: string
  slug: string
  name_de: string
  description: string | null
  estimated_min: number
  difficulty: number
  sort_order: number
  prerequisite_slugs: string[]
  progress: ModuleProgress | null
}

export interface ModuleItem {
  item_id: string
  item_type: 'blurt' | 'cued' | 'application'
  prompt: string
  points: number
  difficulty: number
  estimated_time_sec: number
  calculator_hint: unknown
}

export interface ModuleStartResponse {
  module: ModuleCard
  theory_markdown: string | null
  first_item: ModuleItem | null
}

export interface ModuleSubmitResponse {
  pct: number
  passed: boolean
  points_earned: number
  feedback: {
    summary: string
    correct_aspects: string[]
    missing_aspects: string[]
    partial_aspects: string[]
    incorrect_aspects: string[]
    suggestions: string[]
  }
  progress: ModuleProgress
  next_item: ModuleItem | null
}

export async function listModules(): Promise<ModuleCard[]> {
  const res = await http.get<{ modules: ModuleCard[] }>(BASE)
  return res.data.modules
}

export async function startModule(moduleId: string): Promise<ModuleStartResponse> {
  const res = await http.post<ModuleStartResponse>(`${BASE}/${moduleId}/start`)
  return res.data
}

export async function submitModuleAnswer(
  moduleId: string,
  itemId: string,
  answer: string,
): Promise<ModuleSubmitResponse> {
  const res = await http.post<ModuleSubmitResponse>(
    `${BASE}/${moduleId}/submit`,
    { item_id: itemId, answer },
  )
  return res.data
}

export async function getRecallItem(moduleId: string): Promise<ModuleItem | null> {
  const res = await http.get<{ item: ModuleItem | null }>(`${BASE}/${moduleId}/recall-item`)
  return res.data.item
}

export async function getSpotcheckItem(moduleId: string): Promise<ModuleItem | null> {
  const res = await http.get<{ item: ModuleItem | null }>(`${BASE}/${moduleId}/spotcheck-item`)
  return res.data.item
}
